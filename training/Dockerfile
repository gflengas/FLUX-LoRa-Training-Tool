FROM python:3.12-slim-bookworm

ARG AI_TOOLKIT_REVISION=f7a1fb9a77e5418269b1e9eda4ace6d7c1b7bb47
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HF_HOME=/cache/huggingface \
    HOME=/cache MODELS_PATH=/models DO_NOT_TRACK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential libgl1 libglib2.0-0 ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN git init /opt/ai-toolkit && cd /opt/ai-toolkit \
    && git remote add origin https://github.com/ostris/ai-toolkit.git \
    && git fetch --depth 1 origin ${AI_TOOLKIT_REVISION} \
    && git checkout --detach FETCH_HEAD && rm -rf .git
WORKDIR /opt/ai-toolkit
# Match the pinned toolkit's Linux/CUDA dependency versions.
RUN printf 'torch==2.13.0\ntorchvision==0.28.0\ntorchaudio==2.11.0\n' > /tmp/torch-constraints.txt \
    && pip install -c /tmp/torch-constraints.txt torch torchvision torchaudio \
       --index-url https://download.pytorch.org/whl/cu130 \
    && pip install -c /tmp/torch-constraints.txt -r requirements.txt
USER 1000:1000
ENTRYPOINT ["python", "run.py"]
