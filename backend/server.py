from io import BytesIO
from flask import Blueprint, Flask, json, request, jsonify, send_file
from flask_cors import CORS
from gridfs import GridFS
from pymongo import MongoClient
from bson import ObjectId

from config import MONGO_URI, BACKEND_PORT

from file_handling import file_handling_bp
from tasks_management import task_management_bp
from si_management import si_management_bp

from communication import send_project_status_email

app = Flask(__name__)
CORS(app)

app.register_blueprint(file_handling_bp, url_prefix='/files')
app.register_blueprint(task_management_bp, url_prefix='/api')
app.register_blueprint(si_management_bp, url_prefix='/api/si')


client = MongoClient(MONGO_URI)
dbProject = client["project"]
dbPipeline = client["pipeline"]

projects_collection = dbProject["project_details"]
pipelines_collection = dbPipeline["pipeline_details"]



# Helper to convert ObjectId to string
def serialize_doc(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@app.route("/api/projects", methods=["GET"])
def get_projects():
    projects = list(projects_collection.find())
    projects = [serialize_doc(p) for p in projects]
    print("Projects:", projects)  
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


if __name__ == "__main__":
    app.run(port=BACKEND_PORT, debug=True)


