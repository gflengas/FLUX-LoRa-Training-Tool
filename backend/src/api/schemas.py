from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Literal, Optional

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


class LocalTrainingSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    steps: int = Field(default=1000, ge=1, le=10000, strict=True)
    loraRank: int = Field(default=16, ge=4, le=128, strict=True)
    learningRate: float = Field(default=1e-4, gt=0, le=1e-3)
    batchSize: int = Field(default=1, ge=1, le=4, strict=True)
    resolution: str = "512"
    optimizer: Literal["adamw8bit", "adamw"] = "adamw8bit"
    captionDropoutRate: float = Field(default=0.05, ge=0, le=0.5)
    autoCaptioning: Literal[False] = False
    saveEvery: int = Field(default=250, ge=1, le=1000, strict=True)
    seed: int = Field(default=42, ge=0, le=4294967295, strict=True)

    @field_validator("resolution")
    @classmethod
    def validate_resolutions(cls, value):
        parts = value.split(",")
        if not 1 <= len(parts) <= 3 or any(p.strip() not in {"512", "768", "1024"} for p in parts):
            raise ValueError("Resolution must contain 512, 768 or 1024, separated by commas")
        return ",".join(dict.fromkeys(p.strip() for p in parts))


class LocalModelInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
    type: Literal["human", "item", "pet"] = "human"
    characteristics: str = Field(default="", max_length=2000)


class LocalTrainingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    engine: Literal["local"]
    modelId: Literal["z-image-turbo"] = "z-image-turbo"
    modelInfo: LocalModelInfo
    settings: LocalTrainingSettings = Field(default_factory=LocalTrainingSettings)
    datasetPath: str = Field(min_length=1, max_length=4096)


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
