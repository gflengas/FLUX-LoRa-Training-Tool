# LoRA Studio

A Vue 3 + TypeScript frontend for image inference, model selection, and LoRA
training, with a Flask API. The UI uses native HTML controls, plain CSS, Lucide
icons, and locally served Inter fonts. A small ZIP utility (`fflate`) packages
generated images for transfer to the training form.

## Current status

- **Inference:** generation controls, output gallery, download, seed reuse, and
  transfer to training. Local inference requires the new backend endpoints.
- **Model Settings:** model/LoRA selection and refresh, ready for backend model
  discovery. The UI shows an unavailable state while discovery is unimplemented.
- **Training:** model details, ZIP upload, and the original training settings.
  The existing backend submits FLUX.1 dev training to Replicate and optionally
  uses xAI for captions. Local GPU training is not implemented yet.

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

## Training with the existing backend

1. Open **Training** and enter a model name and subject characteristics.
2. Read the image guidelines and choose a ZIP dataset. A flat ZIP of JPG images
   is the currently smoke-tested format.
3. Review captioning, steps, and advanced settings. Expand **Training service
   connection** to enter Replicate credentials and, if needed, an xAI API key.
4. Start training and follow the returned Replicate progress link.

This sends data to external providers and can incur charges. Credentials are
kept in application memory rather than browser storage; only the theme is
saved in local storage. Optional xAI fallback configuration can be placed in
an untracked repository-root `.env` file as `XAI_API_KEY`.

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

## Optional Docker setup

With Docker and Compose already installed:

```bash
docker compose up --build
```

The frontend is available at <http://localhost:3000>. Stop with
`docker compose down`. Native frontend/backend processes are the verified
local development setup; the Docker configuration is retained as an alternative.

## Verification scope

The frontend build checks Vue and TypeScript. Browser smoke tests used a local
test API to exercise model selection, inference error/retry, gallery actions,
ZIP transfer, and training submission. Backend smoke tests mocked external
services. These checks do not verify current Replicate trainer/xAI availability
or execute real GPU training/inference.

## License

[Apache License 2.0](LICENSE.md).
