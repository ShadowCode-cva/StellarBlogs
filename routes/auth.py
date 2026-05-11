from flask import Blueprint, request, jsonify, current_app
from services.user_service import UserService

auth_bp = Blueprint('auth', __name__)

def get_user_service():
    if current_app.db is None:
        return None
    return UserService(current_app.db)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    service = get_user_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    data = request.get_json()
    response, status_code = service.signup(data)
    return jsonify(response), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    service = get_user_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    data = request.get_json()
    response, status_code = service.login(data)
    return jsonify(response), status_code
