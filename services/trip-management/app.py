from app import create_app, db
from app.rabbitmq_config import MessageBroker
import threading
import os

# Create the Flask application
app = create_app()

# Initialize message broker
message_broker = MessageBroker(app)

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

