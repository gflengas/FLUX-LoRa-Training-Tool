<script setup lang="ts">
import { ref } from 'vue';
import { ChevronDown, ChevronUp } from '@lucide/vue';
import type { TrainingSettings } from '../types';
const settings = defineModel<TrainingSettings>({ required: true });
const advanced = ref(true);
const optimizers = { adamw8bit: 'AdamW 8-bit', adamw: 'AdamW' };
</script>
<template>
  <div class="stack">
    <div class="spread">
      <label for="autoCaptioning">Generate descriptions with a local LLM</label>
      <input
        id="autoCaptioning"
        aria-describedby="captioning-note"
        v-model="settings.autoCaptioning"
        type="checkbox"
      />
    </div>
    <p class="muted" id="captioning-note">
      Planned feature — not available yet. For now, leave this unchecked and
      provide a matching .txt caption for each image.
    </p>
    <div class="field">
      <label for="steps">Steps</label>
      <input
        id="steps"
        v-model.number="settings.steps"
        max="10000"
        type="number"
        min="1"
        required
      />
    </div>
    <button
      type="button"
      class="button outline full"
      :aria-expanded="advanced"
      aria-controls="advanced-settings"
      @click="advanced = !advanced"
    >
      <ChevronUp v-if="advanced" />
      <ChevronDown v-else />
      {{ advanced ? 'Hide' : 'Show' }}
      Advanced Options
    </button>
    <div v-show="advanced" id="advanced-settings" class="field-grid">
      <div class="field">
        <label for="loraRank">LoRA Rank</label>
        <input
          id="loraRank"
          v-model.number="settings.loraRank"
          type="number"
          min="4"
          max="128"
          required
        />
      </div>
      <div class="field">
        <label for="learningRate">Learning Rate</label>
        <input
          id="learningRate"
          v-model.number="settings.learningRate"
          type="number"
          step="any"
          min="0.00000001"
          max="0.001"
          required
        />
      </div>
      <div class="field">
        <label for="batchSize">Batch Size</label>
        <input
          id="batchSize"
          max="4"
          v-model.number="settings.batchSize"
          type="number"
          min="1"
          required
        />
      </div>
      <div class="field">
        <label for="resolution">Resolution</label>
        <input
          id="resolution"
          v-model="settings.resolution"
          placeholder="512,768,1024"
          required
        />
        <p class="muted">
          Comma-separated list of resolutions (e.g., 512,768,1024)
        </p>
      </div>
      <div class="field">
        <label for="captionDropoutRate">Caption Dropout Rate</label>
        <input
          id="captionDropoutRate"
          v-model.number="settings.captionDropoutRate"
          type="number"
          step="0.01"
          min="0"
          max="0.5"
          required
        />
      </div>
      <div class="field">
        <label for="optimizer">Optimizer</label>
        <select id="optimizer" v-model="settings.optimizer">
          <option
            v-for="(label, value) in optimizers"
            :key="value"
            :value="value"
          >
            {{ label }}
          </option>
        </select>
      </div>
    </div>
    <div class="field-grid">
      <div class="field">
        <label for="saveEvery">Save Every (steps)</label>
        <input
          id="saveEvery"
          v-model.number="settings.saveEvery"
          type="number"
          min="1"
          max="1000"
          required
        />
      </div>
      <div class="field">
        <label for="trainingSeed">Seed</label>
        <input
          id="trainingSeed"
          v-model.number="settings.seed"
          type="number"
          min="0"
          max="4294967295"
          required
        />
      </div>
    </div>
  </div>
</template>
