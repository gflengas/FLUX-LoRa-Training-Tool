# LoRA Studio

A Vue 3 + TypeScript frontend for image inference, model selection, and LoRA
training, with a Flask API. The UI uses native HTML controls, plain CSS, Lucide
icons, and locally served Inter fonts.

## Current status

- **Inference:** local SDXL, FLUX.2 klein, Z-Image Turbo and Qwen-Image-2.1 Turbo generation through an on-demand ComfyUI container,
  with queued jobs, output gallery, download and seed reuse.
- **Model Settings:** discovers compatible SDXL checkpoints and complete supported model packages from ComfyUI.
  These workflows use the base models only; LoRA loading is not wired yet.
- **Training:** local Z-Image Turbo LoRA jobs through Ostris AI Toolkit, with a
  dataset folder browser, live logs, cancellation and local output paths.

## Run locally without Docker

Requirements: Node.js 22.12+ (or another version supported by Vite), npm, and
Python 3.11. The Python dependencies are pinned for the existing cloud trainer.

From the repository root:

```bash
python3.11 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cd Frontend
npm ci
cp .env.example .env.local
```

Alternatively, provision Python with `uv venv --python 3.11 backend/.venv`, then
install packages with `uv pip install --python backend/.venv/bin/python -r
backend/requirements.txt` from the repository root.

Start the backend in one terminal:

```bash
cd backend
.venv/bin/python -m flask --app app run --host 127.0.0.1 --port 5000
```

Start the frontend in another terminal:

```bash
cd Frontend
npm run dev
```

Open <http://127.0.0.1:3000>. Backend health is available at
<http://127.0.0.1:5000/api/health>. Keep both terminals running; Ctrl+C stops
each service.

Vite forwards `/api` requests to `http://127.0.0.1:5000`. To change that target,
set `API_PROXY_TARGET` in `Frontend/.env.local`. Use `VITE_API_URL` only when
calling a separate API origin. Restart Vite after changing environment variables.

## Local inference (start only when needed)

Keep Vue and Flask running natively as above. ComfyUI runs separately in Docker
with GPU access through NVIDIA Container Toolkit. The container has `restart: "no"`
and is not started automatically by the app.

### 1. Install Docker and enable GPU access (CachyOS / Arch)

Install the NVIDIA driver appropriate for your GPU first; `nvidia-smi` must work
on the host. Then run these once in your terminal:

```bash
sudo pacman -Syu --needed docker docker-compose nvidia-container-toolkit curl
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl start docker
sudo usermod -aG docker "$USER"
```

If Docker was already running when its runtime configuration changed, run
`sudo systemctl restart docker` (this affects other running containers).
Log out and back in to apply the group membership, or run `newgrp docker` for
one terminal. Membership of the docker group grants administrator-level access.
We use `start`, not `enable`, to avoid enabling Docker at boot.
See the [NVIDIA setup guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
for other distributions. Verify the host and Docker before continuing:

```bash
nvidia-smi
docker info
docker compose version
```

### 2. Clone and create the host folders

For a fresh checkout (skip cloning if you already have the repository):

```bash
git clone https://github.com/gflengas/FLUX-LoRa-Training-Tool.git
cd FLUX-LoRa-Training-Tool
```

Run the remaining commands from that repository directory. Use your regular
user for these folders and model downloads, so the container can write outputs:

```bash
mkdir -p models/checkpoints models/diffusion_models models/text_encoders models/vae models/loras
mkdir -p outputs/comfyui outputs/inference .runtime/comfyui-input .runtime/comfyui-user
```

```text
FLUX-LoRa-Training-Tool/
├── Frontend/                    # Native Vue app, port 3000
├── backend/                     # Native Flask API, port 5000
├── comfyui/
│   ├── Dockerfile               # Downloads pinned ComfyUI and Python/CUDA dependencies
│   ├── download_models.py       # Resumable model downloads with SHA-256 checks
│   └── models.json              # Official source revisions, filenames and checksums
├── compose.inference.yml        # Starts only ComfyUI, port 8188
├── models/                      # Host files mounted read-only at /opt/ComfyUI/models
│   ├── checkpoints/             # Complete SDXL checkpoints (optional)
│   ├── diffusion_models/        # FLUX, Z-Image and Qwen generation weights
│   ├── text_encoders/           # Prompt encoders
│   ├── vae/                     # Image decoders
│   └── loras/                   # Reserved; LoRA loading is not implemented yet
├── outputs/
│   ├── comfyui/                 # Engine originals, mounted at /data/output
│   └── inference/               # Flask copies and job JSON, served by our API
└── .runtime/
    ├── comfyui-input/           # Mounted at /data/input
    └── comfyui-user/            # Mounted at /data/user; settings, caches and logs
```

Model weights, outputs and runtime data are ignored by Git. ComfyUI source and
its Python environment live inside the Docker image; no host ComfyUI checkout
or Python environment is required. The frontend/backend setup is described above.

### 3. Download the models

Install Python 3 if needed, then run:

```bash
python3 comfyui/download_models.py
```

This downloads **FLUX.2 klein Base 4B, Z-Image Turbo INT8 and Qwen-Image-2.1
Turbo INT8**, including their encoders and VAEs, into the folders above. Allow
about **40 GB for these weights**, plus extra space for the Docker image and
outputs. It uses pinned official Comfy Org files from `comfyui/models.json`,
checks sizes and SHA-256 hashes, and renames `.part` files only after verification.
Run the same command to resume an interrupted download; existing complete files
are verified and reused. Do not run two copies of the downloader simultaneously.

SDXL is optional. To keep using the original model, place the
[official SDXL base checkpoint](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/sd_xl_base_1.0.safetensors)
at `models/checkpoints/sd_xl_base_1.0.safetensors` (about 6.94 GB extra).
The component filenames and shared encoder are listed below.

### 4. Build and launch ComfyUI

The container defaults to UID/GID 1000. If your IDs differ, run
`export LOCAL_UID=$(id -u) LOCAL_GID=$(id -g)` before the first `up` command.

```bash
docker compose -f compose.inference.yml up --build -d comfyui
docker compose -f compose.inference.yml logs -f comfyui
```

The first build downloads ComfyUI, PyTorch/CUDA and the remaining dependencies;
it can take several minutes. The image includes the compiler needed by Triton.
Press Ctrl+C to leave the log viewer; the container keeps running. Check GPU
access and engine readiness with:

```bash
docker compose -f compose.inference.yml exec comfyui python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
curl --fail http://127.0.0.1:8188/system_stats
```

Both services bind to loopback: ComfyUI's Docker port is accessible only on this
PC, and the native Flask launch above uses `127.0.0.1`. Start the native frontend
and backend using the earlier instructions.

### 5. Use, stop and restart

Wait for ComfyUI to start, then refresh **Model Settings** at
<http://127.0.0.1:3000> and generate an image. ComfyUI itself is available at
<http://127.0.0.1:8188>. Stop it to release GPU memory:

```bash
docker compose -f compose.inference.yml stop comfyui
```

Use `docker compose -f compose.inference.yml start comfyui` for subsequent starts.
If Docker itself is stopped, run `sudo systemctl start docker` first. No boot-time
service enabling is needed. After joining the docker group, open a new login
session or run `newgrp docker` in your terminal.

Models are mounted read-only. Engine outputs remain
in `outputs/comfyui`; Flask copies completed images and job metadata to
`outputs/inference`, so downloaded results remain accessible with ComfyUI stopped.
Polling once after completion is required to copy the result.

### Model discovery and inference settings

Text-to-image supports 512–1024 dimensions in multiples of 64, with 1–4 images.
LoRA loading is not wired into inference yet.

Add complete SDXL `.safetensors` checkpoints to `models/checkpoints/` (subfolders
are supported), then click **Refresh** in Model Settings. The backend checks
SDXL tensor names/shapes without loading the weights. Standard base/finetuned
checkpoints must contain the UNet, both encoders and VAE; refiners, inpainting,
legacy `.ckpt` files and incomplete downloads are excluded.

The following component packages are also discovered through ComfyUI. All three
files for a package must be present and complete; use the filenames below.

| Model | `models/diffusion_models/` | `models/text_encoders/` | `models/vae/` |
| --- | --- | --- | --- |
| [FLUX.2 klein Base 4B](https://huggingface.co/Comfy-Org/flux2-klein) | `flux-2-klein-base-4b.safetensors` | `qwen_3_4b.safetensors` | `flux2-vae.safetensors` |
| [Z-Image Turbo](https://huggingface.co/Comfy-Org/z_image_turbo) | `z_image_turbo_int8_convrot.safetensors` | `qwen_3_4b.safetensors` | `ae.safetensors` |
| [Qwen-Image-2.1 Turbo](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) | `qwen_image_2.1_turbo_int8_convrot.safetensors` | `qwen3vl_8b_int8_convrot.safetensors` | `qwen_image_2.1_vae_bf16.safetensors` |

FLUX and Z-Image share one text encoder. These packages total about 40 GB.
Download into a `.part` file and rename only when complete. Refresh the model
list after adding files; no `.env` change or restart is needed. Header checks are
cached by file size and modification time. The component profiles select the
matching workflow; arbitrary new architectures still require a workflow.

Selecting a model applies its sampling defaults: FLUX Base uses 20 steps/CFG 5,
Z-Image Turbo uses 8 steps/CFG 1, and Qwen Turbo uses its fixed official 8-step
sigma schedule/CFG 1. Unsupported controls are disabled, and the API rejects
incompatible fixed settings. Precision stays in the backend profiles.

`COMFYUI_URL` can be set in the repository-root `.env`. `MODELS_DIR` optionally
changes the backend's model root; it must match the host directory mounted into
ComfyUI.

API flow: `GET /api/models`, `POST /api/inference` (202 with `jobId`), then
`GET /api/inference/<jobId>` until completed or failed. Completed results contain
local image URLs and seeds. Multiple images use consecutive seeds.

## Training from the local frontend

1. Open **Training** and enter a LoRA name/trigger word.
2. Browse to a dataset folder on this PC, or paste its absolute path. Each image
   needs a matching `.txt` caption (for example `photo.jpg` and `photo.txt`).
3. Review the Z-Image Turbo settings. Start with the 512px, rank-16 defaults.
4. Start training. The page polls progress, shows logs and local output paths,
   and lets you stop the job. The last job ID is kept in browser storage so
   refreshing the page reconnects to it; training continues independently.

Folder browsing uses `GET /api/training/folders?path=...` on the local backend.
Keep the frontend and API bound to loopback as shown above.

**Planned: local LLM image descriptions.** The checkbox is a placeholder for
using a local vision-language model to generate captions, replacing the old xAI
API step. This is not implemented yet. While checked, training is disabled;
uncheck it and supply existing captions to train now. Future work: connect a
local vision model, use the trigger/subject information when describing images,
and write caption sidecars without silently overwriting existing captions.

## Local Z-Image Turbo training backend

Build the separate training image once (Docker and NVIDIA setup is shared with
inference). Run Flask from a login session with Docker group access:

```bash
backend/.venv/bin/python -m pip install -r backend/requirements.txt
docker compose -f compose.training.yml --profile training build trainer
docker compose -f compose.inference.yml stop comfyui
```

Flask launches one GPU container per request; it exits when training finishes,
uses `restart: no`, and exposes no ports. Stop ComfyUI before submitting training.
An active training container blocks another training job. No cloud training or
captioning service is called for `engine: local`. Omit `engine` (or use
`replicate`) to retain the existing cloud API behavior.

Use an existing local folder containing JPG/PNG/WebP images and matching UTF-8
`.txt` captions (subfolders are allowed). Include the subject trigger in your
captions. Images must be at least 256px per side. Missing captions are rejected;
automatic local captioning is not implemented. The backend snapshots the dataset
into the job folder, leaving your originals untouched. No upload is needed.

Send `POST /api/training/start` with the absolute dataset directory:

```json
{
  "engine": "local",
  "modelId": "z-image-turbo",
  "modelInfo": {"name": "person_xyz", "type": "human"},
  "datasetPath": "/absolute/path/to/person-dataset",
  "settings": {
    "steps": 1000,
    "loraRank": 16,
    "learningRate": 0.0001,
    "batchSize": 1,
    "resolution": "512",
    "optimizer": "adamw8bit",
    "captionDropoutRate": 0.05,
    "autoCaptioning": false,
    "saveEvery": 250,
    "seed": 42
  }
}
```

Settings are optional; the example shows the defaults. Model names use letters,
digits, underscores or hyphens and also serve as trigger words. `resolution`
accepts `512`, `768`, `1024` or a comma-separated combination. Start at 512 on a
16 GB GPU; actual memory use must be checked on the dataset.

- Submission returns HTTP 202 with `trainingId` and `trainingUrl`.
- Poll `GET /api/training/<trainingId>` for status and the last 200 log lines.
- Cancel with `POST /api/training/<trainingId>/cancel`.
- `outputPath` points to the local checkpoint/sample directory. On completion,
  `loraPath` points to the final adapter in `models/loras/`; no download is needed.
- HTTP 400 indicates invalid input; 409 indicates a busy GPU workflow; 503
  indicates unavailable Docker, missing training image or a launch failure.

The pinned AI Toolkit revision uses its v2 Z-Image Turbo training adapter, a
BF16 transformer before the adapter merge, then float8 quantization, gradient
checkpointing and layer offloading (30% of transformer layers, 100% of text
encoder layers) to leave GPU memory for the desktop. Sampling uses the toolkit's
9-step, guidance-1 Turbo preset.
The first job downloads the BF16 transformer (about 12.3 GB), adapter, text
encoder, VAE and tokenizer/config files as needed. These can add roughly 21 GB;
the existing INT8 inference checkpoint is not used as the training source.
Downloads require network access and persist for later jobs.

Storage:

- `.runtime/training/<id>/`: prepared dataset, generated config and job status.
- `.runtime/training/cache/`: Hugging Face and compilation caches.
- `outputs/training/<id>/`: checkpoints, samples and optimizer state.
- `models/loras/<id>.safetensors`: receives the final adapter when completion
  is polled. Training weights are retained in the Hugging Face cache above.

Completed results remain available after Docker stops. Stopped containers are
retained for diagnostics; remove a specific one with
`docker rm lora-training-<trainingId>` after completion/cancellation. Do not
remove active containers. The inference LoRA loader is separate follow-up work.

## Development

```bash
cd Frontend
npm run typecheck
npm run build
npm run format
```

The build writes static files to `Frontend/dist`. `npm run preview` serves the
build on port 3000 with the same API proxy; stop the dev server first. Deployment
needs a static file server and an `/api` proxy to Flask.

- `Frontend/src/App.vue`: page navigation and shared state.
- `Frontend/src/components/`: feature components using typed Vue bindings.
- `Frontend/src/composables/useModels.ts`: model discovery and selection.
- `Frontend/src/api.ts`: backend requests.
- `Frontend/src/style.css`: shared colors, controls, and responsive layouts.
- `backend/src/api/`: Flask routes and request/response schemas.

No router, global state library, UI component kit, CSS framework, or HTTP client
library is required. The retired React/Next.js frontend and legacy CLI have
been removed.

## Verification scope

The frontend build checks Vue and TypeScript. Run backend tests with
`cd backend && .venv/bin/python -m unittest discover -s tests -v`.
They cover validation, unavailable engines, model filtering, submission/seeds,
image persistence, local dataset handling, training lifecycle and cancellation.

Local SDXL inference was verified through the Vue page, Flask API, and ComfyUI
Docker container on an RTX 5060 Ti (16 GB), using a 1024 × 768 dog/Ferrari prompt.
On 2026-10-13, FLUX.2 klein Base 4B, Z-Image Turbo INT8 and Qwen-Image-2.1
Turbo INT8 also completed through the Vue page at 1024 × 1024, using the same
portrait prompt and seed 42. ComfyUI reported 74.20 s, 16.03 s and 17.88 s
respectively, including model loading for those runs; these are smoke-test
measurements, not a controlled performance benchmark. All eight downloaded
component files passed their official SHA-256 checks.

On 2026-10-14, local Z-Image Turbo training completed a two-step, rank-16,
512px smoke test on the RTX 5060 Ti using one previously generated portrait.
The API returned the saved LoRA path; all 240 saved `lora_B` tensors contained
nonzero updates, and all 480 tensors were finite. Layer offloading was needed
with the desktop using about 3 GB of VRAM. This verifies the training pipeline,
not portrait identity quality or sustained training at larger resolutions.
The connected frontend also completed a two-step job, including folder selection,
submission, polling, refresh recovery and displaying the saved local LoRA path.

Inference still uses base models only. Current Replicate/xAI availability and
a full person-LoRA quality evaluation have not been verified.

## License

[Apache License 2.0](LICENSE.md).
