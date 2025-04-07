import os
import json
import pika
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageBroker:
    """
    Handles RabbitMQ message publishing for the group-management service.
    """
    
    @staticmethod
    def publish_message(queue_name, message_data):
        """
        Publishes a message to the specified RabbitMQ queue.
        
        Args:
            queue_name (str): Name of the queue to publish to
            message_data (dict): Data to be published
            
        Returns:
            bool: True if successful, False otherwise
        """
        rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        
        try:
            # Establish connection
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbitmq_host,
                    port=5672,
                    connection_attempts=5,
                    retry_delay=5
                )
            )
            channel = connection.channel()
            
            # Declare queue (creates if doesn't exist)
            channel.queue_declare(queue=queue_name, durable=True)
            
            # Publish message
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"✅ Published message to {queue_name}: {message_data}")
            connection.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish message to RabbitMQ: {str(e)}")
            return False

    @staticmethod
    def publish_user_availability(calendar_id, user_id, available_dates):
        """
        Publishes a user availability update to the calendar service.
        
        Args:
            calendar_id (int): ID of the calendar
            user_id (int): ID of the user
            available_dates (list): List of available date strings
            
        Returns:
            bool: True if successful, False otherwise
        """
        message = {
            'calendar_id': calendar_id,
            'user_id': user_id,
            'available_dates': available_dates
        }
        
        return MessageBroker.publish_message('user_availability', message) 