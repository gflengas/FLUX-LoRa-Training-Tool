import json
import os
import secrets
import struct
import tempfile
from functools import lru_cache
from pathlib import Path
from uuid import UUID

import httpx
from src.config import COMFYUI_URL, MODELS_DIR, INFERENCE_OUTPUT
from src.services.comfy_workflows import MODEL_PROFILES, create_component_workflow


def call_comfy(method, path, **kwargs):
    response = httpx.request(method, f"{COMFYUI_URL}{path}", timeout=30, **kwargs)
    response.raise_for_status()
    return response.json()


@lru_cache(maxsize=128)
def read_model_header(path, size, modified):
    # Read only the safetensors header. Size/mtime invalidate the cache on replacement.
    try:
        with open(path, "rb") as file:
            header_size = struct.unpack("<Q", file.read(8))[0]
            if not 0 < header_size <= min(32 * 1024 * 1024, size - 8):
                return {}
            header = json.loads(file.read(header_size))
        if not isinstance(header, dict):
            return {}

        # Do not offer a partially downloaded or malformed checkpoint.
        data_size = size - 8 - header_size
        for name, tensor in header.items():
            if name == "__metadata__":
                continue
            offsets = tensor.get("data_offsets", [])
            if (len(offsets) != 2 or not all(type(value) is int for value in offsets)
                    or not 0 <= offsets[0] <= offsets[1] <= data_size):
                return {}

        return header
    except (OSError, ValueError, TypeError, AttributeError, struct.error):
        return {}


def is_sdxl_checkpoint(path, size, modified):
    header = read_model_header(path, size, modified)
    signatures = {
        "model.diffusion_model.input_blocks.0.0.weight": [320, 4, 3, 3],
        "model.diffusion_model.input_blocks.4.1.transformer_blocks.0.attn2.to_k.weight": [640, 2048],
        "conditioner.embedders.0.transformer.text_model.embeddings.token_embedding.weight": [49408, 768],
        "conditioner.embedders.1.model.token_embedding.weight": [49408, 1280],
        "first_stage_model.decoder.conv_out.weight": [3, 128, 3, 3],
    }
    return all(header.get(name, {}).get("shape") == shape for name, shape in signatures.items())


def component_available(category, name, filenames):
    root = (MODELS_DIR / category).resolve()
    path = (root / name).resolve()
    if name not in filenames or not path.is_relative_to(root):
        return False
    try:
        stat = path.stat()
        return bool(read_model_header(str(path), stat.st_size, stat.st_mtime_ns))
    except OSError:
        return False


def get_models():
    # ComfyUI supplies the filenames it can load; local headers identify compatible models.
    checkpoints = call_comfy("GET", "/models/checkpoints")
    checkpoint_dir = (MODELS_DIR / "checkpoints").resolve()
    models = []
    for name in sorted(set(checkpoints), key=str.casefold):
        path = (checkpoint_dir / name).resolve()
        if path.suffix.lower() != ".safetensors" or not path.is_relative_to(checkpoint_dir):
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        if is_sdxl_checkpoint(str(path), stat.st_size, stat.st_mtime_ns):
            label = str(Path(name).with_suffix("")).replace("_", " ")
            models.append({"id": name, "name": label, "family": "SDXL"})
    categories = {category: call_comfy("GET", f"/models/{category}")
                  for category in ("diffusion_models", "text_encoders", "vae")}
    for model_id, profile in MODEL_PROFILES.items():
        if all(component_available(category, profile[category], filenames)
               for category, filenames in categories.items()):
            models.append({"id": model_id, **{key: profile[key] for key in
                           ("name", "family", "defaults", "fixedSteps", "fixedGuidance", "negativePrompt")}})
    return {"models": models, "loras": [], "inferenceAvailable": bool(models)}


def create_workflow(settings, seed):
    if settings.modelId in MODEL_PROFILES:
        return create_component_workflow(settings, seed, MODEL_PROFILES[settings.modelId])
    # Load the model, encode both prompts, then sample and save each image.
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": settings.modelId}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": settings.prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": settings.negativePrompt, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {
            "width": settings.width, "height": settings.height, "batch_size": 1
        }},
    }
    for index in range(settings.images):
        sampler, decoder, output = str(10 + index * 3), str(11 + index * 3), str(12 + index * 3)
        workflow[sampler] = {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
            "latent_image": ["4", 0], "seed": (seed + index) % 4294967296,
            "steps": settings.steps, "cfg": settings.guidance,
            "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0
        }}
        workflow[decoder] = {"class_type": "VAEDecode", "inputs": {"samples": [sampler, 0], "vae": ["1", 2]}}
        workflow[output] = {"class_type": "SaveImage", "inputs": {
            "images": [decoder, 0], "filename_prefix": "LoRA-Studio/image"
        }}
    return workflow


def start_inference(settings):
    if settings.loraId:
        raise ValueError("LoRA loading is not implemented yet")
    if settings.modelId not in [model["id"] for model in get_models()["models"]]:
        raise ValueError("Select an available model")

    # Create storage before queueing a GPU job.
    INFERENCE_OUTPUT.mkdir(parents=True, exist_ok=True)
    seed = settings.seed if settings.seed is not None else secrets.randbits(32)
    result = call_comfy("POST", "/prompt", json={"prompt": create_workflow(settings, seed)})
    job_id = str(UUID(result["prompt_id"]))
    job = {"seed": seed, "settings": settings.model_dump()}
    (INFERENCE_OUTPUT / f"{job_id}.json").write_text(json.dumps(job))
    return {"status": "queued", "jobId": job_id}


def get_inference_status(job_id):
    job_id = str(UUID(job_id))
    job_path = INFERENCE_OUTPUT / f"{job_id}.json"
    job = json.loads(job_path.read_text())
    settings = job["settings"]
    if "result" in job:
        return job["result"]

    history = call_comfy("GET", f"/history/{job_id}").get(job_id)
    if not history:
        queue = call_comfy("GET", "/queue")
        for key, status in [("queue_running", "running"), ("queue_pending", "queued")]:
            if any(item[1] == job_id for item in queue.get(key, [])):
                return {"status": status}
        # Check again in case the job completed between the two requests.
        history = call_comfy("GET", f"/history/{job_id}").get(job_id)
        if not history:
            return {"status": "failed", "message": "Generation disappeared from the engine. Please retry."}

    if history.get("status", {}).get("status_str") == "error":
        return {"status": "failed", "message": "ComfyUI could not generate the image. Check its container logs."}
    if not history.get("status", {}).get("completed"):
        return {"status": "running"}

    # Copy completed images to the app so they remain available after stopping Docker.
    images = []
    for index in range(settings["images"]):
        outputs = history.get("outputs", {}).get(str(12 + index * 3), {}).get("images", [])
        if not outputs:
            return {"status": "failed", "message": "ComfyUI returned no image for this generation."}
        output = outputs[0]
        response = httpx.get(f"{COMFYUI_URL}/view", params={
            "filename": output["filename"], "subfolder": output.get("subfolder", ""), "type": "output"
        }, timeout=30)
        response.raise_for_status()
        filename = f"{job_id}_{index}.png"
        (INFERENCE_OUTPUT / filename).write_bytes(response.content)
        images.append({"url": f"/api/inference/images/{filename}",
                       "seed": (job["seed"] + index) % 4294967296,
                       "width": settings["width"], "height": settings["height"]})
    job["result"] = {"status": "completed", "images": images}
    # Atomic replacement prevents overlapping status requests from reading partial JSON.
    with tempfile.NamedTemporaryFile(mode="w", dir=INFERENCE_OUTPUT, delete=False) as temp:
        json.dump(job, temp)
    os.replace(temp.name, job_path)
    return job["result"]
