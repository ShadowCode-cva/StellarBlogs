import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/blog_db')
    JWT_SECRET = os.getenv('JWT_SECRET', 'default_secret_key')
