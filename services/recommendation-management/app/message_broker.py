import pika
import json
import os
import logging
import time
import traceback
from datetime import datetime, timedelta
from app.openai_service import get_recommendations
from app.models import db, Recommendation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory cache to track recently processed trip_ids to avoid duplicate processing
# Format: {trip_id: timestamp}
processed_trip_ids = {}
CACHE_EXPIRY_SECONDS = 300  # 5 minutes

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

def process_recommendation_request(ch, method, properties, body, app=None):
    """Process incoming recommendation requests"""
    try:
        logger.info(f"Received recommendation request: {body}")
        
        # Parse the request
        try:
            data = json.loads(body)
            logger.info(f"Successfully parsed recommendation request data: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse recommendation request JSON: {e}")
            logger.error(f"Request body: {body}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Extract trip details
        try:
            trip_id = data.get('trip_id')
            destination = data.get('destination')
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            
            # Validate required fields
            if not all([trip_id, destination, start_date_str, end_date_str]):
                missing_fields = []
                if not trip_id: missing_fields.append('trip_id')
                if not destination: missing_fields.append('destination')
                if not start_date_str: missing_fields.append('start_date')
                if not end_date_str: missing_fields.append('end_date')
                
                logger.error(f"Missing required fields in recommendation request: {', '.join(missing_fields)}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Check in-memory cache for recently processed trip_id to avoid duplicate processing
            current_time = datetime.utcnow()
            if trip_id in processed_trip_ids:
                last_processed = processed_trip_ids[trip_id]
                time_diff = current_time - last_processed
                if time_diff.total_seconds() < CACHE_EXPIRY_SECONDS:
                    logger.info(f"Skipping duplicate request for trip_id={trip_id} - processed {time_diff.total_seconds():.2f} seconds ago")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
            
            # Update the in-memory cache
            processed_trip_ids[trip_id] = current_time
            
            # Clean up old entries from the cache
            expired_trip_ids = [t_id for t_id, timestamp in processed_trip_ids.items() 
                              if (current_time - timestamp).total_seconds() > CACHE_EXPIRY_SECONDS]
            for expired_id in expired_trip_ids:
                del processed_trip_ids[expired_id]
            
            # Convert string dates to date objects
            start_date = datetime.fromisoformat(start_date_str).date()
            end_date = datetime.fromisoformat(end_date_str).date()
            
            logger.info(f"Processing recommendation request for trip_id={trip_id}, destination={destination}")
        except Exception as e:
            logger.error(f"Error extracting trip details from request: {e}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Check if recommendation already exists in the database
        existing_recommendation = None
        recommendations = None
        
        if app:
            try:
                with app.app_context():
                    existing_recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
                    if existing_recommendation and existing_recommendation.recommendations:
                        logger.info(f"Found existing recommendations in database for trip_id={trip_id}")
                        recommendations = existing_recommendation.recommendations
            except Exception as e:
                logger.error(f"Error checking existing recommendations: {e}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
        
        # Only call OpenAI if we don't already have recommendations
        if not recommendations:
            try:
                logger.info(f"Calling OpenAI service for recommendations for trip_id={trip_id}")
                recommendations = get_recommendations(destination, start_date, end_date)
                logger.info(f"Received recommendations from OpenAI for trip_id={trip_id}: {json.dumps(recommendations)[:200]}...")
            except Exception as e:
                logger.error(f"Error getting recommendations from OpenAI: {e}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        else:
            logger.info(f"Using existing recommendations for trip_id={trip_id} instead of calling OpenAI again")
        
        # Save to database (within app context)
        if app:
            try:
                with app.app_context():
                    if existing_recommendation:
                        # Update existing record
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
                        logger.info(f"Saved new recommendation for trip_id: {trip_id}")
            except Exception as e:
                logger.error(f"Error saving recommendation to database: {e}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        else:
            logger.error("No Flask app context provided, cannot save to database")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Acknowledge the message first
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
        # Prepare response - include all original data plus recommendations
        try:
            response = {
                'trip_id': trip_id,
                'destination': destination,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'recommendations': recommendations,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Preparing to send response for trip_id: {trip_id}")
            
            # Send the response with a separate connection
            response_connection, response_channel = connect_to_rabbitmq()
            
            # Ensure the response queue exists
            response_queue = 'recommendation_responses'
            response_channel.queue_declare(queue=response_queue, durable=True)
            
            # Publish the response
            response_channel.basic_publish(
                exchange='',
                routing_key=response_queue,
                body=json.dumps(response),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Sent recommendation response for trip_id: {trip_id}")
            
            # Close the connection
            response_connection.close()
        except Exception as e:
            logger.error(f"Error sending recommendation response: {e}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            
    except Exception as e:
        logger.error(f"Unhandled error processing recommendation request: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        # Acknowledge the message even on error to avoid queue blockage
        try:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            pass

def setup_rabbitmq_consumer(app):
    """Set up RabbitMQ consumer for recommendation requests"""
    def callback_wrapper(ch, method, properties, body):
        process_recommendation_request(ch, method, properties, body, app)
    
    # Connection retry loop
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
        connection = None
        channel = None
        try:
            logger.info(f"Attempting to connect to RabbitMQ (attempt {retry_count + 1}/{max_retries})")
            connection, channel = connect_to_rabbitmq()
            
            # Declare queues with more explicit naming
            request_queue = 'recommendation_requests'
            channel.queue_declare(queue=request_queue, durable=True)
            
            # Also declare the response queue to ensure it exists
            response_queue = 'recommendation_responses'
            channel.queue_declare(queue=response_queue, durable=True)
            
            logger.info(f"Declared queues: {request_queue}, {response_queue}")
            
            # Set QoS to avoid overwhelming the consumer
            channel.basic_qos(prefetch_count=1)
            
            # Set up consumer
            channel.basic_consume(
                queue=request_queue,
                on_message_callback=callback_wrapper,
                auto_ack=False
            )
            
            logger.info(f"Started consuming from RabbitMQ queue: {request_queue}")
            
            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                logger.info("Interrupted by user, shutting down...")
                channel.stop_consuming()
                connection.close()
                break
            except Exception as e:
                logger.error(f"Error during message consumption: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                # Try to close the connection and retry
                try:
                    channel.stop_consuming()
                except Exception:
                    pass
                try:
                    connection.close()
                except Exception:
                    pass
                
                logger.info("Retrying in 10 seconds...")
                time.sleep(10)
                retry_count += 1
                continue
                
        except Exception as e:
            logger.error(f"Connection to RabbitMQ failed: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            retry_count += 1
            
            # Try to close any open connection
            try:
                if channel and channel.is_open:
                    channel.close()
            except Exception:
                pass
            try:
                if connection and connection.is_open:
                    connection.close()
            except Exception:
                pass
            
            if retry_count >= max_retries:
                logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts. Will keep trying in the background.")
                # Reset retry count to keep trying indefinitely, but with a longer delay
                retry_count = 0
                time.sleep(30)
            else:
                logger.info(f"Retrying in 10 seconds... (attempt {retry_count}/{max_retries})")
                time.sleep(10)

def start_consumer_thread(app):
    """Start RabbitMQ consumer in a separate thread"""
    import threading
    consumer_thread = threading.Thread(target=setup_rabbitmq_consumer, args=(app,))
    consumer_thread.daemon = True
    consumer_thread.start()
    logger.info("Started RabbitMQ consumer thread")
    
    # Declare and test the queues immediately to verify connection
    try:
        conn, channel = connect_to_rabbitmq()
        # Declare both queues
        channel.queue_declare(queue='recommendation_requests', durable=True)
        channel.queue_declare(queue='recommendation_responses', durable=True)
        logger.info("Successfully verified RabbitMQ queues")
        conn.close()
    except Exception as e:
        logger.error(f"Failed to verify RabbitMQ queues: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
    
    return consumer_thread