import os
import click
from src.services.xai_integration import generate_description
import src.services.file_processing as fp

def prepare(zip_path, token):
    temp_folder = "./temp"
    os.makedirs(temp_folder, exist_ok=True)

    print("Unzipping files...")
    fp.unzip_file(zip_path, temp_folder)

    print("Renaming files...")
    fp.rename_files(temp_folder, token)

    print("Generating descriptions...")
    for file_name in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, file_name)
        description = generate_description(file_path)
        desc_file = file_path.replace(".jpg", ".txt")
        with open(desc_file, "w") as f:
            f.write(description)

    print("Zipping prepared files...")
    output_zip = f"{token}.zip"
    fp.zip_files(temp_folder, output_zip)
    fp.delete_temp_folder("./temp")
    print(f"Prepared files saved as {output_zip}")
