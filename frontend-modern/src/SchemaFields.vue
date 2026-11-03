<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import EditorField from './EditorField.vue';
import EditorStrings from './EditorStrings.vue';
import EditorRecords from './EditorRecords.vue';
import EdamConcepts from './EdamConcepts.vue';
import UiIcon from './UiIcon.vue';
import { sectionIcon } from './ui-icons';
import { fieldId, type ConceptItem } from './nested-editor';
import { newEditorItem, type EditorError, type EditorItem, type EditorPath, type Field } from './resource-editor';

const props = defineProps<{ record: Record<string, unknown>; fields: Record<string, Field>; path: EditorPath;
  errors: EditorError[]; disabled: boolean; endpoint: string; exclude?: string[] }>();
const visible = computed(() => Object.entries(props.fields).filter(([name, field]) => field.writable && !props.exclude?.includes(name)));
const protectedIds = ref(new Set<string>());
watch(() => props.record, record => {
  protectedIds.value = new Set(records(record.otherID).filter(item =>
    typeof item.value?.value === 'string' && item.value.value.trim().toLowerCase().startsWith('biotools:')).map(item => item.id));
}, { immediate: true });
function object(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : null;
}
function records(value: unknown) { return (Array.isArray(value) ? value : []) as EditorItem<Record<string, unknown>>[]; }
function primitives(value: unknown) { return (Array.isArray(value) ? value : []) as EditorItem<string | boolean | number | null>[]; }
function concepts(value: unknown) { return (Array.isArray(value) ? value : []) as ConceptItem[]; }
function emptyValue(field: Field): unknown {
  if (field.kind === 'object') return Object.fromEntries(Object.entries(field.fields || {})
    .filter(([, child]) => child.writable && child.required).map(([name, child]) => [name, emptyValue(child)]));
  if (field.kind === 'array') return field.empty === false && field.item ? [newEditorItem(emptyValue(field.item))] : [];
  return field.kind === 'boolean' ? false : field.kind === 'number' ? null : '';
}
</script>

<template>
  <div class="metadata-grid schema-fields">
    <template v-for="[name, field] in visible" :key="name">
      <EdamConcepts v-if="field.path === 'topic'" :model-value="concepts(record[name])" @update:model-value="record[name] = $event"
        scope="topic" :schema="field" :path="[...path, name]" :endpoint="endpoint" :errors="errors" :disabled="disabled" />
      <EditorField v-else-if="['string', 'number', 'boolean'].includes(field.kind)" :record="record" :field="name" :schema="field"
        :path="[...path, name]" :label="field.label || name" :multiline="field.multiline" :errors="errors" :disabled="disabled" />
      <EditorStrings v-else-if="field.kind === 'array' && field.item && ['string', 'number', 'boolean'].includes(field.item.kind)"
        :model-value="primitives(record[name])" @update:model-value="record[name] = $event" :schema="field"
        :path="[...path, name]" :label="field.label || name" :item-label="field.itemLabel || field.label || name" :errors="errors" :disabled="disabled" />
      <EditorRecords v-else-if="field.kind === 'array' && field.item?.kind === 'object'" class="schema-wide"
        :model-value="records(record[name])" @update:model-value="record[name] = $event" :empty="() => emptyValue(field.item!) as Record<string, unknown>" :field="name"
        :parent-path="[...path, name]" :label="field.label || name" :item-label="field.itemLabel || field.label || name" :icon="sectionIcon(field.path, field.kind)"
        :errors="errors" :disabled="disabled" :readonly-ids="field.path === 'otherID' ? protectedIds : undefined" v-slot="{ item, path: itemPath, readonly }">
        <SchemaFields v-if="object(item.value)" :record="object(item.value)!" :fields="field.item.fields || {}" :path="itemPath"
          :errors="errors" :disabled="disabled || readonly" :endpoint="endpoint" />
        <p v-else class="nested-error">Invalid stored value; retained in the draft.</p>
      </EditorRecords>
      <section v-else-if="field.kind === 'object'" :id="fieldId([...path, name])" class="schema-wide" :aria-label="field.label || name">
        <h3><UiIcon :name="sectionIcon(field.path, field.kind)" />{{ field.label || name }}</h3>
        <SchemaFields v-if="object(record[name])" :record="object(record[name])!" :fields="field.fields || {}" :path="[...path, name]"
          :errors="errors" :disabled="disabled" :endpoint="endpoint" />
        <button v-else type="button" class="secondary" :disabled="disabled" @click="record[name] = emptyValue(field)">Add {{ field.label || name }}</button>
      </section>
      <p v-else class="nested-error">{{ field.label || name }}: unsupported control. Stored data is retained.</p>
    </template>
  </div>
</template>

<style>
.schema-fields > .schema-wide { grid-column: 1 / -1; min-width: 0; }
.schema-help { font-size: 13px; color: #575757; margin-block: 6px 12px; overflow-wrap: anywhere; }
.metadata-field input[type="checkbox"] { width: 18px; min-height: 18px; height: 18px; accent-color: #337ab7; }
</style>
