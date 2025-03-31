import pika
import json
import sys

# Connect to RabbitMQ
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
        'calendar_id': 1,
        'user_id': 2,  # Different user to verify it works
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
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1) 