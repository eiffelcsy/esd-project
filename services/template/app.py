from flask import Flask, jsonify
from flask_cors import CORS
import os
from app.models import db
from app.routes import register_routes

app = Flask(__name__)
CORS(app)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@template-db:5432/template_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Register routes
register_routes(app)

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "template"}), 200

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)