<script setup lang="ts">
import EdamSelector from './EdamSelector.vue';
import EdamConcepts from './EdamConcepts.vue';
import SchemaFields from './SchemaFields.vue';
import { newEditorItem, type EditorError, type EditorPath, type Field } from './resource-editor';
import { conceptURIs, errorsAt, fieldId, moveItem, removeSection, selectConcept, type IOItem } from './nested-editor';

const props = defineProps<{ modelValue?: IOItem[] | null; kind: 'input' | 'output';
  path: EditorPath; endpoint: string; errors: EditorError[]; disabled: boolean; schema?: Field }>();
const emit = defineEmits<{ 'update:modelValue': [value: IOItem[]] }>();
function add() { emit('update:modelValue', [...(props.modelValue || []), newEditorItem({ data: {} })]); }
const itemPath = (item: IOItem) => [...props.path, { itemId: item.id }];
const dataPath = (item: IOItem) => [...itemPath(item), 'data'];
</script>
<template>
  <section :id="fieldId(path)" class="io-list" tabindex="-1" :aria-label="kind === 'input' ? 'Inputs' : 'Outputs'">
    <h3>{{ schema?.label || (kind === 'input' ? 'Inputs' : 'Outputs') }}</h3>
    <p class="nested-error">{{ errorsAt(errors, path).join(' ') }}</p>
    <section v-for="(item, index) in modelValue" :key="item.id" :id="fieldId(itemPath(item))" class="io-entry" tabindex="-1"
      :aria-labelledby="fieldId(itemPath(item)) + '-title'" :data-io-id="item.id">
      <header class="nested-heading">
        <h4 :id="fieldId(itemPath(item)) + '-title'">{{ kind === 'input' ? 'Input' : 'Output' }} {{ index + 1 }}</h4>
        <div class="nested-controls">
          <button type="button" class="secondary nested-icon" :disabled="disabled || index === 0" :aria-label="`Move ${kind} ${index + 1} up`" title="Move up" @click="moveItem(modelValue!, index, -1)">&#8593;</button>
          <button type="button" class="secondary nested-icon" :disabled="disabled || index === modelValue!.length - 1" :aria-label="`Move ${kind} ${index + 1} down`" title="Move down" @click="moveItem(modelValue!, index, 1)">&#8595;</button>
          <button type="button" class="secondary nested-icon" :disabled="disabled" :aria-label="`Remove ${kind} ${index + 1}`" title="Remove" @click="removeSection(modelValue!, index, `${kind} ${index + 1}`)">&#215;</button>
        </div>
      </header>
      <p class="nested-error">{{ errorsAt(errors, itemPath(item)).join(' ') }}</p>
      <template v-if="item.value">
        <div :id="fieldId(dataPath(item))" tabindex="-1" :aria-describedby="fieldId(dataPath(item)) + '-errors'">
          <p v-if="item.value.data?.term && !item.value.data.uri" class="unresolved-term">{{ item.value.data.term }} (term only)</p>
          <EdamSelector scope="data" :label="schema?.item?.fields?.data?.label || 'Data'" compact :multiple="false" :endpoint="endpoint" :disabled="disabled"
            :model-value="conceptURIs(item.value.data)" @update:model-value="item.value.data = selectConcept(item.value.data, $event)" />
          <p :id="fieldId(dataPath(item)) + '-errors'" class="nested-error">{{ errorsAt(errors, dataPath(item), true).join(' ') }}</p>
          <SchemaFields v-if="item.value.data" :record="item.value.data" :fields="schema?.item?.fields?.data?.fields || {}" :path="dataPath(item)"
            :exclude="['uri', 'term']" :errors="errors" :disabled="disabled" :endpoint="endpoint" />
        </div>
        <EdamConcepts v-model="item.value.format" scope="format" :schema="schema?.item?.fields?.format" :path="[...itemPath(item), 'format']" :endpoint="endpoint" :errors="errors" :disabled="disabled" />
        <SchemaFields :record="item.value" :fields="schema?.item?.fields || {}" :path="itemPath(item)"
          :exclude="['data', 'format']" :errors="errors" :disabled="disabled" :endpoint="endpoint" />
      </template>
      <p v-else class="nested-error">Invalid {{ kind }} value. Remove this entry and add a new one.</p>
    </section>
    <button type="button" class="secondary" :disabled="disabled" @click="add">Add {{ kind }}</button>
  </section>
</template>
