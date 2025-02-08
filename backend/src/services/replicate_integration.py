import replicate as rep
import time
import os
# from src.config import REPLICATE_OWNER
# from src.config import REPLICATE_API_KEY

def train_LoRa(zip_file_path, settings, token):
    """Trains a LoRA model on Replicate using the specified image dataset.

    Creates a private model repository on Replicate and initiates 
    fine-tuning of a FLUX.1 model with the provided training images. 

    Args:
        zip_file_path (str): Path to the zip file containing training images.
        settings (str): The settings for the training of the model.
        token (str): The token of the model.
    Prints:
        Model creation URL, training status updates, and final model URL.

    Notes:
        Requires Replicate credentials to be configured.
        Uses a specific Replicate training version for FLUX.1 models.
    """

    # Create the model repository on Replicate. All the models are private
    model = rep.models.create(
        owner=REPLICATE_OWNER,
        name=f"flux-{token}",
        visibility="private",  
        hardware="gpu-t4",  # Replicate will override this for fine-tuned models
        description=f"A fine-tuned FLUX.1 model for {token}"
    )
 
    print(f"Model created: {model.name}")
    print(f"Model URL: https://replicate.com/{model.owner}/{model.name}")

    # Now use this model as the destination for your training
    training = rep.trainings.create(
        destination=f"{model.owner}/{model.name}",
        version="ostris/flux-dev-lora-trainer:e440909d3512c31646ee2e0c7d6f6f4923224863a6a10c494606e79fb5844497",
        input={

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
    
def train_LoRa_with_api(zip_file_path, settings, token):
    """Trains a LoRA model on Replicate using the specified image dataset.

    Creates a private model repository on Replicate and initiates 
    fine-tuning of a FLUX.1 model with the provided training images.
    This is the version that will be used on the API call from the frontend.

    Args:
        zip_file_path (str): Path to the zip file containing training images.
        settings (str): The settings for the training of the model.
        token (str): The token of the model.
    Prints:
        Model creation URL, training status updates, and final model URL.

    Notes:
        Requires Replicate credentials to be configured.
        Uses a specific Replicate training version for FLUX.1 models.
    """
    # Set the API token for this session
    os.environ["REPLICATE_API_TOKEN"] = settings.replicateApiKey

    # Create the model repository on Replicate. All the models are private
    model = rep.models.create(
        owner=settings.replicateUsername,
        name=f"flux-{token}",
        visibility="private",  
        hardware="gpu-t4",  # Replicate will override this for fine-tuned models
        description=f"A fine-tuned FLUX.1 model for {token}"
    )
 
    print(f"Model created: {model.name}")
    print(f"Model URL: https://replicate.com/{model.owner}/{model.name}")

    # Now use this model as the destination for your training
    training = rep.trainings.create(
        destination=f"{model.owner}/{model.name}",
        version="ostris/flux-dev-lora-trainer:e440909d3512c31646ee2e0c7d6f6f4923224863a6a10c494606e79fb5844497",
        input={

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


    model_url = f"https://replicate.com/{model.owner}/{model.name}" 

    return {
        "status": training.status,
        "id": training.id,
        "modelUrl": model_url,
        "trainingUrl": f"https://replicate.com/p/{training.id}"
    }