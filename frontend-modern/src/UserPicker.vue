<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { browserRequest } from './browser-auth';
const props = defineProps<{ selected: string[]; disabled: boolean; id: string }>();
const emit = defineEmits<{ add: [username: string] }>();
const query = ref('');
const suggestions = ref<string[]>([]);
const lookupMessage = ref('');
const canAdd = computed(() => !props.disabled && query.value.trim()
  && !props.selected.includes(query.value.trim()));

function add() {
  if (!canAdd.value) return;
  emit('add', query.value.trim());
  query.value = '';
}
watch(query, (value, _, cleanup) => {
  suggestions.value = [];
  lookupMessage.value = '';
  if (!value.trim()) return;
  const controller = new AbortController();
  const timer = setTimeout(async () => {
    lookupMessage.value = 'Searching...';
    try {
      const response = await browserRequest('/api/user-list/?format=json&term=' + encodeURIComponent(value.trim()),
        { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(10000)]) });
      const users: { username: string }[] = await response.json();
      if (controller.signal.aborted) return;
      suggestions.value = users.map(user => user.username).filter(username => !props.selected.includes(username));
      lookupMessage.value = suggestions.value.length ? '' : 'No matching users.';
    } catch {
      if (!controller.signal.aborted) lookupMessage.value = 'User search unavailable.';
    }
  }, 250);
  cleanup(() => { clearTimeout(timer); controller.abort(); });
});
</script>
<template>
  <div>
    <label :for="id">Username</label>
    <div class="permission-add">
      <input :id="id" v-model="query" :list="id + '-options'" maxlength="150" autocomplete="off" :disabled="disabled" @keydown.enter.prevent="add">
      <datalist :id="id + '-options'"><option v-for="username in suggestions" :key="username" :value="username" /></datalist>
      <button type="button" class="secondary" :disabled="!canAdd" @click="add">Add user</button>
    </div>
    <p aria-live="polite">{{ lookupMessage }}</p>
  </div>
</template>
<style scoped>
.permission-add { display: flex; gap: 8px; align-items: center; max-width: 480px; }
.permission-add input { min-width: 0; flex: 1; }
.permission-add button { flex: 0 0 auto; }
</style>
