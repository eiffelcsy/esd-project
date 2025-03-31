import pika
import json
import os
from functools import partial

class MessageBroker:
    def __init__(self, app):
        self.app = app
        self.connection = None
        self.channel = None
        self.trip_queue = 'trip_queue'
        self.recommendation_queue = 'recommendation_queue'

    def connect(self):
        try:
            # Get RabbitMQ URL from environment or use default
            rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
            
            # Create a connection parameters object
            parameters = pika.URLParameters(rabbitmq_url)
            
            # Create a connection
            self.connection = pika.BlockingConnection(parameters)
            
            # Create a channel
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue=self.trip_queue, durable=True)
            self.channel.queue_declare(queue=self.recommendation_queue, durable=True)
            
            # Set up consumer for trip queue
            self.channel.basic_consume(
                queue=self.trip_queue,
                on_message_callback=self._process_trip_message,
                auto_ack=True
            )
            
            print("Connected to RabbitMQ successfully")
            
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {str(e)}")
            raise

    def _process_trip_message(self, ch, method, properties, body):
        with self.app.app_context():
            try:
                message = json.loads(body)
                # Process trip creation message
                from app.routes import create_trip
                create_trip(message)
            except Exception as e:
                print(f"Error processing message: {str(e)}")

    def send_recommendation_request(self, trip_data):
        try:
            message = {
                'trip_id': trip_data['id'],
                'city': trip_data['city'],
                'start_date': trip_data['start_date'],
                'end_date': trip_data['end_date']
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key=self.recommendation_queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2  # make message persistent
                )
            )
            print(f"Sent recommendation request for trip {trip_data['id']}")
            
        except Exception as e:
            print(f"Error sending recommendation request: {str(e)}")
            raise

    def start_consuming(self):
        print("Starting to consume messages...")
        self.channel.start_consuming()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close() 