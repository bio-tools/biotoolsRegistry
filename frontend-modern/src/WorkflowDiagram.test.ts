import { mount } from '@vue/test-utils';
import { expect, it } from 'vitest';
import WorkflowDiagram from './WorkflowDiagram.vue';
import type { Graph, Step } from './workflow-graph';

const step = (id: string): Step => ({
  id, resource: { id, name: `Tool ${id}`, revision: { token: 'r' } }, note: '', schemaRevision: 's', vocabularyRevisions: {},
  selection: { direction: 'input', ioId: 'i', fingerprint: '', evidence: {} },
  function: { id, token: 'f', operations: [{ uri: 'operation', term: 'Alignment' }],
    input: [{ id: 'i', data: { uri: 'data', term: 'Sequences' }, formats: [{ uri: 'format', term: 'FASTA' }] }],
    output: [{ id: 'o', data: { uri: 'data', term: 'Sequences' }, formats: [{ uri: 'format', term: 'FASTA' }] }] },
});

it('shows annotated steps and distinguishes reviewed and unreviewed branches', async () => {
  const graph: Graph = { version: 1, steps: ['a', 'b', 'c'].map(step), connections: [
    { id: 'ab', from: { step: 'a', io: 'o' }, to: { step: 'b', io: 'i' }, evidence: 'exact', reason: '' },
    { id: 'ac', from: { step: 'a', io: 'o' }, to: { step: 'c', io: 'i' }, evidence: 'related', reason: 'Review' },
  ] };
  const wrapper = mount(WorkflowDiagram, { props: { graph, unreviewedEdges: ['ac'], needsReview: [] } });
  expect(wrapper.text()).toContain('Alignment');
  expect(wrapper.text()).toContain('Sequences');
  expect(wrapper.text()).toContain('FASTA');
  expect(wrapper.text()).toContain('1. exact');
  expect(wrapper.text()).toContain('2. Unreviewed');
  expect(wrapper.findAll('path[marker-end]')).toHaveLength(2);
  expect(wrapper.findAll('path[marker-end]')[1]!.attributes('stroke-dasharray')).toBe('6 4');
  graph.steps[0]!.function.input = [];
  await wrapper.setProps({ graph: { ...graph } });
  expect(wrapper.text()).toContain('Not annotated');
});
