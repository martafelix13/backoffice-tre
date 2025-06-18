from flask import Blueprint
import requests
from config import FUNNEL_URL

task_management_bp = Blueprint('task_management', __name__)


@task_management_bp.route('/tasks', methods=['GET'])
def get_tasks():
    print("[DEBUG] Fetching tasks from the funnel service...")

    # Call the funnel service to get the tasks
    response = requests.get(FUNNEL_URL)

    # Debugging output to check the response status
    print("[DEBUG] Funnel service response:", response.json())
    print(f"[DEBUG] Funnel service response status: {response.status_code}")
    
    if response.status_code == 200:
        return response.json(), 200
    else:
        return {"error": "Failed to retrieve tasks"}, 500
