from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
from app.models import db
from app.routes import register_routes
from app.message_broker import start_consumer_thread

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Configure the database
database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@trip-db:5432/trip_db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Register routes
register_routes(app)

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "trip-management"}), 200

if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Add group_id column if it doesn't exist
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('trips')]
        if 'group_id' not in columns:
            logging.info("Adding group_id column to trips table")
            with db.engine.connect() as connection:
                connection.execute(text('ALTER TABLE trips ADD COLUMN group_id INTEGER'))
                connection.commit()
    
        # Start RabbitMQ consumer thread
        try:
            consumer_thread = start_consumer_thread(app)
            logger.info("RabbitMQ consumer thread started successfully")
        except Exception as e:
            logger.error(f"Error starting RabbitMQ consumer thread: {e}")
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=5005, debug=True)

