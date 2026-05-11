import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/blog_db')
    
    # Security
    JWT_SECRET = os.getenv('JWT_SECRET', 'default_secret_key')
    JWT_EXPIRATION = 86400  # 24 hours in seconds
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_AUTH = "1000/hour"
    RATELIMIT_SEARCH = "50/hour"
    
    # API
    API_VERSION = 'v1'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max request size
    
    # Caching
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
