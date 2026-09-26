<script setup lang="ts">
import { Activity, Hash, Link2, ExternalLink, CircleAlert } from '@lucide/vue';
import { computed } from 'vue';
import type { TrainingResult } from '../types';
const props = defineProps<{ result?: TrainingResult; error: string }>();
const trainingUrl = computed(
  () =>
    safeLink(props.result?.trainingUrl) ||
    `https://replicate.com/p/${encodeURIComponent(props.result?.trainingId || '')}`,
);
function safeLink(url?: string) {
  if (!url) return undefined;
  try {
    const parsed = new URL(url);
    return ['https:', 'http:'].includes(parsed.protocol)
      ? parsed.href
      : undefined;
  } catch {
    return undefined;
  }
}
</script>
<template>
  <div v-if="result || error" class="card inset status" aria-live="polite">
    <div class="inline">
      <Activity />
      <strong>Status:</strong>
      <span>{{ error ? 'Failed' : 'Training' }}</span>
    </div>
    <template v-if="result">
      <div class="inline">
        <Hash />
        <strong>Training ID:</strong>
        <code>{{ result.trainingId }}</code>
      </div>
      <div v-if="safeLink(result.modelUrl)">
        <div class="inline">
          <Link2 />
          <strong>Model:</strong>
          <a
            :href="safeLink(result.modelUrl)"
            target="_blank"
            rel="noopener noreferrer"
          >
            View Model Page
            <ExternalLink />
          </a>
        </div>
        <p class="url muted">
          {{ result.modelUrl?.replace(/^https?:\/\//, '') }}
        </p>
      </div>
      <div>
        <div class="inline">
          <Activity />
          <strong>Training:</strong>
          <a :href="trainingUrl" target="_blank" rel="noopener noreferrer">
            View Progress
            <ExternalLink />
          </a>
        </div>
        <p class="url muted">{{ trainingUrl.replace(/^https?:\/\//, '') }}</p>
      </div>
    </template>
    <p v-if="error" class="error inline" role="alert">
      <CircleAlert />
      {{ error }}
    </p>
  </div>
</template>
