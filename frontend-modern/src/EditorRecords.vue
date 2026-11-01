<script setup lang="ts" generic="T">
import { errorsAt, fieldId, moveItem, removeSection } from './nested-editor';
import type { EditorError, EditorPath } from './resource-editor';
const props = defineProps<{ modelValue?: { id: string; value: T }[] | null; empty: () => T; field: string; label: string;
  itemLabel: string; errors: EditorError[]; disabled: boolean; readonlyIds?: Set<string>; parentPath?: EditorPath }>();
const emit = defineEmits<{ 'update:modelValue': [value: { id: string; value: T }[]] }>();
const basePath = (): EditorPath => props.parentPath || [props.field];
const path = (id: string): EditorPath => [...basePath(), { itemId: id }];
function add() { emit('update:modelValue', [...(props.modelValue || []), { id: crypto.randomUUID(), value: props.empty() }]); }
</script>
<template>
  <section :id="fieldId(basePath())" class="metadata-section" tabindex="-1" :aria-label="label">
    <header class="nested-heading"><h2>{{ label }}</h2>
      <button type="button" class="secondary" :disabled="disabled" @click="add">Add {{ itemLabel.toLowerCase() }}</button></header>
    <p class="nested-error">{{ errorsAt(errors, basePath()).join(' ') }}</p>
    <section v-for="(item, index) in modelValue" :key="item.id" :id="fieldId(path(item.id))" class="metadata-record" tabindex="-1" :aria-label="`${itemLabel} ${index + 1}`">
      <header class="nested-heading"><h3>{{ itemLabel }} {{ index + 1 }}</h3><div class="nested-controls">
        <button type="button" class="secondary nested-icon" :disabled="disabled || index === 0" :aria-label="`Move ${itemLabel.toLowerCase()} ${index + 1} up`" title="Move up" @click="moveItem(modelValue!, index, -1)">&#8593;</button>
        <button type="button" class="secondary nested-icon" :disabled="disabled || index === modelValue!.length - 1" :aria-label="`Move ${itemLabel.toLowerCase()} ${index + 1} down`" title="Move down" @click="moveItem(modelValue!, index, 1)">&#8595;</button>
        <button type="button" class="secondary nested-icon" :disabled="disabled || readonlyIds?.has(item.id)" :aria-label="`Remove ${itemLabel.toLowerCase()} ${index + 1}`" title="Remove" @click="removeSection(modelValue!, index, `${itemLabel.toLowerCase()} ${index + 1}`)">&#215;</button>
      </div></header>
      <p class="nested-error">{{ errorsAt(errors, path(item.id)).join(' ') }}</p>
      <slot :item="item" :path="path(item.id)" :readonly="readonlyIds?.has(item.id) || false" />
    </section>
  </section>
</template>
