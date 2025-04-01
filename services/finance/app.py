from flask import Flask, request, jsonify
from flask_cors import CORS
from client import ExchangeRateClient
from models import Expense, db
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'mysql+mysqlconnector://is213@host.docker.internal:3306/expenses')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize the database
db.init_app(app)

# Routes to check health (BOTH WORK)
@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "User Service API. Use /health for health check."}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "finance"}), 200

# WORKS
@app.route('/finance/rates', methods=['GET'])
def get_rates():
    # TEST response
    if False:
        response = requests.get(f"{BASE_URL}/{API_KEY}/latest/SGD").json()
        return jsonify({"result": "success", "conversion_rates": response["conversion_rates"]})
    base_currency = request.args.get('base', 'SGD')
    target_currencies = request.args.get('symbols')
    
    try:
        rates = ExchangeRateClient.get_latest_rates(base_currency, target_currencies)
        return jsonify(rates)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# WORKS (smh)
@app.route('/finance/convert/<string:from_currency>/<string:to_currency>/<float:amount>', methods=['GET'])
def convert_currency(from_currency, to_currency, amount):
    
    if not all([from_currency, to_currency, amount]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        converted_amount = ExchangeRateClient.convert_amount(from_currency.upper(), to_currency.upper(), amount)
        return jsonify({
            'from': from_currency.upper(),
            'to': to_currency.upper(),
            'original_amount': amount,
            'converted_amount': converted_amount,
            'rate': converted_amount / amount
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# WORKS
@app.route('/finance/calculate/<string:trip_id>', methods=['GET'])
def get_all_expenses(trip_id):
    try:
        # Get the base currency from query params, default to SGD
        base_currency = request.args.get('base', 'SGD')

        stmt = db.select(Expense).where(Expense.trip_id == trip_id)
        expenses = db.session.scalars(stmt).all()  # Explicit conversion to list
            
        if not expenses:
            return jsonify({
                'trip_id': trip_id,
                'message': 'No expenses found for this trip',
                'total_amount': 0,
                'currency': base_currency
            }), 200
        
        # Initialize total amount
        total_amount = 0
            
        # Convert all expenses to base currency and sum them up
        for expense in expenses:
            if expense.base_currency == base_currency:
                total_amount += expense.amount
            else:
                # Convert to base currency using your ExchangeRateClient
                converted_amount = ExchangeRateClient.convert_amount(
                    from_currency=expense.base_currency,
                    to_currency=base_currency,
                    amount=expense.amount
                )
                total_amount += converted_amount
            
        return jsonify({
            'trip_id': trip_id,
            'total_amount': round(total_amount, 2),  # Round to 2 decimal places
            'currency': base_currency,
            'expense_count': len(expenses)
        }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    #print("Registered routes:", app.url_map) # Test for registered routes (actually registers)
    app.run(host='0.0.0.0', port=5006)