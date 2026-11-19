<script setup lang="ts">
import type { Graph, IO, Term } from './workflow-graph';

defineProps<{ graph: Graph; unreviewedEdges: string[]; needsReview: string[] }>();
const term = (value: Term | null) => value?.term || (value?.uri ? 'Unlabelled EDAM term' : 'Unknown');
const io = (items: IO[]) => items.length ? `${term(items[0]!.data)} / ${items[0]!.formats.map(term).join(', ') || 'Unknown format'}${items.length > 1 ? ` (+${items.length - 1})` : ''}` : 'Not annotated';
const dataLabel = (items: IO[]) => items.length ? term(items[0]!.data) + (items.length > 1 ? ` (+${items.length - 1})` : '') : 'Not annotated';
const formatLabel = (items: IO[]) => items.length ? items[0]!.formats.map(term).join(', ') || 'Unknown format' : 'Not annotated';
const short = (value: string) => value.length > 26 ? value.slice(0, 25) + '…' : value;
const position = (graph: Graph, id: string) => graph.steps.findIndex(step => step.id === id) * 150 + 75;
</script>

<template>
  <div class="diagram" role="region" tabindex="0" aria-label="Workflow diagram, scroll horizontally to see connections">
    <svg :viewBox="`0 0 800 ${graph.steps.length * 150}`" role="img" aria-label="Connections between workflow steps; details and controls follow">
      <defs><marker id="workflow-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#425f6b" /></marker></defs>
      <g v-for="(edge, index) in graph.connections" :key="edge.id">
        <title>{{ edge.evidence }} connection from {{ graph.steps.find(step => step.id === edge.from.step)?.resource.name }} to {{ graph.steps.find(step => step.id === edge.to.step)?.resource.name }}</title>
        <path :d="`M 590 ${position(graph, edge.from.step)} C ${Math.min(760, 640 + index * 18)} ${position(graph, edge.from.step)}, ${Math.min(760, 640 + index * 18)} ${position(graph, edge.to.step)}, 590 ${position(graph, edge.to.step)}`"
          fill="none" stroke="#425f6b" stroke-width="2" :stroke-dasharray="edge.evidence === 'exact' && !unreviewedEdges.includes(edge.id) && !needsReview.includes(edge.from.step) && !needsReview.includes(edge.to.step) ? undefined : '6 4'" marker-end="url(#workflow-arrow)" />
        <text x="602" :y="(position(graph, edge.from.step) + position(graph, edge.to.step)) / 2 + (index % 3 - 1) * 14" class="connection-label">{{ index + 1 }}. {{ unreviewedEdges.includes(edge.id) || needsReview.includes(edge.from.step) || needsReview.includes(edge.to.step) ? 'Unreviewed' : edge.evidence }}</text>
      </g>
      <g v-for="(step, index) in graph.steps" :key="step.id" :transform="`translate(5 ${index * 150 + 10})`">
        <title>{{ step.resource.name }}. Inputs: {{ io(step.function.input) }}. Operations: {{ step.function.operations.map(term).join(', ') || 'Not annotated' }}. Outputs: {{ io(step.function.output) }}.</title>
        <rect width="580" height="130" rx="8" fill="#fff" stroke="#aecbd7" />
        <text x="12" y="23" class="step-title">{{ index + 1 }}. {{ short(step.resource.name) }}</text>
        <rect x="10" y="34" width="180" height="82" rx="5" fill="var(--edam-data)" />
        <rect x="10" y="86" width="180" height="30" rx="5" fill="var(--edam-format)" />
        <rect x="200" y="34" width="180" height="82" rx="5" fill="var(--edam-operation)" />
        <rect x="390" y="34" width="180" height="82" rx="5" fill="var(--edam-data)" />
        <rect x="390" y="86" width="180" height="30" rx="5" fill="var(--edam-format)" />
        <text x="18" y="55" class="diagram-label">INPUT</text><text x="208" y="55" class="diagram-label">OPERATION</text><text x="398" y="55" class="diagram-label">OUTPUT</text>
        <text x="18" y="78">{{ short(dataLabel(step.function.input)) }}</text>
        <text x="208" y="78">{{ short(step.function.operations.map(term).join(', ') || 'Not annotated') }}</text>
        <text x="398" y="78">{{ short(dataLabel(step.function.output)) }}</text>
        <text x="18" y="105">{{ short(formatLabel(step.function.input)) }}</text><text x="398" y="105">{{ short(formatLabel(step.function.output)) }}</text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.diagram { overflow-x: auto; max-width: 100%; }
svg { display: block; width: 800px; max-width: none; font: 13px system-ui, sans-serif; fill: #263a43; }
.step-title { font-weight: 600; font-size: 15px; }
.diagram-label { font-size: 11px; font-weight: 600; fill: #425f6b; }
.connection-label { font-size: 11px; fill: #425f6b; }
</style>
