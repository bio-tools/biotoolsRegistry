<script setup lang="ts">
import SchemaFields from './SchemaFields.vue';
import type { EditorError, Field, ResourceEditor } from './resource-editor';
defineProps<{ draft: ResourceEditor; fields: Record<string, Field>; endpoint: string; errors: EditorError[]; disabled: boolean }>();
</script>
<template>
  <div id="metadata-labels" class="metadata-editor" tabindex="-1">
    <SchemaFields :record="draft" :fields="fields" :path="[]"
      :exclude="['name', 'description', 'homepage', 'toolType', 'function']"
      :endpoint="endpoint" :errors="errors" :disabled="disabled" />
  </div>
</template>
<style>
.metadata-section { border-top: 1px solid #ddd; padding-block: 24px; margin-top: 24px; min-width: 0; }
.metadata-section h2 { font-size: 20px; margin: 0 0 16px; }
.metadata-section h3 { font-size: 16px; margin: 0; }
.metadata-record { border-top: 1px solid #d6dfe5; padding-block: 20px; }
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
