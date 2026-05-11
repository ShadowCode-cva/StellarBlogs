from flask import Blueprint, request, jsonify, current_app
from services.blog_service import BlogService
from middleware.auth import token_required, author_required

blog_bp = Blueprint('blog', __name__)

def get_blog_service():
    return BlogService(current_app.db)

@blog_bp.route('/', methods=['POST'])
@author_required
def create_blog(current_user):
    data = request.get_json()
    response, status_code = get_blog_service().create_blog(data, current_user['user_id'])
    return jsonify(response), status_code

@blog_bp.route('/', methods=['GET'])
def get_all_blogs():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    response, status_code = get_blog_service().get_all_blogs(page=page, limit=limit)
    return jsonify(response), status_code

@blog_bp.route('/<blog_id>', methods=['GET'])
def get_blog(blog_id):
    response, status_code = get_blog_service().get_blog(blog_id)
    return jsonify(response), status_code

@blog_bp.route('/<blog_id>', methods=['PUT'])
@author_required
def update_blog(current_user, blog_id):
    data = request.get_json()
    response, status_code = get_blog_service().update_blog(blog_id, data, current_user['user_id'])
    return jsonify(response), status_code

@blog_bp.route('/<blog_id>', methods=['DELETE'])
@author_required
def delete_blog(current_user, blog_id):
    response, status_code = get_blog_service().delete_blog(blog_id, current_user['user_id'])
    return jsonify(response), status_code

@blog_bp.route('/search', methods=['GET'])
def search_blogs():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    response, status_code = get_blog_service().search_blogs(query, page=page, limit=limit)
    return jsonify(response), status_code

@blog_bp.route('/author/<author_id>', methods=['GET'])
def get_blogs_by_author(author_id):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    response, status_code = get_blog_service().get_blogs_by_author(author_id, page=page, limit=limit)
    return jsonify(response), status_code

@blog_bp.route('/author/works', methods=['GET'])
@author_required
def get_my_works(current_user):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    response, status_code = get_blog_service().get_blogs_by_author(current_user['user_id'], page=page, limit=limit)
    return jsonify(response), status_code

@blog_bp.route('/tag/<tag>', methods=['GET'])
def get_blogs_by_tag(tag):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    response, status_code = get_blog_service().get_blogs_by_tag(tag, page=page, limit=limit)
    return jsonify(response), status_code
