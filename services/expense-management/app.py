from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Itinerary service endpoint
ITINERARY_SERVICE = "http://itinerary:5004"

@app.route('/expenses', methods=['POST'])
def add_expense():
    """Process and forward expense data to the Itinerary service."""
    expense_data = request.get_json()

    # Validate required fields
    required_fields = ['trip_id', 'amount', 'paid_by', 'split_details']
    missing_fields = [field for field in required_fields if field not in expense_data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Forward the expense data to the Itinerary service
    try:
        response = requests.post(
            f"{ITINERARY_SERVICE}/itinerary/{expense_data['trip_id']}/expenses",
            json=expense_data
        )

        if response.status_code == 200:
            return jsonify({"message": "Expense processed successfully"}), 200
        else:
            return jsonify({"error": "Failed to store expense in itinerary"}), response.status_code

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "expense-management"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
