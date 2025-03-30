from flask import Flask, request, jsonify, send_file
import requests
import json
from datetime import datetime
from icalendar import Calendar, Event
import os

app = Flask(__name__)

# In-memory storage for demonstration
itineraries = {}

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "itinerary"}), 200

@app.route('/itinerary/<trip_id>', methods=['GET'])
def get_itinerary(trip_id):
    # Fetch trip details from Trip Management Service
    response = requests.get(f"http://trip-management:5001/trips/{trip_id}")
    
    if response.status_code != 200:
        return jsonify({"error": "Trip not found"}), 404
    
    trip_data = response.json()
    
    # Organize activities by date
    organized_activities = {}
    for activity in trip_data['activities']:
        date = activity['date']
        if date not in organized_activities:
            organized_activities[date] = []
        organized_activities[date].append(activity)
    
    # Sort activities by time for each date
    for date in organized_activities:
        organized_activities[date] = sorted(organized_activities[date], key=lambda x: x['time'])
    
    itinerary = {
        "tripId": trip_id,
        "destination": trip_data['destination'],
        "startDate": trip_data['startDate'],
        "endDate": trip_data['endDate'],
        "dailyActivities": organized_activities
    }
    
    # Store the itinerary
    itineraries[trip_id] = itinerary
    
    return jsonify(itinerary), 200

@app.route('/itinerary/<trip_id>/export', methods=['POST'])
def export_to_calendar(trip_id):
    if trip_id not in itineraries:
        # Try to fetch it first
        response = requests.get(f"http://localhost:5002/itinerary/{trip_id}")
        if response.status_code != 200:
            return jsonify({"error": "Itinerary not found"}), 404
        itineraries[trip_id] = response.json()
    
    itinerary = itineraries[trip_id]
    
    # Create an iCalendar file
    cal = Calendar()
    cal.add('prodid', '-//My Planned Trip//itinerary-added//')
    cal.add('version', '2.0')
    
    for date, activities in itinerary['dailyActivities'].items():
        for activity in activities:
            event = Event()
            start_time = f"{date}T{activity['time']}:00"
            start_dt = datetime.fromisoformat(start_time)
            end_dt = start_dt.replace(hour=start_dt.hour + 1)
            
            event.add('summary', activity.get('name', 'No Title'))
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            event.add('location', activity.get('location', 'No Location'))
            event.add('description', activity.get('description', ''))
            
            cal.add_component(event)
    
    # Save the calendar to a file
    ics_filename = f"itinerary_{trip_id}.ics"
    with open(ics_filename, 'wb') as f:
        f.write(cal.to_ical())
    
    return send_file(ics_filename, as_attachment=True, download_name=ics_filename)

@app.route('/itinerary/<trip_id>/activities', methods=['PUT'])
def add_activity(trip_id):
    """Add an activity to the itinerary."""
    activity_data = request.get_json()
    
    if trip_id not in itineraries:
        return jsonify({"error": "Itinerary not found"}), 404
    
    itinerary = itineraries[trip_id]
    date = activity_data['date']
    
    if date not in itinerary['dailyActivities']:
        itinerary['dailyActivities'][date] = []
    
    itinerary['dailyActivities'][date].append(activity_data)
    
    return jsonify({"message": "Activity added successfully"}), 200

@app.route('/itinerary/<trip_id>/export', methods=['POST'])
def export_to_google_calendar(trip_id):
    """Export itinerary to Google Calendar."""
    if trip_id not in itineraries:
        return jsonify({"error": "Itinerary not found"}), 404
    
    itinerary = itineraries[trip_id]
    
    # Create an iCalendar file
    cal = Calendar()
    cal.add('prodid', '-//My Planned Trip//itinerary-added//')
    cal.add('version', '2.0')
    
    for date, activities in itinerary['dailyActivities'].items():
        for activity in activities:
            event = Event()
            start_time = f"{date}T{activity['time']}:00"
            start_dt = datetime.fromisoformat(start_time)
            end_dt = start_dt.replace(hour=start_dt.hour + 1)
            
            event.add('summary', activity['name'])
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            event.add('location', activity['location'])
            event.add('description', activity.get('description', ''))
            
            cal.add_component(event)
    
    # Save the calendar to a file
    ics_filename = f"itinerary_{trip_id}.ics"
    with open(ics_filename, 'wb') as f:
        f.write(cal.to_ical())
    
    # Simulate Google Calendar API call
    try:
        response = requests.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"},
            json={"calendar": cal.to_ical().decode()}
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to export to Google Calendar"}), response.status_code
        
    except Exception as e:
        return jsonify({"error": f"Failed to export to Google Calendar: {str(e)}"}), 500
    
    return send_file(ics_filename, as_attachment=True, download_name=ics_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)