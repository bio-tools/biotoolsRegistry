<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue';
import { browserRequest, BrowserRequestError } from './browser-auth';

const props = defineProps<{ endpoint: string }>();
const pending = ref(false);
const message = ref('');
const controller = new AbortController();
onBeforeUnmount(() => controller.abort());

async function verify() {
  pending.value = true;
  message.value = '';
  try {
    await browserRequest(props.endpoint, { method: 'POST', signal: AbortSignal.any([controller.signal, AbortSignal.timeout(10000)]) });
    message.value = 'Session verified.';
  } catch (error) {
    message.value = error instanceof BrowserRequestError && ['authentication_required', 'csrf_failed'].includes(error.code)
      ? 'Session verification requires reconnection.' : 'Could not verify the session. Try again.';
  } finally {
    pending.value = false;
  }
}
</script>
<template>
  <button type="button" :disabled="pending" @click="verify">{{ pending ? 'Verifying...' : 'Verify session' }}</button>
  <p role="status">{{ message }}</p>
</template>
