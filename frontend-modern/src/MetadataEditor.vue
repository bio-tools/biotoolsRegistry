<script setup lang="ts">
import { computed } from 'vue';
import SchemaFields from './SchemaFields.vue';
import type { EditorError, Field, ResourceEditor } from './resource-editor';
const props = defineProps<{ draft: ResourceEditor; fields: Record<string, Field>; endpoint: string; errors: EditorError[]; disabled: boolean }>();
const visible = computed(() => Object.entries(props.fields).filter(([name, field]) => field.writable &&
  !['name', 'description', 'homepage', 'toolType', 'function'].includes(name)));
const basicFields = computed(() => Object.fromEntries(visible.value.filter(([name, field]) => name === 'topic' ||
  (field.kind !== 'object' && field.item?.kind !== 'object'))));
const recordFields = computed(() => Object.fromEntries(visible.value.filter(([name, field]) => name !== 'topic' &&
  (field.kind === 'object' || field.item?.kind === 'object'))));
</script>
<template>
  <div id="metadata-labels" class="metadata-editor" tabindex="-1">
    <section v-if="Object.keys(basicFields).length" class="metadata-section" aria-label="Additional details">
      <h2>Additional details</h2>
      <SchemaFields :record="draft" :fields="basicFields" :path="[]" :endpoint="endpoint" :errors="errors" :disabled="disabled" />
    </section>
    <SchemaFields :record="draft" :fields="recordFields" :path="[]" :endpoint="endpoint" :errors="errors" :disabled="disabled" />
  </div>
</template>
<style>
.metadata-section { padding: 24px; margin-top: 20px; min-width: 0; border: 1px solid #dce8ed; border-radius: 10px; background: #fff; box-shadow: 0 2px 10px #173e4b0a; }
.metadata-section h2 { font-size: 20px; margin: 0 0 16px; }
.metadata-section h3 { font-size: 16px; margin: 0; }
.metadata-record { border: 1px solid #dce8ed; border-radius: 8px; padding: 16px; margin-block: 12px; background: #f8fbfc; }
.metadata-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px 24px; margin-block: 16px; }
.metadata-field, .metadata-strings { min-width: 0; }
.metadata-strings { border: 0; padding: 0; margin: 0; }
.metadata-strings legend { font-weight: 600; padding: 0; margin-bottom: 8px; }
.metadata-string { display: grid; grid-template-columns: minmax(0, 1fr) 32px; gap: 8px; align-items: center; margin-bottom: 8px; }
.metadata-string .nested-error { grid-column: 1 / -1; margin: 0; }
.metadata-editor select, .metadata-editor textarea { width: 100%; max-width: 100%; min-height: 44px; padding: 10px; font-family: inherit; font-size: var(--text-body); color: #333; background: white; border: 1px solid #767676; border-radius: 4px; }
.metadata-editor textarea { min-height: 80px; resize: vertical; }
.visually-hidden { position: absolute; width: 1px; height: 1px; padding: 0; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
@media (max-width: 600px) { .metadata-grid { grid-template-columns: minmax(0, 1fr); } }
</style>
