from flask import Blueprint, request, jsonify, send_from_directory, current_app
from .schemas import TrainingRequest, TrainingResponse, InferenceRequest, InferenceResponse
from pydantic import ValidationError
import httpx
import re
from src.services.comfy_integration import get_models, start_inference, get_inference_status
from src.config import INFERENCE_OUTPUT
import src.services.file_processing as fp
from src.services.replicate_integration import train_LoRa_with_api
from src.services.xai_integration import generate_description
import os

api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health():
    return jsonify(status='ok')


@api.route('/models', methods=['GET'])
def list_models():
    try:
        return jsonify(get_models())
    except httpx.RequestError:
        return jsonify(status="error", message="ComfyUI is stopped. Start the inference container, then refresh."), 503
    except Exception:
        current_app.logger.exception("Could not read ComfyUI models")
        return jsonify(status="error", message="Could not read the ComfyUI model catalog."), 502


@api.route('/inference', methods=['POST'])
def generate_image():
    try:
        # Validate settings and submit the workflow to the local engine.
        req_data = InferenceRequest.model_validate(request.get_json(silent=True))
        inference_info = start_inference(req_data)
        response = InferenceResponse(**inference_info)
        return jsonify(response.model_dump()), 202
    except ValidationError as e:
        return jsonify(status="error", message=e.errors()[0]["msg"]), 400
    except ValueError as e:
        return jsonify(status="error", message=str(e)), 400
    except httpx.RequestError:
        return jsonify(status="error", message="Cannot reach ComfyUI. Start the inference container and retry."), 503
    except Exception:
        current_app.logger.exception("Could not submit ComfyUI generation")
        return jsonify(status="error", message="Could not submit generation. Check the backend and ComfyUI logs."), 502


@api.route('/inference/<uuid:job_id>', methods=['GET'])
def inference_status(job_id):
    try:
        return jsonify(get_inference_status(str(job_id)))
    except FileNotFoundError:
        return jsonify(status="error", message="Generation not found."), 404
    except httpx.RequestError:
        return jsonify(status="error", message="ComfyUI disconnected. Start the container and retry."), 503
    except Exception:
        current_app.logger.exception("Could not read ComfyUI generation")
        return jsonify(status="error", message="Could not read generation results. Check the backend logs."), 502


@api.route('/inference/images/<filename>', methods=['GET'])
def inference_image(filename):
    # Only expose generated PNGs, not job metadata or arbitrary files.
    if not re.fullmatch(r"[0-9a-f-]{36}_[0-3]\.png", filename):
        return jsonify(status="error", message="Image not found."), 404
    return send_from_directory(INFERENCE_OUTPUT, filename, mimetype="image/png")

@api.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file part"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No selected file"
            }), 400
            
        if file and file.filename.endswith('.zip'):
            # Save the file to a temporary location
            upload_folder = "./uploads"
            os.makedirs(upload_folder, exist_ok=True)
            
            filepath = os.path.join(upload_folder, file.filename)
            file.save(filepath)
            
            return jsonify({
                "status": "success",
                "filePath": filepath
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid file type. Please upload a ZIP file."
            }), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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
        
        # generate descriptions for each image if autoCaptioning is off
        if not req_data.settings.autoCaptioning:
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
        train_info = train_LoRa_with_api(output_zip, req_data.settings, req_data.modelInfo.name)
        
        response = TrainingResponse(
            status=train_info["status"],
            trainingId=train_info["id"],
            modelUrl=train_info["modelUrl"],
            trainingUrl=train_info["trainingUrl"]
        )
        
        return jsonify(response.model_dump())
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
