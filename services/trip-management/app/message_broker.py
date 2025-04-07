import pika
import json
import os
import logging
import time
import traceback
import threading
from datetime import datetime
from app.models import db, Recommendation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_rabbitmq():
    """Connect to RabbitMQ and return connection and channel"""
    # Get RabbitMQ connection details
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    
    logger.info(f"Connecting to RabbitMQ at {rabbitmq_host}...")
    
    # Add connection parameters with increased heartbeat and timeout
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host,
            port=5672,
            connection_attempts=5,
            retry_delay=5,
            heartbeat=600,  # Set heartbeat to 10 minutes
            blocked_connection_timeout=300,  # Set blocked connection timeout
            socket_timeout=10.0  # Add socket timeout
        )
    )
    
    channel = connection.channel()
    logger.info(f"Connected to RabbitMQ at {rabbitmq_host}")
    return connection, channel

def process_recommendation_response(ch, method, properties, body, app=None):
    """Process incoming recommendation responses"""
    try:
        logger.info(f"Received recommendation response: {body[:200]}...")
        
        # Parse the response
        try:
            data = json.loads(body)
            logger.info(f"Successfully parsed recommendation response data for trip_id: {data.get('trip_id')}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse recommendation response JSON: {e}")
            logger.error(f"Response body: {body}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Extract recommendation details
        try:
            trip_id = data.get('trip_id')
            recommendations = data.get('recommendations')
            
            # Validate required fields
            if not all([trip_id, recommendations]):
                missing_fields = []
                if not trip_id: missing_fields.append('trip_id')
                if not recommendations: missing_fields.append('recommendations')
                
                logger.error(f"Missing required fields in recommendation response: {', '.join(missing_fields)}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            logger.info(f"Processing recommendation response for trip_id={trip_id}")
        except Exception as e:
            logger.error(f"Error extracting recommendation details from response: {e}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Save to database (within app context)
        if app:
            try:
                with app.app_context():
                    # Check if recommendation already exists for this trip
                    existing_recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
                    
                    if existing_recommendation:
                        # Update existing recommendation
                        existing_recommendation.recommendations = recommendations
                        existing_recommendation.updated_at = datetime.utcnow()
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
                        logger.info(f"Created new recommendation for trip_id: {trip_id}")
            except Exception as e:
                logger.error(f"Error saving recommendation to database: {e}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        else:
            logger.error("No Flask app context provided, cannot save to database")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"Unhandled error processing recommendation response: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        # Acknowledge the message even on error to avoid queue blockage
        try:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            pass

def setup_rabbitmq_consumer(app):
    """Set up RabbitMQ consumer for recommendation responses"""
    def callback_wrapper(ch, method, properties, body):
        process_recommendation_response(ch, method, properties, body, app)
    
    # Connection retry loop
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
        connection = None
        channel = None
        try:
            logger.info(f"Attempting to connect to RabbitMQ (attempt {retry_count + 1}/{max_retries})")
            connection, channel = connect_to_rabbitmq()
            
            # Declare the response queue
            response_queue = 'recommendation_responses'
            channel.queue_declare(queue=response_queue, durable=True)
            
            logger.info(f"Declared queue: {response_queue}")
            
            # Set QoS to avoid overwhelming the consumer
            channel.basic_qos(prefetch_count=1)
            
            # Set up consumer
            channel.basic_consume(
                queue=response_queue,
                on_message_callback=callback_wrapper,
                auto_ack=False
            )
            
            logger.info(f"Consumer registered for queue: {response_queue}")
            logger.info("Waiting for recommendation responses. To exit press CTRL+C")
            
            # Start consuming
            channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Error in RabbitMQ consumer: {e}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            
            # Increment retry count
            retry_count += 1
            
            # Wait before retrying
            if retry_count < max_retries:
                retry_delay = min(30, 2 ** retry_count)  # Exponential backoff, max 30 seconds
                logger.info(f"Retrying connection in {retry_delay} seconds...")
                time.sleep(retry_delay)
            
            # Close any open connection
            if connection and connection.is_open:
                try:
                    connection.close()
                except Exception:
                    pass
        
        # If we reach here, we either had an error or the connection was closed
        if retry_count >= max_retries:
            logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts")
            break

def start_consumer_thread(app):
    """Start a thread to consume recommendation responses"""
    
    # RabbitMQ consumer thread
    consumer_thread = threading.Thread(target=setup_rabbitmq_consumer, args=(app,))
    consumer_thread.daemon = True
    consumer_thread.start()
    
    return consumer_thread

def publish_recommendation_request(trip_id, destination, start_date, end_date):
    """Publish a recommendation request to RabbitMQ"""
    try:
        # Format dates as strings if they are date objects
        if not isinstance(start_date, str):
            start_date = start_date.isoformat()
        if not isinstance(end_date, str):
            end_date = end_date.isoformat()
            
        # Prepare request data
        request_data = {
            'trip_id': trip_id,
            'destination': destination,
            'start_date': start_date,
            'end_date': end_date,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Connect to RabbitMQ
        connection, channel = connect_to_rabbitmq()
        
        # Declare the request queue
        request_queue = 'recommendation_requests'
        channel.queue_declare(queue=request_queue, durable=True)
        
        # Publish the request
        channel.basic_publish(
            exchange='',
            routing_key=request_queue,
            body=json.dumps(request_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json',
                headers={'source': 'trip-service'}
            )
        )
        
        logger.info(f"Published recommendation request for trip_id: {trip_id}")
        
        # Close the connection
        connection.close()
        
        return True
    except Exception as e:
        logger.error(f"Error publishing recommendation request: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return False 