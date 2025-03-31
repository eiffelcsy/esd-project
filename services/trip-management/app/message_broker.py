import pika
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageBroker:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.setup_connection()

    def setup_connection(self):
        """Set up RabbitMQ connection and channel."""
        try:
            # Get RabbitMQ URL from environment or use default
            rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
            
            # Parse the URL
            parameters = pika.URLParameters(rabbitmq_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300
            parameters.connection_attempts = 3
            parameters.retry_delay = 5
            
            # Create connection
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare the queue
            self.channel.queue_declare(
                queue='recommendation_requests',
                durable=True
            )
            
            logger.info("Successfully connected to RabbitMQ")
            
        except Exception as e:
            logger.error(f"Error setting up RabbitMQ connection: {str(e)}")
            raise

    def send_recommendation_request(self, trip_data):
        """Send a recommendation request for a trip."""
        try:
            if self.channel is None or self.channel.is_closed:
                logger.info("Channel is closed, attempting to reconnect...")
                self.setup_connection()
            
            message = {
                'trip_id': trip_data['id'],
                'destination': trip_data['city'],
                'start_date': trip_data['start_date'],
                'end_date': trip_data['end_date']
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key='recommendation_requests',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Sent recommendation request for trip {trip_data['id']}")
            
        except Exception as e:
            logger.error(f"Error sending recommendation request: {str(e)}")
            # Try to reconnect and send again
            try:
                self.setup_connection()
                self.channel.basic_publish(
                    exchange='',
                    routing_key='recommendation_requests',
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type='application/json'
                    )
                )
                logger.info(f"Successfully resent recommendation request for trip {trip_data['id']}")
            except Exception as retry_error:
                logger.error(f"Failed to resend recommendation request: {str(retry_error)}")
                raise

    def close(self):
        """Close the connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

# Create a singleton instance
message_broker = MessageBroker() 