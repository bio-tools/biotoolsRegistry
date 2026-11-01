<script setup lang="ts">
import { errorsAt, fieldId } from './nested-editor';
import EditorField from './EditorField.vue';
import { newEditorItem, type EditorError, type EditorItem, type EditorPath, type Field } from './resource-editor';
type Item = EditorItem<string | number | boolean | null>;
const props = defineProps<{ modelValue?: Item[] | null; path: EditorPath; label: string; itemLabel: string;
  options?: string[]; errors: EditorError[]; disabled: boolean; schema?: Field }>();
const emit = defineEmits<{ 'update:modelValue': [value: Item[]] }>();
const itemPath = (id: string) => [...props.path, { itemId: id }];
</script>
<template>
  <fieldset :id="fieldId(path)" class="metadata-strings" :disabled="disabled" tabindex="-1">
    <legend>{{ label }}</legend>
    <p v-if="schema?.help" class="schema-help">{{ schema.help }}</p>
    <p class="nested-error">{{ errorsAt(errors, path).join(' ') }}</p>
    <div v-for="(item, index) in modelValue" :key="item.id" class="metadata-string">
      <EditorField :record="item" field="value" :path="itemPath(item.id)" :label="`${itemLabel} ${index + 1}`" hide-label retain-empty
        :schema="schema?.item ? { ...schema.item, choices: schema.choices } : undefined" :options="options" :errors="errors" :disabled="disabled" />
      <button type="button" class="secondary nested-icon" :aria-label="`Remove ${itemLabel.toLowerCase()} ${index + 1}`" title="Remove"
        @click="emit('update:modelValue', modelValue!.filter(row => row.id !== item.id))">&#215;</button>
    </div>
    <button type="button" class="secondary" @click="emit('update:modelValue', [...(modelValue || []), newEditorItem(schema?.item?.kind === 'boolean' ? false : schema?.item?.kind === 'number' ? 0 : '')])">Add {{ itemLabel.toLowerCase() }}</button>
  </fieldset>
</template>
