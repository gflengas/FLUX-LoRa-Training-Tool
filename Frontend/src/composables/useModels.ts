import { computed, ref, watch } from 'vue';
import { ApiError, fetchModels } from '../api';
import type { ModelCatalog } from '../types';

export function useModels() {
  const catalog = ref<ModelCatalog>({
    models: [],
    loras: [],
    inferenceAvailable: false,
  });
  const modelId = ref('');
  const loraId = ref('');
  const loading = ref(false);
  const error = ref('');
  const connectionError = ref('');
  function reportConnectionError(cause: unknown) {
    if (cause instanceof ApiError && cause.status === 503) {
      connectionError.value = cause.message;
      catalog.value.inferenceAvailable = false;
    }
  }
  const compatibleLoras = computed(() =>
    catalog.value.loras.filter((lora) => lora.baseModelId === modelId.value),
  );
  watch(modelId, () => {
    loraId.value = '';
  });
  async function refresh() {
    if (loading.value) return;
    loading.value = true;
    error.value = '';
    try {
      const data = await fetchModels();
      if (!Array.isArray(data.models) || !Array.isArray(data.loras))
        throw new Error('Invalid model catalog');
      catalog.value = data;
      connectionError.value = '';
      if (!data.models.some((model) => model.id === modelId.value))
        modelId.value = data.models[0]?.id || '';
      if (!compatibleLoras.value.some((lora) => lora.id === loraId.value))
        loraId.value = '';
    } catch (cause) {
      catalog.value = { models: [], loras: [], inferenceAvailable: false };
      modelId.value = '';
      loraId.value = '';
      error.value =
        cause instanceof Error
          ? cause.message
          : 'Could not discover local models.';
      return cause;
    } finally {
      loading.value = false;
    }
  }
  return {
    catalog,
    modelId,
    loraId,
    compatibleLoras,
    loading,
    error,
    connectionError,
    reportConnectionError,
    refresh,
  };
}
export type ModelLibrary = ReturnType<typeof useModels>;
