from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
import traceback
import threading
import time
from app.models import db
from app.routes import register_routes
from app.message_broker import start_consumer_thread, processed_trip_ids, connect_to_rabbitmq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)

# Configure CORS with proper error handling
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type"]
    }
})

# Add error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Log environment variables (excluding sensitive info)
logger.info("Environment variables:")
for key, value in os.environ.items():
    if "KEY" not in key.upper() and "SECRET" not in key.upper() and "PASS" not in key.upper():
        logger.info(f"  {key}: {value}")
    else:
        logger.info(f"  {key}: [REDACTED]")

# Configure the database
try:
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@recommendation-db:5432/recommendation_db')
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

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Recommendation Management Service API. Use /health for health check."}), 200

@app.route('/health', methods=['GET'])
def health_check():
    db_status = "connected"
    try:
        with app.app_context():
            # Try to execute a simple database query
            from app.models import Recommendation
            Recommendation.query.limit(1).all()
    except Exception:
        db_status = "disconnected"

    # Count existing recommendations
    recommendation_count = 0
    try:
        with app.app_context():
            from app.models import Recommendation
            recommendation_count = Recommendation.query.count()
    except Exception:
        pass

    return jsonify({
        "status": "healthy", 
        "service": "recommendation-management",
        "database_status": db_status,
        "recommendation_count": recommendation_count,
        "cached_trip_ids": len(processed_trip_ids)
    }), 200

# Function to periodically clear the processed_trip_ids cache
def clear_processed_trip_ids_cache():
    """Clear the processed_trip_ids cache periodically"""
    while True:
        try:
            time.sleep(300)  # 5 minutes
            current_size = len(processed_trip_ids)
            processed_trip_ids.clear()
            logger.info(f"Cleared processed_trip_ids cache (removed {current_size} entries)")
        except Exception as e:
            logger.error(f"Error clearing processed_trip_ids cache: {e}")
            logger.error(traceback.format_exc())

# Check OpenAI API Key
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    logger.error("OPENAI_API_KEY environment variable is not set. Service may not function correctly.")
else:
    logger.info("OPENAI_API_KEY is set")

# Check RabbitMQ configuration
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
logger.info(f"RabbitMQ host is set to: {rabbitmq_host}")

# Purge the recommendation_requests queue at startup
def purge_recommendation_requests_queue():
    """Purge the recommendation_requests queue to avoid processing old messages"""
    try:
        conn, channel = connect_to_rabbitmq()
        queue_name = 'recommendation_requests'
        
        # Declare the queue (this won't delete it)
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Purge the queue
        message_count = channel.queue_purge(queue=queue_name)
        logger.info(f"Purged {message_count} messages from {queue_name} queue")
        
        # Close the connection
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error purging recommendation_requests queue: {e}")
        logger.error(traceback.format_exc())
        return False

# Create tables if they don't exist
try:
    with app.app_context():
        # Drop existing tables
        db.drop_all()
        logger.info("Dropped existing database tables")
        
        # Create tables with updated schema
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=clear_processed_trip_ids_cache)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        logger.info("Started cache cleanup thread")
        
        # Purge the recommendation_requests queue
        purge_success = purge_recommendation_requests_queue()
        if purge_success:
            logger.info("Successfully purged recommendation_requests queue")
        else:
            logger.warning("Failed to purge recommendation_requests queue")
        
        # Start RabbitMQ consumer thread
        try:
            consumer_thread = start_consumer_thread(app)
            logger.info("RabbitMQ consumer thread started successfully")
        except Exception as e:
            logger.error(f"Error starting RabbitMQ consumer thread: {e}")
            logger.error(traceback.format_exc())
except Exception as e:
    logger.error(f"Error creating database tables: {e}")
    logger.error(traceback.format_exc())

if __name__ == '__main__':
    logger.info("Starting Recommendation Management Service on port 5002")
    app.run(host='0.0.0.0', port=5002, debug=True)