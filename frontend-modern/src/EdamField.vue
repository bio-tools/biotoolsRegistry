<script setup lang="ts">
import { computed, ref } from 'vue';
import EdamSelector from './EdamSelector.vue';
import type { EdamSelectorProps } from './edam';

const props = defineProps<Omit<EdamSelectorProps, 'modelValue'> & { initial: string[] }>();
defineOptions({ inheritAttrs: false });
const value = ref([...props.initial]);
const selectorProps = computed(() => { const { initial, ...selector } = props; return selector; });
</script>
<template><EdamSelector v-bind="selectorProps" v-model="value" /></template>
