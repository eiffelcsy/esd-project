import pika
import json
import os
import logging
from datetime import datetime
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageBroker:
    def __init__(self, app):
        self.app = app
        self.connection = None
        self.channel = None
        self.recommendation_requests_queue = 'recommendation_requests'
        self.recommendation_responses_queue = 'recommendation_responses'
        self.trip_details_queue = 'trip_details'

    def connect(self):
        """Connect to RabbitMQ."""
        try:
            # Get RabbitMQ URL from environment or use default
            rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
            
            # Parse the URL
            parameters = pika.URLParameters(rabbitmq_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300
            parameters.connection_attempts = 3
            parameters.retry_delay = 5
            
            # Close any existing connection first
            self.close()
            
            # Create connection
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(
                queue=self.recommendation_requests_queue,
                durable=True
            )
            self.channel.queue_declare(
                queue=self.recommendation_responses_queue,
                durable=True
            )
            self.channel.queue_declare(
                queue=self.trip_details_queue,
                durable=True
            )
            
            # Set up consumer for recommendation responses
            self.channel.basic_consume(
                queue=self.recommendation_responses_queue,
                on_message_callback=self._process_recommendation_response,
                auto_ack=True
            )
            
            logger.info("Successfully connected to RabbitMQ")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {str(e)}")
            return False

    def send_trip_created_event(self, trip_data):
        """Send a trip creation event to the trip_details queue."""
        # Create a new connection for sending messages
        try:
            # Get RabbitMQ URL from environment or use default
            rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
            
            # Parse the URL
            parameters = pika.URLParameters(rabbitmq_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300
            parameters.connection_attempts = 3
            parameters.retry_delay = 5
            
            # Create a separate connection just for this message
            with pika.BlockingConnection(parameters) as connection:
                channel = connection.channel()
                
                # Declare the queue
                channel.queue_declare(
                    queue=self.trip_details_queue,
                    durable=True
                )
                
                # Publish the message
                channel.basic_publish(
                    exchange='',
                    routing_key=self.trip_details_queue,
                    body=json.dumps(trip_data),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                        content_type='application/json'
                    )
                )
                
                logger.info(f"Sent trip creation event for trip {trip_data['id']}")
                return True
                
        except Exception as e:
            logger.error(f"Error sending trip creation event: {str(e)}")
            # Try again with a short delay
            time.sleep(2)
            try:
                with pika.BlockingConnection(parameters) as connection:
                    channel = connection.channel()
                    
                    # Declare the queue
                    channel.queue_declare(
                        queue=self.trip_details_queue,
                        durable=True
                    )
                    
                    # Publish the message
                    channel.basic_publish(
                        exchange='',
                        routing_key=self.trip_details_queue,
                        body=json.dumps(trip_data),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type='application/json'
                        )
                    )
                    logger.info(f"Successfully resent trip creation event for trip {trip_data['id']}")
                    return True
            except Exception as retry_error:
                logger.error(f"Failed to resend trip creation event: {str(retry_error)}")
                return False

    def send_recommendation_request(self, trip_data):
        """Send a recommendation request to the recommendation_requests queue."""
        # Create a new connection for sending messages
        try:
            # Get RabbitMQ URL from environment or use default
            rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
            
            # Parse the URL
            parameters = pika.URLParameters(rabbitmq_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300
            parameters.connection_attempts = 3
            parameters.retry_delay = 5
            
            # Create a separate connection just for this message
            with pika.BlockingConnection(parameters) as connection:
                channel = connection.channel()
                
                # Declare the queue
                channel.queue_declare(
                    queue=self.recommendation_requests_queue,
                    durable=True
                )
                
                # Publish the message
                channel.basic_publish(
                    exchange='',
                    routing_key=self.recommendation_requests_queue,
                    body=json.dumps(trip_data),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                        content_type='application/json'
                    )
                )
                
                logger.info(f"Sent recommendation request for trip {trip_data['id']}")
                return True
                
        except Exception as e:
            logger.error(f"Error sending recommendation request: {str(e)}")
            # Try again with a short delay
            time.sleep(2)
            try:
                with pika.BlockingConnection(parameters) as connection:
                    channel = connection.channel()
                    
                    # Declare the queue
                    channel.queue_declare(
                        queue=self.recommendation_requests_queue,
                        durable=True
                    )
                    
                    # Publish the message
                    channel.basic_publish(
                        exchange='',
                        routing_key=self.recommendation_requests_queue,
                        body=json.dumps(trip_data),
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type='application/json'
                        )
                    )
                    logger.info(f"Successfully resent recommendation request for trip {trip_data['id']}")
                    return True
            except Exception as retry_error:
                logger.error(f"Failed to resend recommendation request: {str(retry_error)}")
                return False

    def _process_recommendation_response(self, channel, method, properties, body):
        """Process a recommendation response from the recommendation_responses queue."""
        try:
            data = json.loads(body)
            trip_id = data.get('trip_id')
            recommendations = data.get('recommendations', [])
            
            logger.info(f"Received recommendations for trip {trip_id}")
            
            # Send the recommendations to the itinerary service to update the trip
            itinerary_service_url = os.getenv('ITINERARY_SERVICE_URL', 'http://itinerary:5004')
            response = requests.post(
                f"{itinerary_service_url}/api/itinerary/{trip_id}/recommendations",
                json={'recommendations': recommendations}
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully added recommendations to itinerary for trip {trip_id}")
            else:
                logger.error(f"Failed to add recommendations to itinerary: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error processing recommendation response: {str(e)}")

    def start_consuming(self):
        """Start consuming messages."""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info("Starting to consume messages")
                
                # Make sure we have a valid connection
                if self.connection is None or self.connection.is_closed or self.channel is None or self.channel.is_closed:
                    logger.info("Connection is not valid, attempting to reconnect...")
                    if not self.connect():
                        logger.error("Failed to connect, retrying in 5 seconds...")
                        time.sleep(5)
                        retry_count += 1
                        continue
                
                # Start consuming messages
                self.channel.start_consuming()
                
            except Exception as e:
                logger.error(f"Error starting consumer: {str(e)}")
                # Try to clean up
                try:
                    if self.channel and self.channel.is_open:
                        self.channel.stop_consuming()
                except Exception:
                    pass
                
                self.close()
                
                # Retry with a delay
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Retrying in 5 seconds (attempt {retry_count}/{max_retries})...")
                    time.sleep(5)
                else:
                    logger.error("Max retries reached, giving up.")
                    break

    def close(self):
        """Close the connection."""
        try:
            if self.channel and self.channel.is_open:
                try:
                    self.channel.stop_consuming()
                except Exception:
                    pass
                try:
                    self.channel.close()
                except Exception:
                    pass
                
            if self.connection and self.connection.is_open:
                try:
                    self.connection.close()
                except Exception:
                    pass
                
            self.channel = None
            self.connection = None
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}") 