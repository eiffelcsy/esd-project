from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Service endpoints
TRIP_SERVICE = "http://trip-management:5001"
RECOMMENDATION_SERVICE = "http://recommendation-management:5002"
ITINERARY_SERVICE = "http://itinerary:5004"
EXPENSE_MANAGEMENT_SERVICE = "http://expense-management:5005"

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/trips/new', methods=['GET', 'POST'])
def new_trip():
    """Create a new trip."""
    if request.method == 'POST':
        response = requests.post(
            f"{TRIP_SERVICE}/trips",
            json={
                "userId": session.get('user_id', '12345'),
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
    trip_response = requests.get(f"{TRIP_SERVICE}/trips/{trip_id}")
    
    if trip_response.status_code != 200:
        return render_template('error.html', message="Trip not found"), 404
    
    trip_data = trip_response.json()
    
    rec_response = requests.get(f"{RECOMMENDATION_SERVICE}/recommendations/{trip_id}")
    recommendations = []
    
    if rec_response.status_code == 200:
        recommendations = rec_response.json().get('recommendations', [])
    
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
    return jsonify(response.json()), 200

@app.route('/itinerary/<trip_id>', methods=['GET'])
def get_itinerary(trip_id):
    """Fetch itinerary for a specific trip."""
    response = requests.get(f"{ITINERARY_SERVICE}/itinerary/{trip_id}")
    if response.status_code != 200:
        return render_template('error.html', message="Itinerary not found"), 404
    
    itinerary = response.json()
    return jsonify(itinerary), 200

@app.route('/trips/<trip_id>/add_activity', methods=['POST'])
def add_activity(trip_id):
    """Add an activity to a trip."""
    activity_data = {
        "name": request.form['name'],
        "date": request.form['date'],
        "time": request.form['time'],
        "end_time": request.form['end_time'],
        "location": request.form['location'],
        "description": request.form.get('description', '')
    }
    
    response = requests.put(
        f"{ITINERARY_SERVICE}/itinerary/{trip_id}/activities",
        json=activity_data
    )
    
    if response.status_code == 200:
        return redirect(url_for('view_trip', trip_id=trip_id))
    else:
        error = response.json().get('error', 'Failed to add activity')
        return render_template('error.html', message=error), response.status_code
    
@app.route('/itinerary/<trip_id>/activities', methods=['PUT'])
def add_activity_to_itinerary(trip_id):
    """Add an activity to the itinerary."""
    activity_data = request.get_json()
    response = requests.put(f"{ITINERARY_SERVICE}/itinerary/{trip_id}/activities", json=activity_data)
    if response.status_code != 200:
        return jsonify({"error": "Failed to add activity"}), response.status_code
    
    return jsonify({"message": "Activity added successfully"}), 200

@app.route('/trips/<trip_id>/delete_activity', methods=['POST'])
def delete_activity(trip_id):
    """Delete an activity from a trip."""
    activity_data = {
        "date": request.form['date'],
        "time": request.form['time'],
        "name": request.form['name']
    }
    
    response = requests.delete(
        f"{ITINERARY_SERVICE}/itinerary/{trip_id}/activities",
        json=activity_data
    )
    
    if response.status_code == 200:
        return redirect(url_for('view_trip', trip_id=trip_id))
    else:
        error = response.json().get('error', 'Failed to delete activity')
        return render_template('error.html', message=error), response.status_code

@app.route('/trips/<trip_id>/delete', methods=['POST'])
def delete_itinerary(trip_id):
    """Delete an itinerary."""
    response = requests.delete(f"{ITINERARY_SERVICE}/itinerary/{trip_id}")
    
    if response.status_code == 200:
        return redirect(url_for('index'))
    else:
        error = response.json().get('error', 'Failed to delete itinerary')
        return render_template('error.html', message=error), response.status_code

@app.route('/trips/<trip_id>/export_calendar', methods=['POST'])
def export_calendar(trip_id):
    """Export itinerary to Google Calendar."""
    token = request.form.get('google_token', '')
    
    if not token:
        return render_template('error.html', message="Google token is required"), 400
    
    response = requests.post(
        f"{ITINERARY_SERVICE}/itinerary/{trip_id}/export",
        json={"token": token}
    )
    
    if response.status_code == 200:
        return response  # Return the ICS file directly
    else:
        error = response.json().get('error', 'Failed to export to calendar')
        return render_template('error.html', message=error), response.status_code

@app.route('/expenses', methods=['POST'])
def add_expense():
    """Send expense data to the Expense Management service."""
    expense_data = request.get_json()

    try:
        response = requests.post(
            f"{EXPENSE_MANAGEMENT_SERVICE}/expenses",
            json=expense_data
        )

        if response.status_code == 200:
            return jsonify({"message": "Expense added successfully"}), 200
        else:
            return jsonify({"error": "Failed to add expense"}), response.status_code

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)