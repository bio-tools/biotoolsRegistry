<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useSearch } from './use-search';
import type { SearchConfig } from './search-state';
import AdvancedFilters from './AdvancedFilters.vue';
import SearchFilterGroup from './SearchFilterGroup.vue';
import ChoiceSelector from './ChoiceSelector.vue';
import EdamSelector from './EdamSelector.vue';
import type { SearchFilterGroup as FilterGroup } from './search-state';
import { filterLabel } from './advanced-filters';
import { defaultColumns, layoutKey, readColumns } from './search-layout';

const props = defineProps<SearchConfig>();
const { state, result, loading, error, update, reset, retry,
  candidates, visibleItems, localFilters, localError, setLocalFilters, promote } = useSearch(props);
const view = computed(() => state.value.view);
const layout = ref(defaultColumns(props.comparisonFields || {}));
const layoutMessage = ref('');
try {
  const saved = localStorage.getItem(layoutKey), legacy = localStorage.getItem('gridState');
  if (props.comparisonFields) layout.value = readColumns(props.comparisonFields, saved, legacy);
  if (!saved && legacy) layoutMessage.value = 'Your previous table columns, order and widths have been restored.';
} catch { layoutMessage.value = 'Saved columns could not be loaded. You can still customize this table.'; }
watch(layout, value => {
  try { localStorage.setItem(layoutKey, JSON.stringify(value)); layoutMessage.value = 'Table layout saved on this browser.'; }
  catch { layoutMessage.value = 'Browser storage is unavailable. This layout will last until you leave the page.'; }
}, { deep: true });
const columns = computed(() => layout.value.filter(column => column.key !== 'name' && column.visible));
function moveColumn(index: number, direction: number) {
  const [column] = layout.value.splice(index, 1);
  layout.value.splice(index + direction, 0, column!);
}
function columnWidth(event: Event, index: number) {
  const width = Number(text(event));
  if (Number.isFinite(width)) layout.value[index]!.width = Math.max(120, Math.min(800, width));
}
const pageInput = ref(1);
const filtersOpen = ref(false);
const optionSearch = ref<Record<string, string>>({});
const scientific = [
  { key: 'topicID', scope: 'topic', label: 'EDAM topic' },
  { key: 'operationID', scope: 'operation', label: 'EDAM operation' },
  { key: 'dataTypeID', scope: 'data', label: 'EDAM data type' },
  { key: 'dataFormatID', scope: 'format', label: 'EDAM format' },
] as const;
const directionKeys = {
  dataTypeID: { any: 'dataTypeID', input: 'inputDataTypeID', output: 'outputDataTypeID' },
  dataFormatID: { any: 'dataFormatID', input: 'inputDataFormatID', output: 'outputDataFormatID' },
} as const;
type DirectionalKey = keyof typeof directionKeys;
type Direction = 'any' | 'input' | 'output';
const directions = ref<Record<DirectionalKey, Direction>>({ dataTypeID: 'any', dataFormatID: 'any' });
function isDirectional(key: string): key is DirectionalKey { return key in directionKeys; }
function currentKey(key: string) { return isDirectional(key) ? directionKeys[key][directions.value[key]] : key; }
watch(() => state.value.filters, filters => {
  for (const key of Object.keys(directionKeys) as DirectionalKey[]) {
    const active = (Object.keys(directionKeys[key]) as Direction[]).filter(direction => filters[directionKeys[key][direction]]?.trim());
    if (active.length && !active.includes(directions.value[key])) directions.value[key] = active[0]!;
  }
}, { immediate: true, deep: true });
function changeDirection(key: DirectionalKey, direction: Direction) {
  const previous = currentKey(key), target = directionKeys[key][direction];
  directions.value[key] = direction;
  const value = state.value.filters[previous];
  if (previous !== target && value && !state.value.filters[target]) {
    update({ filters: { ...state.value.filters, [previous]: '', [target]: value } });
  }
}
const excluded = new Set(['topic', 'topicID', 'function', 'operation', 'operationID', 'dataType', 'dataTypeID',
  'dataFormat', 'dataFormatID', 'input', 'inputID', 'inputDataFormat', 'inputDataFormatID', 'inputDataType',
  'inputDataTypeID', 'output', 'outputID', 'outputDataFormat', 'outputDataFormatID', 'outputDataType',
  'outputDataTypeID', 'credit']);
function visibleGroup(group: FilterGroup): FilterGroup | null {
  if (group.id === 'function' || group.id.startsWith('function.') || group.id === 'topic') return null;
  const children = group.children.map(visibleGroup).filter((child): child is FilterGroup => !!child);
  const keys = group.keys.filter(key => !excluded.has(key));
  return keys.length || children.length ? { ...group, keys, children } : null;
}
const groups = computed(() => (props.filterGroups || [{ id: '', label: 'Tool details', keys: Object.keys(props.filters), children: [] }])
  .map(visibleGroup).filter((group): group is FilterGroup => !!group));
const domains = ref<{ value: string; label: string }[]>([]);
const domainError = ref('');
onMounted(async () => {
  if (!props.optionsEndpoint) return;
  try {
    const response = await fetch(`${props.optionsEndpoint}?field=domain`);
    if (!response.ok) throw new Error();
    domains.value = (await response.json()).items;
  } catch { domainError.value = 'Domains are temporarily unavailable.'; }
});
function edamValue(key: string, scope: string) {
  const value = state.value.filters[key] || '';
  const matches = value.match(new RegExp(`${scope}_[0-9]+`, 'g')) || [];
  return [...new Set(matches)].map(id => `http://edamontology.org/${id}`);
}
function setEdam(key: string, values: string[]) {
  filter(key, values.map(value => `"${value.split('/').pop()}"`).join(' '));
}
function text(event: Event) { return (event.target as HTMLInputElement).value; }
function filter(key: string, value: string) {
  update({ filters: { ...state.value.filters, [key]: value } });
}
function choiceValue(key: string) { return (state.value.filters[key] || '').replace(/^"(.*)"$/, '$1'); }
function setChoice(key: string, value: string) {
  filter(key, !value || key === 'domain' || /["\\]/.test(value) ? value : `"${value}"`);
}
function usedOptions(key: string) {
  const query = (optionSearch.value[key] || '').toLocaleLowerCase();
  const values = result.value?.facets[key]?.values || [];
  return query ? values.filter(item => (props.filterChoices?.[key]?.find(choice => choice.value === item.value)?.label || item.value).toLocaleLowerCase().includes(query)) : values.slice(0, 5);
}
function options(key: string) {
  const values = result.value?.facets[key]?.values || [];
  const declared = props.filterChoices?.[key] || [];
  return [...values.map(item => ({ ...item, label: declared.find(choice => choice.value === item.value)?.label || item.value })),
    ...declared.filter(choice => !values.some(item => item.value === choice.value)).map(choice => ({ ...choice, count: undefined }))];
}
</script>

<template>
  <div class="search-workspace">
    <form class="query-form" @submit.prevent="update({ q: state.q })">
      <label for="workspace-query">Search bio.tools</label>
      <div class="search-controls">
        <input id="workspace-query" type="search" :value="state.q" maxlength="256"
               placeholder="Name, description, topic..." @input="update({ q: text($event) }, 300)">
        <button type="submit">Search</button>
      </div>
    </form>
    <div class="workspace-layout">
      <aside aria-label="Search filters" :class="{ 'filters-collapsed': !filtersOpen }">
        <div class="filter-heading"><h2>Filters</h2><button class="filter-toggle secondary" type="button"
          aria-controls="workspace-filters" :aria-expanded="filtersOpen" @click="filtersOpen = !filtersOpen">{{ filtersOpen ? 'Hide filters' : 'Show filters' }}</button>
          <button class="secondary" type="button" @click="reset">Clear all</button></div>
        <div id="workspace-filters" class="filter-list">
        <details class="scientific-filters" open>
          <summary>EDAM annotations</summary>
          <p>Find tools by scientific annotations. Multiple selections must all match.</p>
          <div v-for="item in scientific" :key="item.key" class="scientific-field">
            <label v-if="isDirectional(item.key)" :for="`direction-${item.key}`">Match {{ item.label }} in</label>
            <select v-if="isDirectional(item.key)" :id="`direction-${item.key}`" :value="directions[item.key]"
              :aria-label="`Match ${item.label} in`" @change="changeDirection(item.key, text($event) as Direction)">
              <option value="any">Input or output</option><option value="input">Input only</option><option value="output">Output only</option>
            </select>
            <EdamSelector v-if="edamEndpoint" :model-value="edamValue(currentKey(item.key), item.scope)" :endpoint="edamEndpoint"
              :scope="item.scope" :label="item.label" multiple :max-selections="10" @update:model-value="setEdam(currentKey(item.key), $event)" />
          </div>
        </details>
        <SearchFilterGroup v-for="group in groups" :key="group.id" :group="group" :values="state.filters">
          <template #default="{ filterKey: key }">
          <template v-if="key === 'domain' && domains.length <= 20">
            <label :for="`filter-${key}`">{{ filters[key] }}</label>
            <select :id="`filter-${key}`" :value="state.filters[key] || ''" @change="filter(key, text($event))">
              <option value="">Any domain</option>
              <option v-if="state.filters[key] && !domains.some(domain => domain.value === state.filters[key])" :value="state.filters[key]">{{ state.filters[key] }}</option>
              <option v-for="domain in domains" :key="domain.value" :value="domain.value">{{ domain.label }} ({{ domain.value }})</option>
            </select>
            <small v-if="domainError" role="alert">{{ domainError }}</small>
          </template>
          <template v-else-if="(optionsEndpoint && ['creditName', 'collectionID', 'name'].includes(key)) || key === 'domain' || options(key).length > 20">
            <label :for="`filter-${key}`">{{ filters[key] }}</label>
            <ChoiceSelector :id="`filter-${key}`" :model-value="choiceValue(key)" :label="filters[key] || key"
              :choices="key === 'domain' ? domains : options(key)" :field="key"
              :endpoint="['creditName', 'collectionID', 'name'].includes(key) ? optionsEndpoint : undefined"
              @update:model-value="setChoice(key, $event)" />
            <small v-if="key === 'domain' && domainError" role="alert">{{ domainError }}</small>
          </template>
          <template v-else>
          <label :for="`filter-${key}`">{{ filters[key] }}</label>
          <input :id="`filter-${key}`" type="text" :list="`values-${key}`" :value="state.filters[key] || ''"
                 maxlength="256" @change="filter(key, text($event))">
          <datalist :id="`values-${key}`">
            <option v-for="option in options(key)" :key="option.value"
                    :value="`&quot;${option.value}&quot;`">{{ option.label }}{{ option.count === undefined ? '' : `: ${option.count} tools` }}</option>
          </datalist>
          <template v-if="(result?.facets[key]?.values.length || 0) > 5">
            <label :for="`find-options-${key}`">Find used values</label>
            <input :id="`find-options-${key}`" v-model="optionSearch[key]" type="search" maxlength="256" :aria-label="`Find used values for ${filters[key]}`">
          </template>
          <ul class="facet-options">
            <li v-for="option in usedOptions(key)" :key="option.value">
              <button type="button" class="facet-option" :aria-pressed="state.filters[key] === `&quot;${option.value}&quot;`"
                @click="filter(key, state.filters[key] === `&quot;${option.value}&quot;` ? '' : `&quot;${option.value}&quot;`)">
                <span>{{ filterChoices?.[key]?.find(choice => choice.value === option.value)?.label || option.value }}</span><span>{{ option.count }}</span>
              </button>
            </li>
          </ul>
          <p v-if="optionSearch[key] && !usedOptions(key).length">No matching used values.</p>
          </template>
          </template>
        </SearchFilterGroup>
        <details class="advanced-panel">
          <summary>Publication, dates and scores<span v-if="state.advanced.length || localFilters.length" class="active-filter">Active</span></summary>
          <div v-if="state.advanced.length" class="server-filters">
            <h3>Applied to all matches</h3>
            <ul><li v-for="(condition, index) in state.advanced" :key="index">
              <span>{{ filterLabel(condition, scores) }}</span>
              <button type="button" class="secondary" :aria-label="`Remove ${filterLabel(condition, scores)}`"
                @click="update({ advanced: state.advanced.filter((_, position) => position !== index) })">Remove</button>
            </li></ul>
          </div>
          <p class="filter-help">Preview these filters on loaded tools, then apply them to all matches.</p>
          <AdvancedFilters :filters="localFilters" :scores="scores || []" :disabled="loading || !result" @change="setLocalFilters" />
          <p v-if="localError" role="alert">{{ localError }}</p>
          <div class="advanced-actions">
            <button type="button" :disabled="!localFilters.length || !!localError || loading" @click="promote">Apply to all matches</button>
            <button type="button" class="secondary" :disabled="(!localFilters.length && !localError) || loading" @click="setLocalFilters([])">Clear candidate filters</button>
          </div>
        </details>
        </div>
      </aside>
      <section class="workspace-results" aria-label="Search results" :aria-busy="loading">
        <ul class="active-constraints" aria-label="Active filters">
          <template v-for="(value, key) in state.filters" :key="key"><li v-if="value">
            <span>{{ filters[key] }}: {{ value }}</span>
            <button type="button" class="secondary" :aria-label="`Remove ${key} filter`" @click="filter(key, '')">&#215;</button>
          </li></template>
        </ul>
        <div class="results-toolbar">
          <div><label for="search-sort">Sort by</label><select id="search-sort" :value="state.sort" @change="update({ sort: text($event) })">
            <option v-for="(label, value) in sorts" :key="value" :value="value">{{ label }}</option>
          </select></div>
          <div><label for="search-order">Order</label><select id="search-order" :value="state.ord" @change="update({ ord: text($event) as 'asc' | 'desc' })">
            <option value="desc">Descending</option><option value="asc">Ascending</option>
          </select></div>
          <div><label for="search-size">Page size</label><select id="search-size" :value="state.per_page" @change="update({ per_page: Number(text($event)) })">
            <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}</option>
          </select></div>
          <fieldset class="view-switch"><legend>View</legend>
            <label><input :checked="view === 'cards'" @change="update({ view: 'cards', page: state.page })" type="radio" value="cards" name="result-view">Cards</label>
            <label><input :checked="view === 'table'" @change="update({ view: 'table', page: state.page })" type="radio" value="table" name="result-view">Table</label>
          </fieldset>
        </div>
        <details v-if="view === 'table' && comparisonFields" class="comparison-columns">
          <summary>Columns</summary>
          <p>Choose, reorder and size columns. Your layout is remembered on this browser. Name stays first.</p>
          <ol class="column-settings">
            <li v-for="(column, index) in layout" :key="column.key">
              <label><input v-model="column.visible" type="checkbox" :disabled="column.key === 'name'">{{ comparisonFields[column.key] }}</label>
              <div class="column-actions">
                <button type="button" class="secondary" :disabled="index === 0 || column.key === 'name'" :aria-label="`Move ${comparisonFields[column.key]} earlier`" @click="moveColumn(index, -1)">&#8593;</button>
                <button type="button" class="secondary" :disabled="index === layout.length - 1 || column.key === 'name'" :aria-label="`Move ${comparisonFields[column.key]} later`" @click="moveColumn(index, 1)">&#8595;</button>
                <label>Width <input type="number" min="120" max="800" step="20" :value="column.width" :aria-label="`${comparisonFields[column.key]} column width in pixels`" @change="columnWidth($event, index)"></label>
              </div>
            </li>
          </ol>
          <button type="button" class="secondary" @click="layout = defaultColumns(comparisonFields)">Reset columns</button>
          <p role="status">{{ layoutMessage }}</p>
        </details>
        <p v-if="loading" role="status" class="result-status">Searching...</p>
        <div v-else-if="error" class="search-error" role="alert">
          <p>{{ error }}</p><button type="button" @click="retry">Retry</button>
          <button type="button" class="secondary" @click="update({ page: 1 })">Page 1</button>
        </div>
        <template v-else-if="result">
          <p role="status" class="result-status">{{ result.count.toLocaleString() }} tools<span v-if="result.count"> · Page {{ result.pagination.page }} of {{ result.pagination.pages }}</span></p>
          <p v-if="localFilters.length" class="candidate-scope" role="status">
            Candidate-only: {{ visibleItems.length }} of {{ candidates.length }} loaded tools.
            {{ result.count.toLocaleString() }} server matches.
            {{ result.candidates?.complete ? 'All server matches loaded.' : 'Partial candidate set.' }}
          </p>
          <div v-if="!result.count" class="empty-results"><h2>No tools found</h2><button type="button" class="secondary" @click="reset">Clear search</button></div>
          <div v-else-if="!visibleItems.length" class="empty-results"><h2>No candidates match</h2>
            <button type="button" class="secondary" @click="setLocalFilters([])">Clear candidate filters</button></div>
          <div v-else-if="view === 'cards'" class="result-cards">
            <article v-for="tool in visibleItems" :key="tool.id" class="tool-result" :data-tool-id="tool.id">
              <h2><a :href="tool.url">{{ tool.name }}</a></h2>
              <span class="tool-id">bio.tools:{{ tool.id }}</span>
              <p>{{ tool.description }}</p>
              <ul class="tool-types"><li v-for="type in tool.toolTypes" :key="type">{{ type }}</li></ul>
              <dl><template v-if="tool.topics.length"><dt>Topics</dt><dd>{{ tool.topics.join(', ') }}</dd></template>
                <template v-if="tool.operations.length"><dt>Operations</dt><dd>{{ tool.operations.join(', ') }}</dd></template>
              </dl>
              <div class="record-dates"><span>Added <time>{{ tool.added || '-' }}</time></span><span>Updated <time>{{ tool.updated || '-' }}</time></span></div>
            </article>
          </div>
          <div v-else class="result-table" tabindex="0" role="region" aria-label="Tool results table">
            <table v-if="comparisonFields" :style="{ width: `${(layout.find(column => column.key === 'name')?.width || 180) + columns.reduce((total, column) => total + column.width, 0)}px`, tableLayout: 'fixed' }">
              <colgroup><col :style="{ width: `${layout.find(column => column.key === 'name')?.width || 180}px` }"><col v-for="column in columns" :key="column.key" :style="{ width: `${column.width}px` }"></colgroup>
              <thead><tr><th>{{ comparisonFields.name }}</th><th v-for="column in columns" :key="column.key">{{ comparisonFields[column.key] }}</th></tr></thead>
              <tbody><tr v-for="tool in visibleItems" :key="tool.id" :data-tool-id="tool.id">
                <th scope="row"><a :href="tool.url">{{ tool.name }}</a></th>
                <td v-for="column in columns" :key="column.key">{{ tool.comparison?.[column.key] || '-' }}</td>
              </tr></tbody>
            </table>
            <table v-else><thead><tr><th>Name</th><th>Description</th><th>Tool type</th><th>Added</th><th>Updated</th></tr></thead>
              <tbody><tr v-for="tool in visibleItems" :key="tool.id" :data-tool-id="tool.id">
                <th scope="row"><a :href="tool.url">{{ tool.name }}</a></th><td>{{ tool.description }}</td>
                <td>{{ tool.toolTypes.join(', ') }}</td><td>{{ tool.added || '-' }}</td><td>{{ tool.updated || '-' }}</td>
              </tr></tbody>
            </table>
          </div>
          <p v-if="result.pagination.limited" class="result-status">Showing the first 10,000 matches. Narrow your search for more specific results.</p>
          <nav v-if="result.count" class="pagination" aria-label="Result pages">
            <button type="button" class="secondary" :disabled="!result.pagination.previous" @click="update({ page: result.pagination.previous! })">Previous</button>
            <span>{{ result.pagination.page }} / {{ result.pagination.pages }}</span>
            <button type="button" class="secondary" :disabled="!result.pagination.next" @click="update({ page: result.pagination.next! })">Next</button>
            <form @submit.prevent="update({ page: pageInput })"><label for="go-page">Go to page</label>
              <input id="go-page" v-model.number="pageInput" type="number" min="1" :max="result.pagination.pages" required><button type="submit">Go</button>
            </form>
          </nav>
        </template>
      </section>
    </div>
  </div>
</template>

<style scoped>
.search-workspace { margin-top: 24px; }
.active-constraints { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }
.active-constraints li { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 4px 6px 4px 12px; background: #e8f3f7; border: 1px solid #c8dfe8; border-radius: 20px; font-size: var(--text-ui); overflow-wrap: anywhere; }
.active-constraints button { padding: 4px 10px; flex-shrink: 0; }
.comparison-columns p { margin-block: 12px; font-size: 14px; }
.column-settings { list-style: none; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr)); gap: 12px; }
.column-settings li { padding: 12px; border: 1px solid #d5dce0; border-radius: 4px; min-width: 0; }
.column-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.column-actions button { width: 36px; min-height: 36px; padding: 0; }
.column-actions input { width: 76px; max-width: 100%; min-height: 36px; }
.comparison-columns label { display: flex; align-items: center; gap: 6px; margin: 0; }
.comparison-columns input { min-height: 0; }
.advanced-panel { margin-bottom: 16px; border-bottom: 1px solid #ddd; }
.advanced-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.advanced-actions button, .server-filters button { font-size: var(--text-control); padding: 7px 10px; }
.server-filters h3 { font-size: 14px; margin: 16px 0 8px; }
.server-filters ul { list-style: none; padding: 0; }
.server-filters li { display: flex; align-items: center; gap: 8px; justify-content: space-between; padding-block: 4px; font-size: var(--text-ui); overflow-wrap: anywhere; }
.candidate-scope { border-left: 3px solid #31708f; padding: 8px 12px; font-size: 14px; background: #edf4f8; }
.query-form { margin-bottom: 28px; }
.workspace-layout { display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 28px; align-items: start; }
aside { background: #f8fbfc; border: 1px solid #d5e5eb; border-radius: 12px; padding: 20px; min-width: 0; }
.scientific-filters p, .filter-help { color: #526d79; font-size: var(--text-caption); line-height: 1.45; margin: 8px 0 14px; }
.scientific-field { padding: 10px 0; }
.scientific-field select { margin-bottom: 10px; }
.scientific-field > label { font-size: var(--text-ui); }
.scientific-field :deep(.edam-selector > button) { width: 100%; text-align: left; }
.filter-list select { width: 100%; }
.filter-list :deep(.filter-field input) { width: 100%; }
.filter-list :deep(.filter-field small) { display: block; margin-top: 5px; line-height: 1.4; }
.filter-heading { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 12px; }
.filter-heading h2 { margin: 0; }
.filter-heading button { padding: 4px 10px; font-size: var(--text-control); }
.filter-toggle { display: none; }
details { border-top: 1px solid #ddd; padding-block: 12px; }
summary { cursor: pointer; font-weight: 600; overflow-wrap: anywhere; }
.scientific-filters > summary, .advanced-panel > summary { font-size: var(--text-ui); }
.filter-field label { font-size: var(--text-ui); }
.filter-field small { font-size: var(--text-caption); color: #666; font-weight: normal; overflow-wrap: anywhere; }
.active-filter { font-size: var(--text-caption); margin-left: 8px; color: #286044; }
.facet-options { margin: 8px 0 0; padding: 0; list-style: none; }
.facet-option { display: flex; justify-content: space-between; gap: 8px; background: none; color: #23527c; border: 0; width: 100%; padding: 6px 0; text-align: left; font-size: var(--text-control); }
.facet-option span:first-child { overflow-wrap: anywhere; }
.facet-option:hover { background: #edf4f8; }
.results-toolbar { display: flex; gap: 12px; align-items: end; flex-wrap: wrap; padding-bottom: 16px; border-bottom: 1px solid #dce8ec; }
.results-toolbar label, legend { font-size: var(--text-ui); margin-bottom: 4px; }
select { min-height: 40px; max-width: 100%; padding: 6px; background: white; color: #333; border: 1px solid #767676; border-radius: 4px; font-family: inherit; font-size: var(--text-body); }
.view-switch { display: flex; gap: 12px; border: 0; margin: 0; padding: 0; }
.view-switch label { display: flex; align-items: center; gap: 5px; margin: 0; min-height: 40px; }
.view-switch input { min-height: 0; }
.result-status { margin: 16px 0; font-size: 14px; font-weight: 600; color: #425f6b; }
.result-cards { display: grid; gap: 16px; }
.tool-result { border: 1px solid #d5e3e8; border-left: 4px solid #005472; border-radius: 9px; padding: 20px; background: #fff; box-shadow: 0 2px 8px #173e4b0a; min-width: 0; overflow-wrap: anywhere; }
.tool-result h2 { margin-bottom: 4px; font-size: 20px; }
.tool-id { display: block; font-size: var(--text-caption); color: #526d79; margin-bottom: 10px; }
.tool-result p { font-size: var(--text-body); margin-bottom: 12px; white-space: pre-line; }
.tool-types { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; padding: 0; margin: 12px 0; }
.tool-types li { background: #e6f3f7; color: #005472; padding: 4px 10px; border-radius: 20px; font-size: var(--text-caption); font-weight: 600; }
dl { display: grid; grid-template-columns: 80px minmax(0, 1fr); gap: 4px 12px; font-size: var(--text-ui); }
dt { font-weight: 600; } dd { margin: 0; }
.record-dates { display: flex; flex-wrap: wrap; gap: 16px; font-size: var(--text-caption); color: #666; }
.result-table { overflow: auto; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
td, th { padding: 12px 8px; text-align: left; vertical-align: top; border-bottom: 1px solid #ddd; min-width: 105px; overflow-wrap: anywhere; }
td:nth-child(2) { min-width: 220px; }
.pagination { margin-top: 24px; gap: 12px; font-size: 14px; }
.pagination button { padding-inline: 12px; }
.pagination form { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.pagination label { margin: 0; font-size: 13px; }
.pagination input { width: 65px; padding: 6px; }
.search-error, .empty-results { margin-block: 24px; }
.search-error { border-left: 3px solid #a94442; padding-left: 16px; }
.search-error button { margin: 0 8px 8px 0; }
@media (max-width: 760px) {
  .workspace-layout { grid-template-columns: minmax(0, 1fr); gap: 20px; }
  aside { padding: 16px; }
  .filter-toggle { display: inline-block; }
  .filters-collapsed .filter-list { display: none; }
  .results-toolbar { gap: 12px 16px; }
  .tool-result { padding: 16px; }
}
</style>
