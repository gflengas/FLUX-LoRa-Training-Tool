FROM python:3.12-slim-bookworm

ARG COMFYUI_REVISION=79be670e2d9be63e238785af307369d2b9039ed1
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends git libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
RUN git init /opt/ComfyUI && cd /opt/ComfyUI \
    && git remote add origin https://github.com/Comfy-Org/ComfyUI.git \
    && git fetch --depth 1 origin ${COMFYUI_REVISION} && git checkout --detach FETCH_HEAD \
    && rm -rf .git
WORKDIR /opt/ComfyUI
RUN pip install torch==2.14.0 torchvision==0.29.0 --index-url https://download.pytorch.org/whl/cu130 \
    && pip install -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /data/input /data/output /data/user && chown -R 1000:1000 /data /opt/ComfyUI
USER 1000:1000
EXPOSE 8188
