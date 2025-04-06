# This file is intentionally left empty to mark directory as Python package 

# Group management microservice package
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-User-ID", "X-User-Email"]
        }
    })
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_CONNECTION')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Import and register blueprints
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

__all__ = ['db', 'create_app'] 