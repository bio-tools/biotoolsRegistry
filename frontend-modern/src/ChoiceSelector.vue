<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref, useId, watch } from 'vue';

type Choice = { value: string; label: string };
const props = withDefaults(defineProps<{ modelValue: string; label: string; choices?: Choice[]; endpoint?: string;
  field?: string; disabled?: boolean; id?: string; required?: boolean; nativeValidation?: boolean; invalid?: boolean; describedby?: string }>(),
  { choices: () => [], endpoint: '', field: '', disabled: false, id: undefined, required: false, nativeValidation: false, invalid: false, describedby: undefined });
const emit = defineEmits<{ 'update:modelValue': [value: string] }>();
const dialogId = 'choices-' + useId();
const dialog = ref<HTMLDialogElement>();
const input = ref<HTMLInputElement>();
const opener = ref<HTMLButtonElement>();
const isOpen = ref(false);
const query = ref('');
const remote = ref<Choice[]>([]);
const loading = ref(false);
const error = ref('');
const more = ref(false);
const selectedLabel = computed(() => props.choices.find(item => item.value === props.modelValue)?.label || props.modelValue);
const items = computed(() => props.endpoint ? remote.value : props.choices.filter(item =>
  `${item.label} ${item.value}`.toLocaleLowerCase().includes(query.value.trim().toLocaleLowerCase())).slice(0, 50));
let controller: AbortController | undefined;
let timer: ReturnType<typeof setTimeout> | undefined;
let sequence = 0;
function lookup() {
  if (!props.endpoint) return;
  clearTimeout(timer); controller?.abort(); const current = ++sequence;
  remote.value = []; error.value = ''; more.value = false;
  const value = query.value.trim();
  if (value.length < 2) { loading.value = false; return; }
  loading.value = true;
  timer = setTimeout(async () => {
    controller = new AbortController();
    try {
      const params = new URLSearchParams({ field: props.field, q: value.slice(0, 80) });
      const response = await fetch(`${props.endpoint}?${params}`, { signal: controller.signal });
      if (!response.ok) throw new Error();
      const body = await response.json();
      if (current === sequence) { remote.value = body.items; more.value = body.more; }
    } catch { if (current === sequence) error.value = 'Choices are temporarily unavailable. Please retry.'; }
    finally { if (current === sequence) loading.value = false; }
  }, 300);
}
async function begin() {
  if (dialog.value?.open) return;
  query.value = ''; remote.value = []; error.value = ''; more.value = false;
  isOpen.value = true;
  await nextTick();
  dialog.value?.showModal();
  await nextTick(); input.value?.focus();
}
function close() {
  ++sequence; clearTimeout(timer); controller?.abort(); loading.value = false;
  dialog.value?.close(); isOpen.value = false; nextTick(() => opener.value?.focus());
}
function choose(value: string) { emit('update:modelValue', value); close(); }
function firstChoice() { dialog.value?.querySelector<HTMLButtonElement>('.choice-list button')?.focus(); }
watch(() => props.disabled, disabled => { if (disabled && dialog.value?.open) close(); });
onUnmounted(() => { ++sequence; clearTimeout(timer); controller?.abort(); dialog.value?.close(); });
</script>
<template>
  <div class="choice-selector">
    <input v-if="nativeValidation && required" class="choice-validation" type="text" tabindex="-1" aria-hidden="true"
      :value="modelValue" :disabled="disabled" required @invalid.prevent="begin">
    <button :id="props.id" ref="opener" type="button" class="secondary choice-opener" :disabled="disabled" aria-haspopup="dialog"
      :aria-required="required || undefined" :aria-invalid="invalid || undefined" :aria-describedby="describedby" @click="begin">
      {{ selectedLabel || `Choose ${label.toLowerCase()}` }}
    </button>
    <dialog ref="dialog" class="choice-dialog" :aria-labelledby="`${dialogId}-title`" @cancel.prevent="close">
      <template v-if="isOpen">
      <h2 :id="`${dialogId}-title`">Choose {{ label.toLowerCase() }}</h2>
      <label :for="`${dialogId}-query`">Search {{ label.toLowerCase() }}</label>
      <input :id="`${dialogId}-query`" ref="input" v-model="query" type="search" autocomplete="off" maxlength="80"
        :aria-describedby="`${dialogId}-status`" @input="lookup" @keydown.down.prevent="firstChoice">
      <p :id="`${dialogId}-status`" class="choice-status" role="status">
        <template v-if="loading">Searching…</template>
        <template v-else-if="error">{{ error }}</template>
        <template v-else-if="endpoint && query.trim().length < 2">Enter at least two characters.</template>
        <template v-else-if="!items.length">No matching choices.</template>
        <template v-else>{{ items.length }} choices<span v-if="more || (!endpoint && items.length === 50)">; refine the search for more</span>.</template>
      </p>
      <ul v-if="items.length" class="choice-list" :aria-label="`${label} choices`">
        <li v-for="item in items" :key="item.value"><button type="button" @click="choose(item.value)">{{ item.label }}</button></li>
      </ul>
      <div class="choice-actions"><button v-if="modelValue" type="button" class="secondary" @click="choose('')">Clear selection</button>
        <button type="button" class="secondary" @click="close">Cancel</button></div>
      </template>
    </dialog>
  </div>
</template>
<style scoped>
.choice-selector { min-width: 0; }
.choice-validation { position: absolute; width: 1px; height: 1px; min-height: 0; opacity: 0; pointer-events: none; }
.choice-opener { width: 100%; text-align: left; overflow-wrap: anywhere; }
.choice-dialog { box-sizing: border-box; width: min(680px, calc(100% - 24px)); max-height: calc(100dvh - 32px); padding: 24px; border: 1px solid #767676; border-radius: 6px; background: #fff; color: #263a43; overflow: auto; }
.choice-dialog::backdrop { background: rgb(0 0 0 / 35%); }
.choice-dialog h2 { font-size: var(--text-heading); margin: 0 0 16px; }
.choice-dialog input { width: 100%; }
.choice-status { font-size: var(--text-caption); color: #526d79; margin: 8px 0; }
.choice-list { list-style: none; padding: 0; margin: 0; border: 1px solid #d5dce0; max-height: 310px; overflow-y: auto; }
.choice-list button { width: 100%; text-align: left; color: #263a43; background: #fff; border: 0; border-radius: 0; border-bottom: 1px solid #e0e8eb; padding: 10px 12px; overflow-wrap: anywhere; }
.choice-list button:hover, .choice-list button:focus-visible { color: #005472; background: #edf4f8; }
.choice-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; }
</style>
