from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from flask import jsonify

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def rate_limit(limit_string: str):
    """Custom rate limit decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        decorated_function._rate_limit = limit_string
        return decorated_function
    return decorator
