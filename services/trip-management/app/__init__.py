from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()

# Import message broker
from app.message_broker import message_broker

def create_app(testing=False):
    # Initialize the Flask application
    app = Flask(__name__)
    CORS(app)

    # Configure the database
    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@trip-db:5432/trip_db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = testing

    # Initialize extensions
    db.init_app(app)

    # Import and register blueprints/routes
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app 