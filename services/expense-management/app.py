from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Itinerary service endpoint
ITINERARY_SERVICE = "http://itinerary:5004"
# Finance service endpoint
FINANCE_SERVICE = "http://finance:5010"

@app.route('/expenses', methods=['POST'])
def add_expense():
    """Process and forward expense data to the Itinerary service."""
    expense_data = request.get_json()

    # Validate required fields
    # required_fields = ['trip_id', 'amount', 'paid_by', 'split_details']
    required_fields = ['trip_id', 'user_id', 'date', 'location', 'amount', 'base_currency', 'description', 'is_paid']
    missing_fields = [field for field in required_fields if field not in expense_data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Forward the expense data to the Itinerary service
    try:
        response1 = requests.post(
            f"{ITINERARY_SERVICE}/itinerary/{expense_data['trip_id']}/expenses",
            json=expense_data,
            timeout=5
        )
        response1.raise_for_status()
        result1 = response1.json()

        response2 = requests.post(
            f"{FINANCE_SERVICE}/finance/{expense_data['trip_id']}/add",
            json=expense_data,
            timeout=5
        )
        response2.raise_for_status()
        result2 = response2.json()

        return jsonify({
            'result1': result1,
            'result2': result2,
            'message': "Expense successfully processed."
        }), 200 # Success for both routes

        # if response.status_code == 200:
        #     return jsonify({"message": "Expense processed successfully"}), 200
        # else:
        #     return jsonify({"error": "Failed to store expense in itinerary"}), response.status_code
    except requests.exceptions.RequestException as e:
            return jsonify({'error': f"Error occured for one of the services: {str(e)}"}), 501
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "expense-management"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
