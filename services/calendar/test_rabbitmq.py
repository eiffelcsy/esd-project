"""
Utility script to test the RabbitMQ integration with the calendar service.
This script sends a test message to the RabbitMQ queue that the calendar service consumes.

Usage: python test_rabbitmq.py
"""

import pika
import json
import sys

def send_test_message(calendar_id=1, user_id=2):
    """
    Send a test message to the RabbitMQ queue.
    
    Args:
        calendar_id (int): The ID of the calendar to update
        user_id (int): The ID of the user whose availability to update
    """
    try:
        print("Connecting to RabbitMQ...")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5673,  # Modified port for host machine
                connection_attempts=3,
                retry_delay=2
            )
        )
        channel = connection.channel()
        print("Connected to RabbitMQ!")

        # Declare the queue
        channel.queue_declare(queue='user_availability')
        print("Queue declared: user_availability")

        # Prepare the message
        message = {
            'calendar_id': calendar_id,
            'user_id': user_id,
            'available_dates': [
                '2024-04-03T10:00:00',
                '2024-04-04T14:00:00',
                '2024-04-05T09:00:00'
            ]
        }

        # Publish the message
        channel.basic_publish(
            exchange='',
            routing_key='user_availability',
            body=json.dumps(message)
        )

        print(f"📤 Sent message: {message}")

        # Close the connection
        connection.close()
        print("Connection closed")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = send_test_message()
    sys.exit(0 if success else 1) 