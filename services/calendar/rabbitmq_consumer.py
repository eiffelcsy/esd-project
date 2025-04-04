import os
import json
import time
import pika
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import UserAvailability, Calendar  # Import models from app.py

# Database connection
database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@calendar-db:5432/calendar_db')
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)

def process_message(ch, method, properties, body):
    """Process a message from RabbitMQ"""
    try:
        # Create a new session for this message
        session = Session()
        
        data = json.loads(body)
        print(f"📬 Received message: {data}")
        
        calendar_id = data.get('calendar_id')
        user_id = data.get('user_id')
        available_dates = data.get('available_dates', [])

        # Update or create user availability
        availability = session.query(UserAvailability).filter_by(
            calendar_id=calendar_id,
            user_id=user_id
        ).first()

        if availability:
            availability.available_dates = available_dates
        else:
            availability = UserAvailability(
                calendar_id=calendar_id,
                user_id=user_id,
                available_dates=available_dates
            )
            session.add(availability)

        session.commit()
        print(f"✅ Updated availability for user {user_id} in calendar {calendar_id}")
        
    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")
        if 'session' in locals():
            session.rollback()
    finally:
        if 'session' in locals():
            session.close()

def connect_to_rabbitmq():
    """Connect to RabbitMQ and return connection and channel"""
    # Get RabbitMQ connection details
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    
    print(f"🔄 Connecting to RabbitMQ at {rabbitmq_host}...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host,
            port=5672,
            connection_attempts=5,
            retry_delay=5
        )
    )
    
    channel = connection.channel()
    print(f"✅ Connected to RabbitMQ at {rabbitmq_host}")
    return connection, channel

def main():
    """Main consumer function"""
    # Connection retry loop
    while True:
        try:
            connection, channel = connect_to_rabbitmq()
            
            # Declare queue
            channel.queue_declare(queue='user_availability')
            print("✅ Declared queue: user_availability")
            
            # Set up consumer
            channel.basic_consume(
                queue='user_availability',
                on_message_callback=process_message,
                auto_ack=True
            )
            
            print("🐰 Started consuming from RabbitMQ...")
            channel.start_consuming()
            
        except Exception as e:
            print(f"❌ Connection to RabbitMQ failed: {str(e)}")
            print("⏳ Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    # Allow some time for the Flask app to initialize the DB if needed
    time.sleep(10)
    main() 