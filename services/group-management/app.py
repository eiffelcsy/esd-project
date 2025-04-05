from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from app.models import db
from app.routes import register_routes

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
# Configure CORS to allow requests from frontend
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost"], supports_credentials=True, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@grouprequest-db:5432/grouprequest_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Register routes
register_routes(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "group-management"}), 200

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True) 