from flask import Blueprint, request, jsonify, current_app
from services.user_service import UserService

auth_bp = Blueprint('auth', __name__)

def get_user_service():
    return UserService(current_app.db)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    response, status_code = get_user_service().signup(data)
    return jsonify(response), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response, status_code = get_user_service().login(data)
    return jsonify(response), status_code
