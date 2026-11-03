<script setup lang="ts">
defineProps<{ name: string }>();
const sprite = document.querySelector<HTMLMetaElement>('meta[name="ui-icons-url"]')?.content || '/static/html/field-icons.svg';
</script>

<template>
  <svg class="ui-icon" aria-hidden="true" focusable="false"><use :href="`${sprite}#${name}`" /></svg>
</template>
