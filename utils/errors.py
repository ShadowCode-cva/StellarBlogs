from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
import traceback

class APIError(Exception):
    """Custom API error class"""
    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or 'API_ERROR'
    
    def to_dict(self):
        return {
            'status': 'error',
            'error_code': self.error_code,
            'message': self.message
        }

def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = error.to_dict()
        current_app.logger.warning(f"API Error: {error.error_code} - {error.message}")
        return jsonify(response), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        response = {
            'status': 'error',
            'error_code': f'HTTP_{error.code}',
            'message': error.description or 'An error occurred'
        }
        current_app.logger.warning(f"HTTP Error: {error.code} - {error.description}")
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        # Log full traceback for debugging
        current_app.logger.error(f"Unhandled Exception: {str(error)}\n{traceback.format_exc()}")
        
        response = {
            'status': 'error',
            'error_code': 'INTERNAL_SERVER_ERROR',
            'message': 'An internal server error occurred. Please try again later.'
        }
        
        # Return more details in development
        if current_app.config.get('DEBUG'):
            response['details'] = str(error)
        
        return jsonify(response), 500
