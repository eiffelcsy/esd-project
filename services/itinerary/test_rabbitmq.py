import pika
import json
import os
import logging
import time
import uuid
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
    rabbitmq_port = os.getenv('RABBITMQ_PORT', '5672')
    rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
    rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')
    
    rabbitmq_url = os.getenv('RABBITMQ_URL', f'amqp://{rabbitmq_user}:{rabbitmq_pass}@{rabbitmq_host}:{rabbitmq_port}/')
    
    logger.info(f"Connecting to RabbitMQ with URL: {rabbitmq_url.replace(rabbitmq_pass, '******')}")
    
    # Create connection parameters
    parameters = pika.URLParameters(rabbitmq_url)
    parameters.heartbeat = 600
    parameters.blocked_connection_timeout = 300
    parameters.connection_attempts = 3
    parameters.retry_delay = 5
    parameters.socket_timeout = 10.0
    
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    logger.info(f"Connected to RabbitMQ at {rabbitmq_host}")
    return connection, channel

def send_test_recommendation_request():
    """Send a test recommendation request to the queue and wait for response"""
    try:
        # Connect to RabbitMQ
        connection, channel = connect_to_rabbitmq()
        
        # Declare queues
        recommendation_requests_queue = 'recommendation_requests'
        recommendation_responses_queue = 'recommendation_responses'
        
        channel.queue_declare(queue=recommendation_requests_queue, durable=True)
        channel.queue_declare(queue=recommendation_responses_queue, durable=True)
        
        # Create unique trip ID for the test
        trip_id = f"test-{uuid.uuid4()}"
        
        # Create test message
        test_message = {
            'trip_id': trip_id,
            'destination': 'Paris',
            'start_date': datetime.now().date().isoformat(),
            'end_date': (datetime.now().date() + timedelta(days=7)).isoformat()
        }
        
        # Publish the message
        message_body = json.dumps(test_message)
        channel.basic_publish(
            exchange='',
            routing_key=recommendation_requests_queue,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )
        
        logger.info(f"Sent test recommendation request: {test_message}")
        
        # Set up to wait for response
        responses = []
        
        def callback(ch, method, properties, body):
            try:
                response_data = json.loads(body)
                if response_data.get('trip_id') == trip_id:
                    logger.info(f"Received response for trip_id {trip_id}: {response_data}")
                    responses.append(response_data)
                else:
                    logger.info(f"Received response for different trip_id: {response_data.get('trip_id')}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
        
        # Consume from the response queue
        channel.basic_consume(
            queue=recommendation_responses_queue,
            on_message_callback=callback,
            auto_ack=False
        )
        
        # Wait for response for up to 60 seconds
        wait_time = 60
        logger.info(f"Waiting for response for up to {wait_time} seconds...")
        
        # Use consume with a timeout to avoid blocking indefinitely
        for _ in range(wait_time):
            channel.connection.process_data_events(time_limit=1)
            if responses:
                break
            time.sleep(1)
        
        if responses:
            logger.info("Test successful! Received response:")
            logger.info(json.dumps(responses[0], indent=2))
        else:
            logger.warning("No response received within timeout period.")
            logger.warning("This could mean:")
            logger.warning("1. The recommendation service is not running")
            logger.warning("2. The RabbitMQ connection is not working properly")
            logger.warning("3. The recommendation service is not processing requests")
            logger.warning("4. The recommendation service is not sending responses")
        
        # Close the connection
        connection.close()
        logger.info("Connection closed")
        
    except Exception as e:
        logger.error(f"Error in test: {e}")

if __name__ == "__main__":
    logger.info("Starting RabbitMQ test from itinerary service...")
    send_test_recommendation_request()
    logger.info("Test completed.") 