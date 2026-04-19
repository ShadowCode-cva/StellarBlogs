from functools import wraps
from flask import request, jsonify
import jwt
from config.settings import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            current_user = {
                'user_id': data['user_id'],
                'role': data['role']
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def author_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') != 'author':
            return jsonify({'error': 'Author privileges required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated
