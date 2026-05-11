from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_caching import Cache
from pymongo import MongoClient
from config.settings import Config
from utils.errors import register_error_handlers
from utils.ratelimit import limiter
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Log import status for debugging
print("[v0] Starting app import", file=sys.stderr)

def create_app():
    # Get the base directory
    basedir = os.path.abspath(os.path.dirname(__file__))
    template_folder = os.path.join(basedir, 'templates')
    
    app = Flask(__name__, template_folder=template_folder)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize CORS with production settings
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)
    
    # Initialize Cache
    cache = Cache(app, config={'CACHE_TYPE': app.config['CACHE_TYPE']})
    app.cache = cache

    # Initialize Rate Limiter
    limiter.init_app(app)
    
    # Setup Advanced Logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/stellarblogs.log', 
                                           maxBytes=10240000, 
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('StellarBlogs startup')

    # Initialize MongoDB client with connection pooling
    try:
        client = MongoClient(
            app.config['MONGO_URI'],
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=5000,
            connectTimeoutMS=10000,
            maxPoolSize=50,
            minPoolSize=10
        )
        # Test connection
        client.admin.command('ping')
        app.logger.info("Connected to MongoDB successfully!")
        
        # Create indexes for better query performance
        db = client.get_database()
        
        # Blog indexes
        if 'blogs' in db.list_collection_names():
            try:
                db.blogs.create_index('author_id')
                db.blogs.create_index('created_at')
                db.blogs.create_index('tags')
                # Text search index - skip if it already exists
                try:
                    db.blogs.create_index([('title', 'text'), ('content', 'text')])
                except Exception:
                    pass  # Index already exists
                app.logger.info("Blog indexes created successfully")
            except Exception as e:
                app.logger.warning(f"Some blog indexes already exist: {e}")
        
        # User indexes
        if 'users' in db.list_collection_names():
            try:
                db.users.create_index('email', unique=True)
                db.users.create_index('username', unique=True)
                app.logger.info("User indexes created successfully")
            except Exception as e:
                app.logger.warning(f"Some user indexes already exist: {e}")
        
        app.db = db
        
    except Exception as e:
        app.logger.error(f"Failed to connect to MongoDB: {e}")
        # Continue anyway - app can still serve frontend
        app.db = None

    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except Exception as e:
            app.logger.error(f"Error rendering index: {e}")
            return jsonify({
                "message": "StellarBlogs API",
                "version": app.config['API_VERSION'],
                "status": "running"
            }), 200

    # Add Security Headers middleware
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        return response

    # Register blueprints
    from routes.auth import auth_bp
    from routes.blog import blog_bp
    from routes.comment import comment_bp
    from routes.interaction import interaction_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(blog_bp, url_prefix='/api/v1/blogs')
    app.register_blueprint(comment_bp, url_prefix='/api/v1/comments')
    app.register_blueprint(interaction_bp, url_prefix='/api/v1/interactions')

    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/api/v1/health', methods=['GET'])
    def health():
        try:
            return jsonify({
                'status': 'healthy',
                'service': 'StellarBlogs API',
                'version': app.config['API_VERSION']
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Debug endpoint
    @app.route('/test', methods=['GET'])
    def test():
        return jsonify({'message': 'App is running'}), 200

    return app


app = create_app()
print("[v0] App created successfully", file=sys.stderr)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
