import pika
import json
import os
import logging
import time
from datetime import datetime
from app.openai_service import get_recommendations
from app.models import db, Recommendation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageBroker:
    def __init__(self, app=None):
        self.app = app
        self.connection = None
        self.channel = None
        self.consumer_thread = None
        self.should_reconnect = True
        self.reconnect_delay = 5  # seconds
        
        # RabbitMQ connection settings
        self.rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'localhost')
        self.rabbitmq_port = int(os.environ.get('RABBITMQ_PORT', 5672))
        self.rabbitmq_user = os.environ.get('RABBITMQ_USER', 'guest')
        self.rabbitmq_pass = os.environ.get('RABBITMQ_PASS', 'guest')
        
        # Queue names
        self.request_queue = 'recommendation_requests'
        self.response_queue = 'recommendation_responses'
        
        if app is not None:
            self.init_app(app)
        
    def init_app(self, app):
        self.app = app
        
        # Connect to RabbitMQ when the app starts
        with app.app_context():
            self.connect()
        
    def connect(self):
        """Establish connection to RabbitMQ and set up channels"""
        try:
            # Create connection parameters with better stability settings
            credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
                connection_attempts=3,
                retry_delay=5
            )
            
            # Connect to RabbitMQ
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue=self.request_queue, durable=True)
            self.channel.queue_declare(queue=self.response_queue, durable=True)
            
            # Set QoS to avoid overwhelming the consumer
            self.channel.basic_qos(prefetch_count=1)
            
            # Set up consumer for recommendation requests
            self.channel.basic_consume(
                queue=self.request_queue,
                on_message_callback=self.process_recommendation_request,
                auto_ack=False
            )
            
            logger.info(f"Connected to RabbitMQ at {self.rabbitmq_host}:{self.rabbitmq_port}")
            logger.info(f"Listening for messages on '{self.request_queue}' queue")
            
            # Start consuming in a separate thread
            import threading
            self.consumer_thread = threading.Thread(target=self.start_consuming)
            self.consumer_thread.daemon = True
            self.consumer_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def start_consuming(self):
        """Start consuming messages from the request queue with reconnection logic"""
        while self.should_reconnect:
            try:
                logger.info("Starting to consume messages...")
                
                # This is a blocking call that will keep the thread alive
                self.channel.start_consuming()
                
            except pika.exceptions.AMQPConnectionError as e:
                logger.error(f"Connection to RabbitMQ lost: {e}")
                self.handle_connection_error()
                
            except pika.exceptions.AMQPChannelError as e:
                logger.error(f"Channel error: {e}")
                self.handle_connection_error()
                
            except Exception as e:
                logger.error(f"Error while consuming messages: {e}")
                self.handle_connection_error()
    
    def handle_connection_error(self):
        """Handle connection errors with reconnection logic"""
        if not self.should_reconnect:
            return
            
        # Clean up existing connection
        self.safe_channel_close()
        self.safe_connection_close()
        
        # Wait before reconnecting
        logger.info(f"Waiting {self.reconnect_delay} seconds before reconnecting...")
        time.sleep(self.reconnect_delay)
        
        # Try to reconnect
        reconnect_success = self.connect()
        
        if not reconnect_success:
            logger.error("Failed to reconnect, will try again later")
            # Will be retried in the next loop iteration
    
    def safe_channel_close(self):
        """Safely close the channel if it exists and is open"""
        if self.channel is not None:
            try:
                if self.channel.is_open:
                    self.channel.close()
            except Exception as e:
                logger.error(f"Error closing channel: {e}")
    
    def safe_connection_close(self):
        """Safely close the connection if it exists and is open"""
        if self.connection is not None:
            try:
                if self.connection.is_open:
                    self.connection.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
    
    def process_recommendation_request(self, ch, method, properties, body):
        """Process incoming recommendation requests"""
        try:
            logger.info(f"Received recommendation request: {body}")
            
            # Parse the request
            data = json.loads(body)
            
            # Extract trip details
            trip_id = data.get('trip_id')
            destination = data.get('destination')
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            
            # Convert string dates to date objects
            start_date = datetime.fromisoformat(start_date_str).date()
            end_date = datetime.fromisoformat(end_date_str).date()
            
            # Get recommendations from OpenAI
            recommendations = get_recommendations(destination, start_date, end_date)
            
            # Save to database (within app context)
            if self.app:
                with self.app.app_context():
                    # Check if recommendation already exists
                    existing_recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
                    
                    if existing_recommendation:
                        # Update existing record
                        existing_recommendation.recommendations = recommendations
                        db.session.commit()
                        logger.info(f"Updated existing recommendation for trip_id: {trip_id}")
                    else:
                        # Create new recommendation
                        new_recommendation = Recommendation(
                            trip_id=trip_id,
                            recommendations=recommendations
                        )
                        db.session.add(new_recommendation)
                        db.session.commit()
                        logger.info(f"Saved new recommendation for trip_id: {trip_id}")
            
            # Prepare response - include all original data plus recommendations
            response = {
                'trip_id': trip_id,
                'destination': destination,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'recommendations': recommendations,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send the response - using a new channel to avoid issues
            self.send_recommendation_response(response)
            
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing recommendation request: {e}")
            # Acknowledge the message even on error to avoid queue blockage
            # In a production system, you might want to implement a dead-letter queue instead
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def send_recommendation_response(self, response):
        """Send recommendation response to the response queue using a new channel"""
        try:
            # Create a new connection and channel just for publishing
            credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                credentials=credentials,
                heartbeat=30  # Shorter heartbeat for publishers
            )
            
            publish_connection = pika.BlockingConnection(parameters)
            publish_channel = publish_connection.channel()
            
            # Ensure the queue exists
            publish_channel.queue_declare(queue=self.response_queue, durable=True)
            
            # Publish the response
            publish_channel.basic_publish(
                exchange='',
                routing_key=self.response_queue,
                body=json.dumps(response),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Sent recommendation response for trip_id: {response.get('trip_id')}")
            
            # Close the publish channel and connection
            publish_channel.close()
            publish_connection.close()
            
        except Exception as e:
            logger.error(f"Error sending recommendation response: {e}")
    
    def close(self):
        """Close the connection to RabbitMQ"""
        self.should_reconnect = False
        self.safe_channel_close()
        self.safe_connection_close()
        logger.info("Closed connection to RabbitMQ") 