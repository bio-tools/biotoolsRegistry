<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{ label: string; initial: number }>();
const count = ref(props.initial);
</script>

<template>
  <div class="counter-demo">
    <h2>{{ label }}</h2>
    <div class="counter-controls">
      <button type="button" :aria-label="`Decrease ${label}`" title="Decrease" @click="count--">-</button>
      <output aria-live="polite" :aria-label="label">{{ count }}</output>
      <button type="button" :aria-label="`Increase ${label}`" title="Increase" @click="count++">+</button>
    </div>
  </div>
</template>

<style scoped>
.counter-demo { padding-block: 24px; border-bottom: 1px solid #e6e6e6; }
h2 { overflow-wrap: anywhere; }
.counter-controls { display: flex; align-items: center; gap: 16px; }
button { width: 44px; height: 44px; padding: 0; }
output { min-width: 80px; text-align: center; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
</style>
