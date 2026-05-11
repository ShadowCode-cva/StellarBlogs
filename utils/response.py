from flask import jsonify
from typing import Dict, Any, Optional

class APIResponse:
    """Standardized API response wrapper"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200):
        """Return a success response"""
        response = {
            'status': 'success',
            'message': message,
            'data': data
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(message: str, error_code: str = "ERROR", status_code: int = 400, data: Any = None):
        """Return an error response"""
        response = {
            'status': 'error',
            'error_code': error_code,
            'message': message
        }
        if data:
            response['data'] = data
        return jsonify(response), status_code
    
    @staticmethod
    def paginated(data: list, page: int, limit: int, total: int, message: str = "Success"):
        """Return a paginated response"""
        total_pages = (total + limit - 1) // limit
        response = {
            'status': 'success',
            'message': message,
            'data': data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        return jsonify(response), 200
