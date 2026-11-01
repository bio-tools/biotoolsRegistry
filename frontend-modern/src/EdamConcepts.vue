<script setup lang="ts">
import EdamSelector from './EdamSelector.vue';
import SchemaFields from './SchemaFields.vue';
import { newEditorItem, type EditorError, type EditorPath, type Field } from './resource-editor';
import { conceptURIs, errorsAt, fieldId, selectConcept, type ConceptItem } from './nested-editor';

const props = defineProps<{ modelValue?: ConceptItem[] | null; scope: 'operation' | 'format' | 'topic';
  path: EditorPath; endpoint: string; errors: EditorError[]; disabled: boolean; schema?: Field }>();
const emit = defineEmits<{ 'update:modelValue': [value: ConceptItem[]] }>();
function add() { emit('update:modelValue', [...(props.modelValue || []), newEditorItem({})]); }
function remove(index: number) { emit('update:modelValue', props.modelValue!.filter((_, position) => position !== index)); }
const itemPath = (item: ConceptItem) => [...props.path, { itemId: item.id }];
const labels = { operation: 'Operation', format: 'Format', topic: 'Topic' };
</script>
<template>
  <fieldset :id="fieldId(path)" class="concept-list" tabindex="-1" :aria-describedby="fieldId(path) + '-errors'" :disabled="disabled">
    <legend>{{ schema?.label || labels[scope] + 's' }}</legend>
    <p :id="fieldId(path) + '-errors'" class="nested-error">{{ errorsAt(errors, path).join(' ') }}</p>
    <div v-for="(item, index) in modelValue" :key="item.id" :id="fieldId(itemPath(item))" class="concept-row" tabindex="-1"
      :aria-describedby="fieldId(itemPath(item)) + '-errors'" :data-concept-id="item.id">
      <div>
        <p v-if="item.value?.term && !item.value.uri" class="unresolved-term">{{ item.value.term }} (term only)</p>
        <EdamSelector :scope="scope" :label="`${labels[scope]} ${index + 1}`" :multiple="false"
          compact :endpoint="endpoint" :disabled="disabled" :model-value="conceptURIs(item.value)"
          @update:model-value="item.value = selectConcept(item.value, $event)" />
        <p :id="fieldId(itemPath(item)) + '-errors'" class="nested-error">{{ errorsAt(errors, itemPath(item), true).join(' ') }}</p>
        <SchemaFields v-if="item.value && schema?.item?.fields" :record="item.value" :fields="schema.item.fields" :path="itemPath(item)"
          :exclude="['uri', 'term']" :errors="errors" :disabled="disabled" :endpoint="endpoint" />
      </div>
      <button type="button" class="secondary nested-icon" :aria-label="`Remove ${scope} ${index + 1}`" :title="`Remove ${scope} ${index + 1}`" @click="remove(index)">&#215;</button>
    </div>
    <button type="button" class="secondary" @click="add">Add {{ scope }}</button>
  </fieldset>
</template>
