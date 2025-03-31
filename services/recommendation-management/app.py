from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from app.models import db, Recommendation
from app.routes import register_routes
from app.message_broker import MessageBroker

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:postgres@recommendation-db:5432/recommendation_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Register routes
register_routes(app)

# Initialize message broker
message_broker = MessageBroker(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "recommendation-management"}), 200

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    
    # Connect to RabbitMQ
    message_broker.connect()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)