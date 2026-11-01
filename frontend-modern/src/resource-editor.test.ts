import { describe, expect, it } from 'vitest';
import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';
import { richSubmission } from './resource-editor.fixtures';
import { resourceContract } from '../../backend/elixir/resource-contract.generated';
import {
  backendErrorsToEditor, currentEditorPath, editorToResource, editorToSubmission,
  newEditorItem, resourceToEditor, type Resource,
} from './resource-editor';

describe('resource editor data contract', () => {
  it.each(['minimal', 'rich'] as const)('round trips %s without changing its source', key => {
    const original = structuredClone(fixtures[key]);
    const editor = resourceToEditor(fixtures[key]);
    expect(editorToResource(editor)).toEqual(original);
    const snapshot = editorToSubmission(editor);
    expect(snapshot.payload).toEqual(key === 'rich' ? richSubmission : original);
    expect(snapshot.normalizations.map(item => item.reason)).toEqual(key === 'rich' ? Array(8).fill('edam-label-from-uri') : []);
    expect(snapshot.blockers).toEqual([]);
    expect(fixtures[key]).toEqual(original);
    expect(Object.keys(fixtures.rich).sort()).toEqual(Object.keys(resourceContract.fields).sort());
  });

  it('edits one basic field or nested field without dropping unrelated data', () => {
    const editor = resourceToEditor(fixtures.rich);
    editor.name = 'Changed name';
    expect(editorToSubmission(editor).payload).toEqual({ ...richSubmission, name: 'Changed name' });
    editor.function[0].value.output![1].value.data.term = 'Changed term';
    const expected = structuredClone(fixtures.rich);
    expected.name = editor.name;
    expected.function[0].output![1].data.term = 'Changed term';
    expect(editorToResource(editor)).toEqual(expected);
    expect(editorToSubmission(editor).payload).toEqual({ ...richSubmission, name: 'Changed name' });
    expect(fixtures.rich.function[0].output![1].data.term).toBe('Sequence name');
  });

  it('keeps IDs with items across nested add/remove/reorder, including scalar lists', () => {
    const editor = resourceToEditor(fixtures.rich);
    const retained = editor.function[0];
    editor.function.reverse();
    retained.value.output!.reverse();
    retained.value.output!.splice(1, 1);
    retained.value.output!.push(newEditorItem({ data: { uri: 'http://edamontology.org/data_0863', term: 'Sequence' } }));
    editor.version.reverse();
    editor.version.push(newEditorItem('3.0'));
    expect(editor.function[1]).toBe(retained);
    const payload = editorToSubmission(editor).payload;
    expect(payload.version).toEqual(['2.0', '1.0', '3.0']);
    expect(payload.function).toEqual([
      richSubmission.function[1],
      { ...richSubmission.function[0], output: [richSubmission.function[0].output![1],
        { data: { uri: 'http://edamontology.org/data_0863' } }] },
    ]);
    expect(JSON.stringify(payload)).not.toContain(retained.id);
    expect(JSON.stringify(payload)).not.toContain('itemId');
    expect(editorToResource(editor).function[1].output![1].data.term).toBe('Sequence');
  });

  it('maps delayed errors using the submitted snapshot, never current indices', () => {
    const editor = resourceToEditor(fixtures.rich);
    const func = editor.function[0];
    const output = func.value.output![1];
    const publicationId = editor.publication[0].id;
    const submitted = editorToSubmission(editor);
    editor.function.reverse();
    func.value.output!.reverse();
    editor.publication.splice(0, 1);
    editor.publication.unshift(newEditorItem(fixtures.rich.publication[0]));
    const errors = backendErrorsToEditor(fixtures.errors, submitted);
    expect(errors.map(error => error.path)).toEqual([
      ['name'], ['function', { itemId: func.id }, 'output', { itemId: output.id }, 'data'],
      ['publication', { itemId: publicationId }], [],
    ]);
    expect(currentEditorPath(editor, errors[1].path!)).toEqual(['function', 1, 'value', 'output', 0, 'value', 'data']);
    expect(currentEditorPath(editor, errors[2].path!)).toBeNull();
    func.value.output!.splice(0, 1);
    expect(currentEditorPath(editor, errors[1].path!)).toBeNull();
    expect(submitted.payload).toEqual(richSubmission);
    expect(Object.isFrozen(submitted.payload.function)).toBe(true);
    expect(() => { (submitted.payload as Resource).name = 'Mutation'; }).toThrow();
  });

  it('handles missing fields, scalar item errors, numeric dictionaries and global messages', () => {
    const editor = resourceToEditor({ version: ['1', '2'], function: [{ output: [{}] }] });
    const snapshot = editorToSubmission(editor);
    const errors = backendErrorsToEditor({ name: ['Required.'], version: [[], ['Invalid version.']],
      function: { '0': { output: { '0': { data: ['Required.'] } } }, '9': { cmd: ['Out of range.'] } },
      detail: 'Permission denied.', general_errors: ['Resource error.'] }, snapshot);
    expect(errors[0].path).toEqual(['name']);
    expect(errors[1].path).toEqual(['version', { itemId: editor.version[1].id }]);
    expect(errors[2].path).toEqual(['function', { itemId: editor.function[0].id }, 'output',
      { itemId: editor.function[0].value.output[0].id }, 'data']);
    expect(errors[3].path).toBeNull();
    expect(errors.slice(4).map(error => error.path)).toEqual([[], []]);
    expect(backendErrorsToEditor(['Failure.'], snapshot)[0].path).toEqual([]);
  });

  it('preserves missing/null/blank/list distinctions locally and reports only allowed omissions', () => {
    const resource: Resource = { ...fixtures.minimal, license: null, version: [], additionDate: null,
      name: '', description: null, editPermission: { type: 'group', authors: [] },
      function: [{ operation: [], input: [{ data: null, format: [] }], note: '', cmd: null }],
      publication: [{ pmid: '12345', note: '', type: [], metadata: null }],
      topic: [{ uri: 'http://edamontology.org/topic_0091', term: null }] };
    const editor = resourceToEditor(resource);
    expect(editorToResource(editor)).toEqual(resource);
    const snapshot = editorToSubmission(editor);
    expect(snapshot.payload).toEqual({ ...fixtures.minimal, additionDate: null, name: '', description: null,
      editPermission: { type: 'group', authors: [] },
      function: [{ operation: [], input: [{ data: null }], note: '' }],
      publication: [{ pmid: '12345', note: '', metadata: null }],
      topic: [{ uri: 'http://edamontology.org/topic_0091' }] });
    expect(snapshot.normalizations.map(item => item.reason)).toEqual([
      'optional-null-to-absent', 'optional-empty-list-to-absent', 'optional-empty-list-to-absent',
      'optional-null-to-absent', 'optional-empty-list-to-absent', 'edam-label-from-uri',
    ]);
    expect(snapshot.blockers).toEqual([]);
    expect(editorToResource(editor)).toEqual(resource);
  });

  it('retains enriched metadata and protected IDs while blocking unknown fields', () => {
    const resource = { ...fixtures.rich, homepage_status: 2, elixir_badge: 4,
      futureField: { id: 'public-id', value: null, items: [] },
      publication: [{ pmid: '12345', metadata: { title: 'Preserved title', authors: [{ name: 'Author' }] } }] };
    const editor = resourceToEditor(resource);
    expect(editorToResource(editor)).toEqual(resource);
    const snapshot = editorToSubmission(editor);
    expect(snapshot.payload).toEqual({ ...resource, function: richSubmission.function, topic: richSubmission.topic });
    expect(snapshot.blockers.map(item => item.reason)).toEqual(['unsupported-field']);
    expect(editorToSubmission(resourceToEditor({ ...fixtures.minimal, community: {} })).blockers)
      .toEqual([{ path: ['community'], reason: 'unsupported-field' }]);
    const protectedIds = resourceToEditor({ ...fixtures.minimal, otherID: [
      { value: 'biotools:previous-id', type: 'biotoolsCURIE' }, { value: 'DOI:10.1234/example' },
    ] });
    const protectedSnapshot = editorToSubmission(protectedIds);
    expect(protectedSnapshot.payload).toEqual(editorToResource(protectedIds));
    expect(protectedSnapshot.blockers).toEqual([]);
    const unusual = JSON.parse('{"name":"x","__proto__":{"polluted":true}}');
    expect(editorToResource(resourceToEditor(unusual))).toEqual(unusual);
    expect(editorToSubmission(resourceToEditor(unusual)).blockers[0].path).toEqual(['__proto__']);
    expect(({} as { polluted?: boolean }).polluted).toBeUndefined();
  });

  it('rejects non-JSON values and duplicate identities instead of silently corrupting data', () => {
    const cyclic: Record<string, unknown> = {};
    cyclic.self = cyclic;
    for (const value of [[], null, 'not an object', { x: undefined }, { x: NaN }, { x: new Date() },
      { x: [ , 'sparse'] }, cyclic]) {
      expect(() => resourceToEditor(value as object)).toThrow(TypeError);
    }
    const editor = resourceToEditor({ version: ['1', '1'] });
    expect(editor.version[0].id).not.toBe(editor.version[1].id);
    editor.version.push(editor.version[0]);
    expect(() => editorToSubmission(editor)).toThrow('unique client IDs');
    expect(() => editorToSubmission({ name: undefined })).toThrow('delete absent properties');
    expect(() => editorToSubmission(cyclic)).toThrow('acyclic JSON');
  });
});
