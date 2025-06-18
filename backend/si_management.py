from flask import Blueprint


si_management_bp = Blueprint('si_management', __name__)

# Placeholder for future SI management endpoints
@si_management_bp.route('/get_files', methods=['GET'])
def get_si_files():
    # Placeholder implementation
    return {"status": "SI management service is running"}, 200