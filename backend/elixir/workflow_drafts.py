"""Validation for portable, non-executable workflow descriptions."""
import json

MAX_BYTES = 1_000_000


def validate_graph(graph):
    def text(value, *, empty=True):
        if not isinstance(value, str) or (not empty and not value):
            return False
        try:
            return len(value.encode('utf-16-le')) <= 2000
        except UnicodeEncodeError:
            return False

    def term(value):
        return (isinstance(value, dict) and all(key in value and (value[key] is None or text(value[key]))
                                                for key in ('uri', 'term')))

    def ios(value):
        return (isinstance(value, list) and len(value) <= 200 and
                all(isinstance(io, dict) and text(io.get('id'), empty=False) and 'data' in io and
                    (io['data'] is None or term(io['data'])) and isinstance(io.get('formats'), list) and
                    len(io['formats']) <= 200 and all(term(item) for item in io['formats']) for io in value) and
                len({io['id'] for io in value}) == len(value))

    if not isinstance(graph, dict) or type(graph.get('version')) is not int or graph['version'] != 1:
        raise ValueError('Unsupported workflow draft version.')
    steps, edges = graph.get('steps'), graph.get('connections')
    if not isinstance(steps, list) or len(steps) > 100 or not isinstance(edges, list) or len(edges) > 300:
        raise ValueError('Invalid workflow graph size.')
    try:
        if len(json.dumps(graph, ensure_ascii=False, allow_nan=False).encode('utf-8')) > MAX_BYTES:
            raise ValueError('The workflow draft is too large.')
    except (TypeError, RecursionError) as exc:
        raise ValueError('Invalid workflow draft.') from exc
    by_id = {}
    for step in steps:
        if not isinstance(step, dict) or not text(step.get('id'), empty=False) or step['id'] in by_id:
            raise ValueError('Invalid or duplicate workflow step.')
        resource, function, selection = step.get('resource'), step.get('function'), step.get('selection')
        vocab = step.get('vocabularyRevisions')
        if (not isinstance(resource, dict) or not text(resource.get('id')) or not text(resource.get('name')) or
                not isinstance(resource.get('revision'), dict) or not text(resource['revision'].get('token')) or
                not text(step.get('note')) or not text(step.get('schemaRevision')) or not isinstance(vocab, dict) or
                any(key not in ('data', 'format', 'operation') or not text(value) for key, value in vocab.items()) or
                not isinstance(function, dict) or not text(function.get('id'), empty=False) or
                not text(function.get('token'), empty=False) or not isinstance(function.get('operations'), list) or
                len(function['operations']) > 200 or not all(term(item) for item in function['operations']) or
                not ios(function.get('input')) or not ios(function.get('output')) or not isinstance(selection, dict) or
                selection.get('direction') not in ('input', 'output') or 'ioId' not in selection or not text(selection.get('fingerprint')) or
                not isinstance(selection.get('evidence'), dict)):
            raise ValueError('Invalid workflow step snapshot.')
        io_id = selection.get('ioId')
        if io_id is not None and (not text(io_id, empty=False) or not any(io['id'] == io_id for io in function[selection['direction']])):
            raise ValueError('The selected annotation is missing from the step snapshot.')
        for scope, evidence in selection['evidence'].items():
            if (scope not in ('data', 'format', 'operation') or not isinstance(evidence, dict) or
                    evidence.get('state') not in ('exact', 'related', 'unknown', 'conflict', 'not_requested') or
                    ('relation' in evidence and not text(evidence['relation'])) or
                    ('obsolete' in evidence and type(evidence['obsolete']) is not bool) or
                    ('reasons' in evidence and (not isinstance(evidence['reasons'], list) or
                     len(evidence['reasons']) > 10 or not all(text(reason) for reason in evidence['reasons'])))):
                raise ValueError('Invalid workflow selection evidence.')
        by_id[step['id']] = step
    edge_ids, pairs, adjacency = set(), set(), {key: [] for key in by_id}
    for edge in edges:
        if not isinstance(edge, dict) or not text(edge.get('id'), empty=False) or edge['id'] in edge_ids or not text(edge.get('reason')):
            raise ValueError('Invalid workflow connection.')
        source, target = edge.get('from'), edge.get('to')
        if not isinstance(source, dict) or not isinstance(target, dict):
            raise ValueError('Invalid workflow connection endpoint.')
        src, dst = source.get('step'), target.get('step')
        if not text(src, empty=False) or not text(dst, empty=False) or src not in by_id or dst not in by_id or src == dst:
            raise ValueError('Invalid workflow connection endpoint.')
        output = next((io for io in by_id[src]['function']['output'] if io['id'] == source.get('io')), None)
        input_io = next((io for io in by_id[dst]['function']['input'] if io['id'] == target.get('io')), None)
        if not output or not input_io:
            raise ValueError('Invalid workflow connection annotation.')
        pair = (src, source['io'], dst, target['io'])
        if pair in pairs:
            raise ValueError('Duplicate workflow connection.')
        data_uri = (output.get('data') or {}).get('uri')
        exact_data = bool(data_uri) and data_uri == (input_io.get('data') or {}).get('uri')
        formats = {item.get('uri') for item in output['formats'] if item.get('uri')}
        exact_format = any(item.get('uri') in formats for item in input_io['formats'] if item.get('uri'))
        state = edge.get('evidence')
        if (state not in ('exact', 'related', 'unknown', 'conflict') or
                (state == 'exact' and not (exact_data and exact_format)) or (state != 'exact' and not edge['reason'].strip())):
            raise ValueError('Invalid workflow connection evidence.')
        dimensions = edge.get('dimensions')
        if 'dimensions' in edge:
            if not isinstance(dimensions, dict) or any(scope not in ('data', 'format') or not isinstance(value, dict) or
                    value.get('state') not in ('exact', 'related', 'unknown', 'conflict') or
                    ('relation' in value and not text(value['relation'])) or
                    ('reasons' in value and (not isinstance(value['reasons'], list) or len(value['reasons']) > 10 or
                                              not all(text(reason) for reason in value['reasons']))) for scope, value in dimensions.items()):
                raise ValueError('Invalid workflow connection details.')
        revisions = edge.get('vocabularyRevisions')
        if (('schemaRevision' in edge and not text(edge['schemaRevision'])) or
                ('vocabularyRevisions' in edge and (not isinstance(revisions, dict) or
                 any(scope not in ('data', 'format') or not text(value) for scope, value in revisions.items())))):
            raise ValueError('Invalid workflow connection revisions.')
        pending, seen = [dst], set()
        while pending:
            node = pending.pop()
            if node == src:
                raise ValueError('Workflow connections cannot contain cycles.')
            if node not in seen:
                seen.add(node)
                pending.extend(adjacency[node])
        adjacency[src].append(dst)
        edge_ids.add(edge['id'])
        pairs.add(pair)
    return graph
