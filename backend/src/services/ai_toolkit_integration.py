import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from contextlib import contextmanager
from uuid import uuid4

from src.config import (
    PROJECT_ROOT, MODELS_DIR, TRAINING_DIR, TRAINING_OUTPUT, TRAINING_IMAGE,
)


class TrainingUnavailable(RuntimeError):
    pass


class TrainingBusy(RuntimeError):
    pass


def call_docker(*args, timeout=30):
    """Run Docker directly; request values are never interpreted by a shell."""
    try:
        return subprocess.run(
            ["docker", *args], capture_output=True, text=True, timeout=timeout, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise TrainingUnavailable("Docker is unavailable or timed out. Check Docker and retry.") from exc


def check_training_engine():
    if call_docker("info", "--format", "{{.ServerVersion}}").returncode:
        raise TrainingUnavailable("Cannot reach Docker. Start Docker and check your docker group permissions.")
    if call_docker("image", "inspect", TRAINING_IMAGE).returncode:
        raise TrainingUnavailable(
            "Training image is missing. Run docker compose -f compose.training.yml --profile training build trainer."
        )


@contextmanager
def training_lock():
    # Cross-process lock also covers multiple Flask/Gunicorn workers.
    TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    with (TRAINING_DIR / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def write_job(job):
    path = TRAINING_DIR / job["trainingId"] / "job.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(job, indent=2))
    temporary.replace(path)


def read_job(job_id):
    return json.loads((TRAINING_DIR / job_id / "job.json").read_text())


def prepare_dataset(dataset_path, output_folder):
    """Snapshot local images and paired captions so training never changes the originals."""
    from PIL import Image, UnidentifiedImageError

    source = Path(dataset_path).expanduser()
    if not source.is_absolute() or not source.is_dir():
        raise ValueError("datasetPath must be an existing absolute directory path.")
    source = source.resolve()
    if source == Path(source.anchor) or output_folder.resolve().is_relative_to(source):
        raise ValueError("Choose the specific image dataset folder, not the filesystem or project root.")
    count, entries, total_bytes = 0, 0, 0
    try:
        for directory, folders, filenames in os.walk(source, followlinks=False):
            folders[:] = sorted(name for name in folders if not name.startswith(".") and not (Path(directory) / name).is_symlink())
            entries += len(filenames) + len(folders)
            if entries > 5000:
                raise ValueError("Dataset folder exceeds 5,000 entries.")
            for name in sorted(filenames):
                image_path = Path(directory) / name
                if name.startswith(".") or image_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                    continue
                caption_path = image_path.with_suffix(".txt")
                if image_path.is_symlink() or caption_path.is_symlink():
                    raise ValueError("Dataset images and captions must be regular files, not symbolic links.")
                if not caption_path.is_file():
                    raise ValueError(f"Missing caption for {name}. Include a matching .txt file; local auto-captioning is not implemented.")
                size = image_path.stat().st_size
                total_bytes += size
                if count >= 500 or total_bytes > 2 * 1024**3:
                    raise ValueError("Dataset exceeds 500 images or 2 GB.")
                if caption_path.stat().st_size > 16000 or size > 50 * 1024**2:
                    raise ValueError("An image exceeds 50 MB or a caption exceeds 16 KB.")
                caption = caption_path.read_text(encoding="utf-8-sig").strip()
                if not caption:
                    raise ValueError(f"Caption for {name} is empty.")
                target = output_folder / f"image_{count:04d}{image_path.suffix.lower()}"
                shutil.copyfile(image_path, target)
                with Image.open(target) as image:
                    if image.width * image.height > 40_000_000 or min(image.size) < 256:
                        raise ValueError("Images must be at least 256px per side and at most 40 megapixels.")
                    image.verify()
                target.with_suffix(".txt").write_text(caption, encoding="utf-8")
                count += 1
        if not count:
            raise ValueError("Dataset folder contains no JPG, PNG or WebP images.")
        return count
    except (UnicodeError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ValueError("Dataset contains an invalid image or UTF-8 caption.") from exc


def build_training_config(req, job_id):
    """Translate the existing camelCase training settings into Ostris's job format."""
    settings = req.settings
    interval = min(settings.saveEvery, settings.steps)
    return {"job": "extension", "config": {
        "name": req.modelInfo.name,
        "process": [{
            "type": "sd_trainer", "training_folder": f"/output/{job_id}",
            "device": "cuda:0", "trigger_word": req.modelInfo.name, "training_seed": settings.seed,
            "network": {"type": "lora", "linear": settings.loraRank, "linear_alpha": settings.loraRank},
            "save": {"dtype": "bf16", "save_every": interval, "max_step_saves_to_keep": 4},
            "datasets": [{
                "folder_path": "/job/dataset", "caption_ext": "txt",
                "caption_dropout_rate": settings.captionDropoutRate,
                "cache_latents_to_disk": True,
                "resolution": [int(size) for size in settings.resolution.split(",")],
            }],
            "train": {
                "batch_size": settings.batchSize, "steps": settings.steps,
                "gradient_checkpointing": True, "train_unet": True, "train_text_encoder": False,
                "noise_scheduler": "flowmatch", "timestep_type": "weighted",
                "optimizer": settings.optimizer, "lr": settings.learningRate, "dtype": "bf16",
            },
            "model": {
                # Force full precision for the adapter merge before runtime quantization.
                "name_or_path": "Comfy-Org/z_image_turbo/split_files/diffusion_models/z_image_turbo_bf16.safetensors",
                "extras_name_or_path": "Tongyi-MAI/Z-Image-Turbo",
                "arch": "zimage", "quantize": True, "qtype": "qfloat8",
                "quantize_te": True, "qtype_te": "qfloat8", "low_vram": True,
                "layer_offloading": True,
                "layer_offloading_transformer_percent": 0.3,
                "layer_offloading_text_encoder_percent": 1.0,
                "assistant_lora_path": "ostris/zimage_turbo_training_adapter/zimage_turbo_training_adapter_v2.safetensors",
            },
            "sample": {
                "sampler": "flowmatch", "sample_every": interval, "width": 512, "height": 512,
                "seed": settings.seed, "walk_seed": False, "guidance_scale": 1, "sample_steps": 9,
                "prompts": [f"A photograph of {req.modelInfo.name}, soft daylight, neutral background"],
            },
        }],
    }}


def train_LoRa_locally(req):
    """Prepare an isolated dataset and submit one on-demand AI Toolkit container."""
    with training_lock():
        check_training_engine()
        label = "lora-studio.project=" + hashlib.sha256(str(PROJECT_ROOT).encode()).hexdigest()[:16]
        active = call_docker("ps", "-aq", "--filter", f"label={label}",
                             "--filter", "status=running", "--filter", "status=created",
                             "--filter", "status=restarting", "--filter", "status=paused")
        if active.returncode:
            raise TrainingUnavailable("Could not check running training jobs.")
        if active.stdout.strip():
            raise TrainingBusy("A local training job is already running. Wait for it or cancel it first.")
        comfy = call_docker("ps", "-q", "--filter", "label=com.docker.compose.service=comfyui")
        if comfy.returncode:
            raise TrainingUnavailable("Could not check GPU availability.")
        if comfy.stdout.strip():
            raise TrainingBusy("Stop the ComfyUI inference container before training to free GPU memory.")

        job_id = str(uuid4())
        folder = TRAINING_DIR / job_id
        dataset = folder / "dataset"
        dataset.mkdir(parents=True)
        try:
            image_count = prepare_dataset(req.datasetPath, dataset)
            config = build_training_config(req, job_id)
            (folder / "config.json").write_text(json.dumps(config, indent=2))
        except Exception:
            shutil.rmtree(folder)
            raise
        for path in (TRAINING_DIR / "cache", TRAINING_OUTPUT, MODELS_DIR):
            path.mkdir(parents=True, exist_ok=True)
        container = f"lora-training-{job_id}"
        job = {
            "trainingId": job_id, "status": "starting", "modelId": req.modelId,
            "name": req.modelInfo.name, "triggerWord": req.modelInfo.name,
            "modelType": req.modelInfo.type, "settings": req.settings.model_dump(),
            "imageCount": image_count, "steps": req.settings.steps,
            "datasetPath": str(Path(req.datasetPath).expanduser().resolve()),
            "outputPath": str(TRAINING_OUTPUT / job_id / req.modelInfo.name),
            "container": container, "trainingUrl": f"/api/training/{job_id}",
        }
        write_job(job)
        try:
            created = call_docker(
                "create", "--name", container, "--label", label, "--gpus", "all",
                "--restart", "no", "--user", f"{os.getuid()}:{os.getgid()}",
                "--env", f"SEED={req.settings.seed}",
                "--env", "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
                "--shm-size", "2g", "--log-opt", "max-size=10m", "--log-opt", "max-file=2",
                "--mount", f"type=bind,src={folder},dst=/job",
                "--mount", f"type=bind,src={TRAINING_DIR / 'cache'},dst=/cache",
                "--mount", f"type=bind,src={TRAINING_OUTPUT},dst=/output",
                "--mount", f"type=bind,src={MODELS_DIR.resolve()},dst=/models",
                TRAINING_IMAGE, "/job/config.json",
            )
            if created.returncode:
                raise TrainingUnavailable("Could not create the training container: " + created.stderr[-2000:])
            started = call_docker("start", container)
            if started.returncode:
                raise TrainingUnavailable("Could not start training. Check NVIDIA Container Toolkit: " + started.stderr[-2000:])
        except TrainingUnavailable as exc:
            job.update(status="failed", message=str(exc))
            write_job(job)
            # A timed-out start may still have launched the container. Keep its
            # identity so status/cancel can reconcile it; never silently remove it.
            raise TrainingUnavailable(f"{exc} Job status: /api/training/{job_id}") from exc
        job["status"] = "running"
        write_job(job)
        return {key: value for key, value in job.items() if key != "container"}


def get_training_status(job_id):
    with training_lock():
        job = read_job(job_id)
        if job["status"] in {"completed", "cancelled"} or job.get("finished"):
            return {key: value for key, value in job.items() if key != "container"}
        state_result = call_docker("inspect", "--format", "{{json .State}}", job["container"])
        if state_result.returncode:
            # A stopped daemon is not evidence that the job failed.
            if call_docker("info", "--format", "{{.ServerVersion}}").returncode:
                raise TrainingUnavailable("Cannot reach Docker to check training. Start Docker and retry.")
            job.update(status="failed", finished=True, message="Training container is missing.")
        else:
            state = json.loads(state_result.stdout)
            logs = call_docker("logs", "--tail", "200", job["container"])
            if logs.returncode:
                raise TrainingUnavailable("Could not read training logs. Retry the status request.")
            job["logs"] = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", logs.stdout + logs.stderr)[-24000:]
            if state["Running"]:
                job["status"] = "running"
            elif state["Status"] == "created":
                job["status"] = "starting"
            else:
                job.update(status="failed", finished=True, exitCode=state["ExitCode"])
                artifact = TRAINING_OUTPUT / job_id / job["name"] / f"{job['name']}.safetensors"
                if state["ExitCode"] == 0 and artifact.is_file() and artifact.stat().st_size > 8:
                    destination = MODELS_DIR / "loras" / f"{job_id}.safetensors"
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    temporary = destination.with_suffix(".part")
                    shutil.copyfile(artifact, temporary)
                    temporary.replace(destination)
                    job.update(status="completed", loraPath=str(destination.resolve()), loraId=destination.name)
                else:
                    job["message"] = state.get("Error") or "Training exited without a final LoRA. Check the logs."
        write_job(job)
        return {key: value for key, value in job.items() if key != "container"}


def cancel_training(job_id):
    with training_lock():
        job = read_job(job_id)
        if job["status"] in {"completed", "cancelled"} or job.get("finished"):
            return {key: value for key, value in job.items() if key != "container"}
        stopped = call_docker("stop", "--time", "15", job["container"], timeout=25)
        if stopped.returncode:
            raise TrainingUnavailable("Could not stop the training container. Check Docker and retry.")
        job.update(status="cancelled", finished=True)
        write_job(job)
        return {key: value for key, value in job.items() if key != "container"}
