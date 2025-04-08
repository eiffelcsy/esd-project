from flask import jsonify, request, current_app
from datetime import datetime
import requests
import json
import logging
import traceback
from app.models import db, Itinerary, Recommendation
from app.recommendation_service import RecommendationService
import os
import pika
from sqlalchemy.orm.attributes import flag_modified

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure service URLs
TRIP_MANAGEMENT_URL = os.getenv('TRIP_MANAGEMENT_URL', 'http://trip-management:5005')

def register_routes(app):
    @app.route('/api/itinerary/<trip_id>', methods=['GET'])
    def get_itinerary(trip_id):
        try:
            logger.info(f"Fetching itinerary for trip_id: {trip_id}")
            itinerary = Itinerary.query.get(trip_id)

            if not itinerary:
                logger.warning(f"Itinerary not found for trip_id: {trip_id}")
                # Fetch trip data from trip-management service
                response = requests.get(f"{TRIP_MANAGEMENT_URL}/api/trips/{trip_id}")
                if response.status_code != 200:
                    return jsonify({"error": "Trip not found"}), 404
                
                trip_data = response.json()
                logger.info(f"Retrieved trip data: {trip_data}")

                # Create a new itinerary
                itinerary = Itinerary(
                    trip_id=trip_id,
                    destination=trip_data['city'],
                    start_date=datetime.fromisoformat(trip_data['start_date']).date(),
                    end_date=datetime.fromisoformat(trip_data['end_date']).date(),
                    daily_activities={}
                )
                db.session.add(itinerary)
                db.session.commit()
                logger.info(f"Created new itinerary for trip_id: {trip_id}")

                # Request recommendations for the new itinerary via message broker
                try:
                    # Get the message broker instance
                    from app import message_broker
                    
                    # Request recommendations
                    message_broker.send_recommendation_request(
                        trip_id=trip_id,
                        destination=trip_data['city'],
                        start_date=trip_data['start_date'],
                        end_date=trip_data['end_date']
                    )
                    
                    logger.info(f"Sent recommendation request via message broker for trip_id: {trip_id}")
                except Exception as e:
                    logger.error(f"Error requesting recommendations for trip_id {trip_id}: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Continue even if recommendation request fails

            return jsonify(itinerary.to_dict()), 200
        except Exception as e:
            logger.error(f"Error fetching itinerary for trip_id {trip_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Failed to fetch itinerary"}), 500

    @app.route('/api/itinerary', methods=['POST'])
    def create_itinerary():
        """Create a new itinerary from trip data."""
        try:
            data = request.json
            logger.info(f"Received request to create itinerary: {data}")
            
            # Validate required fields
            required_fields = ['trip_id', 'destination', 'start_date', 'end_date']
            if not all(field in data for field in required_fields):
                return jsonify({"error": "Missing required fields"}), 400
                
            # Check if itinerary already exists
            existing_itinerary = Itinerary.query.get(data['trip_id'])
            if existing_itinerary:
                logger.info(f"Itinerary already exists for trip_id: {data['trip_id']}")
                return jsonify(existing_itinerary.to_dict()), 200
                
            # Create new itinerary
            itinerary = Itinerary(
                trip_id=data['trip_id'],
                destination=data['destination'],
                start_date=datetime.fromisoformat(data['start_date']).date(),
                end_date=datetime.fromisoformat(data['end_date']).date(),
                daily_activities={}
            )
            db.session.add(itinerary)
            db.session.commit()
            logger.info(f"Created new itinerary for trip_id: {data['trip_id']}")
            
            # Request recommendations for the new itinerary via message broker
            try:
                # Get the message broker instance
                from app import message_broker
                
                # Request recommendations
                message_broker.send_recommendation_request(
                    trip_id=data['trip_id'],
                    destination=data['destination'],
                    start_date=data['start_date'],
                    end_date=data['end_date']
                )
                
                logger.info(f"Sent recommendation request via message broker for trip_id: {data['trip_id']}")
            except Exception as e:
                logger.error(f"Error requesting recommendations for trip_id {data['trip_id']}: {str(e)}")
                logger.error(traceback.format_exc())
                # Continue even if recommendation request fails
                
            return jsonify(itinerary.to_dict()), 201
        except Exception as e:
            logger.error(f"Error creating itinerary: {str(e)}")
            logger.error(traceback.format_exc())
            db.session.rollback()
            return jsonify({"error": f"Failed to create itinerary: {str(e)}"}), 500

    @app.route('/api/itinerary/<trip_id>/activities', methods=['PUT'])
    def add_activity(trip_id):
        """Add an activity to the itinerary."""
        activity_data = request.get_json()
        required_fields = ['name', 'date', 'time', 'end_time', 'location']
        missing_fields = [field for field in required_fields if field not in activity_data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        if activity_data['end_time'] <= activity_data['time']:
            return jsonify({"error": "End time must be later than start time"}), 400

        try:
            logger.info(f"Adding activity to itinerary for trip_id: {trip_id}")
            itinerary = Itinerary.query.get(trip_id)
            if not itinerary:
                logger.warning(f"Itinerary not found for trip_id: {trip_id}")
                return jsonify({"error": "Itinerary not found"}), 404

            daily_activities = itinerary.daily_activities
            if activity_data['date'] not in daily_activities:
                daily_activities[activity_data['date']] = []

            daily_activities[activity_data['date']].append(activity_data)
            itinerary.daily_activities = daily_activities

            flag_modified(itinerary, "daily_activities")
            db.session.commit()
            logger.info(f"Activity added successfully for trip_id: {trip_id}")
            return jsonify({"message": "Activity added successfully"}), 200
        except Exception as e:
            logger.error(f"Error adding activity for trip_id {trip_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": "Failed to add activity"}), 500

    @app.route('/api/recommendations/<trip_id>', methods=['GET'])
    def retrieve_recommendations(trip_id):
        """Retrieve recommendations for a specific trip from database."""
        try:
            # Check for recommendations in database
            success, result = RecommendationService.retrieve_recommendations(trip_id)
            
            if success:
                logger.info(f"Retrieved recommendations for trip_id: {trip_id}")
                return jsonify(result), 200
            else:
                logger.warning(f"No recommendations found for trip_id: {trip_id}")
                return jsonify(result), 404
                
        except Exception as e:
            logger.error(f"Error retrieving recommendations for trip_id {trip_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": f"Failed to retrieve recommendations: {str(e)}"}), 500

    @app.route('/api/itinerary/<trip_id>/add_recommended_activity', methods=['POST'])
    def add_recommended_activity(trip_id):
        """Add an activity to the itinerary based on a recommendation."""
        try:
            data = request.json
            activity_type = data.get('type', 'attraction')  # Default to attraction if not specified
            activity_index = data.get('index')
            
            if activity_index is None:
                return jsonify({"error": "Activity index is required"}), 400
                
            # Get date from request or use suggested day if available
            date = data.get('date')
            
            # Retrieve recommendations from database
            success, result = RecommendationService.retrieve_recommendations(trip_id)
            if not success:
                logger.warning(f"No recommendations found for trip_id: {trip_id}")
                return jsonify({"error": "No recommendations found for this trip. Please wait for recommendations to be processed."}), 404
            
            recommendations = result.get('recommendations', {})
            
            # Get the correct category of recommendations based on type
            if activity_type == 'attraction':
                items = recommendations.get('attractions', [])
            elif activity_type == 'restaurant':
                items = recommendations.get('restaurants', [])
            elif activity_type == 'activity':
                items = recommendations.get('activities', [])
            elif activity_type == 'event':
                items = recommendations.get('events', [])
            else:
                return jsonify({"error": f"Invalid activity type: {activity_type}"}), 400
                
            # Make sure the index is valid
            if activity_index < 0 or activity_index >= len(items):
                return jsonify({"error": f"Invalid index for {activity_type}: {activity_index}"}), 400
                
            # Get the recommended activity
            recommended_activity = items[activity_index]
            
            # If date not provided, use suggested_day from the recommendation or today's date
            if not date:
                date = recommended_activity.get('suggested_day', datetime.now().date().isoformat())
            
            # Retrieve the itinerary
            itinerary = Itinerary.query.get(trip_id)
            if not itinerary:
                return jsonify({"error": "Itinerary not found"}), 404

            # Add to daily activities
            daily_activities = itinerary.daily_activities
            logger.info(f"Daily activities: {daily_activities}")
            if date not in daily_activities:
                daily_activities[date] = []

            # Add the activity with appropriate structure based on type
            activity_entry = {
                "name": recommended_activity.get('name', ''),
                "description": recommended_activity.get('description', ''),
                "time": data.get('time', '09:00'),
                "end_time": data.get('end_time', '11:00'),
                "location": recommended_activity.get('location', ''),
                "date": date,
                "type": activity_type
            }
            
            # Add specific fields based on activity type
            if activity_type == 'restaurant':
                activity_entry.update({
                    "cuisine": recommended_activity.get('cuisine', ''),
                    "price_range": recommended_activity.get('price_range', '')
                })
            elif activity_type == 'event':
                activity_entry.update({
                    "event_date": recommended_activity.get('date', '')
                })

            # Add the activity to the itinerary
            daily_activities[date].append(activity_entry)

            itinerary.daily_activities = daily_activities
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(itinerary, "daily_activities")
            db.session.commit()
            

            logger.info(f"Added recommended {activity_type} to itinerary for trip_id: {trip_id}")
            return jsonify({"message": f"Recommended {activity_type} added successfully"}), 200
            
        except Exception as e:
            logger.error(f"Error adding recommended activity for trip_id {trip_id}: {str(e)}")
            return jsonify({"error": f"Failed to add recommended activity: {str(e)}"}), 500

    @app.route('/api/itinerary/<trip_id>/activities', methods=['DELETE'])
    def delete_activity(trip_id):
        """Delete an activity from the itinerary."""
        activity_data = request.get_json()
        required_fields = ['date', 'time', 'name']
        missing_fields = [field for field in required_fields if field not in activity_data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        try:
            logger.info(f"Deleting activity from itinerary for trip_id: {trip_id}")
            itinerary = Itinerary.query.get(trip_id)
            if not itinerary:
                logger.warning(f"Itinerary not found for trip_id: {trip_id}")
                return jsonify({"error": "Itinerary not found"}), 404

            daily_activities = itinerary.daily_activities
            date = activity_data['date']
            if date not in daily_activities:
                logger.warning(f"No activities found for date {date} in trip_id: {trip_id}")
                return jsonify({"error": "No activities found for this date"}), 404

            # Find and remove the activity
            activities = daily_activities[date]
            for i, activity in enumerate(activities):
                if activity['time'] == activity_data['time'] and activity['name'] == activity_data['name']:
                    del activities[i]
                    break
            else:
                logger.warning(f"Activity not found for trip_id: {trip_id}, date: {date}, time: {activity_data['time']}")
                return jsonify({"error": "Activity not found"}), 404

            # Remove the date if no more activities
            if not activities:
                del daily_activities[date]

            itinerary.daily_activities = daily_activities
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(itinerary, "daily_activities")
            db.session.commit()

            logger.info(f"Activity deleted successfully for trip_id: {trip_id}")
            return jsonify({"message": "Activity deleted successfully"}), 200
        except Exception as e:
            logger.error(f"Error deleting activity for trip_id {trip_id}: {str(e)}")
            return jsonify({"error": "Failed to delete activity"}), 500

    @app.route('/api/itinerary/<trip_id>', methods=['DELETE'])
    def delete_itinerary(trip_id):
        """Delete an itinerary."""
        try:
            logger.info(f"Attempting to delete itinerary for trip_id: {trip_id}")
            
            # Fetch the itinerary from the database
            itinerary = Itinerary.query.get(trip_id)
            if not itinerary:
                logger.warning(f"Itinerary not found for trip_id: {trip_id}")
                return jsonify({"error": "Itinerary not found"}), 404

            # Delete the itinerary
            db.session.delete(itinerary)
            db.session.commit()
            
            logger.info(f"Successfully deleted itinerary for trip_id: {trip_id}")
            return jsonify({"message": "Itinerary deleted successfully"}), 200
        except Exception as e:
            logger.error(f"Error deleting itinerary for trip_id {trip_id}: {str(e)}")
            db.session.rollback()
            return jsonify({"error": "Failed to delete itinerary"}), 500

    @app.route('/api/itinerary/<trip_id>/recommendations', methods=['POST'])
    def add_recommendations(trip_id):
        """Add recommendations to the itinerary database."""
        try:
            recommendations_data = request.get_json()
            logger.info(f"Received recommendations for trip_id: {trip_id}")
            
            if 'recommendations' not in recommendations_data:
                return jsonify({"error": "Missing recommendations data"}), 400
                
            recommendation_data = recommendations_data['recommendations']
            
            # Store recommendations in database
            from app.models import db, Recommendation
            
            # Check if recommendations already exist for this trip
            existing_recommendation = Recommendation.query.filter_by(trip_id=trip_id).first()
            
            if existing_recommendation:
                # Update existing record
                existing_recommendation.destination = recommendations_data.get('destination', '')
                existing_recommendation.attractions = recommendation_data.get('attractions', [])
                existing_recommendation.restaurants = recommendation_data.get('restaurants', [])
                existing_recommendation.activities = recommendation_data.get('activities', [])
                existing_recommendation.events = recommendation_data.get('events', [])
                existing_recommendation.tips = recommendation_data.get('tips', [])
                db.session.commit()
                logger.info(f"Updated existing recommendations in database for trip_id: {trip_id}")
            else:
                # Create new recommendation record
                new_recommendation = Recommendation(
                    trip_id=trip_id,
                    destination=recommendations_data.get('destination', ''),
                    attractions=recommendation_data.get('attractions', []),
                    restaurants=recommendation_data.get('restaurants', []),
                    activities=recommendation_data.get('activities', []),
                    events=recommendation_data.get('events', []),
                    tips=recommendation_data.get('tips', [])
                )
                db.session.add(new_recommendation)
                db.session.commit()
                logger.info(f"Stored new recommendations in database for trip_id: {trip_id}")
            
            return jsonify({"message": "Recommendations added successfully"}), 200
        except Exception as e:
            logger.error(f"Error adding recommendations for trip_id {trip_id}: {str(e)}")
            return jsonify({"error": f"Failed to add recommendations: {str(e)}"}), 500