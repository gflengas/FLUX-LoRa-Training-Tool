export type ModelType = 'human' | 'item' | 'pet';

export type Gender = 'male' | 'female' | 'other';
export type EyeColor = 'brown' | 'blue' | 'green' | 'hazel' | 'gray';
export type BodyType = 'slim' | 'athletic' | 'average' | 'curvy' | 'muscular';
export type Ethnicity = 'asian' | 'black' | 'hispanic' | 'white' | 'middleEastern' | 'other';
export type OptimizerType = 'adamw8bit' | 'prodigy' | 'adam8bit' | 'lion8bit' | 'adam' | 'adamw' | 'lion' | 'adagrad' | 'adafactor';

export interface HumanCharacteristics {
  age: number;
  gender: Gender;
  eyeColor: EyeColor;
  bodyType: BodyType;
  ethnicity: Ethnicity;
}

export interface PetCharacteristics {
  species: string;
  color: string;
  distinctiveTrait: string;
}

export interface ItemCharacteristics {
  purpose: string;
}

export type ModelCharacteristics = HumanCharacteristics | PetCharacteristics | ItemCharacteristics;

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
  optimizer: OptimizerType;
}

export interface ModelInfo {
  name: string;
  type: ModelType;
  characteristics: ModelCharacteristics;
  images: File[];
}

export interface TrainingStatus {
  status: 'idle' | 'training' | 'failed';
  error?: string;
  replicateUrl?: string;
  trainingId?: string;
  modelUrl?: string;
}