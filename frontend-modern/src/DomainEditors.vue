<script setup lang="ts">
import { ref } from 'vue';
import UserPicker from './UserPicker.vue';
const props = defineProps<{ initial: string[] }>();
const editors = ref([...props.initial]);
</script>
<template>
  <fieldset>
    <legend>Domain editors</legend>
    <input type="hidden" name="editors" :value="editors.join('\n')">
    <ul><li v-for="username in editors" :key="username">{{ username }}
      <button type="button" class="secondary" :aria-label="'Remove ' + username" @click="editors = editors.filter(value => value !== username)">Remove</button>
    </li></ul>
    <UserPicker id="domain-user" :selected="editors" :disabled="false" @add="editors.push($event)" />
  </fieldset>
</template>
