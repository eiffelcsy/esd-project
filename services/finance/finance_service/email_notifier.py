import pika
import json
import os

class EmailNotifier:
    def __init__(self):
        # Obtain environment variables
        self.amqp_url = os.getenv('AMQP_URL')
        self.queue_name = os.getenv('NOTIFICATION_QUEUE')

    def send_notification(self, user_email: str, trip_id: str, amount: float):
        connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url)) # Create physical network to the broker
        channel = connection.channel() # Create a virtual lightweight connection to the broker for microservice
        
        channel.queue_declare(queue=self.queue_name, durable=True) # Declare a queue called 'expense_notifications'
        
        message = {
            'email': user_email,
            'subject': f'Payment due for trip {trip_id}',
            'body': f'Your total expenses for trip {trip_id} amount to {amount:.2f} USD.'
        }
        
        channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        ) # Publish a message to the queue
        
        connection.close()