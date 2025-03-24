#!/usr/bin/env python3
import pika
import json
import os
import signal
import sys
import time
from dotenv import load_dotenv
from pathlib import Path

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

# Define callback function
def callback(ch, method, properties, body):
    try:
        response = json.loads(body)
        print("\n✅ Received recommendation response:")
        print(f"Trip ID: {response.get('trip_id')}")
        print(f"Destination: {response.get('destination')}")
        print(f"Date Range: {response.get('start_date')} to {response.get('end_date')}")
        
        # Pretty print the recommendations
        if 'recommendations' in response:
            print("\n📋 Recommendations:")
            recommendations = response['recommendations']
            
            if 'attractions' in recommendations:
                print("\n🏛️  Top Attractions:")
                for attraction in recommendations['attractions']:
                    print(f"- {attraction.get('name')}: {attraction.get('description')}")
            
            if 'restaurants' in recommendations:
                print("\n🍽️  Restaurants:")
                for restaurant in recommendations['restaurants']:
                    print(f"- {restaurant.get('name')} ({restaurant.get('cuisine')}, {restaurant.get('price_range')})")
            
            if 'activities' in recommendations:
                print("\n🎭 Activities:")
                for activity in recommendations['activities']:
                    print(f"- {activity.get('name')}: {activity.get('description')}")
            
            if 'tips' in recommendations:
                print("\n💡 Tips:")
                for tip in recommendations['tips']:
                    print(f"- {tip}")
        
        print("\nTimestamp:", response.get('timestamp'))
        print("-" * 80)
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON: {body}")
    except Exception as e:
        print(f"❌ Error processing message: {e}")
    
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Handle graceful shutdown
def signal_handler(sig, frame):
    print('\n⏹️  Stopping consumer...')
    try:
        if channel and channel.is_open:
            channel.stop_consuming()
        if connection and connection.is_open:
            connection.close()
    except Exception as e:
        print(f"Error during shutdown: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Setup connection with reconnection logic
def connect_to_rabbitmq():
    max_retries = 5
    retry_delay = 3  # seconds
    
    for attempt in range(max_retries):
        try:
            print(f"Connecting to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}...")
            credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
            parameters = pika.ConnectionParameters(
                host=rabbitmq_host,
                port=rabbitmq_port,
                credentials=credentials,
                heartbeat=600,  # Higher heartbeat for better stability
                blocked_connection_timeout=300
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # Ensure the queue exists
            channel.queue_declare(queue='recommendation_responses', durable=True)
            
            print('🔍 Waiting for recommendation responses. Press CTRL+C to exit')
            return connection, channel
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"❌ Failed to connect to RabbitMQ: {e}")
                print(f"Retrying in {retry_delay} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"❌ Failed to connect to RabbitMQ after {max_retries} attempts: {e}")
                print("Please check your RabbitMQ service and connection settings.")
                sys.exit(1)

# Start consuming with reconnection logic
def start_consuming():
    global connection, channel
    
    # Initial connection
    connection, channel = connect_to_rabbitmq()
    
    # Set up consumer with prefetch count to avoid overwhelming the consumer
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='recommendation_responses',
        on_message_callback=callback,
        auto_ack=False
    )
    
    # Start consuming loop with reconnection logic
    while True:
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ Connection to RabbitMQ lost: {e}")
            print("Attempting to reconnect...")
            
            try:
                # Clean up previous connection
                if connection and connection.is_open:
                    connection.close()
                
                # Reconnect
                connection, channel = connect_to_rabbitmq()
                
                # Re-establish consumer
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue='recommendation_responses',
                    on_message_callback=callback,
                    auto_ack=False
                )
            except Exception as e:
                print(f"❌ Failed to reconnect: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

# Initialize global variables
connection = None
channel = None

# Start the consumer
if __name__ == "__main__":
    try:
        start_consuming()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None) 