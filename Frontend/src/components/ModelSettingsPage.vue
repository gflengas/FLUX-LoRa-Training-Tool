<script setup lang="ts">
import { RefreshCw, Box, Layers } from '@lucide/vue';
import type { ModelLibrary } from '../composables/useModels';
const { library } = defineProps<{ library: ModelLibrary }>();
const { catalog, modelId, loraId, compatibleLoras, loading, error } = library;
defineEmits<{ use: [] }>();
</script>
<template>
  <div class="model-library stack-large">
    <section class="card panel stack-large">
      <div class="spread">
        <div>
          <h2>Available Models</h2>
          <p class="muted">Models discovered by the backend</p>
        </div>
        <button
          class="button outline"
          :disabled="loading"
          @click="library.refresh"
        >
          <RefreshCw :class="{ spin: loading }" />
          {{ loading ? 'Refreshing…' : 'Refresh' }}
        </button>
      </div>
      <p v-if="error" class="notice" role="status">{{ error }}</p>
      <div v-if="!catalog.models.length" class="empty-small">
        <Box />
        <p>{{ loading ? 'Looking for models…' : 'No models available' }}</p>
        <span class="muted">Discovered base models will appear here.</span>
      </div>
      <label
        v-for="model in catalog.models"
        :key="model.id"
        class="selection-row"
        :class="{ selected: modelId === model.id }"
      >
        <input
          v-model="modelId"
          type="radio"
          name="base-model"
          :value="model.id"
        />
        <span>
          <strong>{{ model.name }}</strong>
          <small>Base model</small>
        </span>
      </label>
    </section>
    <section class="card panel stack">
      <div>
        <h2>Available LoRAs</h2>
        <p class="muted">Compatible with the selected model</p>
      </div>
      <label class="selection-row" :class="{ selected: !loraId }">
        <input v-model="loraId" type="radio" name="lora-model" value="" />
        <strong>None</strong>
      </label>
      <label
        v-for="lora in compatibleLoras"
        :key="lora.id"
        class="selection-row"
        :class="{ selected: loraId === lora.id }"
      >
        <input
          v-model="loraId"
          type="radio"
          name="lora-model"
          :value="lora.id"
        />
        <span>
          <strong>{{ lora.name }}</strong>
          <small v-if="lora.triggerWord">Trigger: {{ lora.triggerWord }}</small>
        </span>
      </label>
      <p v-if="!compatibleLoras.length" class="muted inline">
        <Layers />
        No compatible LoRAs discovered.
      </p>
    </section>
    <button
      class="button primary full"
      :disabled="!modelId || loading"
      @click="$emit('use')"
    >
      Use Selected Models
    </button>
  </div>
</template>
