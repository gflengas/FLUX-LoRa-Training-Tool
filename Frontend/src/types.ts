export type ModelType = 'human' | 'item' | 'pet';
export interface ModelInfo {
  name: string;
  type: ModelType;
  characteristics: Record<string, string | number>;
}
export interface TrainingSettings {
  autoCaptioning: boolean;
  steps: number;
  loraRank: number;
  learningRate: number;
  batchSize: number;
  resolution: string;
  captionDropoutRate: number;
  optimizer: 'adamw8bit' | 'adamw';
  saveEvery: number;
  seed: number;
}
export function defaultSettings(): TrainingSettings {
  return {
    autoCaptioning: false,
    steps: 1000,
    loraRank: 16,
    learningRate: 0.0001,
    batchSize: 1,
    resolution: '512',
    captionDropoutRate: 0.05,
    optimizer: 'adamw8bit',
    saveEvery: 250,
    seed: 42,
  };
}
export interface TrainingResult {
  status: 'starting' | 'running' | 'completed' | 'failed' | 'cancelled';
  trainingId: string;
  name: string;
  modelType?: ModelType;
  settings?: TrainingSettings;
  imageCount: number;
  steps: number;
  datasetPath: string;
  outputPath: string;
  loraPath?: string;
  logs?: string;
  message?: string;
}
export interface DatasetFolders {
  path: string;
  parent: string | null;
  folders: { name: string; path: string }[];
}

export interface LocalModel {
  id: string;
  name: string;
  family?: string;
  defaults?: { steps: number; guidance: number };
  fixedSteps?: boolean;
  fixedGuidance?: boolean;
  negativePrompt?: boolean;
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
