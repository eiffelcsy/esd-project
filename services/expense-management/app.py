from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes with all origins
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    """Process and forward expense data to the Finance service."""
    expense_data = request.get_json()

    # Validate required fields
    required_fields = ['trip_id', 'user_id', 'date', 'location', 'amount', 'base_currency', 'description', 'is_paid', 'category']
    missing_fields = [field for field in required_fields if field not in expense_data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Add payee_id if not present
    if 'payee_id' not in expense_data:
        expense_data['payee_id'] = None

    # Forward the expense data to the Finance service
    try:
        response = requests.post(
            f"http://finance:5008/api/finance/{expense_data['trip_id']}/add",
            json=expense_data,
            timeout=5
        )
        response.raise_for_status()
        result = response.json()

        return jsonify({
            'result': result,
            'message': "Expense successfully processed."
        }), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Error communicating with finance service: {str(e)} Response: {response.json()}"}), 501
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/expenses/<trip_id>', methods=['GET'])
def get_trip_expenses(trip_id):
    """Get all expenses for a specific trip without calculations."""
    try:
        # Get expenses from Finance service
        response = requests.get(
            f"http://finance:5008/api/finance/expenses/{trip_id}",
            timeout=5
        )
        response.raise_for_status()
        result = response.json()

        return jsonify(result), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Error communicating with finance service: {str(e)}"}), 501
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/expenses/convert/<string:from_currency>/<string:to_currency>/<float:amount>', methods=['GET'])
def convert_currency(from_currency, to_currency, amount):
    """Convert currency using the finance service."""
    try:
        print(f"Attempting currency conversion: {from_currency} to {to_currency}, amount: {amount}")
        # Forward the conversion request to the Finance service
        response = requests.get(
            f"http://finance:5008/api/finance/convert/{from_currency}/{to_currency}/{amount}",
            timeout=5
        )
        print(f"Finance service response status: {response.status_code}")
        response.raise_for_status()
        result = response.json()
        print(f"Conversion result: {result}")

        # Ensure we return in the expected format
        if isinstance(result, dict) and 'rate' in result:
            return jsonify(result), 200
        elif isinstance(result, dict) and 'error' in result:
            return jsonify(result), 400
        else:
            # If the response doesn't contain a rate, create one
            return jsonify({
                'rate': float(result) if isinstance(result, (int, float, str)) else 1.0,
                'from': from_currency,
                'to': to_currency
            }), 200

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with finance service: {str(e)}")
        return jsonify({
            'error': f"Error communicating with finance service: {str(e)}",
            'rate': 1.0,  # Fallback rate
            'from': from_currency,
            'to': to_currency
        }), 200  # Return 200 with fallback rate instead of error
    except Exception as e:
        print(f"Unexpected error in currency conversion: {str(e)}")
        return jsonify({
            'error': f"An error occurred: {str(e)}",
            'rate': 1.0,  # Fallback rate
            'from': from_currency,
            'to': to_currency
        }), 200  # Return 200 with fallback rate instead of error

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "expense-management"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)
