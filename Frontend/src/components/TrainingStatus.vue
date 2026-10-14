<script setup lang="ts">
import { Activity, CircleAlert, Square } from '@lucide/vue';
import type { TrainingResult } from '../types';
defineProps<{
  result?: TrainingResult;
  error: string;
  active: boolean;
  stopping: boolean;
}>();
defineEmits<{ cancel: [] }>();
const labels = {
  starting: 'Starting',
  running: 'Training',
  completed: 'Completed',
  failed: 'Failed',
  cancelled: 'Cancelled',
};
</script>
<template>
  <section v-if="result || error" class="card panel training-ready stack">
    <div class="spread">
      <div class="inline" aria-live="polite">
        <Activity />
        <h2>Training Status</h2>
        <span class="badge">
          {{
            result ? labels[result.status] : active ? 'Checking' : 'Not started'
          }}
        </span>
      </div>
      <button
        v-if="active"
        class="button outline"
        type="button"
        :disabled="stopping"
        @click="$emit('cancel')"
      >
        <Square />
        {{ stopping ? 'Stopping…' : 'Stop Training' }}
      </button>
    </div>
    <p v-if="error" class="error inline" role="alert">
      <CircleAlert />
      {{ error }}
    </p>
    <p v-if="error && active" class="muted">
      The job may still be running. Retrying the status check automatically.
    </p>
    <template v-if="result">
      <p>
        {{ result.name }} · {{ result.imageCount }} images ·
        {{ result.steps }} steps requested
      </p>
      <p class="muted local-path">Job: {{ result.trainingId }}</p>
      <p v-if="result.message" role="status">{{ result.message }}</p>
      <p class="local-path">
        <strong>Dataset:</strong>
        {{ result.datasetPath }}
      </p>
      <p class="local-path">
        <strong>Output folder:</strong>
        {{ result.outputPath }}
      </p>
      <p v-if="result.loraPath" class="local-path">
        <strong>Saved LoRA:</strong>
        {{ result.loraPath }}
      </p>
      <details v-if="result.logs" open>
        <summary>Training Logs</summary>
        <pre class="training-logs">{{ result.logs }}</pre>
      </details>
    </template>
  </section>
</template>
