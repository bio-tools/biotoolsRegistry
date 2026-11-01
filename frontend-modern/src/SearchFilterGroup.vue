<script setup lang="ts">
import { computed } from 'vue';
import type { SearchFilterGroup } from './search-state';

const props = defineProps<{ group: SearchFilterGroup; values: Record<string, string> }>();
defineSlots<{ default(props: { filterKey: string }): unknown }>();
function count(group: SearchFilterGroup): number {
  return group.keys.filter(key => props.values[key]?.trim()).length
    + group.children.reduce((total, child) => total + count(child), 0);
}
const active = computed(() => count(props.group));
</script>

<template>
  <details class="search-filter-group" :data-filter-group="group.id" :open="active > 0">
    <summary>{{ group.label }}<span v-if="active" class="filter-group-count">{{ active }} active</span></summary>
    <div class="filter-group-body">
      <div v-for="key in group.keys" :key="key" class="filter-field"><slot :filter-key="key" /></div>
      <SearchFilterGroup v-for="child in group.children" :key="child.id" :group="child" :values="values">
        <template #default="slotProps"><slot v-bind="slotProps" /></template>
      </SearchFilterGroup>
    </div>
  </details>
</template>
