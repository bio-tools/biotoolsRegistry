<script setup lang="ts">
import type { AdvancedFilter, ScoreDefinition } from './advanced-filters';
const props = defineProps<{ filters: AdvancedFilter[]; scores: ScoreDefinition[]; disabled: boolean }>();
const emit = defineEmits<{ change: [filters: AdvancedFilter[]] }>();
function value(event: Event) { return (event.target as HTMLInputElement).value; }
function current(field: string) { return props.filters.find(filter => filter.field === field); }
function replace(field: string, filter?: AdvancedFilter) {
  emit('change', [...props.filters.filter(item => item.field !== field), ...(filter ? [filter] : [])]);
}
function publication(input: string) {
  replace('hasPublication', input ? { type: 'boolean', field: 'hasPublication', scope: 'candidate', value: input === 'yes' } : undefined);
}
function bound(field: string, side: 'min' | 'max', input: string, score?: ScoreDefinition) {
  const existing = current(field);
  const filter: AdvancedFilter = existing && (existing.type === 'range' || existing.type === 'score') ? { ...existing }
    : score ? { type: 'score', field, version: score.version, scope: 'candidate' }
      : { type: 'range', field: 'added', scope: 'candidate' };
  if (input === '') delete filter[side];
  else if (filter.type === 'range') filter[side] = input;
  else filter[side] = Number(input);
  replace(field, filter.min === undefined && filter.max === undefined ? undefined : filter);
}
function selected(field: string, key: 'min' | 'max' | 'value' | 'values') {
  const filter = current(field);
  if (!filter) return '';
  if (key === 'value' && filter.type === 'boolean') return filter.value ? 'yes' : 'no';
  if (key === 'values' && (filter.type === 'categorical' || filter.type === 'ontology')) return filter.values[0] ?? '';
  if ((key === 'min' || key === 'max') && (filter.type === 'range' || filter.type === 'score')) return filter[key] ?? '';
  return '';
}
</script>

<template>
  <fieldset class="advanced-controls" :disabled="disabled">
    <legend>Candidate filters</legend>
    <div><label for="candidate-publication">Publication</label>
      <select id="candidate-publication" :value="selected('hasPublication', 'value')" @change="publication(value($event))">
        <option value="">Any</option><option value="yes">Has publication</option><option value="no">No publication</option>
      </select></div>
    <div><label for="candidate-added-min">Added on or after</label>
      <input id="candidate-added-min" type="date" :value="selected('added', 'min')" @change="bound('added', 'min', value($event))"></div>
    <div><label for="candidate-added-max">Added on or before</label>
      <input id="candidate-added-max" type="date" :value="selected('added', 'max')" @change="bound('added', 'max', value($event))"></div>
    <template v-for="score in scores" :key="score.key">
      <div v-for="side in (['min', 'max'] as const)" :key="side">
        <label :for="`candidate-${score.key}-${side}`">{{ score.label }} {{ side }} ({{ score.version }})</label>
        <input :id="`candidate-${score.key}-${side}`" type="number" step="any" :min="score.min" :max="score.max"
               :value="selected(score.key, side)" @change="bound(score.key, side, value($event), score)">
      </div>
    </template>
  </fieldset>
</template>

<style scoped>
.advanced-controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; padding: 0; margin: 12px 0; border: 0; min-width: 0; }
legend { font-size: 14px; font-weight: 600; margin-bottom: 8px; }
label { font-size: var(--text-ui); }
input, select { width: 100%; min-width: 0; min-height: 40px; padding: 6px; border: 1px solid #767676; border-radius: 4px; background: white; color: #333; font-family: inherit; font-size: var(--text-body); }
</style>
