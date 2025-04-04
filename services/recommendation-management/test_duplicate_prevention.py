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

def send_duplicate_recommendation_requests(trip_id=None, destination="Paris", num_requests=3, delay=2):
    """Send multiple identical recommendation requests to test duplicate prevention"""
    try:
        # Connect to RabbitMQ
        connection, channel = connect_to_rabbitmq()
        
        # Declare queues
        recommendation_requests_queue = 'recommendation_requests'
        recommendation_responses_queue = 'recommendation_responses'
        
        channel.queue_declare(queue=recommendation_requests_queue, durable=True)
        channel.queue_declare(queue=recommendation_responses_queue, durable=True)
        
        # Create unique trip ID for the test if not provided
        if not trip_id:
            trip_id = f"test-{uuid.uuid4()}"
        
        # Create test message
        test_message = {
            'trip_id': trip_id,
            'destination': destination,
            'start_date': datetime.now().date().isoformat(),
            'end_date': (datetime.now().date() + timedelta(days=7)).isoformat()
        }
        
        # Send multiple identical requests
        message_body = json.dumps(test_message)
        for i in range(num_requests):
            channel.basic_publish(
                exchange='',
                routing_key=recommendation_requests_queue,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Sent request {i+1}/{num_requests} for trip_id={trip_id}")
            
            # Wait a bit between requests
            if i < num_requests - 1:
                time.sleep(delay)
        
        # Set up to wait for responses
        responses = []
        
        def callback(ch, method, properties, body):
            try:
                response_data = json.loads(body)
                if response_data.get('trip_id') == trip_id:
                    logger.info(f"Received response for trip_id {trip_id}")
                    responses.append(response_data)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    # Skip responses for other trip IDs
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
        
        # Wait for responses
        wait_time = 30
        logger.info(f"Waiting for responses for up to {wait_time} seconds...")
        
        # Use consume with a timeout to avoid blocking indefinitely
        for _ in range(wait_time):
            channel.connection.process_data_events(time_limit=1)
            time.sleep(1)
            # If we got at least one response, stop waiting
            if responses:
                break
        
        # Summary of results
        logger.info(f"Test summary:")
        logger.info(f"  Sent {num_requests} identical requests for trip_id: {trip_id}")
        logger.info(f"  Received {len(responses)} responses")
        
        if len(responses) < num_requests:
            logger.info(f"  Duplicate prevention worked! {num_requests - len(responses)} duplicate requests were filtered out.")
        elif len(responses) == num_requests:
            logger.warning(f"  Duplicate prevention failed! All {num_requests} requests were processed.")
        else:
            logger.error(f"  Unexpected result: More responses ({len(responses)}) than requests ({num_requests})")
        
        # Close the connection
        connection.close()
        logger.info("Connection closed")
        
        return responses
        
    except Exception as e:
        logger.error(f"Error in test: {e}")
        return []

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    trip_id = None
    destination = "Paris"
    num_requests = 3
    delay = 2
    
    if len(sys.argv) > 1:
        trip_id = sys.argv[1]
    if len(sys.argv) > 2:
        destination = sys.argv[2]
    if len(sys.argv) > 3:
        num_requests = int(sys.argv[3])
    if len(sys.argv) > 4:
        delay = int(sys.argv[4])
    
    logger.info(f"Starting duplicate prevention test with {num_requests} requests for trip_id={trip_id or 'auto-generated'}")
    responses = send_duplicate_recommendation_requests(trip_id, destination, num_requests, delay)
    logger.info("Test completed.") 