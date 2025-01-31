import os
import click
import time
from src.services.xai_integration import generate_description
import src.services.replicate_integration as tr
import src.services.file_processing as fp
from src.config import REPLICATE_OWNER

@click.group()
def cli():
    """FLUX LoRa Training CLI Tool"""
    pass

@cli.command()
@click.argument('zip_path')
@click.argument('token')
@click.argument('type')
def prepare(zip_path, token, type):
    """Prepares image dataset by processing a ZIP file of images.

    This command performs the following operations:
    1. Creates a temporary folder and extracts the input ZIP file
    2. Renames all images using the specified token
    3. Generates descriptions for each image and saves them as text files
    4. Creates a new ZIP file containing the processed images and descriptions
    5. Cleans up temporary files

    Args:
        zip_path (str): Path to the input ZIP file containing images.
        token (str): Identifier used for renaming the images and output ZIP file.
        type (str): Determines which prompt to use ("human", "pet", or "item").

    Example Usage:
        $ python3 cli.py prepare input_images.zip person_name human
    """
    temp_folder = "./temp"
    os.makedirs(temp_folder, exist_ok=True)

    click.echo("Unzipping files...")
    fp.unzip_file(zip_path, temp_folder)

    click.echo("Renaming files...")
    fp.rename_files(temp_folder, token)

    click.echo("Generating descriptions...")
    for file_name in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, file_name)
        description = generate_description(file_path, token, type)
        desc_file = file_path.replace(".jpg", ".txt")
        with open(desc_file, "w") as f:
            f.write(description)

    click.echo("Zipping prepared files...")
    output_zip = f"{token}.zip"
    fp.zip_files(temp_folder, output_zip)
    fp.delete_temp_folder("./temp")
    click.echo(f"Prepared files saved as {output_zip}")


@cli.command()
@click.argument('zip_path')
@click.argument('token')
def train(zip_path, token):
    """Train LoRa model using prepared image files.

    Initiates training process, monitors status, and provides updates.

    Args:
        zip_path (str): Path to ZIP file with training data.
        token (str): Unique identifier for the model.
    """
    click.echo(f"Starting LoRa training model for {token}...")
    tr.train_LoRa(zip_path, token)


if __name__ == '__main__':
    cli()