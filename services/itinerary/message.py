# message_broker.py
import pika
import json
import requests

def process_trip_details(ch, method, properties, body):
    """Process new trip details and request recommendations."""
    try:
        trip_data = json.loads(body)
        response = requests.post("http://recommendation-management:5003/recommendations", json=trip_data)
        if response.status_code == 200:
            print(f"Successfully requested recommendations for trip {trip_data['tripId']}")
        else:
            print(f"Failed to request recommendations: {response.text}")
    except Exception as e:
        print(f"Error processing trip details: {str(e)}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def process_recommendations(ch, method, properties, body):
    """Forward recommendations to the User Interface."""
    try:
        recommendations = json.loads(body)
        response = requests.post("http://user-interface:5000/recommendations", json=recommendations)
        if response.status_code == 200:
            print(f"Successfully forwarded recommendations for trip {recommendations['tripId']}")
        else:
            print(f"Failed to forward recommendations: {response.text}")
    except Exception as e:
        print(f"Error forwarding recommendations: {str(e)}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_broker():
    """Start the message broker service."""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='trip_details', durable=True)
    channel.queue_declare(queue='recommendations', durable=True)
    channel.basic_consume(queue='trip_details', on_message_callback=process_trip_details)
    channel.basic_consume(queue='recommendations', on_message_callback=process_recommendations)
    print("Message Broker is running. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    start_broker()