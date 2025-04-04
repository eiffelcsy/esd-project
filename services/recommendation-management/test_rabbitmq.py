import pika
import json
import os
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
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

def send_test_recommendation_request():
    """Send a test recommendation request to the queue"""
    try:
        connection, channel = connect_to_rabbitmq()
        
        # Declare the request queue
        request_queue = 'recommendation_requests'
        channel.queue_declare(queue=request_queue, durable=True)
        
        # Declare the response queue
        response_queue = 'recommendation_responses'
        channel.queue_declare(queue=response_queue, durable=True)
        
        # Create a test message
        test_message = {
            'trip_id': f'test-{int(time.time())}',
            'destination': 'Paris',
            'start_date': (datetime.now().date()).isoformat(),
            'end_date': (datetime.now().date()).isoformat()
        }
        
        # Publish the message
        channel.basic_publish(
            exchange='',
            routing_key=request_queue,
            body=json.dumps(test_message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )
        
        logger.info(f"Sent test recommendation request: {test_message}")
        
        # Wait for and check response
        logger.info("Waiting for response...")
        
        # Set up a callback function to receive the response
        responses = []
        
        def callback(ch, method, properties, body):
            try:
                response_data = json.loads(body)
                logger.info(f"Received response: {response_data}")
                responses.append(response_data)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
        
        # Consume from the response queue
        channel.basic_consume(
            queue=response_queue,
            on_message_callback=callback,
            auto_ack=False
        )
        
        # Wait for response for up to 30 seconds
        wait_time = 30
        logger.info(f"Waiting for response for {wait_time} seconds...")
        
        # Use consume with a timeout to avoid blocking indefinitely
        for _ in range(wait_time):
            channel.connection.process_data_events(time_limit=1)
            if responses:
                break
            time.sleep(1)
        
        if responses:
            logger.info("Test successful! Received response.")
        else:
            logger.warning("No response received within timeout period.")
        
        # Close the connection
        connection.close()
        
    except Exception as e:
        logger.error(f"Error in test: {e}")

if __name__ == "__main__":
    logger.info("Starting RabbitMQ test...")
    send_test_recommendation_request()
    logger.info("Test completed.") 