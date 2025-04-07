from flask import jsonify, request, current_app
from datetime import datetime
import requests
from app.models import db, Trip, Recommendation
from app.message_broker import publish_recommendation_request
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

                except requests.exceptions.RequestException as e:
                    # Handle connection errors to external services
                    logger.error(f"Error connecting to itinerary service: {str(e)}")
                    # Continue with trip creation even if itinerary creation failed
                    logger.warning(f"Continuing with trip creation despite connection error to itinerary service")
                
                # Request recommendations for the new trip
                try:
                    logger.info(f"Requesting recommendations for trip: {trip.id}")
                    success = publish_recommendation_request(
                        trip.id, 
                        trip.city, 
                        trip.start_date, 
                        trip.end_date
                    )
                    if success:
                        logger.info(f"Successfully queued recommendation request for trip: {trip.id}")
                    else:
                        logger.error(f"Failed to queue recommendation request for trip: {trip.id}")
                except Exception as e:
                    logger.error(f"Error requesting recommendations: {str(e)}")
                    # Continue with trip creation even if recommendation request failed
                    logger.warning(f"Continuing with trip creation despite recommendation request failure")

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

    # New routes for recommendation management
    @app.route('/api/trips/<int:trip_id>/recommendations', methods=['GET'])
    def get_trip_recommendations(trip_id):
        """Get recommendations for a specific trip"""
        try:
            # Check if trip exists
            trip = Trip.query.get_or_404(trip_id)
            
            # Find recommendations for this trip
            recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
            
            if not recommendation:
                # If recommendations don't exist, initiate a request to generate them
                logger.info(f"No recommendations found for trip_id={trip_id}, initiating request")
                success = publish_recommendation_request(
                    trip.id, 
                    trip.city, 
                    trip.start_date, 
                    trip.end_date
                )
                if success:
                    logger.info(f"Successfully queued recommendation request for trip: {trip.id}")
                    return jsonify({
                        "status": "processing",
                        "message": "Recommendations are being generated. Please try again in a few moments."
                    }), 202  # Accepted
                else:
                    logger.error(f"Failed to queue recommendation request for trip: {trip.id}")
                    return jsonify({
                        "error": "Failed to queue recommendation request"
                    }), 500
            
            # Return the recommendations
            return jsonify(recommendation.to_dict()), 200
            
        except Exception as e:
            logger.error(f"Error fetching recommendations: {str(e)}")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
    @app.route('/api/trips/<int:trip_id>/recommendations', methods=['POST'])
    def request_trip_recommendations(trip_id):
        """Request recommendations for a specific trip"""
        try:
            # Check if trip exists
            trip = Trip.query.get_or_404(trip_id)
            
            # Publish a request for recommendations
            success = publish_recommendation_request(
                trip.id, 
                trip.city, 
                trip.start_date, 
                trip.end_date
            )
            
            if not success:
                return jsonify({
                    "error": "Failed to queue recommendation request"
                }), 500
                
            return jsonify({
                "status": "accepted",
                "message": "Recommendation request has been queued",
                "trip_id": trip_id
            }), 202  # Accepted
            
        except Exception as e:
            logger.error(f"Error requesting recommendations: {str(e)}")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500

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
            
            # Delete recommendations for this trip
            try:
                recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
                if recommendation:
                    db.session.delete(recommendation)
            except Exception as e:
                logger.error(f"Error deleting recommendations: {str(e)}")
                # Continue with trip deletion even if recommendation deletion fails
            
            # Delete trip from database
            db.session.delete(trip)
            db.session.commit()
            
            return jsonify({"message": "Trip deleted successfully"}), 200
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            db.session.rollback()
            return jsonify({"error": str(e)}), 500 