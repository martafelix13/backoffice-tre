from typing import List, Optional
from flask import Blueprint, jsonify, request, send_file
from pymongo import MongoClient
from bson import ObjectId
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from datetime import datetime
import os
import shutil

from communication import send_project_status_email

MONGO_URL = "mongodb://localhost:28017/"
client = MongoClient(MONGO_URL)
db = client["tre_db"]
dbProject = client["project"]
projects_collection = dbProject["project_details"]

file_handling_bp = Blueprint('file_handling', __name__)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SHARED_BASE_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "..", "..", "tre-shared-documents"))
TEMPLATE_DIR = os.path.join(SHARED_BASE_DIR, "templates")
SIGNED_DIR = os.path.join(SHARED_BASE_DIR, "legal-documents")


def get_timestamp():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[DEBUG] Generated timestamp: {ts}")
    return ts

def get_project(project_id: str):
    print(f"[DEBUG] Fetching project with ID: {project_id}")
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        print(f"[DEBUG] Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")
    print(f"[DEBUG] Project found: {project_id}")
    return project

# --- ENDPOINTS ---

@file_handling_bp.delete("/templates/<string:filename>")
def delete_template(filename: str):
    file_path = os.path.join(TEMPLATE_DIR, filename)
    print(f"[DEBUG] Deleting template: {file_path}")
    if not os.path.exists(file_path):
        print(f"[DEBUG] Template not found: {file_path}")
        raise HTTPException(status_code=404, detail="Template not found")
    os.remove(file_path)
    print(f"[DEBUG] Template deleted: {file_path}")
    return {"status": "deleted", "file": filename}


@file_handling_bp.get("/templates/<string:filename>")
def download_template(filename: str):
    file_path = os.path.join(TEMPLATE_DIR, filename)
    print(f"[DEBUG] Downloading template: {file_path}")
    if not os.path.exists(file_path):
        print(f"[DEBUG] Template not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"Template not found: {file_path}")
    return send_file(file_path)

@file_handling_bp.get("/signed/<string:project_id>/<string:filename>")
def download_signed_document(project_id:str, filename: str):
    file_path = os.path.join(SIGNED_DIR, project_id, filename)
    print(f"[DEBUG] Downloading signed document: {file_path}")
    if not os.path.exists(file_path):
        print(f"[DEBUG] File not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    return send_file(file_path)

@file_handling_bp.post("/upload-template")
def upload_template(file: UploadFile = File(...)):
    print(f"[DEBUG] Uploading template, filename: {file.filename}")

     # Only allow PDF files
    if not file.filename.lower().endswith('.pdf') or file.content_type != "application/pdf":
        print(f"[DEBUG] Rejected upload: not a PDF file ({file.filename}, {file.content_type})")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    

    filename = file.filename if file.filename.endswith('.pdf') else f"{file.filename}.pdf"
    project_folder = os.path.join(TEMPLATE_DIR)
    os.makedirs(project_folder, exist_ok=True)
    file_path = os.path.join(project_folder, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"[DEBUG] Template uploaded to: {file_path}")

    return jsonify({ "status": "uploaded", "file": filename}), 200

@file_handling_bp.post("/assign-templates/<project_id>")
def assign_templates(project_id: str):

    templates = request.get_json()
    print(templates)

    if not templates:
        print(f"[DEBUG] No templates provided for project: {project_id}")
        raise HTTPException(status_code=400, detail="Templates not provided")

    print(f"[DEBUG] Assigning templates to project: {project_id}, templates: {templates}")
    get_project(project_id)  # ensure project exists
    template_files = [
        {"filename": t, "required": True}
        for t in templates
    ]
    projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"templateFiles": template_files}}
    )
    print(f"[DEBUG] Template files assigned: {template_files}")

    projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"status": 'A-E'}}
    )
    print(f"[DEBUG] Project status set to A-E for project: {project_id}")
    # TODO: Uncomment to send email notification
    # send_project_status_email(project_id, "A-E")
    return {"status": "files assigned", "templates": templates}

@file_handling_bp.get("/templates")
def get_template():
    print(f"[DEBUG] Listing templates in: {TEMPLATE_DIR}")
    templates = os.listdir(TEMPLATE_DIR)
    print(f"[DEBUG] Templates found: {templates}")
    return jsonify(templates), 200

@file_handling_bp.get("/signed-files/<string:project_id>")
def get_signed_files(project_id: str):
    print(f"[DEBUG] Getting signed files for project: {project_id}")
    get_project(project_id)
    signed_dir = os.path.join(SIGNED_DIR, project_id)
    print(f"[DEBUG] Signed directory: {signed_dir}")
    signed_files = os.listdir(signed_dir)
    print(f"[DEBUG] Signed files found: {signed_files}")
    return jsonify(signed_files), 200

@file_handling_bp.get("/signed-files/<string:project_id>/<string:filename>")
def get_signed_file(project_id: str, filename: str):
    print(f"[DEBUG] Getting signed file: {filename} for project: {project_id}")
    get_project(project_id)
    signed_dir = os.path.join(SIGNED_DIR, project_id)
    file_path = os.path.join(signed_dir, filename)
    print(f"[DEBUG] File path: {file_path}")

    if not os.path.exists(file_path):
        print(f"[DEBUG] Signed file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Signed file not found")

    return send_file(file_path)

@file_handling_bp.post("/validate-file/<project_id>")
def validate_file(project_id: str):
    print(f"[DEBUG] Validating file for project: {project_id}")
    if not request.json:
        print(f"[DEBUG] No request data provided for validation in project: {project_id}")
        raise HTTPException(status_code=400, detail="Request data is required")
    print(f"[DEBUG] Request data: {request.json}")

    filename = request.json.get("filename")
    approved = request.json.get("approved", False)
    feedback = request.json.get("feedback", None)

    print(f"[DEBUG] Validating file: {filename}, approved: {approved}, feedback: {feedback}")

    if not filename:
        print(f"[DEBUG] Filename is required for validation in project: {project_id}")
        raise HTTPException(status_code=400, detail="Filename is required")
    
    if not approved and not feedback:
        print(f"[DEBUG] Feedback is required if file is not approved in project: {project_id}")
        raise HTTPException(status_code=400, detail="Feedback is required if file is not approved")
    

    project = get_project(project_id)
    if not project:
        print(f"[DEBUG] Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")
    
    print(f"[DEBUG] Project found: {project_id}, proceeding with validation")
    
    match = next((f for f in project.get("userSignedFiles", []) if f["filename"] == filename), None)
    if not match:
        print(f"[DEBUG] File not found in project: {filename}")
        raise HTTPException(status_code=404, detail="File not found in project")
    
    update_query = {
        "$set": {
            "userSignedFiles.$[elem].verified": approved,
            "userSignedFiles.$[elem].feedback": feedback or None
        }
    }

    array_filters = [{"elem.filename": filename}]

    projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {**update_query},
        array_filters=array_filters
    )

    return {"status": "file validated", "file": filename, "approved": approved, "feedback": feedback}, 200