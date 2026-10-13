from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional

class ModelInfo(BaseModel):
    name: str
    type: str
    characteristics: str

class TrainingSettings(BaseModel):
    replicateUsername: str
    replicateApiKey: str
    # Make xaiApiKey optional with None as default
    xaiApiKey: Optional[str] = None
    steps: int
    loraRank: int
    learningRate: float
    batchSize: int
    resolution: str
    optimizer: str
    autoCaptioning: bool
    hfRepoId: Optional[str] = None
    hfToken: Optional[str] = None
    captionDropoutRate: float

class TrainingRequest(BaseModel):
    modelInfo: ModelInfo
    settings: TrainingSettings
    imageLocation: str

class TrainingResponse(BaseModel):
    status: str
    trainingId: str
    modelUrl: Optional[str]
    trainingUrl: Optional[str] = None


class InferenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    modelId: str = Field(min_length=1, max_length=255)
    prompt: str = Field(min_length=1, max_length=8000)
    negativePrompt: str = Field(default="", max_length=8000)
    width: int = Field(default=1024, ge=512, le=1024, strict=True)
    height: int = Field(default=1024, ge=512, le=1024, strict=True)
    images: int = Field(default=1, ge=1, le=4, strict=True)
    steps: int = Field(default=30, ge=1, le=150, strict=True)
    guidance: float = Field(default=7, ge=0, le=30)
    seed: Optional[int] = Field(default=None, ge=0, le=4294967295, strict=True)
    loraId: Optional[str] = None
    strength: float = Field(default=0.8, ge=0, le=2)

    @field_validator("width", "height")
    @classmethod
    def validate_dimensions(cls, value):
        if value % 64:
            raise ValueError("Image dimensions must be multiples of 64")
        return value

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value):
        if not value.strip():
            raise ValueError("Enter a prompt")
        return value.strip()


class InferenceResponse(BaseModel):
    status: str
    jobId: str
