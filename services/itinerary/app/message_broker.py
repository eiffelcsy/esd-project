import pika
import json
import logging
import os
import time
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MessageBroker:
    def __init__(self, app):
        self.app = app
        self.connection = None
        self.channel = None
        self.recommendations_queue = 'recommendation_responses'
        self.recommendation_requests_queue = 'recommendation_requests'
        
    def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            # Get RabbitMQ URL from environment or use default
            rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
            rabbitmq_port = os.getenv('RABBITMQ_PORT', '5672')
            rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
            rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')
            
            rabbitmq_url = os.getenv('RABBITMQ_URL', f'amqp://{rabbitmq_user}:{rabbitmq_pass}@{rabbitmq_host}:{rabbitmq_port}/')
            
            logger.info(f"Connecting to RabbitMQ with URL: {rabbitmq_url.replace(rabbitmq_pass, '******')}")
            
            # Create a connection parameters object
            parameters = pika.URLParameters(rabbitmq_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300
            parameters.connection_attempts = 3
            parameters.retry_delay = 5
            parameters.socket_timeout = 10.0  # Add socket timeout
            
            # Close any existing connection first
            self.close()
            
            # Create a connection
            self.connection = pika.BlockingConnection(parameters)
            
            # Create a channel
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue=self.recommendations_queue, durable=True)
            self.channel.queue_declare(queue=self.recommendation_requests_queue, durable=True)
            
            logger.info(f"Successfully declared queues: {self.recommendations_queue}, {self.recommendation_requests_queue}")
            
            # Set up consumer for recommendations queue
            self.channel.basic_consume(
                queue=self.recommendations_queue,
                on_message_callback=self._process_recommendations,
                auto_ack=True
            )
            
            logger.info("Connected to RabbitMQ successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def send_recommendation_request(self, trip_id, destination, start_date, end_date):
        """Send a recommendation request to the recommendation service."""
        try:
            recommendation_data = {
                "trip_id": trip_id,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date
            }
            
            logger.info(f"Preparing to send recommendation request for trip_id: {trip_id}, destination: {destination}")
            
            # Use a separate connection to publish the message for reliability
            rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
            rabbitmq_port = os.getenv('RABBITMQ_PORT', '5672')
            rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
            rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')
            
            rabbitmq_url = os.getenv('RABBITMQ_URL', f'amqp://{rabbitmq_user}:{rabbitmq_pass}@{rabbitmq_host}:{rabbitmq_port}/')
            
            logger.info(f"Connecting to RabbitMQ for recommendation request with URL: {rabbitmq_url.replace(rabbitmq_pass, '******')}")
            
            parameters = pika.URLParameters(rabbitmq_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300
            parameters.connection_attempts = 3
            parameters.retry_delay = 5
            parameters.socket_timeout = 10.0
            
            with pika.BlockingConnection(parameters) as connection:
                channel = connection.channel()
                
                # Declare the queue
                channel.queue_declare(
                    queue=self.recommendation_requests_queue,
                    durable=True
                )
                
                # Publish message to recommendation requests queue
                message_body = json.dumps(recommendation_data)
                channel.basic_publish(
                    exchange='',
                    routing_key=self.recommendation_requests_queue,
                    body=message_body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                        content_type='application/json'
                    )
                )
                
                logger.info(f"Successfully sent recommendation request message for trip_id: {trip_id}")
                logger.info(f"Message body: {message_body}")
            
        except Exception as e:
            logger.error(f"Error requesting recommendations for trip_id {trip_id}: {str(e)}")
            logger.error(traceback.format_exc())

    def _process_recommendations(self, ch, method, properties, body):
        """Process recommendation responses and update the itinerary."""
        with self.app.app_context():
            try:
                recommendations = json.loads(body)
                trip_id = recommendations.get('trip_id')
                logger.info(f"Received recommendation response for trip_id: {trip_id}")
                
                # Store the recommendations in database
                from app.models import db, Recommendation
                
                # Extract recommendation data
                recommendation_data = recommendations.get('recommendations', {})
                
                # Check if recommendations already exist for this trip
                existing_recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
                
                if existing_recommendation:
                    # Update existing record
                    existing_recommendation.destination = recommendations.get('destination', '')
                    existing_recommendation.attractions = recommendation_data.get('attractions', [])
                    existing_recommendation.restaurants = recommendation_data.get('restaurants', [])
                    existing_recommendation.activities = recommendation_data.get('activities', [])
                    existing_recommendation.events = recommendation_data.get('events', [])
                    existing_recommendation.tips = recommendation_data.get('tips', [])
                    db.session.commit()
                    logger.info(f"Updated existing recommendations in database for trip_id: {trip_id}")
                else:
                    # Create new recommendation record
                    new_recommendation = Recommendation(
                        trip_id=trip_id,
                        destination=recommendations.get('destination', ''),
                        attractions=recommendation_data.get('attractions', []),
                        restaurants=recommendation_data.get('restaurants', []),
                        activities=recommendation_data.get('activities', []),
                        events=recommendation_data.get('events', []),
                        tips=recommendation_data.get('tips', [])
                    )
                    db.session.add(new_recommendation)
                    db.session.commit()
                    logger.info(f"Stored new recommendations in database for trip_id: {trip_id}")
                
            except Exception as e:
                logger.error(f"Error processing recommendations: {str(e)}")
                logger.error(traceback.format_exc())

    def publish_message(self, queue, message):
        """Publish a message to a RabbitMQ queue."""
        try:
            # Check if we have a valid connection and channel
            if self.connection is None or self.connection.is_closed or self.channel is None or self.channel.is_closed:
                logger.info("Connection is not valid, attempting to reconnect...")
                if not self.connect():
                    logger.error("Failed to connect to RabbitMQ, cannot publish message")
                    return False
            
            # Convert message to JSON if it's a dict
            if isinstance(message, dict):
                message = json.dumps(message)
                
            # Publish message
            self.channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published message to queue: {queue}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing message to RabbitMQ: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def start_consuming(self):
        """Start consuming messages from RabbitMQ."""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info("Starting to consume messages from RabbitMQ")
                
                # Check if we have a valid connection and channel
                if self.connection is None or self.connection.is_closed or self.channel is None or self.channel.is_closed:
                    logger.info("Connection is not valid, attempting to reconnect...")
                    if not self.connect():
                        logger.error("Failed to connect to RabbitMQ, retrying in 5 seconds...")
                        time.sleep(5)
                        retry_count += 1
                        continue
                
                # Start consuming messages
                logger.info("Starting to consume messages")
                self.channel.start_consuming()
                
                logger.info("Message consumption ended")
                
            except pika.exceptions.AMQPConnectionError as e:
                logger.error(f"AMQP connection error: {str(e)}")
                logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)
                retry_count += 1
                
            except pika.exceptions.ChannelClosedByBroker as e:
                logger.error(f"Channel closed by broker: {str(e)}")
                logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)
                retry_count += 1
                
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                logger.error(traceback.format_exc())
                logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)
                retry_count += 1
                
        logger.error(f"Failed to consume messages after {max_retries} retries")

    def close(self):
        """Close the connection to RabbitMQ."""
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("Closed RabbitMQ connection")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {str(e)}")
            logger.error(traceback.format_exc()) 