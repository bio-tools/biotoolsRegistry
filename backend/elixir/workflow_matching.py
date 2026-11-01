"""Bounded, relationship-aware candidate scans for workflow design."""
from collections import defaultdict
from hashlib import sha256
from urllib.parse import quote

from django.core import signing
from django.db.models import Count, Exists, OuterRef, Q
from django.db.models.functions import Lower, SHA256
from django.utils import timezone

from elixir.edam_lookup import EdamUnavailable, EdamVocabulary, nodes
from elixir.models import Data, Format, Function, Input, Operation, Output, Resource
from elixir.resource_schema import digest
from elixir.resource_ui import SchemaUnavailable, resource_descriptor

SCAN_LIMIT = 100
RELATED_LIMIT = 200
CURSOR_AGE = 900
PREFILTER_LIMIT = 5000
SALT = 'biotools.workflow-matching.v1'


class StaleCursor(ValueError):
    pass


def public_shape(descriptor):
    """Refuse to expose fields if the active schema no longer permits this projection."""
    try:
        root = descriptor['contract']['fields']
        function = root['function']
        fields = function['item']['fields']
        checks = [all(root[key]['public'] for key in ('biotoolsID', 'name')),
                  function['public'] and function['kind'] == 'array' and function['item']['kind'] == 'object']
        operation = fields['operation']
        checks.append(operation['public'] and operation['kind'] == 'array' and operation['item']['kind'] == 'object')
        checks.append(all(operation['item']['fields'][key]['public'] for key in ('uri', 'term')))
        for direction in ('input', 'output'):
            io = fields[direction]
            checks.append(io['public'] and io['kind'] == 'array' and io['item']['kind'] == 'object')
            data, formats = io['item']['fields']['data'], io['item']['fields']['format']
            checks.append(data['public'] and data['kind'] == 'object')
            checks.append(formats['public'] and formats['kind'] == 'array' and formats['item']['kind'] == 'object')
            checks.append(all(data['fields'][key]['public'] and formats['item']['fields'][key]['public'] for key in ('uri', 'term')))
        if not all(checks):
            raise SchemaUnavailable('The active schema cannot safely describe workflow matching.')
    except (KeyError, TypeError) as exc:
        raise SchemaUnavailable('The active schema cannot safely describe workflow matching.') from exc


def parent_map(vocabulary):
    parents = defaultdict(set)
    try:
        for node in nodes(vocabulary.validator.EDAM_Ontology):
            parent = node['data']['uri']
            for child in node.get('children', []):
                parents[child['data']['uri']].add(parent)
    except (KeyError, TypeError) as exc:
        raise EdamUnavailable('EDAM relationships are temporarily unavailable.') from exc
    return parents


def ancestors(uri, parents):
    seen, pending = set(), list(parents.get(uri, ()))
    while pending:
        value = pending.pop()
        if value not in seen:
            seen.add(value)
            pending.extend(parents.get(value, ()))
    return seen


def evidence(requested, annotations, vocabulary, parents, mode, direction, ancestor_cache=None):
    if not requested:
        return {'state': 'not_requested'}
    known = vocabulary.current
    obsolete = vocabulary.obsolete
    usable = [item.get('uri') for item in annotations if isinstance(item.get('uri'), str) and item['uri']]
    reasons = set()
    if not annotations:
        reasons.add('missing')
    for item in annotations:
        uri = item.get('uri')
        if not uri:
            reasons.add('term_only' if item.get('term') else 'missing')
        elif uri in obsolete:
            reasons.add('obsolete')
        elif uri not in known:
            reasons.add('unrecognized')
    if requested in usable:
        return {'state': 'exact', 'requested': requested, 'matched': requested,
                'obsolete': requested in obsolete}
    if mode == 'related':
        def hierarchy(uri):
            if ancestor_cache is None:
                return ancestors(uri, parents)
            if uri not in ancestor_cache:
                ancestor_cache[uri] = ancestors(uri, parents)
            return ancestor_cache[uri]
        for uri in usable:
            if uri not in known or requested not in known:
                continue
            if uri in hierarchy(requested):
                relation = 'requested_more_specific'
            elif requested in hierarchy(uri):
                relation = 'annotated_more_specific'
            else:
                continue
            return {'state': 'related', 'requested': requested, 'matched': uri,
                    'relation': relation, 'direction': direction}
    if reasons:
        return {'state': 'unknown', 'requested': requested, 'reasons': sorted(reasons)}
    return {'state': 'conflict', 'requested': requested, 'annotated': usable}


def matching_parameters(parameters):
    allowed = {'direction', 'data', 'format', 'operation', 'mode', 'include', 'limit', 'cursor'}
    if set(parameters) - allowed or any(len(values) != 1 for _, values in parameters.lists()):
        raise ValueError('Unsupported or repeated matching parameter.')
    direction = parameters.get('direction', '')
    if direction not in ('input', 'output'):
        raise ValueError('Choose input or output direction.')
    selected = {scope: parameters.get(scope, '') for scope in ('data', 'format', 'operation')}
    if not selected['data'] and not selected['format']:
        raise ValueError('Choose a data type or format.')
    mode = parameters.get('mode', 'exact')
    include = parameters.get('include', 'matches')
    if mode not in ('exact', 'related') or include not in ('matches', 'unknown', 'all'):
        raise ValueError('Choose a supported match mode and inclusion policy.')
    raw_limit = parameters.get('limit', '20')
    if not raw_limit.isascii() or not raw_limit.isdecimal() or not 1 <= int(raw_limit) <= 50:
        raise ValueError('Choose a result limit between 1 and 50.')
    return {'direction': direction, **selected, 'mode': mode, 'include': include, 'limit': int(raw_limit)}


def annotations(items):
    return sorted(({'uri': item.uri, 'term': item.term} for item in items),
                  key=lambda item: (item['uri'] or '', item['term'] or ''))


def compare_annotations(payload):
    if not isinstance(payload, dict) or set(payload) != {'output', 'input'}:
        raise ValueError('Supply an output and input annotation.')
    for item in payload.values():
        if (not isinstance(item, dict) or set(item) != {'data', 'formats'} or not isinstance(item['formats'], list) or
                len(item['formats']) > RELATED_LIMIT or any(not isinstance(term, dict) for term in item['formats'])):
            raise ValueError('Invalid input/output annotation.')
        for term in [item['data'], *item['formats']]:
            if term is not None and (not isinstance(term, dict) or
                    any(value is not None and (not isinstance(value, str) or len(value) > 1000) for value in (term.get('uri'), term.get('term')))):
                raise ValueError('Invalid annotation value.')
    descriptor = resource_descriptor()
    public_shape(descriptor)
    vocabularies = {scope: EdamVocabulary(scope) for scope in ('data', 'format')}
    dimensions = {}
    for scope in ('data', 'format'):
        source = [payload['output']['data']] if scope == 'data' and payload['output']['data'] else payload['output']['formats'] if scope == 'format' else []
        target = [payload['input']['data']] if scope == 'data' and payload['input']['data'] else payload['input']['formats'] if scope == 'format' else []
        vocab = vocabularies[scope]
        parents = parent_map(vocab)
        values, ancestry = [], {}
        for annotation in source:
            uri = annotation.get('uri') if annotation else None
            if not uri or uri not in vocab.current:
                values.append({'state': 'unknown', 'reasons': ['obsolete' if uri in vocab.obsolete else 'unrecognized' if uri else 'missing']})
            else:
                result = evidence(uri, target, vocab, parents, 'related', 'input', ancestry)
                values.append({'state': 'unknown', 'reasons': ['obsolete']} if result.get('obsolete') else result)
            if values[-1]['state'] == 'exact':
                break
        dimensions[scope] = min(values, key=lambda value: {'exact': 0, 'related': 1, 'unknown': 2, 'conflict': 3}[value['state']]) if values else {'state': 'unknown', 'reasons': ['missing']}
    states = {item['state'] for item in dimensions.values()}
    state = next(value for value in ('conflict', 'unknown', 'related', 'exact') if value in states)
    return {'state': state, 'dimensions': dimensions, 'schemaRevision': descriptor['revision'],
            'vocabularyRevisions': {scope: vocab.revision for scope, vocab in vocabularies.items()}}


def reference(kind, *parts):
    return signing.Signer(salt='biotools.workflow-reference.' + kind).signature(':'.join(str(part) for part in parts))


def matching_uris(requested, vocabulary, parents, mode):
    values = {requested}
    if mode == 'related' and requested in vocabulary.current:
        values.update(ancestors(requested, parents) & vocabulary.current.keys())
        values.update(uri for uri in vocabulary.current if requested in ancestors(uri, parents))
    return values


def uri_hashes(uris):
    try:
        return [sha256(uri.encode('utf-8')).hexdigest() for uri in uris]
    except (AttributeError, UnicodeEncodeError) as exc:
        raise EdamUnavailable('EDAM terms are temporarily unavailable.') from exc


def possible_ids(model, field, possible, vocabulary):
    # URI comparisons must stay case-sensitive even under a case-insensitive database collation.
    records = model.objects.alias(_workflow_uri_hash=SHA256('uri')).filter(
        Q(uri__in=possible) | Q(uri__isnull=True) | Q(uri='') | Q(_workflow_uri_hash__isnull=True) |
        Q(_workflow_uri_hash__in=uri_hashes(vocabulary.obsolete)) |
        ~Q(_workflow_uri_hash__in=uri_hashes(vocabulary.current)))
    if field != 'pk':
        records = records.filter(**{field + '__isnull': False})
    values = set(records.values_list(field, flat=True).order_by().distinct()[:PREFILTER_LIMIT + 1])
    # shortcut: broad candidate sets fall back to scanning, add a scalable index if measured load requires it.
    return values if len(values) <= PREFILTER_LIMIT else None


def function_details(token):
    if not token or len(token) > 2048:
        raise ValueError('Invalid function reference.')
    try:
        ref = signing.loads(token, salt='biotools.workflow-function.v1')
        resource_id, function_id = ref['resource'], ref['function']
        if type(resource_id) is not int or type(function_id) is not int:
            raise ValueError('Invalid function reference.')
    except (signing.BadSignature, KeyError, TypeError) as exc:
        raise ValueError('Invalid function reference.') from exc
    descriptor = resource_descriptor()
    public_shape(descriptor)
    function = Function.objects.select_related('resource').filter(pk=function_id, resource_id=resource_id,
                                                                  resource__visibility=1).first()
    if not function:
        return None
    resource = function.resource
    if Resource.objects.filter(visibility=1, biotoolsID__iexact=resource.biotoolsID).count() != 1:
        raise SchemaUnavailable('Duplicate visible resource identifiers require administrator repair.')
    operations = list(function.operation.all()[:RELATED_LIMIT + 1])
    if len(operations) > RELATED_LIMIT:
        raise SchemaUnavailable('The function has too many operations to inspect safely.')
    result = {}
    for direction in ('input', 'output'):
        records = list(getattr(function, direction).select_related('data').order_by('pk')[:RELATED_LIMIT + 1])
        if len(records) > RELATED_LIMIT or Format.objects.filter(**{direction + '_id__in': [record.pk for record in records]}).count() > RELATED_LIMIT:
            raise SchemaUnavailable('The function has too many annotations to inspect safely.')
        from django.db.models import prefetch_related_objects
        prefetch_related_objects(records, 'format')
        result[direction] = [{'id': reference(direction, function.pk, row.pk),
                              'data': annotations([row.data])[0] if row.data_id else None,
                              'formats': annotations(row.format.all())} for row in records]
    if not Function.objects.filter(pk=function.pk, resource_id=resource.pk, resource__visibility=1).exists():
        return None
    return {'resource': {'id': resource.biotoolsID, 'name': resource.name,
                         'url': '/' + quote(resource.biotoolsID, safe=''),
                         'revision': {'token': reference('resource', resource.pk, resource.lastUpdate)}},
            'function': {'id': reference('function', resource.pk, function.pk), 'token': token,
                         'operations': annotations(operations), **result},
            'schemaRevision': descriptor['revision']}


def matching_candidates(parameters):
    query = matching_parameters(parameters)
    descriptor = resource_descriptor()
    public_shape(descriptor)
    vocabularies = {scope: EdamVocabulary(scope) for scope in ('data', 'format', 'operation') if query[scope]}
    parents = {}
    for scope, vocabulary in vocabularies.items():
        vocabulary.resolve([query[scope]], multiple=False)
        parents[scope] = parent_map(vocabulary) if query['mode'] == 'related' else {}
    revisions = {scope: vocabulary.revision for scope, vocabulary in vocabularies.items()}
    bound = digest({'query': query, 'schema': descriptor['revision'], 'vocabulary': revisions})
    cursor = parameters.get('cursor', '')
    phase, after = 'io', 0
    if cursor:
        if len(cursor) > 2048:
            raise ValueError('Invalid matching cursor.')
        try:
            state = signing.loads(cursor, salt=SALT, max_age=CURSOR_AGE)
        except signing.BadSignature as exc:
            raise ValueError('Invalid or expired matching cursor.') from exc
        if not isinstance(state, dict) or state.get('bound') != bound:
            raise StaleCursor('The query, schema or vocabulary changed. Restart the search.')
        phase, after = state.get('phase'), state.get('after')
        if phase not in ('io', 'missing') or type(after) is not int or after < 0:
            raise ValueError('Invalid matching cursor.')

    direction = query['direction']
    model = Input if direction == 'input' else Output
    if phase == 'missing' and query['include'] == 'matches':
        raise ValueError('Invalid matching cursor.')
    rows = (model.objects.filter(function__resource__visibility=1, pk__gt=after)
            .select_related('data', 'function__resource').order_by('pk') if phase == 'io' else
            Function.objects.filter(resource__visibility=1, pk__gt=after, **{direction + '__isnull': True})
            .select_related('resource').order_by('pk'))
    if query['include'] != 'all':
        possible = {scope: matching_uris(query[scope], vocabulary, parents[scope], query['mode'])
                    for scope, vocabulary in vocabularies.items()}
        uncertain = query['include'] == 'unknown'
        if phase == 'io' and query['data']:
            if uncertain:
                data_ids = possible_ids(Data, 'pk', possible['data'], vocabularies['data'])
                if data_ids is not None:
                    rows = rows.filter(Q(data_id__in=data_ids) | Q(data_id__isnull=True))
            else:
                rows = rows.filter(data__uri__in=possible['data'])
        if phase == 'io' and query['format']:
            formats = Format.objects.filter(**{direction + '_id': OuterRef('pk')}, uri__in=possible['format'])
            if not uncertain:
                rows = rows.filter(Exists(formats))
        if query['operation']:
            operations = Operation.objects.filter(function_id=OuterRef('function_id' if phase == 'io' else 'pk'))
            if uncertain:
                function_ids = possible_ids(Operation, 'function_id', possible['operation'], vocabularies['operation'])
                if function_ids is not None:
                    missing = set(Function.objects.filter(resource__visibility=1, operation__isnull=True)
                                  .values_list('pk', flat=True).order_by()[:PREFILTER_LIMIT + 1])
                    if len(function_ids | missing) <= PREFILTER_LIMIT:
                        rows = rows.filter(**{('function_id' if phase == 'io' else 'pk') + '__in': function_ids | missing})
            else:
                rows = rows.filter(Exists(operations.filter(uri__in=possible['operation'])))
    batch = list(rows[:SCAN_LIMIT + 1])
    scan = batch[:SCAN_LIMIT]
    function_ids = {row.function_id if phase == 'io' else row.pk for row in scan}
    if Operation.objects.filter(function_id__in=function_ids).values('function_id').annotate(n=Count('pk')).filter(n__gt=RELATED_LIMIT).exists():
        raise SchemaUnavailable('A function has too many operations to inspect safely.')
    if phase == 'io' and Format.objects.filter(**{direction + '_id__in': [row.pk for row in scan]}).values(direction + '_id').annotate(n=Count('pk')).filter(n__gt=RELATED_LIMIT).exists():
        raise SchemaUnavailable('An annotation has too many formats to inspect safely.')
    from django.db.models import prefetch_related_objects
    prefetch_related_objects(scan, 'format', 'function__operation') if phase == 'io' else prefetch_related_objects(scan, 'operation')
    resource_ids = {(row.function.resource.biotoolsID if phase == 'io' else row.resource.biotoolsID).lower() for row in scan}
    duplicate_ids = Resource.objects.filter(visibility=1, biotoolsID__in=resource_ids).annotate(
        identifier=Lower('biotoolsID')).values('identifier').annotate(n=Count('pk')).filter(n__gt=1)
    if duplicate_ids.exists():
        raise SchemaUnavailable('Duplicate visible resource identifiers require administrator repair.')

    current_ids = set(Resource.objects.filter(visibility=1, pk__in={
        row.function.resource_id if phase == 'io' else row.resource_id for row in scan
    }).values_list('pk', flat=True))

    items, last, scanned = [], after, 0
    for row in scan:
        function = row.function if phase == 'io' else row
        resource = function.resource
        if resource.pk not in current_ids:
            last, scanned = row.pk, scanned + 1
            continue
        operations = annotations(function.operation.all())
        data = annotations([row.data]) if phase == 'io' and row.data_id else []
        formats = annotations(row.format.all()) if phase == 'io' else []
        found = {scope: evidence(query[scope], values, vocabularies.get(scope), parents.get(scope, {}), query['mode'], direction)
                 for scope, values in (('data', data), ('format', formats), ('operation', operations))}
        states = {value['state'] for value in found.values()}
        accepted = query['include'] == 'all' or ('conflict' not in states and (query['include'] == 'unknown' or 'unknown' not in states))
        last, scanned = row.pk, scanned + 1
        if accepted:
            version = {'token': reference('resource', resource.pk, resource.lastUpdate)}
            fingerprint = reference('candidate', resource.pk, function.pk, row.pk if phase == 'io' else '', direction,
                                    digest({'version': version, 'operation': operations, 'data': data, 'format': formats}))
            items.append({'resource': {'id': resource.biotoolsID, 'name': resource.name, 'url': '/' + quote(resource.biotoolsID, safe=''),
                                       'revision': version},
                          'function': {'id': reference('function', resource.pk, function.pk), 'operations': operations,
                                       'token': signing.dumps({'resource': resource.pk, 'function': function.pk},
                                                              salt='biotools.workflow-function.v1')},
                          'io': {'id': reference(direction, function.pk, row.pk) if phase == 'io' else None, 'direction': direction,
                                 'data': data[0] if data else None, 'formats': formats},
                          'referenceFingerprint': fingerprint, 'evidence': found})
            if len(items) == query['limit']:
                break
    more = scanned < len(batch)
    if not more and phase == 'io' and query['include'] != 'matches':
        phase, last, more = 'missing', 0, True
    next_cursor = signing.dumps({'bound': bound, 'phase': phase, 'after': last}, salt=SALT, compress=True) if more else None
    return {'items': items, 'schemaRevision': descriptor['revision'], 'vocabularyRevisions': revisions,
            'source': {'type': 'database', 'observedAt': timezone.now().isoformat(),
                       'consistency': 'live', 'revision': None, 'scope': 'visible-recorded-functions',
                       'note': 'Resources without a recorded function are not included.'},
            'pagination': {'next': next_cursor, 'complete': not more, 'completeScope': 'live-scan',
                           'scanned': scanned, 'scanLimit': SCAN_LIMIT,
                           'note': 'Live data can change between pages; restart for a fresh scan.'}}
