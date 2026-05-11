from flask import Blueprint, request, jsonify, current_app
from services.interaction_service import InteractionService
from middleware.auth import token_required

interaction_bp = Blueprint('interaction', __name__)

def get_interaction_service():
    if current_app.db is None:
        return None
    return InteractionService(current_app.db)

@interaction_bp.route('/like/<blog_id>', methods=['POST'])
@token_required
def toggle_like(current_user, blog_id):
    service = get_interaction_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    response, status_code = service.toggle_like(blog_id, current_user['user_id'])
    return jsonify(response), status_code

@interaction_bp.route('/favorite/<blog_id>', methods=['POST'])
@token_required
def toggle_favorite(current_user, blog_id):
    service = get_interaction_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    response, status_code = service.toggle_favorite(current_user['user_id'], blog_id)
    return jsonify(response), status_code

@interaction_bp.route('/favorites', methods=['GET'])
@token_required
def get_favorites(current_user):
    service = get_interaction_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    response, status_code = service.get_user_favorites(current_user['user_id'])
    return jsonify(response), status_code
