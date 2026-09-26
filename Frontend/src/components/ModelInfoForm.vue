<script setup lang="ts">
import { ref } from 'vue';
import { Image, Upload, Play, Loader2, CircleHelp } from '@lucide/vue';
import CharacteristicsForm from './CharacteristicsForm.vue';
import ImageGuidelines from './ImageGuidelines.vue';
import TrainingStatus from './TrainingStatus.vue';
import TrainingSettingsForm from './TrainingSettings.vue';
import { startTraining } from '../api';
import type {
  ModelInfo,
  ModelType,
  TrainingSettings,
  TrainingResult,
} from '../types';
const model = defineModel<ModelInfo>({ required: true });
const settings = defineModel<TrainingSettings>('settings', { required: true });
const { suggestedDataset } = defineProps<{ suggestedDataset?: File }>();
const emit = defineEmits<{ notice: [message: string]; datasetUsed: [] }>();
function useSuggestedDataset() {
  file.value = suggestedDataset;
  accepted.value = true;
  emit('datasetUsed');
}
const guidelines = ref<InstanceType<typeof ImageGuidelines>>();
const accepted = ref(false);
const fileInput = ref<HTMLInputElement>();
const file = ref<File>();
const dragging = ref(false);
const busy = ref(false);
const error = ref('');
const result = ref<TrainingResult>();
const modelTypes: ModelType[] = ['human', 'item', 'pet'];
function selectFile(files?: FileList | null) {
  dragging.value = false;
  if (!files?.length) return;
  if (files.length !== 1 || !files[0].name.toLowerCase().endsWith('.zip')) {
    emit('notice', 'Please select one ZIP file.');
    return;
  }
  file.value = files[0];
  error.value = '';
}
async function submit() {
  if (busy.value || result.value) return;
  if (!model.value.name.trim())
    return emit('notice', 'Please enter a model name');
  if (!Object.values(model.value.characteristics).some((value) => value !== ''))
    return emit('notice', 'Please fill in the characteristics');
  if (!file.value) return emit('notice', 'Please select a ZIP file');
  if (
    !settings.value.replicateUsername.trim() ||
    !settings.value.replicateApiKey.trim()
  ) {
    emit(
      'notice',
      'Enter your Replicate username and API key in Training Settings.',
    );
    document
      .querySelector<HTMLDetailsElement>('#cloud-connection')
      ?.setAttribute('open', '');
    document.getElementById('replicateUsername')?.focus();
    return;
  }
  busy.value = true;
  error.value = '';
  try {
    // Snapshot settings so edits during the upload cannot change the submitted job.
    result.value = await startTraining(
      file.value,
      { ...model.value, characteristics: { ...model.value.characteristics } },
      { ...settings.value },
    );
    emit('notice', 'Your model training has begun successfully');
  } catch (cause) {
    error.value =
      cause instanceof Error ? cause.message : 'Failed to start training';
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <form class="model-form" @submit.prevent="submit">
    <fieldset class="training-grid" :disabled="busy || !!result">
      <section class="card panel stack-large">
        <h2>Model Information</h2>
        <div v-if="suggestedDataset" class="notice stack">
          <p>
            A generated portrait is ready to use as a training dataset. This
            replaces the current ZIP selection.
          </p>
          <button
            class="button outline"
            type="button"
            @click="useSuggestedDataset"
          >
            Use generated portrait
          </button>
        </div>
        <div class="field">
          <label for="name">Model Name</label>
          <input
            id="name"
            v-model="model.name"
            placeholder="Enter model name"
          />
        </div>
        <div class="field">
          <label for="training-base">Base Model</label>
          <input
            id="training-base"
            value="FLUX.1 dev (current trainer)"
            readonly
          />
        </div>
        <fieldset class="field">
          <legend>Model Type</legend>
          <div class="radio-row">
            <label v-for="type in modelTypes" :key="type" class="inline">
              <input
                v-model="model.type"
                type="radio"
                name="modelType"
                :value="type"
                @change="model.characteristics = {}"
              />
              {{ type[0].toUpperCase() + type.slice(1) }}
            </label>
          </div>
        </fieldset>
        <div class="stack">
          <span class="field-label">Characteristics</span>
          <CharacteristicsForm
            v-model="model.characteristics"
            :type="model.type"
          />
        </div>
        <div class="stack">
          <div class="spread">
            <span class="field-label">Training Images</span>
            <button
              v-if="accepted"
              type="button"
              class="icon-button"
              aria-label="View image guidelines"
              @click="guidelines?.open()"
            >
              <CircleHelp />
            </button>
          </div>
          <button
            v-if="!accepted"
            type="button"
            class="button outline full"
            @click="guidelines?.open()"
          >
            <Image />
            View Image Guidelines
          </button>
          <template v-else>
            <button
              type="button"
              class="dropzone"
              :class="{ dragging }"
              @click="fileInput?.click()"
              @dragover.prevent="dragging = true"
              @dragleave.prevent="dragging = false"
              @drop.prevent="selectFile($event.dataTransfer?.files)"
            >
              <Upload />
              <span>
                {{
                  dragging
                    ? 'Drop the ZIP file here...'
                    : 'Drag & drop your ZIP file here, or click to select'
                }}
              </span>
            </button>
            <input
              ref="fileInput"
              class="sr-only"
              type="file"
              accept=".zip,application/zip"
              aria-label="Training ZIP file"
              tabindex="-1"
              @change="selectFile(($event.target as HTMLInputElement).files)"
            />
            <div v-if="file" class="card selected-file inline">
              <Image />
              <span>{{ file.name }}</span>
            </div>
          </template>
        </div>
      </section>
      <section class="card panel stack-large">
        <h2>Training Settings</h2>
        <TrainingSettingsForm v-model="settings" />
        <button
          class="button primary full"
          type="submit"
          :disabled="!file || !accepted || busy || !!result"
        >
          <Loader2 v-if="busy" class="spin" />
          <Play v-else />
          {{ busy ? 'Starting Training...' : 'Start Training' }}
        </button>
        <p class="muted">
          Training currently runs on Replicate. Local training support is coming
          next.
        </p>
      </section>
    </fieldset>
    <section v-if="!result && !error" class="card panel training-ready stack">
      <div class="inline">
        <h2>Training Status</h2>
        <span class="badge">{{ busy ? 'Starting' : 'Ready' }}</span>
      </div>
      <p class="muted">
        {{
          busy
            ? 'Uploading your dataset and submitting the training request…'
            : 'Choose a dataset and review your settings to start.'
        }}
      </p>
      <progress v-if="busy" aria-label="Starting training" />
      <div v-else class="empty-progress" />
    </section>
    <TrainingStatus :result="result" :error="error" />
  </form>
  <ImageGuidelines ref="guidelines" @accept="accepted = true" />
</template>
