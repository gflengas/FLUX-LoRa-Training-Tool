<script setup lang="ts">
import { ref } from 'vue';
import { ChevronDown, ChevronUp, CircleHelp } from '@lucide/vue';
import SecretInput from './SecretInput.vue';
import type { TrainingSettings } from '../types';
const settings = defineModel<TrainingSettings>({ required: true });
const advanced = ref(true);
const optimizers = {
  adamw8bit: 'AdamW 8-bit',
  prodigy: 'Prodigy',
  adam8bit: 'Adam 8-bit',
  lion8bit: 'Lion 8-bit',
  adam: 'Adam',
  adamw: 'AdamW',
  lion: 'Lion',
  adagrad: 'Adagrad',
  adafactor: 'Adafactor',
};
</script>
<template>
  <div class="stack">
    <div class="spread">
      <label for="autoCaptioning">Auto Captioning</label>
      <input
        id="autoCaptioning"
        v-model="settings.autoCaptioning"
        class="switch"
        type="checkbox"
        role="switch"
      />
    </div>
    <div class="field">
      <label for="steps">Steps</label>
      <input
        id="steps"
        v-model.number="settings.steps"
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
          min="1"
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
          min="0"
          required
        />
      </div>
      <div class="field">
        <label for="batchSize">Batch Size</label>
        <input
          id="batchSize"
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
          max="1"
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
    <details>
      <summary>Optional publishing</summary>
      <div class="stack details-body">
        <div class="field">
          <label for="hfRepoId">Hugging Face Repository ID</label>
          <input
            id="hfRepoId"
            v-model="settings.hfRepoId"
            placeholder="username/repository"
          />
        </div>
        <div class="field">
          <label for="hfToken">Hugging Face Token</label>
          <SecretInput
            id="hfToken"
            v-model="settings.hfToken"
            label="Hugging Face token"
            placeholder="Enter your Hugging Face token"
          />
        </div>
      </div>
    </details>
    <details id="cloud-connection">
      <summary>Training service connection</summary>
      <div class="stack details-body">
        <p class="muted">
          The current trainer uses Replicate. Enable Auto Captioning to skip
          xAI.
        </p>
        <div class="field">
          <label for="replicateUsername">Replicate Username</label>
          <input
            id="replicateUsername"
            v-model="settings.replicateUsername"
            placeholder="Enter your Replicate username"
            autocomplete="off"
          />
        </div>
        <div class="field">
          <label for="replicateApiKey">Replicate API Key</label>
          <SecretInput
            id="replicateApiKey"
            v-model="settings.replicateApiKey"
            label="Replicate API key"
            placeholder="Enter your Replicate API key"
          />
        </div>
        <div class="field">
          <div class="inline">
            <label for="xaiApiKey">xAI API Key</label>
            <button
              type="button"
              class="help"
              title="Leave empty and enable Auto Captioning to skip detailed descriptions using xAI."
              aria-label="xAI captioning help"
            >
              <CircleHelp />
            </button>
          </div>
          <SecretInput
            id="xaiApiKey"
            v-model="settings.xaiApiKey"
            label="xAI API key"
            placeholder="Enter your xAI API key"
          />
        </div>
      </div>
    </details>
  </div>
</template>
