import os
import logging
import traceback
import threading
import time
from app.message_broker import start_consumer_thread, processed_trip_ids, connect_to_rabbitmq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log environment variables (excluding sensitive info)
logger.info("Environment variables:")
for key, value in os.environ.items():
    if "KEY" not in key.upper() and "SECRET" not in key.upper() and "PASS" not in key.upper():
        logger.info(f"  {key}: {value}")
    else:
        logger.info(f"  {key}: [REDACTED]")

# Function to periodically clear the processed_trip_ids cache
def clear_processed_trip_ids_cache():
    """Clear the processed_trip_ids cache periodically"""
    while True:
        try:
            time.sleep(300)  # 5 minutes
            current_size = len(processed_trip_ids)
            processed_trip_ids.clear()
            logger.info(f"Cleared processed_trip_ids cache (removed {current_size} entries)")
        except Exception as e:
            logger.error(f"Error clearing processed_trip_ids cache: {e}")
            logger.error(traceback.format_exc())

# Check OpenAI API Key
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    logger.error("OPENAI_API_KEY environment variable is not set. Service may not function correctly.")
else:
    logger.info("OPENAI_API_KEY is set")

# Check RabbitMQ configuration
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
logger.info(f"RabbitMQ host is set to: {rabbitmq_host}")

# Purge the recommendation_requests queue at startup
def purge_recommendation_requests_queue():
    """Purge the recommendation_requests queue to avoid processing old messages"""
    try:
        conn, channel = connect_to_rabbitmq()
        queue_name = 'recommendation_requests'
        
        # Declare the queue (this won't delete it)
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Purge the queue
        message_count = channel.queue_purge(queue=queue_name)
        logger.info(f"Purged {message_count} messages from {queue_name} queue")
        
        # Close the connection
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error purging recommendation_requests queue: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Main entry point for the service"""
    logger.info("Starting Recommendation Management Service")
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=clear_processed_trip_ids_cache)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    logger.info("Started cache cleanup thread")
    
    # Purge the recommendation_requests queue
    purge_success = purge_recommendation_requests_queue()
    if purge_success:
        logger.info("Successfully purged recommendation_requests queue")
    else:
        logger.warning("Failed to purge recommendation_requests queue")
    
    # Start RabbitMQ consumer thread
    try:
        # We pass None instead of Flask app since we no longer use Flask
        consumer_thread = start_consumer_thread(None)
        logger.info("RabbitMQ consumer thread started successfully")
        
        # Keep the main thread alive
        while True:
            time.sleep(60)
            logger.debug("Service is running...")
    except Exception as e:
        logger.error(f"Error in main service loop: {e}")
        logger.error(traceback.format_exc())
    except KeyboardInterrupt:
        logger.info("Service shutting down gracefully...")

if __name__ == '__main__':
    main()