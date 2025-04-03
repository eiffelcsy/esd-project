from flask import Flask, request, jsonify, send_file
import requests
import json
from datetime import datetime
from icalendar import Calendar, Event
import io
import os

app = Flask(__name__)

# Configure trip-management service URL from environment
TRIP_MANAGEMENT_URL = os.getenv('TRIP_MANAGEMENT_URL', 'http://trip-management:5007')
FINANCE_SERVICE_URL = os.getenv('FINANCE_SERVICE_URL', 'http://finance:5010')

# In-memory storage for itineraries
itineraries = {}

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "itinerary"}), 200

# Scenario 2: Planning
@app.route('/itinerary/<trip_id>', methods=['GET'])
def get_itinerary(trip_id):
    try:
        # Check if we already have this itinerary with activities
        if trip_id in itineraries and itineraries[trip_id].get('dailyActivities'):
            return jsonify(itineraries[trip_id]), 200

        # If not, get trip data and create new itinerary
        response = requests.get(f"{TRIP_MANAGEMENT_URL}/trips/{trip_id}")
        
        if response.status_code != 200:
            return jsonify({"error": "Trip not found"}), 404
        
        trip_data = response.json()
        
        # Create new itinerary or update existing one
        itinerary = itineraries.get(trip_id, {})
        itinerary.update({
            "tripId": trip_id,
            "destination": trip_data['city'],
            "startDate": trip_data['start_date'],
            "endDate": trip_data['end_date'],
        })
        
        # Preserve existing activities or initialize empty dict
        if 'dailyActivities' not in itinerary:
            itinerary['dailyActivities'] = {}
        
        # Store/update the itinerary
        itineraries[trip_id] = itinerary
        
        return jsonify(itinerary), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error connecting to trip-management service: {str(e)}")
        return jsonify({"error": "Failed to connect to trip-management service"}), 503

# Add activity to itinerary
@app.route('/itinerary/<trip_id>/activities', methods=['PUT'])
def add_activity(trip_id):
    """Add an activity to the itinerary."""
    activity_data = request.get_json()
    
    if trip_id not in itineraries:
        return jsonify({"error": "Itinerary not found"}), 404
    
    required_fields = ['name', 'date', 'time', 'end_time', 'location']
    missing_fields = [field for field in required_fields if field not in activity_data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    if 'time' not in activity_data or 'end_time' not in activity_data:
        return jsonify({"error": "Both start time and end time are required"}), 400
    
    if activity_data['end_time'] <= activity_data['time']:
        return jsonify({"error": "End time must be later than start time"}), 400
    
    itinerary = itineraries[trip_id]
    date = activity_data['date']
    
    if date not in itinerary['dailyActivities']:
        itinerary['dailyActivities'][date] = []
    
    itinerary['dailyActivities'][date].append(activity_data)
    
    return jsonify({"message": "Activity added successfully"}), 200

# Delete activity from itinerary
@app.route('/itinerary/<trip_id>/activities', methods=['DELETE'])
def delete_activity(trip_id):
    """Delete an activity from the itinerary."""
    activity_data = request.get_json()
    
    if trip_id not in itineraries:
        return jsonify({"error": "Itinerary not found"}), 404
    
    required_fields = ['date', 'time', 'name']
    missing_fields = [field for field in required_fields if field not in activity_data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    itinerary = itineraries[trip_id]
    date = activity_data['date']
    
    if date not in itinerary['dailyActivities']:
        return jsonify({"error": "No activities found for this date"}), 404
    
    # Find and remove the activity
    activities = itinerary['dailyActivities'][date]
    for i, activity in enumerate(activities):
        if (activity['time'] == activity_data['time'] and 
            activity['name'] == activity_data['name']):
            del activities[i]
            # Remove the date if no more activities
            if not activities:
                del itinerary['dailyActivities'][date]
            return jsonify({"message": "Activity deleted successfully"}), 200
    
    return jsonify({"error": "Activity not found"}), 404

# Exporting acitvities to Google Calendar
@app.route('/itinerary/<trip_id>/export', methods=['POST'])
def export_to_google_calendar(trip_id):
    """Export itinerary to Google Calendar."""
    if trip_id not in itineraries:
        return jsonify({"error": "Itinerary not found"}), 404
    
    itinerary = itineraries[trip_id]
    
    if not itinerary['dailyActivities']:
        return jsonify({"error": "No activities found in the itinerary to export"}), 400
    
    # Retrieve the token from the request or environment
    token = request.json.get('token')  # Assuming the token is passed in the request body
    if not token:
        return jsonify({"error": "Authorization token is required"}), 400

    headers = {"Authorization": f"Bearer {token}"}
    
    cal = Calendar()
    trip_name = itinerary.get('destination', f"Trip {trip_id}")
    cal.add('prodid', f'-//{trip_name}//')
    cal.add('version', '2.0')
    
    for date, activities in itinerary['dailyActivities'].items():
        for activity in activities:
            event = Event()
            start_time = f"{date}T{activity['time']}:00"
            end_time = f"{date}T{activity['end_time']}:00"
            try:
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time)
            except ValueError:
                return jsonify({"error": "Invalid date or time format"}), 400
            
            event.add('summary', activity['name'])
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            event.add('location', activity['location'])
            event.add('description', activity.get('description', ''))
            
            cal.add_component(event)
    
    # Use in-memory file for ICS
    ics_file = io.BytesIO()
    ics_file.write(cal.to_ical())
    ics_file.seek(0)  # Reset the file pointer to the beginning
    
    # Simulate Google Calendar API call
    try:
        GOOGLE_CALENDAR_API_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        for date, activities in itinerary['dailyActivities'].items():
            for activity in activities:
                start_time = f"{date}T{activity['time']}:00"
                end_time = f"{date}T{activity['end_time']}:00"
                try:
                    start_dt = datetime.fromisoformat(start_time)
                    end_dt = datetime.fromisoformat(end_time)
                except ValueError:
                    return jsonify({"error": "Invalid date or time format"}), 400
                
                # Construct a valid payload for Google Calendar API
                event_payload = {
                    "summary": trip_name,
                    "description": "Itinerary exported from the application",
                    "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
                    "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"}
                }

                response = requests.post(
                    GOOGLE_CALENDAR_API_URL,
                    headers=headers,
                    json=event_payload
                )
                
                if response.status_code != 200:
                    return jsonify({"error": "Failed to export to Google Calendar"}), response.status_code
        
    except Exception as e:
        return jsonify({"error": f"Failed to export to Google Calendar: {str(e)}"}), 500
    
    return send_file(ics_file, as_attachment=True, download_name=f"itinerary_{trip_id}.ics")

# Delete itinerary
@app.route('/itinerary/<trip_id>', methods=['DELETE'])
def delete_itinerary(trip_id):
    """Delete an itinerary."""
    if trip_id not in itineraries:
        return jsonify({"error": "Itinerary not found"}), 404
    
    del itineraries[trip_id]
    return jsonify({"message": "Itinerary deleted successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)