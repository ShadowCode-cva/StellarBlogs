from flask import Blueprint, request, jsonify, current_app
from services.blog_service import BlogService
from middleware.auth import token_required, author_required

blog_bp = Blueprint('blog', __name__)

def get_blog_service():
    if current_app.db is None:
        return None
    return BlogService(current_app.db)

@blog_bp.route('/', methods=['POST'])
@author_required
def create_blog(current_user):
    service = get_blog_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    data = request.get_json()
    response, status_code = service.create_blog(data, current_user['user_id'])
    return jsonify(response), status_code

@blog_bp.route('/', methods=['GET'])
def get_all_blogs():
    service = get_blog_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    response, status_code = service.get_all_blogs(page=page, limit=limit)
    return jsonify(response), status_code

@blog_bp.route('/<blog_id>', methods=['GET'])
def get_blog(blog_id):
    service = get_blog_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    response, status_code = service.get_blog(blog_id)
    return jsonify(response), status_code

@blog_bp.route('/<blog_id>', methods=['PUT'])
@author_required
def update_blog(current_user, blog_id):
    service = get_blog_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    data = request.get_json()
    response, status_code = service.update_blog(blog_id, data, current_user['user_id'])
    return jsonify(response), status_code

@blog_bp.route('/<blog_id>', methods=['DELETE'])
@author_required
def delete_blog(current_user, blog_id):
    service = get_blog_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    response, status_code = service.delete_blog(blog_id, current_user['user_id'])
    return jsonify(response), status_code

@blog_bp.route('/search', methods=['GET'])
def search_blogs():
    service = get_blog_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    response, status_code = service.search_blogs(query, page=page, limit=limit)
    return jsonify(response), status_code

@blog_bp.route('/author/<author_id>', methods=['GET'])
def get_blogs_by_author(author_id):
    service = get_blog_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    response, status_code = service.get_blogs_by_author(author_id, page=page, limit=limit)
    return jsonify(response), status_code

@blog_bp.route('/author/works', methods=['GET'])
@author_required
def get_my_works(current_user):
    service = get_blog_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    response, status_code = service.get_blogs_by_author(current_user['user_id'], page=page, limit=limit)
    return jsonify(response), status_code

@blog_bp.route('/tag/<tag>', methods=['GET'])
def get_blogs_by_tag(tag):
    service = get_blog_service()
    if service is None:
        return jsonify({"error": "Database service unavailable"}), 503
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    response, status_code = service.get_blogs_by_tag(tag, page=page, limit=limit)
    return jsonify(response), status_code
