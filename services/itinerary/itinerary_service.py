from flask import Flask, request, jsonify, send_file
import requests
import json
from datetime import datetime
from icalendar import Calendar, Event
import io

app = Flask(__name__)

# In-memory storage for itineraries
itineraries = {}

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "itinerary"}), 200

# Scenario 2: Planning
@app.route('/itinerary/<trip_id>', methods=['GET'])
def get_itinerary(trip_id):
    response = requests.get(f"http://trip-management:5001/trips/{trip_id}")
    
    if response.status_code != 200:
        return jsonify({"error": "Trip not found"}), 404
    
    trip_data = response.json()
    
    # Organise activities by date
    activities_by_date = {}
    for activity in trip_data['activities']:
        date = activity['date']
        if date not in activities_by_date:
            activities_by_date[date] = []
        activities_by_date[date].append(activity)
    
    # Activities organised by date, now organise by time
    for date in activities_by_date:
        activities_by_date[date] = sorted(activities_by_date[date], key=lambda x: x['time'])
    
    itinerary = {
        "tripId": trip_id,
        "destination": trip_data['destination'],
        "startDate": trip_data['startDate'],
        "endDate": trip_data['endDate'],
        "dailyActivities": activities_by_date
    }
    
    # Store the itinerary
    itineraries[trip_id] = itinerary
    
    return jsonify(itinerary), 200

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

# Scenario 3: Finances

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)