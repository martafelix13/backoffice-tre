from io import BytesIO
from flask import Flask, json, request, jsonify, send_file
from flask_cors import CORS
from gridfs import GridFS
from pymongo import MongoClient
from bson import ObjectId

from communication import send_project_status_email

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
dbProject = client["project"]
dbPipeline = client["pipeline"]

dbFiles = client["files_system"]
fs = GridFS(dbFiles)

projects_collection = dbProject["project_details"]
pipelines_collection = dbPipeline["pipeline_details"]


# Helper to convert ObjectId to string
def serialize_doc(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

# Routes
@app.route('/api/projects/<string:id>/files', methods=['GET'])
def get_files_by_project(id):
    """Return all files for a specific project"""
    print('Getting files for project ', id)
    files = fs.find({"project_id": id})
    file_list = []
    for file in files:
        existing_file = next((f for f in file_list if f["filename"] == file.type), None)
        if existing_file:
            if file.uploadDate > existing_file["upload_date"]:
                file_list.remove(existing_file)
                file_list.append({
                    "filename": file.type,
                    "download_url": f"download/{file._id}",
                    "upload_date": file.uploadDate,
                })
        else:
            file_list.append({
                "filename": file.type,
                "download_url": f"download/{file._id}",
                "upload_date": file.uploadDate,
            })

    for item in file_list:
        item['download_url'] = request.host_url + item['download_url']
    print('Files from project ', id)
    print(file_list)
    return jsonify(file_list), 200

@app.route("/api/projects", methods=["GET"])
def get_projects():
    projects = list(projects_collection.find())
    projects = [serialize_doc(p) for p in projects]
    print("Projects:", projects)  # Debugging line to check the projects
    return jsonify(projects)

@app.route("/api/projects/<id>", methods=["GET"])
def get_project(id):
    project = projects_collection.find_one({"_id": ObjectId(id)})
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(serialize_doc(project))

@app.route("/api/projects/<id>", methods=["PATCH"])
def update_project_status(id):
    print("Updating project with ID:", id)  
    project = projects_collection.find_one({"_id": ObjectId(id)})
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    print("Project found:", project)
    status = request.json.get("status")
    if not status:
        return jsonify({"error": "Status is required"}), 400
    
    result = projects_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Project not found"}), 404

    #TO DO: Uncomment the following line to send email notification
    # Create an email to send the project status updates from
    # send_project_status_email(project.responsible_email, project.name, status, project.feedback)

    updated_project = projects_collection.find_one({"_id": ObjectId(id)})
    return jsonify(serialize_doc(updated_project))

@app.route("/api/pipelines", methods=["GET"])
def get_pipelines():

    pipelines = list(pipelines_collection.find({},{"_id": 0}))
    print("Pipelines:", pipelines)  # Debugging line
    return jsonify(pipelines)


@app.route("/api/pipelines", methods=["POST"])
def create_pipeline():
    data = request.get_json()
    payload = data.get("payload")

    print("Creating pipeline with data:", payload)

    if not payload or "name" not in payload:
        return jsonify({"error": "Pipeline name is required"}), 400

    # Optional: check for duplicate payload name inside the JSON string
    existing = pipelines_collection.find_one({
        "payload": {"$regex": f'"name":"{payload["name"]}"'}
    })
    if existing:
        return jsonify({"error": "Pipeline name already exists"}), 400

    def get_next_string_id():
        docs = pipelines_collection.find({}, {"id": 1})
        max_id = 0
        for doc in docs:
            try:
                max_id = max(max_id, int(doc.get("id", 0)))
            except (ValueError, TypeError):
                pass
        return str(max_id + 1)

    document = {
        "id": get_next_string_id(),
        "payload": json.dumps(payload)
    }

    result = pipelines_collection.insert_one(document)
    return jsonify({"id": str(result.inserted_id)}), 201

@app.route("/api/pipelines/<string:id>", methods=["PUT"])
def update_pipeline(id):
    data = request.json
    payload = data.get("payload")

    print("Updating pipeline with data:", data)  # Debugging line

    if not payload or "name" not in payload or not data["id"]:
        return jsonify({"error": "Pipeline name and ID are required"}), 400

    result = pipelines_collection.update_one({"id": id}, {"$set": {"payload": json.dumps(payload)}})

    if result.matched_count == 0:
        return jsonify({"error": f"No pipeline found with id {id}"}), 40

    return jsonify({"message": f"Pipeline {id} updated successfully"}), 200

@app.route("/api/pipelines/<string:id>", methods=["DELETE"])
def delete_pipeline(id):
    print("Deleting pipeline with ID:", id)
    result = pipelines_collection.delete_one({"id": id})
    if result.deleted_count == 0:
        return jsonify({"error": "Pipeline not found"}), 404
    return jsonify({"message": "Pipeline deleted successfully"}), 200


# Route to download a specific file by file ID
@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    """
    Download a file from GridFS by its file ID.
    """
    try:
        # Retrieve the file from GridFS
        file = fs.get(ObjectId(file_id))
        return send_file(
            BytesIO(file.read()),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=file.type
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 404


if __name__ == "__main__":
    app.run(port=5000, debug=True)


