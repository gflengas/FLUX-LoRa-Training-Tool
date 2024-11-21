import os
import zipfile

def unzip_file(zip_path, output_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

def rename_files(folder_path, token):
    for i, file_name in enumerate(os.listdir(folder_path)):
        old_path = os.path.join(folder_path, file_name)
        new_path = os.path.join(folder_path, f"photo_of_{token}_{i}.jpg")
        os.rename(old_path, new_path)

def zip_files(folder_path, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zip_ref:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zip_ref.write(os.path.join(root, file), file)
