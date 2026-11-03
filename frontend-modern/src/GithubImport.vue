<script setup lang="ts">
import { computed, onBeforeUnmount, ref, shallowRef, watch } from 'vue';
import { browserRequest, BrowserRequestError } from './browser-auth';
import { identity, mergeSuggestions } from './github-import';
import type { Field, Json, ResourceSchema } from './resource-editor';

const props = defineProps<{ endpoint: string; schema: ResourceSchema; current: Record<string, Json>; identifier: string | null; disabled: boolean }>();
const emit = defineEmits<{ apply: [changes: Record<string, Json>] }>();
type Result = { suggestions: Record<string, Json>; rejected: { path: string; reason: string }[]; raw: Json; schemaRevision: string };
const url = ref('');
const result = shallowRef<Result | null>(null);
const choices = ref<Record<string, string>>({});
const selected = ref<Record<string, number[]>>({});
const nestedSelected = ref<Record<string, boolean>>({});
const baseline = shallowRef<Record<string, Json>>({});
const pending = ref(false);
const message = ref('');
let controller: AbortController | null = null;
function discard() {
  controller?.abort(); controller = null; pending.value = false;
  result.value = null; choices.value = {}; selected.value = {}; nestedSelected.value = {};
}
watch(url, () => { discard(); message.value = ''; });
onBeforeUnmount(() => controller?.abort());
const entries = computed(() => Object.entries(result.value?.suggestions || {}).filter(([key, value]) => props.schema.contract.fields?.[key]?.writable && hasValue(value)));
const changes = computed(() => Object.fromEntries(entries.value.flatMap(([key, value]) => {
  const mode = choices.value[key];
  if (!mode || mode === 'keep') return [];
  const merged = mode === 'merge' && Array.isArray(value)
    ? mergeSuggestions(Array.isArray(props.current[key]) ? props.current[key] as Json[] : [], value.flatMap((item, index) =>
      selected.value[key]?.includes(index) ? [filteredItem(item, props.schema.contract.fields?.[key]?.item, [key, index])] : [])) : value;
  return identity(merged) === identity(props.current[key] ?? null) ? [] : [[key, merged]];
})) as Record<string, Json>);
const count = computed(() => Object.keys(changes.value).length);
const stale = computed(() => Object.keys(changes.value).some(key => identity(props.current[key] ?? null) !== identity(baseline.value[key] ?? null)));
const invalidSelection = computed(() => entries.value.some(([key, value]) => choices.value[key] === 'merge' && Array.isArray(value) &&
  value.some((item, index) => selected.value[key]?.includes(index) && !requiredValuesPresent(filteredItem(item, props.schema.contract.fields?.[key]?.item, [key, index]), props.schema.contract.fields?.[key]?.item))));
function keepAll() { choices.value = {}; selected.value = {}; nestedSelected.value = {}; }
function choose(key: string, mode: string, value: Json) {
  choices.value[key] = mode;
  if (mode === 'merge' && Array.isArray(value)) selected.value[key] = items(value, props.schema.contract.fields?.[key]?.item).map(item => item.index);
}
function hasValue(value: Json | undefined): boolean {
  if (value === undefined || value === null || value === '') return false;
  if (Array.isArray(value)) return value.some(hasValue);
  if (typeof value === 'object') return Object.values(value).some(hasValue);
  return true;
}
function edamLabel(value: Json, field?: Field): string | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const uri = typeof value.uri === 'string' ? value.uri : '';
  if (!/^https?:\/\/(?:www\.)?edamontology\.org\//i.test(uri) && !field?.fields?.uri?.help?.startsWith('EDAM ')) return null;
  return typeof value.term === 'string' && value.term ? value.term : uri.split('/').pop() || null;
}
function items(values: Json[], field?: Field) {
  const visible = values.map((value, index) => ({ value, index })).filter(item => hasValue(item.value));
  if (visible.length && visible.every(item => edamLabel(item.value, field) !== null)) {
    visible.sort((a, b) => edamLabel(a.value, field)!.localeCompare(edamLabel(b.value, field)!, undefined, { sensitivity: 'base' }));
  }
  return visible;
}
type NestedTerm = { path: string; label: string; parents: string[] };
function nestedTerms(value: Json, field: Field | undefined, path: (string | number)[], parents: string[] = []): NestedTerm[] {
  if (!field || !value) return [];
  if (field.kind === 'object' && typeof value === 'object' && !Array.isArray(value)) {
    return Object.entries(value).flatMap(([key, item]) => nestedTerms(item, field.fields?.[key], [...path, key], parents));
  }
  if (field.kind !== 'array' || !Array.isArray(value)) return [];
  return items(value, field.item).flatMap(item => {
    const childPath = [...path, item.index];
    const key = JSON.stringify(childPath);
    const data = item.value && typeof item.value === 'object' && !Array.isArray(item.value) ? item.value.data : null;
    const term = edamLabel(item.value, field.item) || (data ? edamLabel(data, field.item?.fields?.data) : null);
    const descendants = nestedTerms(item.value, field.item, childPath, term ? [...parents, key] : parents);
    return term ? [{ path: key, label: `${field.label || 'Term'}: ${term}`, parents }, ...descendants] : descendants;
  });
}
function filteredItem(value: Json, field: Field | undefined, path: (string | number)[]): Json {
  if (Array.isArray(value)) return value.flatMap((item, index) => nestedSelected.value[JSON.stringify([...path, index])] === false
    ? [] : [filteredItem(item, field?.item, [...path, index])]);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).flatMap(([key, item]) => {
    const child = filteredItem(item, field?.fields?.[key], [...path, key]);
    return Array.isArray(child) && !child.length && !field?.fields?.[key]?.required ? [] : [[key, child]];
  }));
  return value;
}
function requiredValuesPresent(value: Json, field?: Field): boolean {
  if (!field) return true;
  if (field.kind === 'array' && Array.isArray(value)) return value.every(item => requiredValuesPresent(item, field.item));
  if (field.kind !== 'object' || !value || typeof value !== 'object' || Array.isArray(value)) return true;
  return Object.entries(field.fields || {}).every(([key, child]) => (!child.required || hasValue(value[key])) &&
    (!Object.hasOwn(value, key) || requiredValuesPresent(value[key], child)));
}
function publicationLabel(value: Json, suggested: boolean): string {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return '';
  const identifiers = ['doi', 'pmid', 'pmcid'].flatMap(key => typeof value[key] === 'string' && value[key] ? [`${key.toUpperCase()}: ${value[key]}`] : []);
  if (suggested) {
    const raw = result.value?.raw;
    const publications = raw && typeof raw === 'object' && !Array.isArray(raw) && Array.isArray(raw.publication) ? raw.publication : [];
    const matching = publications.find(item => item && typeof item === 'object' && !Array.isArray(item) &&
      ['doi', 'pmid', 'pmcid'].some(key => typeof value[key] === 'string' && value[key] && item[key] === value[key]));
    const source = matching && typeof matching === 'object' && !Array.isArray(matching) ? matching : value;
    const metadata = source.metadata && typeof source.metadata === 'object' && !Array.isArray(source.metadata) ? source.metadata : null;
    const title = typeof metadata?.title === 'string' ? metadata.title : typeof source.title === 'string' ? source.title : '';
    if (title) identifiers.unshift(title);
  }
  return identifiers.join(' · ') || 'Publication';
}
function display(value: Json | undefined, field?: Field, suggested = false, publication = false): string {
  if (!hasValue(value)) return '';
  if (Array.isArray(value)) return items(value, field?.item).map(item => display(item.value, field?.item, suggested, field?.path === 'publication')).join('; ');
  if (publication && value !== undefined) return publicationLabel(value, suggested);
  if (value && typeof value === 'object') return edamLabel(value, field) || Object.entries(value).filter(([, item]) => hasValue(item)).map(([key, item]) => {
    const label = field?.fields?.[key]?.label || key.replace(/([a-z])([A-Z])/g, '$1 $2');
    return `${label}: ${display(item, field?.fields?.[key], suggested)}`;
  }).join(' · ');
  return String(value);
}
function refreshComparison() {
  baseline.value = JSON.parse(JSON.stringify(props.current)); keepAll(); message.value = 'Comparison refreshed. Review your choices again.';
}
async function requestSuggestions() {
  discard(); message.value = ''; pending.value = true;
  const active = new AbortController(); controller = active;
  try {
    const response = await browserRequest(props.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url.value, biotoolsID: props.identifier, schemaRevision: props.schema.revision }),
      signal: AbortSignal.any([active.signal, AbortSignal.timeout(60000)]) });
    const data: Result = await response.json();
    if (active.signal.aborted) return;
    if (data.schemaRevision !== props.schema.revision) throw new Error('Schema changed. Export your draft and reload.');
    result.value = data; baseline.value = JSON.parse(JSON.stringify(props.current));
    if (!Object.keys(data.suggestions).length) message.value = 'No compatible suggestions were returned.';
  } catch (error) {
    if (active.signal.aborted) return;
    message.value = error instanceof BrowserRequestError && error.body && typeof error.body === 'object' && 'detail' in error.body
      ? String(error.body.detail) : 'Import failed. Check your session and try again; your draft is unchanged.';
  } finally { if (controller === active) { pending.value = false; controller = null; } }
}
function apply() {
  if (stale.value || invalidSelection.value || !count.value || props.disabled) return;
  emit('apply', changes.value); discard(); message.value = 'Suggestions applied to your draft. Save changes to update the record.';
}
</script>

<template>
  <details class="github-import">
    <summary>Import metadata from GitHub</summary>
    <p>Review suggestions from a public repository. Applying them changes this draft; saving is a separate step.</p>
    <label for="github-repository">GitHub repository URL</label>
    <input id="github-repository" v-model="url" type="url" maxlength="300" placeholder="https://github.com/owner/repository" :disabled="disabled">
    <div class="import-actions">
      <button type="button" :disabled="pending || disabled || !url" @click="requestSuggestions">{{ pending ? 'Importing...' : 'Get suggestions' }}</button>
      <button v-if="pending || result" type="button" class="secondary" @click="discard">{{ pending ? 'Cancel import' : 'Discard suggestions' }}</button>
    </div>
    <p role="status">{{ message }}</p>
    <template v-if="result">
      <div class="import-overview">
        <p>{{ count }} pending field changes</p>
        <button type="button" class="secondary" @click="keepAll">Keep all current values</button>
      </div>
      <section v-for="([key, value], index) in entries" :key="key" class="import-field" :aria-labelledby="`import-field-${index}`">
        <div class="import-field-heading">
          <h3 :id="`import-field-${index}`">{{ schema.contract.fields?.[key]?.label || key }}</h3>
          <div>
            <label class="visually-hidden" :for="`import-choice-${index}`">Action for {{ schema.contract.fields?.[key]?.label || key }}</label>
            <select :id="`import-choice-${index}`" :value="choices[key] || 'keep'" :disabled="disabled" @change="choose(key, ($event.target as HTMLSelectElement).value, value)">
              <option value="keep">Keep current</option><option value="replace">Use suggestion</option>
              <option v-if="Array.isArray(value)" value="merge">Select items</option>
            </select>
          </div>
        </div>
        <div class="import-comparison" :class="{ 'single-value': !hasValue(current[key]) }">
          <div v-if="hasValue(current[key])"><h4>Current</h4><div class="import-value" tabindex="0">{{ display(current[key], schema.contract.fields?.[key]) }}</div></div>
          <div><h4>Suggested</h4>
            <fieldset v-if="choices[key] === 'merge' && Array.isArray(value)" class="import-selection">
              <legend class="visually-hidden">Select {{ schema.contract.fields?.[key]?.label || key }} items to add</legend>
              <template v-for="item in items(value, schema.contract.fields?.[key]?.item)" :key="item.index">
                <label class="import-item">
                  <input type="checkbox" :checked="selected[key]?.includes(item.index)" :disabled="disabled"
                    @change="selected[key] = ($event.target as HTMLInputElement).checked ? [...(selected[key] || []), item.index] : (selected[key] || []).filter(i => i !== item.index)">
                  <span>{{ nestedTerms(item.value, schema.contract.fields?.[key]?.item, [key, item.index]).length ? `${schema.contract.fields?.[key]?.itemLabel || schema.contract.fields?.[key]?.label || 'Item'} ${item.index + 1}` : display(item.value, schema.contract.fields?.[key]?.item, true, key === 'publication') }}</span>
                </label>
                <div v-if="selected[key]?.includes(item.index)" class="import-nested">
                  <label v-for="term in nestedTerms(item.value, schema.contract.fields?.[key]?.item, [key, item.index])" :key="term.path" class="import-item">
                    <input type="checkbox" :checked="nestedSelected[term.path] !== false" :disabled="disabled || term.parents.some(parent => nestedSelected[parent] === false)"
                      @change="nestedSelected[term.path] = ($event.target as HTMLInputElement).checked">
                    <span>{{ term.label }}</span>
                  </label>
                </div>
              </template>
            </fieldset>
            <div v-else class="import-value" tabindex="0">{{ display(value, schema.contract.fields?.[key], true) }}</div>
          </div>
        </div>
      </section>
      <details v-if="result.rejected.length" class="import-notices">
        <summary>{{ result.rejected.length }} suggestion{{ result.rejected.length === 1 ? '' : 's' }} could not be used</summary>
        <ul><li v-for="(item, index) in result.rejected" :key="index">{{ schema.contract.fields?.[item.path]?.label || item.path }}: {{ item.reason }}</li></ul>
      </details>
      <details><summary>Raw bridge result</summary><pre>{{ JSON.stringify(result.raw, null, 2) }}</pre></details>
      <p v-if="stale" role="alert">Your draft changed after this comparison. Refresh it and review your choices again.</p>
      <p v-if="invalidSelection" role="alert">Select the required terms for each chosen item before applying.</p>
      <button v-if="stale" type="button" class="secondary" @click="refreshComparison">Refresh comparison</button>
      <div v-else class="import-actions">
        <button type="button" :disabled="!count || disabled || invalidSelection" @click="apply">Apply to draft</button>
      </div>
    </template>
  </details>
</template>

<style scoped>
.github-import { border: 1px solid #b6cbd8; border-left: 3px solid #337ab7; padding: 16px; margin-block: 20px; }
summary { cursor: pointer; font-weight: 600; }
#github-repository { width: min(100%, 40rem); }
.import-actions, .import-overview, .import-field-heading { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
.import-actions { margin-block: 12px; }
.import-overview, .import-field-heading { justify-content: space-between; }
.import-overview p { margin: 0; }
.import-field { border: 1px solid #d6e2ea; border-radius: 6px; margin-top: 10px; padding: 10px 12px; }
.import-field h3 { margin: 0; font-size: 1em; }
.import-field h4 { margin: 0 0 4px; font-size: .9em; color: #526a7c; }
.import-comparison { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 8px; }
.import-comparison.single-value { grid-template-columns: minmax(0, 1fr); }
.import-value { white-space: pre-wrap; overflow-wrap: anywhere; max-height: 7em; overflow: auto; }
.import-notices { margin-block: 12px; }
.import-selection { border: 0; padding: 0; margin: 0; min-width: 0; }
.import-nested { margin-left: 24px; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; font: inherit; font-size: 14px; background: #f3f7fa; padding: 12px; max-height: 320px; overflow: auto; }
.import-item { display: flex; align-items: flex-start; gap: 8px; margin-block: 4px; }
.import-item input { width: auto; min-height: 0; margin-top: 4px; }
.visually-hidden { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
@media (max-width: 700px) { .import-comparison { grid-template-columns: 1fr; } }
</style>
