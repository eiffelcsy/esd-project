from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from icalendar import Calendar, Event
import requests
import json
import io
import os

app = Flask(__name__)

# Configure service URLs and database connection
TRIP_MANAGEMENT_URL = os.getenv('TRIP_MANAGEMENT_URL', 'http://trip-management:5007')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/itinerary_db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model for itineraries
class Itinerary(db.Model):
    __tablename__ = 'itineraries'
    trip_id = db.Column(db.String, primary_key=True)
    destination = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    daily_activities = db.Column(db.JSON, nullable=False, default={})

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "itinerary"}), 200

# Scenario 2: Planning
@app.route('/itinerary/<trip_id>', methods=['GET'])
def get_itinerary(trip_id):
    try:
        app.logger.info(f"Fetching itinerary for trip_id: {trip_id}")
        itinerary = Itinerary.query.get(trip_id)

        if not itinerary:
            app.logger.warning(f"Itinerary not found for trip_id: {trip_id}")
            # Fetch trip data from trip-management service
            response = requests.get(f"{TRIP_MANAGEMENT_URL}/trips/{trip_id}")
            if response.status_code != 200:
                return jsonify({"error": "Trip not found"}), 404
            
            trip_data = response.json()

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

        return jsonify({
            "tripId": itinerary.trip_id,
            "destination": itinerary.destination,
            "startDate": itinerary.start_date.isoformat(),
            "endDate": itinerary.end_date.isoformat(),
            "dailyActivities": itinerary.daily_activities
        }), 200
    except Exception as e:
        app.logger.error(f"Error fetching itinerary for trip_id {trip_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch itinerary"}), 500

# Add activity to itinerary
@app.route('/itinerary/<trip_id>/activities', methods=['PUT'])
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
        app.logger.info(f"Adding activity to itinerary for trip_id: {trip_id}")
        itinerary = Itinerary.query.get(trip_id)
        if not itinerary:
            app.logger.warning(f"Itinerary not found for trip_id: {trip_id}")
            return jsonify({"error": "Itinerary not found"}), 404

        daily_activities = itinerary.daily_activities
        if activity_data['date'] not in daily_activities:
            daily_activities[activity_data['date']] = []

        daily_activities[activity_data['date']].append(activity_data)
        itinerary.daily_activities = daily_activities

        db.session.commit()
        app.logger.info(f"Activity added successfully for trip_id: {trip_id}")
        return jsonify({"message": "Activity added successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error adding activity for trip_id {trip_id}: {str(e)}")
        return jsonify({"error": "Failed to add activity"}), 500

# Add recommended activity to itinerary
@app.route('/itinerary/<trip_id>/add_recommended_activity', methods=['POST'])
def add_recommended_activity(trip_id):
    """Add an activity to the itinerary based on a recommendation."""
    try:
        # Fetch the recommendation ID from the request
        recommendation_id = request.json.get('recommendation_id')
        if not recommendation_id:
            return jsonify({"error": "Recommendation ID is required"}), 400

        # Fetch the recommendation from the recommendation-management service
        response = requests.get(f"http://recommendation-management:5002/recommendations/{trip_id}")
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch recommendations"}), response.status_code

        recommendations = response.json().get('recommendations', [])
        recommended_activity = next((rec for rec in recommendations if rec['id'] == recommendation_id), None)

        if not recommended_activity:
            return jsonify({"error": "Recommendation not found"}), 404

        # Add the recommended activity to the itinerary
        itinerary = Itinerary.query.get(trip_id)
        if not itinerary:
            return jsonify({"error": "Itinerary not found"}), 404

        daily_activities = itinerary.daily_activities
        date = recommended_activity.get('suggested_date', datetime.now().date().isoformat())
        if date not in daily_activities:
            daily_activities[date] = []

        daily_activities[date].append({
            "name": recommended_activity['name'],
            "description": recommended_activity.get('description', ''),
            "time": recommended_activity.get('time', '09:00'),
            "end_time": recommended_activity.get('end_time', '11:00'),
            "location": recommended_activity.get('location', '')
        })

        itinerary.daily_activities = daily_activities
        db.session.commit()

        return jsonify({"message": "Recommended activity added successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error adding recommended activity for trip_id {trip_id}: {str(e)}")
        return jsonify({"error": "Failed to add recommended activity"}), 500

# Delete activity from itinerary
@app.route('/itinerary/<trip_id>/activities', methods=['DELETE'])
def delete_activity(trip_id):
    """Delete an activity from the itinerary."""
    activity_data = request.get_json()
    required_fields = ['date', 'time', 'name']
    missing_fields = [field for field in required_fields if field not in activity_data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        app.logger.info(f"Deleting activity from itinerary for trip_id: {trip_id}")
        itinerary = Itinerary.query.get(trip_id)
        if not itinerary:
            app.logger.warning(f"Itinerary not found for trip_id: {trip_id}")
            return jsonify({"error": "Itinerary not found"}), 404

        daily_activities = itinerary.daily_activities
        date = activity_data['date']
        if date not in daily_activities:
            app.logger.warning(f"No activities found for date {date} in trip_id: {trip_id}")
            return jsonify({"error": "No activities found for this date"}), 404

        # Find and remove the activity
        activities = daily_activities[date]
        for i, activity in enumerate(activities):
            if activity['time'] == activity_data['time'] and activity['name'] == activity_data['name']:
                del activities[i]
                break
        else:
            app.logger.warning(f"Activity not found for trip_id: {trip_id}, date: {date}, time: {activity_data['time']}")
            return jsonify({"error": "Activity not found"}), 404

        # Remove the date if no more activities
        if not activities:
            del daily_activities[date]

        itinerary.daily_activities = daily_activities
        db.session.commit()

        app.logger.info(f"Activity deleted successfully for trip_id: {trip_id}")
        return jsonify({"message": "Activity deleted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting activity for trip_id {trip_id}: {str(e)}")
        return jsonify({"error": "Failed to delete activity"}), 500

# Delete itinerary
@app.route('/itinerary/<trip_id>', methods=['DELETE'])
def delete_itinerary(trip_id):
    """Delete an itinerary."""
    try:
        app.logger.info(f"Attempting to delete itinerary for trip_id: {trip_id}")
        
        # Fetch the itinerary from the database
        itinerary = Itinerary.query.get(trip_id)
        if not itinerary:
            app.logger.warning(f"Itinerary not found for trip_id: {trip_id}")
            return jsonify({"error": "Itinerary not found"}), 404

        # Delete the itinerary
        db.session.delete(itinerary)
        db.session.commit()
        
        app.logger.info(f"Successfully deleted itinerary for trip_id: {trip_id}")
        return jsonify({"message": "Itinerary deleted successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting itinerary for trip_id {trip_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to delete itinerary"}), 500

if __name__ == '__main__':
    db.create_all()  # Ensure tables are created
    app.run(host='0.0.0.0', port=5004)