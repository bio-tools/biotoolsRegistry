<script setup lang="ts">
import { computed } from 'vue';
import UserPicker from './UserPicker.vue';
import { errorsAt, fieldId } from './nested-editor';
import { newEditorItem, type EditorError, type ResourceEditor } from './resource-editor';

const props = defineProps<{ modelValue?: ResourceEditor['editPermission']; canManage: boolean; disabled: boolean; errors: EditorError[] }>();
const emit = defineEmits<{ 'update:modelValue': [value: NonNullable<ResourceEditor['editPermission']>] }>();
const permission = computed(() => props.modelValue || { type: 'private', authors: [] });
const modes = { private: 'Owner only', group: 'Selected users', public: 'Any signed-in user' };
const authorPath = (id: string) => ['editPermission', 'authors', { itemId: id }];
const authorErrors = computed(() => errorsAt(props.errors, ['editPermission', 'authors'], true));
</script>

<template>
  <section id="nested-editPermission" class="metadata-section" tabindex="-1" aria-label="Editing permissions">
    <h2>Editing permissions</h2>
    <p class="nested-error">{{ errorsAt(errors, ['editPermission']).join(' ') }}</p>
    <fieldset id="nested-editPermission-type" class="permission-modes" :disabled="disabled || !canManage" tabindex="-1" aria-describedby="permission-type-errors">
      <legend>Who can edit</legend>
      <label v-for="(label, mode) in modes" :key="mode">
        <input type="radio" name="edit-permission" :value="mode" :checked="permission.type === mode"
          @change="emit('update:modelValue', { ...permission, type: mode })">{{ label }}
      </label>
    </fieldset>
    <p id="permission-type-errors" class="nested-error">{{ errorsAt(errors, ['editPermission', 'type'], true).join(' ') }}</p>
    <div v-show="permission.type === 'group' || authorErrors.length" id="nested-editPermission-authors" tabindex="-1">
      <h3>Selected users</h3>
      <p v-if="!permission.authors?.length">None</p>
      <ul class="permission-authors">
        <li v-for="item in permission.authors" :id="fieldId(authorPath(item.id))" :key="item.id" tabindex="-1">
          <span>{{ item.value }}</span>
          <button type="button" class="secondary nested-icon" :disabled="disabled || !canManage" :aria-label="`Remove ${item.value}`" title="Remove user"
            @click="emit('update:modelValue', { ...permission, authors: permission.authors!.filter(author => author.id !== item.id) })">&#215;</button>
          <p class="nested-error">{{ errorsAt(errors, authorPath(item.id), true).join(' ') }}</p>
        </li>
      </ul>
      <p class="nested-error">{{ errorsAt(errors, ['editPermission', 'authors']).join(' ') }}</p>
      <UserPicker v-if="canManage" id="permission-user" :selected="(permission.authors || []).map(item => String(item.value))" :disabled="disabled"
        @add="emit('update:modelValue', { ...permission, authors: [...(permission.authors || []), newEditorItem($event)] })" />
    </div>
  </section>
</template>

<style scoped>
.permission-modes { border: 0; padding: 0; margin: 0; min-width: 0; }
.permission-modes legend { font-weight: 600; margin-bottom: 8px; }
.permission-modes label { display: flex; align-items: center; gap: 10px; min-height: 36px; }
.permission-modes input { width: 18px; min-height: 18px; height: 18px; flex: 0 0 18px; accent-color: #337ab7; }
.permission-authors { list-style: none; padding: 0; }
.permission-authors li { display: grid; grid-template-columns: minmax(0, 1fr) 32px; align-items: center; gap: 8px; max-width: 480px; margin-bottom: 8px; }
.permission-authors span { overflow-wrap: anywhere; }
.permission-authors .nested-error { grid-column: 1 / -1; }
.permission-add { display: flex; align-items: center; gap: 8px; max-width: 480px; }
.permission-add input { min-width: 0; flex: 1; }
.permission-add button { flex: 0 0 auto; }
</style>
