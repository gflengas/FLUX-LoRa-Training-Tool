export type ModelType = 'human' | 'item' | 'pet';
export interface ModelInfo {
  name: string;
  type: ModelType;
  characteristics: Record<string, string | number>;
}
export interface TrainingSettings {
  replicateUsername: string;
  replicateApiKey: string;
  xaiApiKey: string;
  autoCaptioning: boolean;
  steps: number;
  loraRank: number;
  hfRepoId: string;
  hfToken: string;
  learningRate: number;
  batchSize: number;
  resolution: string;
  captionDropoutRate: number;
  optimizer: string;
}
export function defaultSettings(): TrainingSettings {
  return {
    replicateUsername: '',
    replicateApiKey: '',
    xaiApiKey: '',
    autoCaptioning: false,
    steps: 1000,
    loraRank: 16,
    hfRepoId: '',
    hfToken: '',
    learningRate: 0.0004,
    batchSize: 1,
    resolution: '512,768,1024',
    captionDropoutRate: 0.05,
    optimizer: 'adamw8bit',
  };
}
export interface TrainingResult {
  status: string;
  trainingId: string;
  modelUrl?: string;
  trainingUrl?: string;
}

export interface LocalModel {
  id: string;
  name: string;
}
export interface LocalLora extends LocalModel {
  baseModelId: string;
  triggerWord?: string;
}
export interface ModelCatalog {
  models: LocalModel[];
  loras: LocalLora[];
  inferenceAvailable: boolean;
}
export interface GenerationSettings {
  prompt: string;
  negativePrompt: string;
  strength: number;
  width: number;
  height: number;
  images: number;
  steps: number;
  seed: number | null;
  guidance: number;
}
export interface GeneratedImage {
  url: string;
  seed: number;
  width: number;
  height: number;
}
export interface GenerationResult {
  images: GeneratedImage[];
}
