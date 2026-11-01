<script setup lang="ts">
import { computed, onBeforeUnmount, ref, shallowRef, watch } from 'vue';
import { browserRequest, BrowserRequestError } from './browser-auth';
import { identity, mergeSuggestions } from './github-import';
import type { Json, ResourceSchema } from './resource-editor';

const props = defineProps<{ endpoint: string; schema: ResourceSchema; current: Record<string, Json>; identifier: string | null; disabled: boolean }>();
const emit = defineEmits<{ apply: [changes: Record<string, Json>] }>();
type Result = { suggestions: Record<string, Json>; rejected: { path: string; reason: string }[]; raw: Json; schemaRevision: string };
const url = ref('');
const result = shallowRef<Result | null>(null);
const choices = ref<Record<string, string>>({});
const selected = ref<Record<string, number[]>>({});
const baseline = shallowRef<Record<string, Json>>({});
const pending = ref(false);
const message = ref('');
const confirming = ref(false);
let controller: AbortController | null = null;
function discard() {
  controller?.abort(); controller = null; pending.value = false;
  result.value = null; choices.value = {}; selected.value = {}; confirming.value = false;
}
watch(url, () => { discard(); message.value = ''; });
onBeforeUnmount(() => controller?.abort());
const entries = computed(() => Object.entries(result.value?.suggestions || {}).filter(([key]) => props.schema.contract.fields?.[key]?.writable));
const changes = computed(() => Object.fromEntries(entries.value.flatMap(([key, value]) => {
  const mode = choices.value[key];
  if (!mode || mode === 'keep') return [];
  const merged = mode === 'merge' && Array.isArray(value)
    ? mergeSuggestions(Array.isArray(props.current[key]) ? props.current[key] as Json[] : [], value.filter((_, index) => selected.value[key]?.includes(index))) : value;
  return identity(merged) === identity(props.current[key] ?? null) ? [] : [[key, merged]];
})) as Record<string, Json>);
const count = computed(() => Object.keys(changes.value).length);
const stale = computed(() => Object.keys(changes.value).some(key => identity(props.current[key] ?? null) !== identity(baseline.value[key] ?? null)));
watch(changes, () => { confirming.value = false; }, { deep: true });
function keepAll() { choices.value = {}; selected.value = {}; confirming.value = false; }
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
  if (!confirming.value || stale.value || !count.value || props.disabled) return;
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
      <p>{{ count }} pending field changes</p>
      <button type="button" class="secondary" @click="keepAll">Keep all current values</button>
      <section v-for="([key, value], index) in entries" :key="key" class="import-field" :aria-labelledby="`import-field-${index}`">
        <h3 :id="`import-field-${index}`">{{ schema.contract.fields?.[key]?.label || key }}</h3>
        <div class="import-comparison">
          <div><h4>Current draft</h4><pre>{{ JSON.stringify(current[key] ?? null, null, 2) }}</pre></div>
          <div><h4>Suggested</h4><pre>{{ JSON.stringify(value, null, 2) }}</pre></div>
        </div>
        <label :for="`import-choice-${index}`">Action for {{ schema.contract.fields?.[key]?.label || key }}</label>
        <select :id="`import-choice-${index}`" :value="choices[key] || 'keep'" :disabled="disabled" @change="choices[key] = ($event.target as HTMLSelectElement).value">
          <option value="keep">Keep current value</option><option value="replace">Replace with suggestion</option>
          <option v-if="Array.isArray(value)" value="merge">Add selected suggested items</option>
        </select>
        <fieldset v-if="choices[key] === 'merge' && Array.isArray(value)">
          <legend>Items to add</legend>
          <label v-for="(item, itemIndex) in value" :key="itemIndex" class="import-item">
            <input type="checkbox" :checked="selected[key]?.includes(itemIndex)" :disabled="disabled"
              @change="selected[key] = ($event.target as HTMLInputElement).checked ? [...(selected[key] || []), itemIndex] : (selected[key] || []).filter(i => i !== itemIndex)">
            <pre>{{ JSON.stringify(item, null, 2) }}</pre>
          </label>
        </fieldset>
      </section>
      <section v-if="result.rejected.length" aria-label="Suggestions not accepted">
        <h3>Suggestions not accepted</h3><ul><li v-for="item in result.rejected" :key="item.path">{{ item.path }}: {{ item.reason }}</li></ul>
      </section>
      <details><summary>Raw bridge result</summary><pre>{{ JSON.stringify(result.raw, null, 2) }}</pre></details>
      <p v-if="stale" role="alert">Your draft changed after this comparison. Refresh it and review your choices again.</p>
      <button v-if="stale" type="button" class="secondary" @click="refreshComparison">Refresh comparison</button>
      <div v-else class="import-actions">
        <button v-if="!confirming" type="button" :disabled="!count || disabled" @click="confirming = true">Review selected changes</button>
        <template v-else>
          <p>Apply {{ count }} selected field changes to this draft?</p>
          <button type="button" :disabled="disabled" @click="apply">Apply to draft</button>
          <button type="button" class="secondary" @click="confirming = false">Back to review</button>
        </template>
      </div>
    </template>
  </details>
</template>

<style scoped>
.github-import { border: 1px solid #b6cbd8; border-left: 3px solid #337ab7; padding: 16px; margin-block: 20px; }
summary { cursor: pointer; font-weight: 600; }
.import-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-block: 16px; }
.import-field { border-top: 1px solid #d6dfe5; margin-top: 20px; padding-top: 12px; }
.import-comparison { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; font: inherit; font-size: 14px; background: #f3f7fa; padding: 12px; max-height: 320px; overflow: auto; }
.import-item { display: flex; align-items: flex-start; gap: 10px; }
.import-item input { width: 20px; min-height: 20px; margin-top: 16px; }
.import-item pre { min-width: 0; }
@media (max-width: 700px) { .import-comparison { grid-template-columns: 1fr; } }
</style>
