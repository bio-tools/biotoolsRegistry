import { describe, expect, it } from 'vitest';
import { connect, readDraft, type Graph, type Step } from './workflow-graph';

const step = (id: string): Step => ({ id, resource: { id, name: id, revision: { token: 'r' } }, note: '', schemaRevision: 's', vocabularyRevisions: {},
  selection: { direction: 'input', ioId: 'i', fingerprint: 'p', evidence: {} },
  function: { id, token: 'f', operations: [], input: [{ id: 'i', data: { uri: 'data', term: '' }, formats: [{ uri: 'format', term: '' }] }],
    output: [{ id: 'o', data: { uri: 'data', term: '' }, formats: [{ uri: 'format', term: '' }] }] } });

describe('workflow graph', () => {
  it('allows branches and blocks duplicate, missing, self and cyclic connections', () => {
    const graph: Graph = { version: 1, steps: ['a', 'b', 'c'].map(step), connections: [] };
    const add = (from: string, to: string) => connect(graph, { step: from, io: 'o' }, { step: to, io: 'i' }, '', from + to);
    graph.connections.push(add('a', 'b'), add('a', 'c'));
    expect(graph.connections).toHaveLength(2);
    expect(() => add('a', 'b')).toThrow('already exists');
    expect(() => add('a', 'a')).toThrow('different steps');
    expect(() => add('b', 'a')).toThrow('cycle');
    expect(() => add('missing', 'a')).toThrow('different steps');
  });
  it('requires an explanation when annotations do not establish an exact match', () => {
    const graph: Graph = { version: 1, steps: [step('a'), step('b')], connections: [] };
    graph.steps[1].function.input[0].formats = [];
    const from = { step: 'a', io: 'o' }, to = { step: 'b', io: 'i' };
    expect(() => connect(graph, from, to, '', 'x')).toThrow('Explain');
    expect(connect(graph, from, to, 'Verify manually', 'x').evidence).toBe('unknown');
  });
  it('restores valid graphs and rejects tampered connections and duplicate identifiers', () => {
    const graph: Graph = { version: 1, steps: [step('a'), step('b')], connections: [] };
    graph.connections.push(connect(graph, { step: 'a', io: 'o' }, { step: 'b', io: 'i' }, '', 'one'));
    expect(readDraft(JSON.stringify(graph))).toEqual(graph);
    graph.connections.push({ id: 'two', from: { step: 'b', io: 'o' }, to: { step: 'a', io: 'i' }, evidence: 'exact', reason: '' });
    expect(() => readDraft(JSON.stringify(graph))).toThrow('cycle');
    graph.connections = [];
    graph.steps.push(step('a'));
    expect(() => readDraft(JSON.stringify(graph))).toThrow('invalid step');
  });
  it('keeps earlier prototype exports as unresolved snapshots', () => {
    const old: any = step('a');
    delete old.selection; delete old.schemaRevision; delete old.vocabularyRevisions;
    const restored = readDraft(JSON.stringify({ version: 1, steps: [old], connections: [] }));
    expect(restored.steps[0].schemaRevision).toBe('');
    expect(restored.steps[0].selection.ioId).toBeNull();
  });
  it('rejects malformed Unicode but keeps normal supplementary characters', () => {
    const graph: Graph = { version: 1, steps: [step('a')], connections: [] };
    graph.steps[0].note = '🧬';
    expect(readDraft(JSON.stringify(graph)).steps[0].note).toBe('🧬');
    graph.steps[0].note = '\uD800';
    expect(() => readDraft(JSON.stringify(graph))).toThrow('invalid step');
  });
  it('preserves compatible extension fields without trusting stored edge evidence', () => {
    const graph: Graph = { version: 1, steps: [step('a'), step('b')], connections: [] };
    graph.connections.push(connect(graph, { step: 'a', io: 'o' }, { step: 'b', io: 'i' }, '', 'one'));
    const extended = JSON.parse(JSON.stringify(graph));
    extended.extra = { purpose: 'Teaching' };
    extended.connections[0].extra = 'Retain this';
    const restored: any = readDraft(JSON.stringify(extended));
    expect(restored.extra).toEqual({ purpose: 'Teaching' });
    expect(restored.connections[0].extra).toBe('Retain this');
    expect(restored.connections[0].evidence).toBe('exact');
    extended.connections[0].evidence = 'forged';
    expect(() => readDraft(JSON.stringify(extended))).toThrow('inconsistent connection evidence');
  });
});
