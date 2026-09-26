import type { ModelInfo, TrainingSettings, TrainingResult } from './types';

const apiUrl = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

async function request<T>(path: string, options: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, options);
  const data = await response.json().catch(() => null);
  if (!response.ok)
    throw new Error(data?.message || `Request failed (${response.status})`);
  if (!data) throw new Error('The server returned an empty response.');
  return data as T;
}

export async function startTraining(
  file: File,
  model: ModelInfo,
  settings: TrainingSettings,
) {
  const form = new FormData();
  form.append('file', file);
  const upload = await request<{ filePath: string }>('/upload', {
    method: 'POST',
    body: form,
  });
  return request<TrainingResult>('/training/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      modelInfo: {
        ...model,
        characteristics: Object.entries(model.characteristics)
          .filter(([, value]) => value !== '')
          .map(([key, value]) => `${key}: ${value}`)
          .join(', '),
      },
      settings,
      imageLocation: upload.filePath,
    }),
  });
}

export async function fetchModels() {
  return request<import('./types').ModelCatalog>('/models', { method: 'GET' });
}
export async function generateImages(
  modelId: string,
  loraId: string,
  settings: import('./types').GenerationSettings,
) {
  return request<import('./types').GenerationResult>('/inference', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ modelId, loraId: loraId || null, ...settings }),
  });
}
