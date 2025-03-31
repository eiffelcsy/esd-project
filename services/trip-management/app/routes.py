from flask import jsonify, request
from datetime import datetime
import requests
from app.models import db, Trip

def register_routes(app, message_broker):
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "service": "trip-management"}), 200

    # Create a new trip via HTTP
    @app.route('/trips', methods=['POST'])
    def http_create_trip():
        return create_trip(request.json)

    # Get trip details
    @app.route('/trips/<int:trip_id>', methods=['GET'])
    def get_trip(trip_id):
        trip = Trip.query.get_or_404(trip_id)
        return jsonify(trip.to_dict()), 200

    # Get all trips for a user
    @app.route('/users/<int:user_id>/trips', methods=['GET'])
    def get_user_trips(user_id):
        trips = Trip.query.filter_by(user_id=user_id).all()
        return jsonify([trip.to_dict() for trip in trips]), 200

    # Update trip itinerary
    @app.route('/trips/<int:trip_id>/itinerary', methods=['PUT'])
    def update_trip_itinerary(trip_id):
        trip = Trip.query.get_or_404(trip_id)
        data = request.json
        
        # Update itinerary in the itinerary service
        itinerary_service_url = f"http://itinerary:5000/itineraries/{trip.itinerary_id}"
        response = requests.put(itinerary_service_url, json=data)
        
        if response.status_code == 200:
            return jsonify({"message": "Itinerary updated successfully"}), 200
        return jsonify({"error": "Failed to update itinerary"}), response.status_code

def create_trip(data):
    try:
        # Validate required fields
        required_fields = ['user_id', 'city', 'start_date', 'end_date']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Parse dates
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))

        # Create trip in database
        trip = Trip(
            user_id=data['user_id'],
            city=data['city'],
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(trip)
        db.session.commit()

        # Create itinerary
        itinerary_service_url = "http://itinerary:5000/itineraries"
        itinerary_data = {
            "trip_id": trip.id,
            "start_date": data['start_date'],
            "end_date": data['end_date']
        }
        response = requests.post(itinerary_service_url, json=itinerary_data)
        
        if response.status_code == 201:
            # Update trip with itinerary ID
            trip.itinerary_id = response.json()['id']
            db.session.commit()

            # Send recommendation request via RabbitMQ
            from app import message_broker
            message_broker.send_recommendation_request(trip.to_dict())

            return jsonify(trip.to_dict()), 201
        else:
            # Rollback if itinerary creation failed
            db.session.delete(trip)
            db.session.commit()
            return jsonify({"error": "Failed to create itinerary"}), response.status_code

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500 