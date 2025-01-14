from flask import Blueprint, request, jsonify
from .schemas import TrainingRequest, TrainingResponse
import src.services.file_processing as fp
from src.services.replicate_integration import train_LoRa
from src.services.xai_integration import generate_description
import os

api = Blueprint('api', __name__)

@api.route('/training/start', methods=['POST'])
def start_training():
    try:
        # Validate request
        req_data = TrainingRequest(**request.json)

        # prepare the data
        temp_folder = "./temp"
        os.makedirs(temp_folder, exist_ok=True)

        fp.unzip_file(req_data.imageLocation, temp_folder)

        fp.rename_files(temp_folder, req_data.modelInfo.name)

        # Get API key if exists
        xai_api_key = None
        if hasattr(req_data, 'settings') and hasattr(req_data.settings, 'xaiApiKey'):
            xai_api_key = req_data.settings.xaiApiKey
        
        # generate descriptions for each image
        for file_name in os.listdir(temp_folder):
            if file_name.endswith('.jpg'):  # Only process image files
                file_path = os.path.join(temp_folder, file_name)
                description = generate_description(
                    image_path=file_path,
                    token=req_data.modelInfo.name,
                    type=req_data.modelInfo.type,
                    infos=req_data.modelInfo.characteristics,
                    API_KEY=xai_api_key
                )
                desc_file = file_path.replace(".jpg", ".txt")
                with open(desc_file, "w") as f:
                    f.write(description)

        output_zip = f"{req_data.modelInfo.name}.zip"
        fp.zip_files(temp_folder, output_zip)
        fp.delete_temp_folder("./temp")

        # Start training process
        # ToDo: Need different intput and also should have a return value that 
        #       stores the results of the training initialization
        # train_info = train_LoRa(output_zip, req_data.settings)
        
        # response = TrainingResponse(
        #     status=  train_info.status,
        #     trainingId= train_info.id,
        #     modelUrl= train_info.modelUrl
        # )
        
        return jsonify({
            "status": "success",
            "message": "Done"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500