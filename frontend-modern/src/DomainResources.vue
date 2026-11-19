<script setup lang="ts">
import { computed, ref } from 'vue';

const props = defineProps<{ initial: string[]; names: Record<string, string> }>();
const resources = ref([...new Set(props.initial.map(value => value.trim()).filter(Boolean))]);
const query = ref('');
const identifier = ref('');
const name = (id: string) => Object.hasOwn(props.names, id) ? props.names[id] : undefined;
const matching = computed(() => {
  const needle = query.value.trim().toLowerCase();
  return resources.value.filter(id => `${id} ${name(id) || ''}`.toLowerCase().includes(needle));
});
function add() {
  const id = identifier.value.trim();
  if (id && !resources.value.some(value => value.toLowerCase() === id.toLowerCase())) resources.value.push(id);
  identifier.value = '';
}
</script>

<template>
  <fieldset class="domain-resources">
    <legend>Domain tools</legend>
    <input type="hidden" name="resources" :value="resources.join('\n')">
    <label for="domain-resource-filter">Find a tool in this domain</label>
    <input id="domain-resource-filter" v-model="query" type="search" placeholder="Search by name or identifier">
    <p role="status">{{ matching.length }} of {{ resources.length }} tools<span v-if="matching.length > 30">; showing the first 30, refine your search to see more</span>.</p>
    <ul><li v-for="id in matching.slice(0, 30)" :key="id">
      <span>{{ name(id) || id }} <small v-if="name(id) && name(id) !== id">({{ id }})</small></span>
      <button type="button" class="secondary" :aria-label="'Remove ' + id" @click="resources = resources.filter(value => value !== id)">Remove</button>
    </li></ul>
    <label for="domain-resource-add">Add a tool by identifier</label>
    <div class="domain-resource-add"><input id="domain-resource-add" v-model="identifier" type="text" @keydown.enter.prevent="add"><button type="button" class="secondary" @click="add">Add tool</button></div>
    <p>Changes are applied when you save the domain.</p>
  </fieldset>
</template>

<style scoped>
.domain-resources { margin-block: 20px; }
.domain-resources ul { list-style: none; padding: 0; }
.domain-resources li { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-block: 6px; }
.domain-resources small { color: #526d79; }
.domain-resources p { margin-block: 8px; }
.domain-resource-add { display: flex; gap: 8px; }
.domain-resource-add input { flex: 1; }
</style>
