from flask import Blueprint, request, jsonify, current_app
from services.comment_service import CommentService
from middleware.auth import token_required

comment_bp = Blueprint('comment', __name__)

def get_comment_service():
    if current_app.db is None:
        return None
    return CommentService(current_app.db)

@comment_bp.route('/', methods=['POST'])
@token_required
def add_comment(current_user):
    service = get_comment_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    data = request.get_json()
    response, status_code = service.add_comment(data, current_user['user_id'])
    return jsonify(response), status_code

@comment_bp.route('/blog/<blog_id>', methods=['GET'])
def get_comments(blog_id):
    service = get_comment_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    response, status_code = service.get_comments_for_blog(blog_id)
    return jsonify(response), status_code

@comment_bp.route('/<comment_id>', methods=['DELETE'])
@token_required
def delete_comment(current_user, comment_id):
    service = get_comment_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    response, status_code = service.delete_comment(comment_id, current_user['user_id'])
    return jsonify(response), status_code

@comment_bp.route('/like/<comment_id>', methods=['POST'])
@token_required
def toggle_like(current_user, comment_id):
    service = get_comment_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    response, status_code = service.toggle_like(comment_id, current_user['user_id'])
    return jsonify(response), status_code
