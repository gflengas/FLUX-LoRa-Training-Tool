<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { Folder, Play, Loader2, CircleHelp } from '@lucide/vue';
import CharacteristicsForm from './CharacteristicsForm.vue';
import ImageGuidelines from './ImageGuidelines.vue';
import DatasetFolderPicker from './DatasetFolderPicker.vue';
import TrainingStatus from './TrainingStatus.vue';
import TrainingSettingsForm from './TrainingSettings.vue';
import { ApiError, startTraining, fetchTraining, cancelTraining } from '../api';
import type {
  ModelInfo,
  ModelType,
  TrainingSettings,
  TrainingResult,
} from '../types';
const model = defineModel<ModelInfo>({ required: true });
const settings = defineModel<TrainingSettings>('settings', { required: true });
const emit = defineEmits<{ notice: [message: string] }>();
const guidelines = ref<InstanceType<typeof ImageGuidelines>>();
const folderPicker = ref<InstanceType<typeof DatasetFolderPicker>>();
const datasetPath = ref('');
const busy = ref(false);
const stopping = ref(false);
const error = ref('');
const result = ref<TrainingResult>();
const jobId = ref('');
const terminal = computed(
  () =>
    !!result.value &&
    ['completed', 'failed', 'cancelled'].includes(result.value.status),
);
const active = computed(() => !!jobId.value && !terminal.value);
const modelTypes: ModelType[] = ['human', 'item', 'pet'];
let timer: ReturnType<typeof setTimeout> | undefined;
let revision = 0;
let disposed = false;
function rememberJob(id: string) {
  try {
    localStorage.setItem('local-training-id', id);
  } catch {
    /* Storage is optional. */
  }
}
function acceptResult(value: TrainingResult) {
  if (!result.value) {
    model.value.name = value.name;
    if (value.modelType) model.value.type = value.modelType;
    datasetPath.value = value.datasetPath;
    if (value.settings) settings.value = { ...value.settings };
    else settings.value.steps = value.steps;
  }
  result.value = value;
  jobId.value = value.trainingId;
  rememberJob(value.trainingId);
}
async function poll() {
  clearTimeout(timer);
  const id = jobId.value;
  const currentRevision = ++revision;
  if (!id || disposed) return;
  try {
    const status = await fetchTraining(id);
    if (disposed || revision !== currentRevision) return;
    acceptResult(status);
    error.value = '';
  } catch (cause) {
    if (disposed || revision !== currentRevision) return;
    error.value =
      cause instanceof Error
        ? cause.message
        : 'Could not read training status.';
    if (cause instanceof ApiError && cause.status === 404) {
      jobId.value = '';
      result.value = undefined;
      rememberJob('');
    }
  } finally {
    if (!disposed && revision === currentRevision && active.value)
      timer = setTimeout(poll, 3000);
  }
}
async function submit() {
  if (busy.value || active.value) return;
  if (settings.value.autoCaptioning)
    return emit(
      'notice',
      'Local LLM descriptions are planned. Uncheck this option and provide .txt captions for now.',
    );
  busy.value = true;
  error.value = '';
  result.value = undefined;
  jobId.value = '';
  rememberJob('');
  try {
    acceptResult(
      await startTraining(
        datasetPath.value.trim(),
        {
          ...model.value,
          name: model.value.name.trim(),
          characteristics: { ...model.value.characteristics },
        },
        { ...settings.value },
      ),
    );
    void poll();
  } catch (cause) {
    error.value =
      cause instanceof Error ? cause.message : 'Failed to start training.';
  } finally {
    busy.value = false;
  }
}
async function cancel() {
  if (!active.value || stopping.value) return;
  stopping.value = true;
  clearTimeout(timer);
  ++revision;
  try {
    acceptResult(await cancelTraining(jobId.value));
    error.value = '';
  } catch (cause) {
    error.value =
      cause instanceof Error ? cause.message : 'Could not stop training.';
  } finally {
    stopping.value = false;
    if (active.value) timer = setTimeout(poll, 3000);
  }
}
onMounted(() => {
  try {
    jobId.value = localStorage.getItem('local-training-id') || '';
  } catch {
    /* Storage is optional. */
  }
  if (jobId.value) void poll();
});
onUnmounted(() => {
  disposed = true;
  ++revision;
  clearTimeout(timer);
});
</script>
<template>
  <form class="model-form" @submit.prevent="submit">
    <fieldset class="training-grid" :disabled="busy || active">
      <section class="card panel stack-large">
        <h2>Model Information</h2>
        <div class="field">
          <label for="name">LoRA Name / Trigger Word</label>
          <input
            id="name"
            v-model="model.name"
            placeholder="e.g. person_xyz"
            pattern="[a-zA-Z0-9][a-zA-Z0-9_\-]*"
            maxlength="64"
            required
          />
          <p class="muted">
            Use this trigger word in your captions. Letters, numbers,
            underscores and hyphens only.
          </p>
        </div>
        <div class="field">
          <label for="training-base">Base Model</label>
          <input id="training-base" value="Z-Image Turbo" readonly />
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
        <details>
          <summary>Characteristics (optional)</summary>
          <div class="stack details-body">
            <p class="muted">
              Reserved for future local descriptions. Training currently uses
              your .txt captions.
            </p>
            <CharacteristicsForm
              v-model="model.characteristics"
              :type="model.type"
            />
          </div>
        </details>
        <div class="stack">
          <div class="spread">
            <label for="dataset-path">Local Dataset Folder</label>
            <button
              type="button"
              class="icon-button"
              aria-label="View image guidelines"
              @click="guidelines?.open()"
            >
              <CircleHelp />
            </button>
          </div>
          <input
            id="dataset-path"
            v-model="datasetPath"
            placeholder="/home/your-user/Pictures/my-dataset"
            required
          />
          <button
            type="button"
            class="button outline full"
            @click="folderPicker?.open(datasetPath.trim())"
          >
            <Folder />
            Browse Folders
          </button>
          <p class="muted">
            Select a folder on this PC with JPG, PNG or WebP images and matching
            .txt captions (photo.jpg + photo.txt). Subfolders are included.
            Original files are kept unchanged.
          </p>
        </div>
      </section>
      <section class="card panel stack-large">
        <h2>Training Settings</h2>
        <TrainingSettingsForm v-model="settings" />
        <button
          class="button primary full"
          type="submit"
          :disabled="
            !datasetPath.trim() || busy || active || settings.autoCaptioning
          "
        >
          <Loader2 v-if="busy" class="spin" />
          <Play v-else />
          {{
            busy
              ? 'Starting Training…'
              : active
                ? 'Training in Progress'
                : 'Start Training'
          }}
        </button>
        <p v-if="settings.autoCaptioning" class="notice" role="status">
          Local LLM descriptions are not implemented yet. Uncheck this option to
          train with existing captions.
        </p>
        <p class="muted">
          Runs locally using Ostris AI Toolkit. Start Docker and stop the
          ComfyUI container before training to free the GPU.
        </p>
      </section>
    </fieldset>
    <section v-if="!result && !error" class="card panel training-ready stack">
      <div class="inline">
        <h2>Training Status</h2>
        <span class="badge">
          {{ busy ? 'Starting' : active ? 'Checking' : 'Ready' }}
        </span>
      </div>
      <p class="muted">
        {{
          busy
            ? 'Preparing the local dataset and starting the training container…'
            : active
              ? 'Restoring your last training job…'
              : 'Choose a dataset folder and review your settings to start.'
        }}
      </p>
      <progress
        v-if="busy || active"
        aria-label="Starting or checking training"
      />
    </section>
    <TrainingStatus
      :result="result"
      :error="error"
      :active="active"
      :stopping="stopping"
      @cancel="cancel"
    />
  </form>
  <DatasetFolderPicker ref="folderPicker" @select="datasetPath = $event" />
  <ImageGuidelines ref="guidelines" />
</template>
