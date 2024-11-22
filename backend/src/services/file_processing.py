import os
import zipfile
import shutil

def unzip_file(zip_path, output_folder):
    """Extracts contents of a ZIP file to specified output folder.

    Args:
        zip_path (str): Path to the ZIP file that needs to be extracted.
        output_folder (str): Destination folder path for extracted contents.

    Returns:
        None
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

def rename_files(folder_path, token):
    """Renames all files in a folder using a specified token and sequential 
    numbering.

    Iterates through files in the specified folder and renames them to the 
    format: 'photo_of_[token]_[index].jpg'

    Args:
        folder_path (str): Path to the folder containing files to be renamed.
        token (str): Token to be used in the new file names.

    Returns:
        None
    """
    for i, file_name in enumerate(os.listdir(folder_path)):
        old_path = os.path.join(folder_path, file_name)
        new_path = os.path.join(folder_path, f"photo_of_{token}_{i}.jpg")
        os.rename(old_path, new_path)

def zip_files(folder_path, output_zip):
    """Creates a ZIP archive containing all files from specified folder.

    Args:
        folder_path (str): Path to the folder containing files to be zipped.
        output_zip (str): Path where the output ZIP file will be created.

    Returns:
        None
    """
    with zipfile.ZipFile(output_zip, 'w') as zip_ref:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zip_ref.write(os.path.join(root, file), file)

def delete_temp_folder(folder_path):
    """Deletes a folder and all its contents if it exists.

    Args:
        folder_path (str): Path to the folder that needs to be deleted.

    Returns:
        None: Prints status message indicating success or failure.
    """
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"Successfully deleted the folder: {folder_path}")
        except Exception as e:
            print(f"Error while deleting folder {folder_path}: {e}")
    else:
        print(f"Folder does not exist: {folder_path}")

def delete_file(file_path):
    """Deletes a single file if it exists.

    Args:
        file_path (str): Path to the file that needs to be deleted.

    Returns:
        None: Prints status message indicating success or failure.
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Successfully deleted the file: {file_path}")
        except Exception as e:
            print(f"Error while deleting file {file_path}: {e}")
    else:
        print(f"File does not exist: {file_path}")