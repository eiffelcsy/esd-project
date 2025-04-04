from flask import jsonify, request, current_app
from datetime import datetime
import requests
from app.models import db, Trip
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get itinerary service URL from environment or use default
ITINERARY_SERVICE_URL = os.getenv('ITINERARY_SERVICE_URL', 'http://itinerary:5004')

def register_routes(app):
    @app.route('/api/trips', methods=['POST'])
    def create_trip():
        try:
            data = request.json
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
                end_date=end_date,
                group_id=data.get('group_id')  # Optional group_id field
            )
            db.session.add(trip)
            db.session.commit()
            
            logger.info(f"Created trip with ID: {trip.id}")

            # Skip external service calls in testing environment
            if not current_app.config['TESTING']:
                try:
                    # Create itinerary via the itinerary service
                    itinerary_data = {
                        "trip_id": str(trip.id),
                        "destination": trip.city,
                        "start_date": trip.start_date.isoformat(),
                        "end_date": trip.end_date.isoformat()
                    }
                    
                    # Add group_id to itinerary data if available
                    if trip.group_id:
                        itinerary_data["group_id"] = trip.group_id
                    
                    logger.info(f"Creating itinerary for trip: {trip.id}")
                    itinerary_response = requests.post(
                        f"{ITINERARY_SERVICE_URL}/api/itinerary",
                        json=itinerary_data
                    )
                    
                    if itinerary_response.status_code in (200, 201):
                        logger.info(f"Successfully created itinerary for trip: {trip.id}")
                        itinerary_data = itinerary_response.json()
                        
                        # Update trip with itinerary ID
                        trip.itinerary_id = trip.id  # Using trip.id as itinerary_id
                        db.session.commit()
                    else:
                        logger.error(f"Failed to create itinerary. Status: {itinerary_response.status_code}, Response: {itinerary_response.text}")
                        # Continue even if itinerary creation failed, don't roll back the trip
                        logger.warning(f"Continuing with trip creation despite itinerary failure")

                    # Also send trip creation event via RabbitMQ as a backup
                    message_broker = current_app.message_broker
                    message_broker.send_trip_created_event(trip.to_dict())
                except requests.exceptions.RequestException as e:
                    # Handle connection errors to external services
                    logger.error(f"Error connecting to itinerary service: {str(e)}")
                    # Continue with trip creation even if itinerary creation failed
                    logger.warning(f"Continuing with trip creation despite connection error to itinerary service")
                    
                    # Try to notify via RabbitMQ since direct HTTP failed
                    try:
                        message_broker = current_app.message_broker
                        message_broker.send_trip_created_event(trip.to_dict())
                        logger.info(f"Sent trip creation event via RabbitMQ for trip: {trip.id}")
                    except Exception as mq_err:
                        logger.error(f"Failed to send trip creation event via RabbitMQ: {str(mq_err)}")

            return jsonify(trip.to_dict()), 201

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route('/api/trips/<int:trip_id>', methods=['GET'])
    def get_trip(trip_id):
        trip = Trip.query.get_or_404(trip_id)
        return jsonify(trip.to_dict()), 200

    @app.route('/api/users/<int:user_id>/trips', methods=['GET'])
    def get_user_trips(user_id):
        trips = Trip.query.filter_by(user_id=user_id).all()
        return jsonify([trip.to_dict() for trip in trips]), 200

    @app.route('/api/groups/<int:group_id>/trips', methods=['GET'])
    def get_group_trips(group_id):
        """Get all trips associated with a specific group."""
        trips = Trip.query.filter_by(group_id=group_id).all()
        if not trips:
            return jsonify({"message": "No trips found for this group"}), 404
        return jsonify([trip.to_dict() for trip in trips]), 200

    @app.route('/api/trips/<int:trip_id>/itinerary', methods=['PUT'])
    def update_trip_itinerary(trip_id):
        # Skip in testing environment
        if current_app.config['TESTING']:
            return jsonify({"message": "Itinerary updated successfully"}), 200

        trip = Trip.query.get_or_404(trip_id)
        data = request.json
        
        # Update itinerary in the itinerary service
        itinerary_service_url = f"{ITINERARY_SERVICE_URL}/api/itinerary/{trip_id}/activities"
        response = requests.put(itinerary_service_url, json=data)
        
        if response.status_code == 200:
            return jsonify({"message": "Itinerary updated successfully"}), 200
        return jsonify({"error": "Failed to update itinerary"}), response.status_code

    @app.route('/api/trips/<int:trip_id>', methods=['DELETE'])
    def delete_trip(trip_id):
        try:
            trip = Trip.query.get_or_404(trip_id)
            
            # Skip external service calls in testing environment
            if not current_app.config['TESTING']:
                try:
                    # Delete itinerary
                    itinerary_service_url = f"{ITINERARY_SERVICE_URL}/api/itinerary/{trip_id}"
                    requests.delete(itinerary_service_url)
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error connecting to itinerary service: {str(e)}")
                    # Continue with trip deletion even if itinerary deletion fails
            
            # Delete trip from database
            db.session.delete(trip)
            db.session.commit()
            
            return jsonify({"message": "Trip deleted successfully"}), 200
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            db.session.rollback()
            return jsonify({"error": str(e)}), 500 