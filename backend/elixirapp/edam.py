from django import forms
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_safe

from elixir.edam_lookup import EdamUnavailable, EdamVocabulary, LIMIT, SCOPES, check_scope, check_uri


@require_safe
def lookup(request):
    try:
        allowed = {'scope', 'branch', 'q', 'id', 'suggest'}
        for key, values in request.GET.lists():
            if key not in allowed or (key not in ('id', 'suggest') and len(values) != 1):
                raise ValueError('Unsupported or repeated lookup parameter.')
        scope, branch = request.GET.get('scope', ''), request.GET.get('branch', '')
        check_scope(scope)
        query = request.GET.get('q', '')
        if len(query) > 128 or any(ord(char) < 32 or ord(char) == 127 for char in query):
            raise ValueError('Use at most 128 characters without control characters.')
        query = query.strip()
        ids, suggestions = request.GET.getlist('id'), request.GET.getlist('suggest')
        for values in (ids, suggestions):
            if len(values) > LIMIT:
                raise ValueError('Choose at most 20 terms.')
            for uri in values:
                check_uri(uri, scope)
        if ids and ('q' in request.GET or suggestions):
            raise ValueError('Resolve identifiers separately from term searches.')
        vocabulary = EdamVocabulary(scope, branch)
        body = {'items': vocabulary.resolve(ids), 'more': False, 'suggestions': []} if ids else vocabulary.search(query, suggestions)
        body['vocabulary'] = {'name': 'EDAM', 'scope': scope, 'source': 'registry Ontology table', 'revision': vocabulary.revision}
        response = JsonResponse(body)
        response['Cache-Control'] = 'no-store'
        return response
    except ValueError as exc:
        return JsonResponse({'error': {'code': 'invalid_edam', 'message': str(exc)}}, status=400)
    except EdamUnavailable:
        return JsonResponse({'error': {'code': 'edam_unavailable', 'message': 'EDAM terms are temporarily unavailable. Please retry.'}}, status=503)


class EdamField(forms.Field):
    widget = forms.MultipleHiddenInput

    def __init__(self, scope, *, multiple=True, branch='', **kwargs):
        self.scope, self.multiple, self.branch = scope, multiple, branch
        super().__init__(**kwargs)

    def clean(self, value):
        identifiers = [item for item in (value or []) if item]
        if not identifiers:
            self.validate(identifiers)
            return []
        try:
            return EdamVocabulary(self.scope, self.branch).resolve(identifiers, self.multiple)
        except (ValueError, EdamUnavailable) as exc:
            raise forms.ValidationError(str(exc)) from exc


class AnnotationForm(forms.Form):
    label = forms.CharField(max_length=120, label='Annotation label')
    topic = EdamField('topic', required=False)
    operation = EdamField('operation', required=False)
    data = EdamField('data', multiple=False, required=False)
    format = EdamField('format', required=False)


@require_http_methods(['GET', 'HEAD', 'POST'])
def preview(request):
    form = AnnotationForm(request.POST if request.method == 'POST' else None)
    valid = form.is_valid() if form.is_bound else False
    selectors = []
    for scope in SCOPES:
        field = form[scope]
        identifiers = [value for value in (field.value() or []) if value][:LIMIT]
        selectors.append({'scope': scope, 'field': field, 'identifiers': identifiers,
                          'config': {'scope': scope, 'label': scope.capitalize(), 'name': scope,
                                     'multiple': scope != 'data', 'initial': identifiers,
                                     'initialTerms': form.cleaned_data.get(scope, []) if form.is_bound else [],
                                     'endpoint': reverse('html:edam-lookup')}})
    payload = None
    if valid:
        def values(scope):
            return [{'uri': item['uri'], 'term': item['term']} for item in form.cleaned_data[scope]]
        payload = {'topic': values('topic'), 'operation': values('operation'),
                   'input': {'data': next(iter(values('data')), None), 'format': values('format')}}
    return render(request, 'html/edam.html', {'form': form, 'selectors': selectors, 'payload': payload},
                  status=400 if form.is_bound and not valid else 200)
