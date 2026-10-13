# Component filenames follow the official Comfy Org packages.
MODEL_PROFILES = {
    "flux-2-klein-base-4b": {
        "name": "FLUX.2 klein Base 4B", "family": "FLUX.2",
        "diffusion_models": "flux-2-klein-base-4b.safetensors",
        "text_encoders": "qwen_3_4b.safetensors", "vae": "flux2-vae.safetensors",
        "defaults": {"steps": 20, "guidance": 5},
        "fixedSteps": False, "fixedGuidance": False, "negativePrompt": True,
    },
    "z-image-turbo": {
        "name": "Z-Image Turbo", "family": "Z-Image",
        "diffusion_models": "z_image_turbo_int8_convrot.safetensors",
        "text_encoders": "qwen_3_4b.safetensors", "vae": "ae.safetensors",
        "defaults": {"steps": 8, "guidance": 1},
        "fixedSteps": False, "fixedGuidance": True, "negativePrompt": False,
    },
    "qwen-image-2.1-turbo": {
        "name": "Qwen-Image-2.1 Turbo", "family": "Qwen-Image",
        "diffusion_models": "qwen_image_2.1_turbo_int8_convrot.safetensors",
        "text_encoders": "qwen3vl_8b_int8_convrot.safetensors",
        "vae": "qwen_image_2.1_vae_bf16.safetensors",
        "defaults": {"steps": 8, "guidance": 1},
        "fixedSteps": True, "fixedGuidance": True, "negativePrompt": False,
    },
}


def create_component_workflow(settings, seed, profile):
    for field, fixed in [("steps", "fixedSteps"), ("guidance", "fixedGuidance")]:
        if profile[fixed] and getattr(settings, field) != profile["defaults"][field]:
            raise ValueError(f"{profile['name']} requires {field}={profile['defaults'][field]}")
    if not profile["negativePrompt"] and settings.negativePrompt.strip():
        raise ValueError(f"{profile['name']} does not use a negative prompt at guidance 1")

    family = profile["family"]
    clip_type = {"FLUX.2": "flux2", "Z-Image": "lumina2", "Qwen-Image": "qwen_image"}[family]
    latent_type = {"FLUX.2": "EmptyFlux2LatentImage", "Z-Image": "EmptySD3LatentImage",
                   "Qwen-Image": "EmptyLatentImage"}[family]
    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {
            "unet_name": profile["diffusion_models"], "weight_dtype": "default"}},
        "5": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": profile["text_encoders"], "type": clip_type, "device": "default"}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": profile["vae"]}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": settings.prompt, "clip": ["5", 0]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": settings.negativePrompt, "clip": ["5", 0]}},
        "4": {"class_type": latent_type, "inputs": {
            "width": settings.width, "height": settings.height, "batch_size": 1}},
    }
    model, positive, negative = ["1", 0], ["2", 0], ["3", 0]
    if family == "Z-Image":
        graph["7"] = {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": model, "shift": 3}}
        graph["3"] = {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": positive}}
        model = ["7", 0]
    elif family == "Qwen-Image":
        graph["2"] = {"class_type": "TextEncodeQwenImage21", "inputs": {
            "clip": ["5", 0], "prompt": settings.prompt, "negative_prompt": "", "resolution": 1024}}
        del graph["3"]
        negative = ["2", 1]
        graph["7"] = {"class_type": "QwenImage21Cache", "inputs": {
            "model": model, "device": "auto", "dtype": "default"}}
        model = ["7", 0]

    if family != "Z-Image":
        graph["8"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}
        graph["9"] = {"class_type": "Flux2Scheduler", "inputs": {
            "steps": settings.steps, "width": settings.width, "height": settings.height}}
        if family == "Qwen-Image":
            # Official Turbo schedule; changing step count requires a different schedule.
            graph["9"] = {"class_type": "ManualSigmas", "inputs": {
                "sigmas": "1.0, 0.978453, 0.95418, 0.926626, 0.89508, 0.845148, 0.704534, 0.414568, 0"}}
        graph["30"] = {"class_type": "CFGGuider", "inputs": {
            "model": model, "positive": positive, "negative": negative, "cfg": settings.guidance}}

    for index in range(settings.images):
        sampler, decoder, output = str(10 + index * 3), str(11 + index * 3), str(12 + index * 3)
        image_seed = (seed + index) % 4294967296
        if family == "Z-Image":
            graph[sampler] = {"class_type": "KSampler", "inputs": {
                "model": model, "positive": positive, "negative": negative,
                "latent_image": ["4", 0], "seed": image_seed, "steps": settings.steps,
                "cfg": 1, "sampler_name": "res_multistep", "scheduler": "simple", "denoise": 1}}
        else:
            noise = str(40 + index)
            graph[noise] = {"class_type": "RandomNoise", "inputs": {"noise_seed": image_seed}}
            graph[sampler] = {"class_type": "SamplerCustomAdvanced", "inputs": {
                "noise": [noise, 0], "guider": ["30", 0], "sampler": ["8", 0],
                "sigmas": ["9", 0], "latent_image": ["4", 0]}}
        graph[decoder] = {"class_type": "VAEDecode", "inputs": {"samples": [sampler, 0], "vae": ["6", 0]}}
        graph[output] = {"class_type": "SaveImage", "inputs": {
            "images": [decoder, 0], "filename_prefix": "LoRA-Studio/image"}}
    return graph
