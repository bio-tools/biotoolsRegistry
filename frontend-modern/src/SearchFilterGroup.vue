<script setup lang="ts">
import { computed, ref } from 'vue';
import type { SearchFilterGroup } from './search-state';

const props = defineProps<{ group: SearchFilterGroup; values: Record<string, string>; labels: Record<string, string> }>();
defineSlots<{ default(props: { filterKey: string }): unknown }>();
function count(group: SearchFilterGroup): number {
  return group.keys.filter(key => props.values[key]?.trim()).length
    + group.children.reduce((total, child) => total + count(child), 0);
}
const active = computed(() => count(props.group));
const showAll = ref(false);
const initialFields = 6;
</script>

<template>
  <details class="search-filter-group" :data-filter-group="group.id" :open="active > 0">
    <summary>{{ group.label }}<span v-if="active" class="filter-group-count">{{ active }} active</span></summary>
    <div class="filter-group-body">
      <details v-for="(key, index) in group.keys" v-show="showAll || index < initialFields || !!values[key]?.trim()" :key="key" class="filter-field" :data-filter-field="key" :open="!!values[key]?.trim()">
        <summary><span>{{ labels[key] || key }}</span><span v-if="values[key]" class="filter-field-value">{{ values[key].replace(/^"(.*)"$/, '$1') }}</span></summary>
        <div class="filter-field-control"><slot :filter-key="key" /></div>
      </details>
      <button v-if="group.keys.length > initialFields" class="filter-show-all secondary" type="button" @click="showAll = !showAll">{{ showAll ? 'Show fewer fields' : `Show all ${group.keys.length} fields` }}</button>
      <SearchFilterGroup v-for="child in group.children" :key="child.id" :group="child" :values="values" :labels="labels">
        <template #default="slotProps"><slot v-bind="slotProps" /></template>
      </SearchFilterGroup>
    </div>
  </details>
</template>

<style scoped>
.filter-show-all { margin: 4px 0 8px; padding: 4px 8px; font-size: var(--text-control); }
</style>
