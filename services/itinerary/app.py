from flask import Flask, jsonify
from flask_cors import CORS
import os
import threading
import logging
import traceback
from app.models import db
from app.routes import register_routes
from app.message_broker import MessageBroker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Log environment variables (excluding sensitive info)
logger.info("Environment variables:")
for key, value in os.environ.items():
    if "KEY" not in key.upper() and "SECRET" not in key.upper() and "PASS" not in key.upper():
        logger.info(f"  {key}: {value}")
    else:
        logger.info(f"  {key}: [REDACTED]")

# Configure the database
try:
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@itinerary-db:5432/itinerary_db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.info(f"Database configuration set with URI: {database_url}")
except Exception as e:
    logger.error(f"Error configuring database: {e}")
    logger.error(traceback.format_exc())

# Initialize the database
try:
    db.init_app(app)
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Error initializing database: {e}")
    logger.error(traceback.format_exc())

# Register routes
try:
    register_routes(app)
    logger.info("Routes registered successfully")
except Exception as e:
    logger.error(f"Error registering routes: {e}")
    logger.error(traceback.format_exc())

# Initialize message broker
try:
    message_broker = MessageBroker(app)
    logger.info("Message broker initialized")
    
    # Make the message broker accessible to other modules
    import app as app_module
    app_module.message_broker = message_broker
except Exception as e:
    logger.error(f"Error initializing message broker: {e}")
    logger.error(traceback.format_exc())
    message_broker = None

# Root route
@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Itinerary Service API. Use /health for health check."}), 200

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    rabbitmq_status = "connected" if message_broker and message_broker.connection and message_broker.connection.is_open else "disconnected"
    return jsonify({
        "status": "healthy", 
        "service": "itinerary",
        "rabbitmq_status": rabbitmq_status
    }), 200

def start_message_consumer():
    """Start consuming messages from RabbitMQ in a separate thread."""
    try:
        with app.app_context():
            if message_broker:
                message_broker.start_consuming()
            else:
                logger.error("Cannot start message consumer: Message broker not initialized")
    except Exception as e:
        logger.error(f"Error starting message consumer: {e}")
        logger.error(traceback.format_exc())

def setup_rabbitmq():
    """Connect to RabbitMQ and set up message consumer thread."""
    global message_broker
    
    if not message_broker:
        logger.error("Cannot connect to RabbitMQ: Message broker not initialized")
        return False
    
    try:
        # Connect to RabbitMQ
        logger.info("Connecting to RabbitMQ...")
        connected = message_broker.connect()
        if not connected:
            logger.error("Failed to connect to RabbitMQ")
            return False
        
        # Start message consumer in a separate thread
        logger.info("Starting RabbitMQ consumer thread...")
        consumer_thread = threading.Thread(target=start_message_consumer)
        consumer_thread.daemon = True
        consumer_thread.start()
        logger.info("RabbitMQ consumer thread started successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up RabbitMQ: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    # Create tables if they don't exist
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        logger.error(traceback.format_exc())
    
    # Setup RabbitMQ
    setup_result = setup_rabbitmq()
    if setup_result:
        logger.info("RabbitMQ setup successful")
    else:
        logger.warning("RabbitMQ setup failed, some features may be unavailable")
        
    # Start the Flask application
    logger.info("Starting Itinerary Service on port 5006")
    app.run(host='0.0.0.0', port=5006, debug=True) 