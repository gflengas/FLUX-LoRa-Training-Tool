from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class ModelInfo(BaseModel):
    name: str
    type: str
    characteristics: str

class TrainingSettings(BaseModel):
    replicateUsername: str
    replicateApiKey: str
    xaiApiKey: Optional[str]
    steps: int
    loraRank: int
    learningRate: float
    batchSize: int
    resolution: str
    optimizer: str
    autoCaptioning: bool
    hfRepoId: Optional[str]
    hfToken: Optional[str]
    captionDropoutRate: float

class TrainingRequest(BaseModel):
    modelInfo: ModelInfo
    settings: TrainingSettings
    imageLocation: str

class TrainingResponse(BaseModel):
    status: str
    trainingId: str
    modelUrl: Optional[str]