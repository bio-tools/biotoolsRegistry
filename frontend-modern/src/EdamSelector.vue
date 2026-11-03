<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref, useId, watch } from 'vue';
import { edamFailure, fetchEdam, type EdamSelectorProps, type EdamTerm } from './edam';

const props = withDefaults(defineProps<EdamSelectorProps>(), {
  branch: '', multiple: true, maxSelections: 20, initialTerms: () => [], suggestions: () => [],
  disabled: false, readonly: false,
});
const emit = defineEmits<{ 'update:modelValue': [value: string[]] }>();
const id = 'edam-' + useId();
const dialog = ref<HTMLDialogElement>();
const input = ref<HTMLInputElement>();
const opener = ref<HTMLButtonElement>();
const cache = ref(new Map<string, EdamTerm>());
let vocabularyRevision = '';
const draft = ref<string[]>([]);
const query = ref('');
const open = ref(false);
const expanded = ref(false);
const loading = ref(false);
const error = ref('');
const selectionError = ref('');
const items = ref<EdamTerm[]>([]);
const hints = ref<EdamTerm[]>([]);
const more = ref(false);
const active = ref(-1);
const editable = computed(() => !props.disabled && !props.readonly);
const limit = computed(() => props.multiple ? Math.min(props.maxSelections, 20) : 1);
const choices = computed(() => items.value.filter(item => !draft.value.includes(item.uri)));
const selectedTitle = computed(() => props.modelValue.map(uri => title(uri) + (cache.value.get(uri)?.obsolete ? ' (obsolete)' : '')).join(', '));
let sequence = 0;
let resolveSequence = 0;
let controller: AbortController | undefined;
let resolver: AbortController | undefined;
let timer: ReturnType<typeof setTimeout> | undefined;

function remember(terms: EdamTerm[], revision?: string) {
  const changed = !!revision && !!vocabularyRevision && revision !== vocabularyRevision;
  if (revision && revision !== vocabularyRevision) {
    cache.value.clear();
    vocabularyRevision = revision;
  }
  for (const term of terms) cache.value.set(term.uri, term);
  return changed;
}
function title(uri: string) { return cache.value.get(uri)?.term || uri; }
function parameters() { return new URLSearchParams({ scope: props.scope, ...(props.branch ? { branch: props.branch } : {}) }); }
function cancelLookup() { sequence++; controller?.abort(); clearTimeout(timer); loading.value = false; }

async function resolveSelection(force = false) {
  const current = ++resolveSequence;
  resolver?.abort();
  selectionError.value = '';
  if (!force) remember(props.initialTerms);
  const missing = force ? props.modelValue : props.modelValue.filter(uri => !cache.value.has(uri));
  if (!missing.length) return;
  const params = parameters();
  missing.forEach(uri => params.append('id', uri));
  const request = new AbortController();
  resolver = request;
  try {
    const result = await fetchEdam(props.endpoint, params, request);
    if (current === resolveSequence && remember(result.items, result.vocabulary?.revision) && open.value) lookup(0);
  } catch (failure) { if (current === resolveSequence) selectionError.value = edamFailure(failure); }
}

function lookup(delay = 300) {
  cancelLookup();
  items.value = []; active.value = -1; more.value = false; error.value = '';
  if (!open.value || !editable.value) return;
  expanded.value = true;
  if (query.value.length > 128 || /[\x00-\x1f\x7f]/.test(query.value)) {
    error.value = 'Use at most 128 characters without control characters.';
    return;
  }
  loading.value = true;
  const current = sequence;
  timer = setTimeout(async () => {
    const request = new AbortController();
    controller = request;
    const params = parameters();
    params.set('q', query.value.trim());
    props.suggestions.forEach(uri => params.append('suggest', uri));
    try {
      const result = await fetchEdam(props.endpoint, params, request);
      if (current !== sequence) return;
      items.value = result.items; hints.value = result.suggestions; more.value = result.more;
      if (remember([...result.items, ...result.suggestions], result.vocabulary?.revision)) resolveSelection(true);
    } catch (failure) { if (current === sequence) error.value = edamFailure(failure); }
    finally { if (current === sequence) loading.value = false; }
  }, delay);
}

async function begin() {
  if (!editable.value) return;
  draft.value = [...props.modelValue]; query.value = ''; hints.value = [];
  open.value = true;
  dialog.value?.showModal();
  await nextTick(); input.value?.focus(); lookup(0);
}
function close() {
  open.value = false; expanded.value = false; cancelLookup();
  dialog.value?.close();
}
function commit() {
  if (!editable.value || draft.value.length > limit.value || draft.value.some(uri => !cache.value.has(uri))) return;
  emit('update:modelValue', [...draft.value]);
  close();
}
function pick(term: EdamTerm) {
  if (!editable.value || (props.multiple && draft.value.length >= limit.value)) return;
  draft.value = props.multiple ? [...draft.value, term.uri] : [term.uri];
  active.value = -1;
  if (!props.multiple) expanded.value = false;
  input.value?.focus();
}
function remove(uri: string, staged = false) {
  if (!editable.value) return;
  if (staged) { draft.value = draft.value.filter(value => value !== uri); input.value?.focus(); }
  else {
    emit('update:modelValue', props.modelValue.filter(value => value !== uri));
    nextTick(() => opener.value?.focus());
  }
}
function hint(term: EdamTerm) { query.value = term.term; lookup(); input.value?.focus(); }
function blur(event: FocusEvent) {
  if (!dialog.value?.contains(event.relatedTarget as Node | null)) expanded.value = false;
}
function keydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    event.preventDefault();
    if (expanded.value) expanded.value = false;
    else close();
  } else if (event.key === 'Tab') expanded.value = false;
  else if (event.key === 'Enter') {
    event.preventDefault();
    if (expanded.value && choices.value[active.value]) pick(choices.value[active.value]);
  } else if (['ArrowDown', 'ArrowUp'].includes(event.key) || (expanded.value && ['Home', 'End'].includes(event.key))) {
    event.preventDefault(); expanded.value = true;
    const length = choices.value.length;
    if (!length) return;
    if (event.key === 'Home') active.value = 0;
    else if (event.key === 'End') active.value = length - 1;
    else active.value = event.key === 'ArrowDown' ? (active.value + 1) % length : (active.value < 0 ? length - 1 : (active.value + length - 1) % length);
    nextTick(() => document.getElementById(`${id}-option-${active.value}`)?.scrollIntoView({ block: 'nearest' }));
  }
}

watch(() => [props.scope, props.branch, props.endpoint], () => { close(); cache.value.clear(); vocabularyRevision = ''; resolveSelection(true); });
watch(() => props.modelValue.join('\u0000'), () => { if (open.value) close(); resolveSelection(); }, { immediate: true });
watch(editable, value => { if (!value) close(); });
onUnmounted(() => { cancelLookup(); resolveSequence++; resolver?.abort(); dialog.value?.close(); });
</script>

<template>
  <div class="edam-selector">
    <span v-if="!compact" class="edam-label" :id="`${id}-label`">{{ label }}</span>
    <ul v-if="modelValue.length && (!compact || readonly)" class="selected-terms" :aria-label="label">
      <li v-for="uri in modelValue" :key="uri"><span>{{ title(uri) }}<small v-if="cache.get(uri)?.obsolete"> (obsolete)</small></span>
        <button v-if="!readonly" type="button" class="remove-term" :disabled="disabled" :aria-label="`Remove ${title(uri)}`"
          :title="`Remove ${title(uri)}`" @click="remove(uri)">&#215;</button>
      </li>
    </ul>
    <button v-if="!readonly" ref="opener" type="button" class="secondary" :class="{ 'concept-picker': compact, 'has-selection': compact && modelValue.length }"
      :aria-label="`Choose ${label.toLowerCase()}` + (compact && modelValue.length ? ': ' + selectedTitle : '')" :title="compact ? `Choose ${label.toLowerCase()}` : undefined"
      aria-haspopup="dialog" :disabled="disabled" @click="begin"><template v-if="compact && modelValue.length">{{ selectedTitle }}</template><template v-else>Choose {{ label.toLowerCase() }}</template></button>
    <p v-else-if="!modelValue.length">None</p>
    <template v-if="name"><input v-for="uri in modelValue" :key="uri" type="hidden" :name="name" :value="uri" :disabled="disabled"></template>
    <div v-if="selectionError" role="alert"><p>{{ selectionError }}</p><button type="button" class="secondary" @click="resolveSelection(true)">Retry selected terms</button></div>
    <dialog ref="dialog" class="edam-dialog" :aria-labelledby="`${id}-title`" @cancel.prevent="close" @close="open = false; cancelLookup()">
      <h2 :id="`${id}-title`">Choose {{ label.toLowerCase() }}</h2>
      <ul v-if="draft.length" class="selected-terms" aria-label="Pending selection">
        <li v-for="uri in draft" :key="uri"><span>{{ title(uri) }}</span>
          <button type="button" class="remove-term" :title="`Remove ${title(uri)}`" :aria-label="`Remove ${title(uri)}`" @click="remove(uri, true)">&#215;</button>
        </li>
      </ul>
      <div v-if="hints.length" class="edam-hints"><span>Suggestions</span>
        <button v-for="term in hints" :key="term.uri" type="button" class="secondary" @click="hint(term)">{{ term.term }}</button>
      </div>
      <label :for="`${id}-query`">Find {{ scope }} terms</label>
      <input :id="`${id}-query`" ref="input" v-model="query" type="text" role="combobox" autocomplete="off" maxlength="128"
        aria-autocomplete="list" aria-haspopup="listbox" :aria-expanded="expanded" :aria-controls="`${id}-choices`"
        :aria-activedescendant="expanded && active >= 0 && choices[active] ? `${id}-option-${active}` : undefined"
        :aria-describedby="`${id}-status`" @input="lookup()" @keydown="keydown" @blur="blur">
      <p :id="`${id}-status`" role="status" class="lookup-status">
        <template v-if="loading">Loading terms...</template>
        <template v-else-if="error">Lookup unavailable.</template>
        <template v-else-if="multiple && draft.length >= limit">Selection limit reached ({{ limit }}).</template>
        <template v-else-if="!choices.length">{{ items.length ? 'All matching terms selected.' : 'No matching terms.' }}</template>
        <template v-else>{{ choices.length }} choices<span v-if="more">; more matches available</span>.</template>
      </p>
      <div v-if="error" role="alert"><p>{{ error }}</p><button type="button" class="secondary" @click="lookup(0)">Retry lookup</button></div>
      <ul v-show="expanded" :id="`${id}-choices`" class="edam-choices" role="listbox" :aria-label="`${scope} terms`" :aria-busy="loading">
        <li v-for="(term, index) in choices" :id="`${id}-option-${index}`" :key="term.uri" role="option"
          :aria-selected="active === index" :aria-disabled="multiple && draft.length >= limit" :class="{ active: active === index }"
          @mousedown.prevent @click="pick(term)">
          <strong>{{ term.term }}</strong><small>{{ term.uri.split('/').pop() }}</small>
          <span v-if="suggestions.includes(term.uri)" class="suggested-term">Suggested</span>
          <span v-if="term.definition" class="term-definition">{{ term.definition }}</span>
          <span v-if="term.synonyms.length" class="term-synonyms">{{ term.synonyms.join('; ') }}</span>
        </li>
      </ul>
      <div class="edam-actions"><button type="button" :disabled="!editable || draft.length > limit || draft.some(uri => !cache.has(uri))" @click="commit">Apply selection</button>
        <button type="button" class="secondary" @click="close">Cancel</button></div>
    </dialog>
  </div>
</template>

<style scoped>
.edam-selector { min-width: 0; }
.edam-label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
.edam-selector button { font-size: var(--text-control); }
.concept-picker { width: 100%; min-height: 40px; text-align: left; white-space: normal; overflow-wrap: anywhere; }
.concept-picker.has-selection { color: #23527c; border-color: transparent; background: transparent; padding: 6px 0; font-weight: 600; }
.concept-picker.has-selection:hover { text-decoration: underline; background: #edf4f8; }
.selected-terms { list-style: none; padding: 0; margin: 8px 0; display: flex; flex-wrap: wrap; gap: 8px; }
.selected-terms li { display: flex; align-items: center; gap: 8px; background: #edf4f8; padding: 4px 8px; max-width: 100%; overflow-wrap: anywhere; }
.remove-term { width: 32px; height: 32px; padding: 0; border: 0; background: transparent; color: #23527c; flex-shrink: 0; font-size: 22px !important; }
.edam-dialog { box-sizing: border-box; width: min(680px, calc(100% - 24px)); max-height: calc(100dvh - 32px); padding: 24px; border: 1px solid #767676; border-radius: 4px; color: #333; overflow: auto; }
.edam-dialog::backdrop { background: rgb(0 0 0 / 35%); }
.edam-dialog h2 { font-size: var(--text-heading); margin: 0 0 16px; }
.edam-dialog input { width: 100%; box-sizing: border-box; }
.lookup-status { font-size: 13px; color: #555; margin: 8px 0; }
.edam-choices { list-style: none; padding: 0; margin: 0; border: 1px solid #d5dce0; max-height: 310px; overflow-y: auto; background: #fff; color: #263a43; }
.edam-choices li { padding: 12px; border-bottom: 1px solid #ddd; cursor: pointer; overflow-wrap: anywhere; }
.edam-choices li:last-child { border: 0; }
.edam-choices li.active, .edam-choices li:hover { background: #edf4f8; box-shadow: inset 3px 0 #337ab7; }
.edam-choices small { margin-left: 8px; color: #666; }
.term-definition, .term-synonyms { display: block; font-size: 13px; margin-top: 4px; }
.term-synonyms { color: #666; }
.suggested-term { font-size: 12px; color: #286044; margin-left: 8px; }
.edam-hints, .edam-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-block: 16px; }
.edam-hints { font-size: 13px; }
.edam-hints button { padding: 4px 8px; }
.edam-actions { margin-bottom: 0; }
@media (max-width: 760px) { .edam-dialog { padding: 16px; } .edam-choices { max-height: 250px; } }
</style>
