<script setup lang="ts">
import { computed } from 'vue';
import { errorsAt, fieldId } from './nested-editor';
import type { EditorError, EditorPath, Field } from './resource-editor';
const props = defineProps<{ record: Record<string, unknown>; field: string; label: string; path: EditorPath;
  errors: EditorError[]; disabled: boolean; options?: string[]; multiline?: boolean; schema?: Field; hideLabel?: boolean; retainEmpty?: boolean }>();
const value = computed(() => {
  const value = props.record[props.field];
  return typeof value === 'string' || typeof value === 'number' ? value : '';
});
const choices = computed(() => props.schema?.choices || props.options?.map(value => ({ value, label: value })));
const deprecated = computed(() => !!choices.value && value.value !== '' && !choices.value.some(item => item.value === value.value));
const messages = computed(() => errorsAt(props.errors, props.path, true));
function update(event: Event) {
  const input = event.target as HTMLInputElement;
  const text = input.value;
  if (text !== value.value && props.path[0] === 'publication' && ['doi', 'pmid', 'pmcid'].includes(props.field)) {
    delete props.record.metadata;
  }
  if (props.schema?.kind === 'boolean') props.record[props.field] = input.checked;
  else if (text === '' && props.retainEmpty) props.record[props.field] = props.schema?.kind === 'number' ? null : '';
  else if (text === '') delete props.record[props.field];
  else if (props.schema?.kind === 'number') props.record[props.field] = input.valueAsNumber;
  else props.record[props.field] = text;
}
</script>
<template>
  <div class="metadata-field">
    <label :for="fieldId(path)" :class="{ 'visually-hidden': hideLabel }">{{ label }}</label>
    <select v-if="choices" :id="fieldId(path)" :value="value" :disabled="disabled" :aria-invalid="!!messages.length || deprecated" :required="schema?.required"
      :aria-describedby="fieldId(path) + '-errors'" @change="update">
      <option value="">Not specified</option><option v-if="deprecated" :value="value" disabled>{{ value }} (no longer allowed)</option>
      <option v-for="choice in choices" :key="choice.value" :value="choice.value">{{ choice.label }}</option>
    </select>
    <textarea v-else-if="multiline" :id="fieldId(path)" :value="value" :disabled="disabled" rows="2" :aria-invalid="!!messages.length"
      :required="schema?.required" :minlength="schema?.minLength" :maxlength="schema?.maxLength"
      :aria-describedby="fieldId(path) + '-errors'" @input="update" />
    <input v-else :id="fieldId(path)" :type="schema?.kind === 'boolean' ? 'checkbox' : schema?.kind === 'number' ? 'number' : 'text'"
      :value="value" :checked="record[field] === true" :disabled="disabled" :aria-invalid="!!messages.length"
      :required="schema?.kind !== 'boolean' && schema?.required" :minlength="schema?.minLength" :maxlength="schema?.maxLength"
      :min="schema?.minimum" :max="schema?.maximum" :step="schema?.kind === 'number' ? 'any' : undefined"
      :aria-describedby="fieldId(path) + '-errors'" @input="update">
    <p v-if="schema?.help && !hideLabel" class="schema-help">{{ schema.help }}</p>
    <p :id="fieldId(path) + '-errors'" class="nested-error">{{ messages.join(' ') }}{{ deprecated ? ' This stored value is no longer allowed. Choose a current value or clear it before saving.' : '' }}</p>
  </div>
</template>
