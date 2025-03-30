import os
import pika
import json
from typing import Callable, Any

class RabbitMQConfig:
    def __init__(self):
        self.host = os.environ.get('RABBITMQ_HOST', 'localhost')
        self.port = int(os.environ.get('RABBITMQ_PORT', 5672))
        self.user = os.environ.get('RABBITMQ_USER', 'guest')
        self.password = os.environ.get('RABBITMQ_PASS', 'guest')
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection to RabbitMQ"""
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def declare_queue(self, queue_name: str):
        """Declare a queue"""
        self.channel.queue_declare(queue=queue_name, durable=True)

    def publish_message(self, queue_name: str, message: dict):
        """Publish a message to a queue"""
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )

    def consume_messages(self, queue_name: str, callback: Callable[[dict], Any]):
        """Consume messages from a queue"""
        def message_handler(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=message_handler
        )
        self.channel.start_consuming()

# Example usage:
"""
# In your service:
from app.rabbitmq_config import RabbitMQConfig

# Initialize RabbitMQ
rabbitmq = RabbitMQConfig()
rabbitmq.connect()

# Declare a queue
rabbitmq.declare_queue('my_queue')

# Publish a message
rabbitmq.publish_message('my_queue', {'key': 'value'})

# Consume messages
def handle_message(message):
    print(f"Received message: {message}")

rabbitmq.consume_messages('my_queue', handle_message)
""" 