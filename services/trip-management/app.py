from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from app.models import db
from app.routes import register_routes
from app.rabbitmq_config import MessageBroker
import threading

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/trip_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Initialize message broker
message_broker = MessageBroker(app)

# Register routes
register_routes(app, message_broker)

def start_message_consumer():
    with app.app_context():
        message_broker.start_consuming()

if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
    # Connect to RabbitMQ
    message_broker.connect()
    
    # Start message consumer in a separate thread
    consumer_thread = threading.Thread(target=start_message_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Start the Flask application
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

