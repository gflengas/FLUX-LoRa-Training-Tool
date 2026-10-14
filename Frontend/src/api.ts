import type {
  DatasetFolders,
  ModelInfo,
  TrainingSettings,
  TrainingResult,
  ModelCatalog,
  GenerationSettings,
  GenerationResult,
} from './types';

const apiUrl = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, options);
  const data = await response.json().catch(() => null);
  if (!response.ok)
    throw new ApiError(
      data?.message || `Request failed (${response.status})`,
      response.status,
    );
  if (!data) throw new Error('The server returned an empty response.');
  return data as T;
}

export async function startTraining(
  datasetPath: string,
  model: ModelInfo,
  settings: TrainingSettings,
) {
  return request<TrainingResult>('/training/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      engine: 'local',
      modelId: 'z-image-turbo',
      modelInfo: {
        ...model,
        characteristics: Object.entries(model.characteristics)
          .filter(([, value]) => value !== '')
          .map(([key, value]) => `${key}: ${value}`)
          .join(', '),
      },
      settings,
      datasetPath,
    }),
  });
}

export function fetchTraining(id: string) {
  return request<TrainingResult>(`/training/${encodeURIComponent(id)}`, {
    method: 'GET',
    signal: AbortSignal.timeout(15000),
  });
}
export function cancelTraining(id: string) {
  return request<TrainingResult>(`/training/${encodeURIComponent(id)}/cancel`, {
    method: 'POST',
  });
}
export function fetchDatasetFolders(path = '') {
  return request<DatasetFolders>(
    `/training/folders?path=${encodeURIComponent(path)}`,
    { method: 'GET', signal: AbortSignal.timeout(15000) },
  );
}

export async function fetchModels() {
  return request<ModelCatalog>('/models', { method: 'GET' });
}
export async function generateImages(
  modelId: string,
  loraId: string,
  settings: GenerationSettings,
  onStatus?: (status: string) => void,
) {
  const job = await request<{ jobId: string; status: string }>('/inference', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ modelId, loraId: loraId || null, ...settings }),
  });
  onStatus?.('Queued');
  const deadline = Date.now() + 30 * 60 * 1000;
  while (Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    const result = await request<
      GenerationResult & {
        status: string;
        message?: string;
      }
    >(`/inference/${job.jobId}`, { method: 'GET' });
    if (result.status === 'completed') return result;
    if (result.status === 'failed')
      throw new Error(result.message || 'Generation failed.');
    onStatus?.(result.status === 'queued' ? 'Queued' : 'Generating');
  }
  throw new Error(
    'Stopped waiting after 30 minutes. The job may still be running in ComfyUI.',
  );
}
