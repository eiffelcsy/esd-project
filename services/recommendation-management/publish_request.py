import pika
import json
import os
import logging
import sys
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_rabbitmq():
    """Connect to RabbitMQ and return connection and channel"""
    # Get RabbitMQ connection details
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    
    logger.info(f"Connecting to RabbitMQ at {rabbitmq_host}...")
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host,
            port=5672,
            connection_attempts=5,
            retry_delay=5,
            heartbeat=600,
            blocked_connection_timeout=300,
            socket_timeout=10.0
        )
    )
    
    channel = connection.channel()
    logger.info(f"Connected to RabbitMQ at {rabbitmq_host}")
    return connection, channel

def publish_recommendation_request(trip_id, destination, start_date=None, end_date=None):
    """
    Publish a recommendation request to RabbitMQ
    
    Args:
        trip_id: The ID of the trip
        destination: The destination city/country
        start_date: Start date (default: today)
        end_date: End date (default: 7 days from today)
    """
    try:
        # Set default dates if not provided
        if start_date is None:
            start_date = datetime.now().date()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
            
        # Connect to RabbitMQ
        connection, channel = connect_to_rabbitmq()
        
        # Declare the queue
        queue_name = 'recommendation_requests'
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Create the request message
        message = {
            'trip_id': trip_id,
            'destination': destination,
            'start_date': start_date.isoformat() if hasattr(start_date, 'isoformat') else start_date,
            'end_date': end_date.isoformat() if hasattr(end_date, 'isoformat') else end_date,
        }
        
        # Publish the message
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )
        
        logger.info(f"Published recommendation request for trip_id={trip_id}, destination={destination}")
        logger.info(f"Message: {message}")
        
        # Close the connection
        connection.close()
        logger.info("Connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error publishing recommendation request: {e}")
        return False

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python publish_request.py <trip_id> <destination> [start_date] [end_date]")
        print("Example: python publish_request.py 123 'Paris' '2025-06-01' '2025-06-07'")
        sys.exit(1)
    
    trip_id = sys.argv[1]
    destination = sys.argv[2]
    
    start_date = None
    if len(sys.argv) > 3:
        start_date = datetime.fromisoformat(sys.argv[3]).date()
    
    end_date = None
    if len(sys.argv) > 4:
        end_date = datetime.fromisoformat(sys.argv[4]).date()
    
    # Publish the request
    logger.info(f"Publishing recommendation request for trip_id={trip_id}, destination={destination}")
    success = publish_recommendation_request(trip_id, destination, start_date, end_date)
    
    if success:
        logger.info("Request published successfully")
    else:
        logger.error("Failed to publish request")
        sys.exit(1) 