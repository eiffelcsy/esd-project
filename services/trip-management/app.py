from flask import Flask, jsonify
from flask_cors import CORS
import os
import threading
import logging
from app.models import db
from app.routes import register_routes
from app.message_broker import MessageBroker

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

# Configure the database
database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@trip-db:5432/trip_db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Initialize the message broker
message_broker = MessageBroker(app)
app.message_broker = message_broker

# Register routes
register_routes(app)

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "trip-management"}), 200

def start_message_consumer():
    """Start consuming messages from RabbitMQ in a separate thread."""
    with app.app_context():
        message_broker.connect()
        message_broker.start_consuming()

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
    
    # Start message consumer in a separate thread
    consumer_thread = threading.Thread(target=start_message_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
        
    # Start the Flask application
    app.run(host='0.0.0.0', port=5005, debug=True)

