#!/usr/bin/env python3
import pika
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import sys

# Get the project root directory (two levels up from this script)
project_root = Path(__file__).parent.parent.parent

# Load environment variables from multiple locations
load_dotenv(project_root / '.env')  # Main .env file
load_dotenv(Path(__file__).parent / '.env.test')  # Test .env file

# RabbitMQ connection settings with better error handling
def get_env_var(key, default=None):
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value

try:
    rabbitmq_host = get_env_var('RABBITMQ_HOST', 'localhost')
    rabbitmq_port = int(get_env_var('RABBITMQ_PORT', '5672'))
    rabbitmq_user = get_env_var('RABBITMQ_USER', 'guest')
    rabbitmq_pass = get_env_var('RABBITMQ_PASS', 'guest')
except ValueError as e:
    print(f"❌ Error: {e}")
    print("Please ensure all required environment variables are set in .env.test")
    sys.exit(1)

# Connect to RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
parameters = pika.ConnectionParameters(
    host=rabbitmq_host,
    port=rabbitmq_port,
    credentials=credentials
)

print(f"Connecting to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}...")
try:
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
except Exception as e:
    print(f"❌ Failed to connect to RabbitMQ: {e}")
    sys.exit(1)

# Ensure the queue exists
channel.queue_declare(queue='recommendation_requests', durable=True)

# Create a test message
today = datetime.now().date()
test_message = {
    'trip_id': f'test-trip-{datetime.now().strftime("%Y%m%d%H%M%S")}',
    'destination': 'Tokyo',
    'start_date': (today + timedelta(days=30)).isoformat(),
    'end_date': (today + timedelta(days=37)).isoformat()
}

# Send the message
try:
    channel.basic_publish(
        exchange='',
        routing_key='recommendation_requests',
        body=json.dumps(test_message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            content_type='application/json'
        )
    )
    print(f"✅ Sent test message to recommendation_requests queue:")
    print(json.dumps(test_message, indent=2))
except Exception as e:
    print(f"❌ Failed to send message: {e}")
finally:
    connection.close() 