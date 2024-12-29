import replicate as rep
import time
from src.config import REPLICATE_API_TOKEN
from src.config import REPLICATE_OWNER

def train_LoRa(zip_file_path, settings):
    """Trains a LoRA model on Replicate using the specified image dataset.

    Creates a private model repository on Replicate and initiates 
    fine-tuning of a FLUX.1 model with the provided training images.

    Args:
        zip_file_path (str): Path to the zip file containing training images.
        settings (str): The settings for the training of the model.

    Prints:
        Model creation URL, training status updates, and final model URL.

    Notes:
        Requires Replicate credentials to be configured.
        Uses a specific Replicate training version for FLUX.1 models.
    """
    # Create the model repository on Replicate. All the models are private
    model = rep.models.create(
        owner=REPLICATE_OWNER,
        name=f"flux-{settings.token}",
        visibility="private",  
        hardware="gpu-t4",  # Replicate will override this for fine-tuned models
        description=f"A fine-tuned FLUX.1 model for {settings.token}"
    )
 
    print(f"Model created: {model.name}")
    print(f"Model URL: https://replicate.com/{model.owner}/{model.name}")

    # Now use this model as the destination for your training
    training = rep.trainings.create(
        destination=f"{model.owner}/{model.name}",
        version="ostris/flux-dev-lora-trainer:e440909d3512c31646ee2e0c7d6f6f4923224863a6a10c494606e79fb5844497",
        input={
            # "steps": 1000,
            # "lora_rank": 16,
            # "optimizer": "adamw8bit",
            # "batch_size": 1,
            # "resolution": "512,768,1024",
            # "autocaption": False,
            # "input_images": open(zip_file_path, "rb"),
            # "trigger_word": token,
            # "learning_rate": 0.0004,
            # "wandb_project": "flux_train_replicate",
            # "wandb_save_interval": 100,
            # "caption_dropout_rate": 0.05,
            # "cache_latents_to_disk": False,
            # "wandb_sample_interval": 100
            "steps": settings.steps,
            "lora_rank": settings.lora_rank,
            "optimizer": settings.optimizer,
            "batch_size": settings.batch_size,
            "resolution": settings.resolution,
            "autocaption": settings.autocaption,
            "input_images": open(zip_file_path, "rb"),
            "trigger_word": settings.token,
            "learning_rate": settings.learning_rate,
            "wandb_project": "flux_train_replicate",
            "wandb_save_interval": settings.wandb_save_interval,
            "caption_dropout_rate": settings.caption_dropout_rate,
            "cache_latents_to_disk": settings.cache_latents_to_disk,
            "wandb_sample_interval": settings.wandb_sample_interval
        },
    )
 
    print(f"Training started: {training.status}")
    print(f"Training URL: https://replicate.com/p/{training.id}")

    status = "starting"
    while status not in ["succeeded", "failed", "canceled"]:
        time.sleep(30)  # Check every 30 seconds
        training.reload()
        print(f"Training status: {training.status}")

    if training.status == "succeeded":
        print("Training completed successfully!")
        print(
            f"Model URL: https://replicate.com/{REPLICATE_OWNER}/flux-{settings.token}"
        )