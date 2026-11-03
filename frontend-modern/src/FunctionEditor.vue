<script setup lang="ts">
import EdamConcepts from './EdamConcepts.vue';
import FunctionIO from './FunctionIO.vue';
import SchemaFields from './SchemaFields.vue';
import UiIcon from './UiIcon.vue';
import { newEditorItem, type EditorError, type Field } from './resource-editor';
import { errorsAt, fieldId, moveItem, removeSection, type FunctionItem } from './nested-editor';

const props = defineProps<{ modelValue?: FunctionItem[] | null; endpoint: string; errors: EditorError[]; disabled: boolean; schema?: Field }>();
const emit = defineEmits<{ 'update:modelValue': [value: FunctionItem[]] }>();
function add() { emit('update:modelValue', [...(props.modelValue || []), newEditorItem({ operation: [{}] })]); }
const path = (item: FunctionItem) => ['function', { itemId: item.id }];
</script>
<template>
  <section id="nested-function" class="function-editor" aria-labelledby="functions-title" tabindex="-1">
    <header class="nested-heading"><h2 id="functions-title"><UiIcon name="function" />{{ schema?.label || 'Functions' }}</h2>
      <button type="button" class="secondary" :disabled="disabled" @click="add">Add function</button></header>
    <p class="nested-error">{{ errorsAt(errors, ['function']).join(' ') }}</p>
    <p v-if="!modelValue?.length" class="empty-functions">No functions.</p>
    <section v-for="(item, index) in modelValue" :key="item.id" :id="fieldId(path(item))" class="function-entry" tabindex="-1"
      :aria-labelledby="fieldId(path(item)) + '-title'" :data-function-id="item.id">
      <header class="nested-heading">
        <h3 :id="fieldId(path(item)) + '-title'">Function {{ index + 1 }}</h3>
        <div class="nested-controls">
          <button type="button" class="secondary nested-icon" :disabled="disabled || index === 0" :aria-label="`Move function ${index + 1} up`" title="Move up" @click="moveItem(modelValue!, index, -1)">&#8593;</button>
          <button type="button" class="secondary nested-icon" :disabled="disabled || index === modelValue!.length - 1" :aria-label="`Move function ${index + 1} down`" title="Move down" @click="moveItem(modelValue!, index, 1)">&#8595;</button>
          <button type="button" class="secondary nested-icon" :disabled="disabled" :aria-label="`Remove function ${index + 1}`" title="Remove" @click="removeSection(modelValue!, index, `function ${index + 1}`)">&#215;</button>
        </div>
      </header>
      <p class="nested-error">{{ errorsAt(errors, path(item)).join(' ') }}</p>
      <template v-if="item.value">
        <div class="function-diagram" role="group" :aria-label="`Function ${index + 1}: inputs to operations to outputs`">
          <FunctionIO v-model="item.value.input" kind="input" :schema="schema?.item?.fields?.input" :path="[...path(item), 'input']" :endpoint="endpoint" :errors="errors" :disabled="disabled" />
          <span class="flow-arrow" aria-hidden="true">&#8594;</span>
          <div class="function-operations">
            <EdamConcepts v-model="item.value.operation" scope="operation" :schema="schema?.item?.fields?.operation" :path="[...path(item), 'operation']" :endpoint="endpoint" :errors="errors" :disabled="disabled" />
          </div>
          <span class="flow-arrow" aria-hidden="true">&#8594;</span>
          <FunctionIO v-model="item.value.output" kind="output" :schema="schema?.item?.fields?.output" :path="[...path(item), 'output']" :endpoint="endpoint" :errors="errors" :disabled="disabled" />
        </div>
        <SchemaFields :record="item.value" :fields="schema?.item?.fields || {}" :path="path(item)" :exclude="['input', 'operation', 'output']"
          :endpoint="endpoint" :errors="errors" :disabled="disabled" />
      </template>
      <p v-else class="nested-error">Invalid function value. Remove this entry and add a new one.</p>
    </section>
  </section>
</template>

<style>
.function-editor { border-top: 1px solid #ddd; margin-top: 12px; padding-top: 24px; }
.function-editor h2, .function-editor h3, .function-editor h4 { margin: 0; font-size: 18px; }
.function-editor h4 { font-size: 16px; }
.nested-heading { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
.nested-controls { display: flex; gap: 4px; }
.nested-icon { width: 32px; height: 32px; min-height: 32px; flex: 0 0 32px; padding: 0; font-size: 18px; }
.function-entry { border-top: 2px solid #005472; padding-block: 20px 8px; margin-top: 20px; min-width: 0; }
.function-entry textarea { width: 100%; font: inherit; padding: 10px; border: 1px solid #767676; border-radius: 4px; resize: vertical; min-height: 80px; }
.function-diagram { display: grid; grid-template-columns: minmax(0, 1fr) 32px minmax(0, 1.1fr) 32px minmax(0, 1fr); align-items: start; gap: 8px; margin-block: 24px; }
.function-operations { min-width: 0; background: #e5f2f7; border: 1px solid #8baebf; border-radius: 8px; padding: 16px; margin-top: 32px; }
.function-operations .concept-list { margin: 0; }
.function-operations .concept-list legend { font-size: 16px; color: #23527c; }
.flow-arrow { color: #005472; text-align: center; font-size: 28px; line-height: 40px; margin-top: 64px; }
.function-details { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-block: 24px; }
.function-details > div { min-width: 0; }
.io-list, .io-entry { min-width: 0; }
.io-entry { border: 1px solid #d6dfe5; border-radius: 4px; padding: 12px; margin-block: 12px; }
.io-entry .nested-heading { gap: 4px; margin-bottom: 8px; }
.function-editor .io-entry h4 { font-size: 14px; }
.concept-list { margin: 0 0 16px; padding: 0; border: 0; min-width: 0; }
.concept-list legend { padding: 0; font-weight: 600; margin-bottom: 8px; }
.concept-row { display: grid; grid-template-columns: minmax(0, 1fr) 32px; align-items: center; gap: 4px; margin-bottom: 4px; }
.io-entry .concept-list { margin-block: 8px 0; }
.io-entry .concept-list legend { font-size: 12px; color: #575757; margin-bottom: 0; }
.nested-error { color: #a94442; font-size: 14px; overflow-wrap: anywhere; margin: 8px 0 16px; }
.nested-error:empty { display: none; }
.unresolved-term, .empty-functions { color: #575757; overflow-wrap: anywhere; }
@media (max-width: 760px) {
  .function-diagram, .function-details { grid-template-columns: minmax(0, 1fr); gap: 12px; }
  .function-operations { margin-top: 0; }
  .flow-arrow { margin: 0; transform: rotate(90deg); justify-self: center; width: 40px; height: 40px; }
}
</style>
