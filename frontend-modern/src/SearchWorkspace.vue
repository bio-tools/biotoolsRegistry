<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useSearch } from './use-search';
import type { SearchConfig } from './search-state';
import AdvancedFilters from './AdvancedFilters.vue';
import SearchFilterGroup from './SearchFilterGroup.vue';
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
const groups = computed(() => props.filterGroups || [{ id: '', label: 'Tool details', keys: Object.keys(props.filters), children: [] }]);
function text(event: Event) { return (event.target as HTMLInputElement).value; }
function filter(key: string, value: string) {
  update({ filters: { ...state.value.filters, [key]: value } });
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
        <SearchFilterGroup v-for="group in groups" :key="group.id" :group="group" :values="state.filters">
          <template #default="{ filterKey: key }">
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
        </SearchFilterGroup>
        </div>
      </aside>
      <section class="workspace-results" aria-label="Search results" :aria-busy="loading">
        <ul class="active-constraints" aria-label="Active filters">
          <template v-for="(value, key) in state.filters" :key="key"><li v-if="value">
            <span>{{ filters[key] }}: {{ value }}</span>
            <button type="button" class="secondary" :aria-label="`Remove ${key} filter`" @click="filter(key, '')">&#215;</button>
          </li></template>
        </ul>
        <details class="advanced-panel">
          <summary>Advanced filters<span v-if="state.advanced.length || localFilters.length" class="active-filter">Active</span></summary>
          <div v-if="state.advanced.length" class="server-filters">
            <h3>Applied to all matches</h3>
            <ul><li v-for="(condition, index) in state.advanced" :key="index">
              <span>{{ filterLabel(condition, scores) }}</span>
              <button type="button" class="secondary" :aria-label="`Remove ${filterLabel(condition, scores)}`"
                @click="update({ advanced: state.advanced.filter((_, position) => position !== index) })">Remove</button>
            </li></ul>
          </div>
          <AdvancedFilters :filters="localFilters" :scores="scores || []" :disabled="loading || !result" :edam-endpoint="edamEndpoint"
            :tool-types="options('toolType').map(option => option.value)" @change="setLocalFilters" />
          <p v-if="localError" role="alert">{{ localError }}</p>
          <div class="advanced-actions">
            <button type="button" :disabled="!localFilters.length || !!localError || loading" @click="promote">Apply to all matches</button>
            <button type="button" class="secondary" :disabled="(!localFilters.length && !localError) || loading" @click="setLocalFilters([])">Clear candidate filters</button>
          </div>
        </details>
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
.active-constraints { list-style: none; padding: 0; }
.active-constraints li { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; font-size: 13px; overflow-wrap: anywhere; }
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
.advanced-actions button, .server-filters button { font-size: 13px; padding: 7px 10px; }
.server-filters h3 { font-size: 14px; margin: 16px 0 8px; }
.server-filters ul { list-style: none; padding: 0; }
.server-filters li { display: flex; align-items: center; gap: 8px; justify-content: space-between; padding-block: 4px; font-size: 13px; overflow-wrap: anywhere; }
.candidate-scope { border-left: 3px solid #31708f; padding: 8px 12px; font-size: 14px; background: #edf4f8; }
.query-form { margin-bottom: 28px; }
.workspace-layout { display: grid; grid-template-columns: 224px minmax(0, 1fr); gap: 28px; }
aside { border-right: 1px solid #ddd; padding-right: 20px; min-width: 0; }
.filter-heading { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 12px; }
.filter-heading h2 { margin: 0; }
.filter-heading button { padding: 4px 10px; font-size: 13px; }
.filter-toggle { display: none; }
details { border-top: 1px solid #ddd; padding-block: 12px; }
summary { cursor: pointer; font-weight: 600; overflow-wrap: anywhere; }
.filter-field label { font-size: 13px; }
.filter-field small { font-size: 11px; color: #666; font-weight: normal; overflow-wrap: anywhere; }
.active-filter { font-size: 11px; margin-left: 8px; color: #286044; }
.facet-options { margin: 8px 0 0; padding: 0; list-style: none; }
.facet-option { display: flex; justify-content: space-between; gap: 8px; background: none; color: #23527c; border: 0; width: 100%; padding: 6px 0; text-align: left; font-size: 13px; }
.facet-option span:first-child { overflow-wrap: anywhere; }
.facet-option:hover { background: #edf4f8; }
.results-toolbar { display: flex; gap: 12px; align-items: end; flex-wrap: wrap; padding-bottom: 16px; border-bottom: 1px solid #ddd; }
.results-toolbar label, legend { font-size: 13px; margin-bottom: 4px; }
select { min-height: 40px; max-width: 100%; padding: 6px; background: white; color: #333; border: 1px solid #767676; border-radius: 4px; font: inherit; font-size: 14px; }
.view-switch { display: flex; gap: 12px; border: 0; margin: 0; padding: 0; }
.view-switch label { display: flex; align-items: center; gap: 5px; margin: 0; min-height: 40px; }
.view-switch input { min-height: 0; }
.result-status { margin: 16px 0; font-size: 14px; color: #575757; }
.result-cards { display: grid; gap: 16px; }
.tool-result { border: 1px solid #d5dce0; border-left: 3px solid #005472; border-radius: 6px; padding: 24px; min-width: 0; overflow-wrap: anywhere; }
.tool-result h2 { margin-bottom: 4px; font-size: 20px; }
.tool-id { display: block; font-size: 12px; color: #666; margin-bottom: 12px; }
.tool-result p { font-size: 14px; margin-bottom: 12px; white-space: pre-line; }
.tool-types { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; padding: 0; margin: 12px 0; }
.tool-types li { background: #edf4f8; color: #23527c; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
dl { display: grid; grid-template-columns: 80px minmax(0, 1fr); gap: 4px 12px; font-size: 13px; }
dt { font-weight: 600; } dd { margin: 0; }
.record-dates { display: flex; flex-wrap: wrap; gap: 16px; font-size: 12px; color: #666; }
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
  aside { border-right: 0; padding: 0; }
  .filter-toggle { display: inline-block; }
  .filters-collapsed .filter-list { display: none; }
  .results-toolbar { gap: 12px 16px; }
  .tool-result { padding: 16px; }
}
</style>
