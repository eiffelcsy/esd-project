# user_interface.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Configure service endpoints
TRIP_SERVICE = "http://trip-management:5001"
ITINERARY_SERVICE = "http://itinerary:5002"
RECOMMENDATION_SERVICE = "http://recommendation-management:5003"

@app.route('/')
def index():
    """Main dashboard page."""
    # In a real app, this would render a frontend template
    return render_template('index.html')

@app.route('/trips/new', methods=['GET', 'POST'])
def new_trip():
    """Create a new trip."""
    if request.method == 'POST':
        # Send data to Trip Management Service
        response = requests.post(
            f"{TRIP_SERVICE}/trips",
            json={
                "userId": session.get('user_id', '12345'),  # In reality, get from auth system
                "destination": request.form['destination'],
                "startDate": request.form['start_date'],
                "endDate": request.form['end_date']
            }
        )
        
        if response.status_code == 201:
            trip_data = response.json()
            return redirect(url_for('view_trip', trip_id=trip_data['tripId']))
        else:
            error = response.json().get('error', 'Failed to create trip')
            return render_template('new_trip.html', error=error)
    
    return render_template('new_trip.html')

@app.route('/trips/<trip_id>')
def view_trip(trip_id):
    """View trip details and itinerary."""
    # Get trip details
    trip_response = requests.get(f"{TRIP_SERVICE}/trips/{trip_id}")
    
    if trip_response.status_code != 200:
        return render_template('error.html', message="Trip not found"), 404
    
    trip_data = trip_response.json()
    
    # Get recommendations
    rec_response = requests.get(f"{RECOMMENDATION_SERVICE}/recommendations/{trip_id}")
    recommendations = []
    
    if rec_response.status_code == 200:
        recommendations = rec_response.json().get('recommendations', [])
    
    # Get itinerary
    itinerary_response = requests.get(f"{ITINERARY_SERVICE}/itinerary/{trip_id}")
    itinerary = {}
    
    if itinerary_response.status_code == 200:
        itinerary = itinerary_response.json()
    
    return render_template(
        'trip_details.html',
        trip=trip_data,
        recommendations=recommendations,
        itinerary=itinerary
    )

@app.route('/trips/<trip_id>/add_activity', methods=['POST'])
def add_activity(trip_id):
    """Add an activity to a trip."""
    activity_data = {
        "name": request.form['name'],
        "date": request.form['date'],
        "time": request.form['time'],
        "location": request.form['location'],
        "description": request.form.get('description', '')
    }
    
    response = requests.put(
        f"{TRIP_SERVICE}/trips/{trip_id}/activities",
        json=activity_data
    )
    
    if response.status_code == 200:
        return redirect(url_for('view_trip', trip_id=trip_id))
    else:
        error = response.json().get('error', 'Failed to add activity')
        return render_template('error.html', message=error), response.status_code

@app.route('/trips/<trip_id>/export_calendar', methods=['POST'])
def export_calendar(trip_id):
    """Export itinerary to Google Calendar."""
    # In a real app, you'd get the token from OAuth flow
    token = request.form.get('google_token', '')
    
    response = requests.post(
        f"{ITINERARY_SERVICE}/itinerary/{trip_id}/export",
        json={"token": token}
    )
    
    if response.status_code == 200:
        return redirect(url_for('view_trip', trip_id=trip_id, calendar_exported=True))
    else:
        error = response.json().get('error', 'Failed to export to calendar')
        return render_template('error.html', message=error), response.status_code

@app.route('/recommendations', methods=['POST'])
def receive_recommendations():
    """Receive recommendations from Message Broker."""
    data = request.json
    
    # In a real app, this endpoint would push to connected clients
    # via WebSockets or similar technology
    
    return jsonify({"status": "received"}), 200

@app.route('/trip/<trip_id>', methods=['GET'])
def get_trip_details(trip_id):
    """Fetch trip details from Trip Management Service."""
    response = requests.get(f"{TRIP_SERVICE}/trips/{trip_id}")
    if response.status_code != 200:
        return render_template('error.html', message="Trip not found"), 404
    
    trip_data = response.json()
    return jsonify(trip_data), 200

@app.route('/recommendations/<trip_id>', methods=['GET'])
def get_recommendations(trip_id):
    """Fetch recommendations for a specific trip."""
    response = requests.get(f"{RECOMMENDATION_SERVICE}/recommendations/{trip_id}")
    if response.status_code != 200:
        return render_template('error.html', message="Recommendations not found"), 404
    
    recommendations = response.json()
    return jsonify(recommendations), 200

@app.route('/itinerary/<trip_id>', methods=['GET'])
def get_itinerary(trip_id):
    """Fetch itinerary for a specific trip."""
    response = requests.get(f"{ITINERARY_SERVICE}/itinerary/{trip_id}")
    if response.status_code != 200:
        return render_template('error.html', message="Itinerary not found"), 404
    
    itinerary = response.json()
    return jsonify(itinerary), 200

@app.route('/itinerary/<trip_id>/activities', methods=['PUT'])
def add_activity(trip_id):
    """Add an activity to the itinerary."""
    activity_data = request.get_json()
    response = requests.put(f"{ITINERARY_SERVICE}/itinerary/{trip_id}/activities", json=activity_data)
    if response.status_code != 200:
        return jsonify({"error": "Failed to add activity"}), response.status_code
    
    return jsonify({"message": "Activity added successfully"}), 200

@app.route('/itinerary/<trip_id>/export', methods=['POST'])
def export_itinerary(trip_id):
    """Export itinerary to Google Calendar."""
    response = requests.post(f"{ITINERARY_SERVICE}/itinerary/{trip_id}/export")
    if response.status_code != 200:
        return jsonify({"error": "Failed to export itinerary"}), response.status_code
    
    return jsonify({"message": "Itinerary exported successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)