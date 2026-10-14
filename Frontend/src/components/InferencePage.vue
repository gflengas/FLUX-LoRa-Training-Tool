<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  Image,
  Play,
  Loader2,
  Download,
  RotateCcw,
  Check,
  Settings2,
  GraduationCap,
} from '@lucide/vue';
import type { ModelLibrary } from '../composables/useModels';
import type { GeneratedImage, GenerationSettings } from '../types';
import { generateImages } from '../api';
const { library } = defineProps<{ library: ModelLibrary }>();
const emit = defineEmits<{
  models: [];
  train: [];
  notice: [message: string];
}>();
const { catalog, modelId, loraId, compatibleLoras, loading } = library;
const settings = ref<GenerationSettings>({
  prompt: '',
  negativePrompt: '',
  strength: 0.8,
  width: 1024,
  height: 1024,
  images: 1,
  steps: 30,
  seed: null,
  guidance: 7,
});
const selectedModel = computed(() =>
  catalog.value.models.find((model) => model.id === modelId.value),
);
watch(
  modelId,
  () => {
    const model = selectedModel.value;
    settings.value.steps = model?.defaults?.steps ?? 30;
    settings.value.guidance = model?.defaults?.guidance ?? 7;
    if (model?.negativePrompt === false) settings.value.negativePrompt = '';
  },
  { immediate: true },
);
const size = ref('1024x1024');
const busy = ref(false);
const generationStatus = ref('Generating');
const error = ref('');
const output = ref<GeneratedImage[]>([]);
const index = ref(0);
const current = computed(() => output.value[index.value]);
const canGenerate = computed(
  () => !!modelId.value && catalog.value.inferenceAvailable && !loading.value,
);
function imageUrl(value: string) {
  const url = new URL(value, window.location.origin);
  if (!['http:', 'https:'].includes(url.protocol))
    throw new Error('Invalid image URL returned by the backend.');
  return url.href;
}
async function generate() {
  if (busy.value || loading.value) return;
  if (!settings.value.prompt.trim()) return;
  busy.value = true;
  error.value = '';
  try {
    // Check the engine on Generate, including when discovery previously failed.
    const discoveryError = await library.refresh();
    if (discoveryError) throw discoveryError;
    if (!canGenerate.value)
      throw new Error('No supported model is available. Check Model Settings.');
    const [width, height] = size.value.split('x').map(Number);
    const request = {
      ...settings.value,
      width,
      height,
      seed:
        settings.value.seed === null || String(settings.value.seed) === ''
          ? null
          : Number(settings.value.seed),
    };
    const result = await generateImages(
      modelId.value,
      loraId.value,
      request,
      (status) => {
        generationStatus.value = status;
      },
    );
    if (!result.images?.length)
      throw new Error('The backend returned no images.');
    output.value = result.images.map((image) => ({
      ...image,
      url: imageUrl(image.url),
    }));
    index.value = 0;
  } catch (cause) {
    library.reportConnectionError(cause);
    error.value = library.connectionError.value
      ? ''
      : cause instanceof Error
        ? cause.message
        : 'Generation failed. Please retry.';
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <div class="inference-grid">
    <form class="card panel stack-large" @submit.prevent="generate">
      <h2>Generation</h2>
      <fieldset class="stack-large" :disabled="busy">
        <div class="field">
          <label for="inference-model">Base model</label>
          <select
            id="inference-model"
            v-model="modelId"
            :disabled="loading || !catalog.models.length"
          >
            <option v-if="!catalog.models.length" value="">
              No models available
            </option>
            <option
              v-for="model in catalog.models"
              :key="model.id"
              :value="model.id"
            >
              {{ model.name }}
            </option>
          </select>
        </div>
        <div class="field">
          <label for="inference-lora">LoRA</label>
          <select id="inference-lora" v-model="loraId">
            <option value="">None</option>
            <option
              v-for="lora in compatibleLoras"
              :key="lora.id"
              :value="lora.id"
            >
              {{ lora.name }}
            </option>
          </select>
        </div>
        <div class="strength">
          <label for="strength">LoRA strength</label>
          <input
            id="strength"
            v-model.number="settings.strength"
            type="range"
            min="0"
            max="2"
            step="0.05"
            :disabled="!loraId"
          />
          <output for="strength">{{ settings.strength.toFixed(2) }}</output>
        </div>
        <div class="field">
          <label for="prompt">Prompt</label>
          <textarea
            id="prompt"
            v-model="settings.prompt"
            rows="4"
            placeholder="Describe the portrait you want to create…"
            required
          />
        </div>
        <details>
          <summary>Negative prompt</summary>
          <div class="field details-body">
            <label for="negative-prompt" class="sr-only">Negative prompt</label>
            <textarea
              id="negative-prompt"
              :disabled="selectedModel?.negativePrompt === false"
              v-model="settings.negativePrompt"
              rows="3"
              placeholder="What should the image avoid?"
            />
          </div>
        </details>
        <div class="field-grid">
          <div class="field">
            <label for="image-size">Size</label>
            <select id="image-size" v-model="size">
              <option value="1024x1024">1024 × 1024</option>
              <option value="768x1024">768 × 1024</option>
              <option value="1024x768">1024 × 768</option>
              <option value="512x512">512 × 512</option>
            </select>
          </div>
          <div class="field">
            <label for="image-count">Images</label>
            <input
              id="image-count"
              v-model.number="settings.images"
              type="number"
              min="1"
              max="4"
              required
            />
          </div>
          <div class="field">
            <label for="inference-steps">Steps</label>
            <input
              id="inference-steps"
              :disabled="selectedModel?.fixedSteps"
              v-model.number="settings.steps"
              type="number"
              min="1"
              max="150"
              required
            />
          </div>
          <div class="field">
            <label for="seed">Seed</label>
            <input
              id="seed"
              v-model.number="settings.seed"
              type="number"
              min="0"
              max="4294967295"
              placeholder="Random"
            />
          </div>
        </div>
        <details>
          <summary>Advanced options</summary>
          <div class="field details-body">
            <label for="guidance">Guidance scale</label>
            <input
              id="guidance"
              :disabled="selectedModel?.fixedGuidance"
              v-model.number="settings.guidance"
              type="number"
              min="0"
              max="30"
              step="0.1"
              required
            />
          </div>
        </details>
        <button
          class="button primary full"
          :disabled="loading || busy || !settings.prompt.trim()"
        >
          <Loader2 v-if="busy" class="spin" />
          <Play v-else />
          {{ busy ? `${generationStatus}…` : 'Generate Image' }}
        </button>
      </fieldset>
      <div v-if="!canGenerate" class="notice">
        <p>Local inference is not connected yet.</p>
        <button
          class="text-button inline"
          type="button"
          @click="emit('models')"
        >
          <Settings2 />
          View available models
        </button>
      </div>
      <p v-else class="muted centered">Runs on this PC</p>
      <p v-if="error" class="error" role="alert">{{ error }}</p>
    </form>
    <section
      class="card panel output-panel stack"
      :aria-busy="busy"
      aria-label="Generated output"
    >
      <div class="spread">
        <h2>Output</h2>
        <span v-if="busy" class="badge">{{ generationStatus }}</span>
        <span v-else-if="current" class="badge inline">
          <Check />
          Completed
        </span>
      </div>
      <div v-if="!current" class="output-empty">
        <Loader2 v-if="busy" class="spin" />
        <Image v-else />
        <h3>
          {{
            busy ? 'Creating your images…' : 'Your next portrait starts here'
          }}
        </h3>
        <p class="muted">
          {{
            busy
              ? 'The result will appear here when it is ready.'
              : 'Choose a model, add a prompt, and generate an image.'
          }}
        </p>
      </div>
      <template v-else>
        <img
          class="generated-image"
          :src="current.url"
          :alt="`Generated portrait ${index + 1}`"
        />
        <div v-if="output.length > 1" class="output-thumbnails">
          <button
            v-for="(image, i) in output"
            :key="i"
            type="button"
            :aria-label="`View image ${i + 1}`"
            :aria-pressed="index === i"
            @click="index = i"
          >
            <img :src="image.url" alt="" />
          </button>
        </div>
        <div class="output-actions">
          <a
            class="button outline"
            :href="current.url"
            :download="`lora-${current.seed}.png`"
          >
            <Download />
            Save Image
          </a>
          <button
            class="button outline"
            @click="
              settings.seed = current!.seed;
              emit('notice', 'Seed copied to generation settings');
            "
          >
            <RotateCcw />
            Reuse Seed
          </button>
          <button class="button outline" @click="emit('train')">
            <GraduationCap />
            Open Training
          </button>
        </div>
        <p class="muted">
          {{ current.width }} × {{ current.height }} · Seed {{ current.seed }}
        </p>
      </template>
    </section>
  </div>
</template>
