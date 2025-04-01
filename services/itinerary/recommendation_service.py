# RECOMMENDATION MANAGEMENT SERVICE
# recommendation_service.py
from flask import Flask, request, jsonify
import requests
import json
import pika
import uuid

app = Flask(__name__)

# In-memory storage for recommendations
recommendations_store = {}

def get_rabbitmq_connection():
    """Establish connection to RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='recommendations')
    return connection, channel

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Request recommendations from external AI API."""
    trip_data = request.json
    
    try:
        # Call external AI API for attractions
        response = requests.post(
            "https://external-ai-api.example.com/recommendations",
            json={
                "city": trip_data['destination'],
                "dates": {
                    "start": trip_data['startDate'],
                    "end": trip_data['endDate']
                }
            }
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to get recommendations from AI service"}), 500
        
        ai_recommendations = response.json()
        
        # Format recommendations for our system
        formatted_recommendations = {
            "tripId": trip_data['tripId'],
            "destination": trip_data['destination'],
            "recommendations": []
        }
        
        for rec in ai_recommendations['attractions']:
            formatted_recommendations['recommendations'].append({
                "id": str(uuid.uuid4()),
                "name": rec['name'],
                "type": rec['type'],
                "description": rec['description'],
                "location": rec['address'],
                "suggestedDuration": rec.get('suggestedDuration', '2 hours'),
                "rating": rec.get('rating', 0)
            })
        
        # Store recommendations
        recommendations_store[trip_data['tripId']] = formatted_recommendations
        
        # Send recommendations to Message Broker
        connection, channel = get_rabbitmq_connection()
        
        channel.basic_publish(
            exchange='',
            routing_key='recommendations',
            body=json.dumps(formatted_recommendations)
        )
        
        connection.close()
        
        return jsonify({"message": "Recommendations processed successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to process recommendations: {str(e)}"}), 500

@app.route('/recommendations/<trip_id>', methods=['GET'])
def retrieve_recommendations(trip_id):
    """Retrieve recommendations for a specific trip."""
    if trip_id not in recommendations_store:
        return jsonify({"error": "No recommendations found for this trip"}), 404
    
    return jsonify(recommendations_store[trip_id]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)