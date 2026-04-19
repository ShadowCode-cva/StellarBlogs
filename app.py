from flask import Flask, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from config.settings import Config
import logging

def create_app():
    app = Flask(__name__)
    
    # Initialize CORS for security
    CORS(app)

    # Setup Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize MongoDB client
    try:
        client = MongoClient(app.config['MONGO_URI'], serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        # We still proceed to create the app, but DB operations might fail.

    app.db = client.get_database()

    @app.route('/')
    def index():
        return render_template('index.html')

    # Register blueprints
    from routes.auth import auth_bp
    from routes.blog import blog_bp
    from routes.comment import comment_bp
    from routes.interaction import interaction_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(blog_bp, url_prefix='/api/blogs')
    app.register_blueprint(comment_bp, url_prefix='/api/comments')
    app.register_blueprint(interaction_bp, url_prefix='/api/interactions')

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the error for the developer
        app.logger.error(f"Server Error: {str(e)}")
        # Return a clean JSON error to the user
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred. Please try again later."
        }), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
