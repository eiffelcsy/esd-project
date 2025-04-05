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

# Gets conversion rates for local currency
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
        return jsonify({'result': rates["result"], 'rates': rates["conversion_rates"]})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Converts a given amount of currency from base currency to target currency
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

# Gets the total amount spent for a trip and splits the total according to the users in the trip
# To add: Split expenses by user -> Show which user owes how much to who
@app.route('/finance/calculate/<trip_id>', methods=['GET'])
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
            }), 200 # Works, but result just means that the database doesn't have any records for the trip
        
        # Initialize total amount
        total_amount = 0
        # Get the list of users for a given trip
        users = []
        for e in expenses:
            if e.user_id not in users:
                users.append(e.user_id)
            
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
        
        # Split the expenses by person
        split_details = {}
        for u in users:
            user_expenditure = 0 # Initialize total amount spent by the user
            descriptions = [] # Initialize the descriptions of user expenditures

            for e in expenses:
                if e.user_id == u:
                    # Add the user's expenditure to the user's running total
                    if e.base_currency == base_currency:
                        user_expenditure += e.amount
                    else:
                        # Convert to base currency using your ExchangeRateClient
                        converted_amount = ExchangeRateClient.convert_amount(
                            from_currency=e.base_currency,
                            to_currency=base_currency,
                            amount=e.amount
                        )
                        user_expenditure += converted_amount
                    
                    # Add user expenditure description
                    descriptions.append(e.description)

                    split_details[u] = {
                        'total_spent': round(user_expenditure, 2),
                        'descriptions': descriptions
                    }

                    # Show the split amount to be paid by other users (total amount split between all users in a trip)
                    split_details[u].update({
                        'split_amount': round((user_expenditure/(len(users))), 2),
                        'payers': [user for user in users if user != u]
                    })

        return jsonify({
            'trip_id': trip_id,
            'total_amount': round(total_amount, 2),  # Round to 2 decimal places
            'currency': base_currency,
            'users': len(users),
            'split_details': split_details 
        }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# Add route to add expense into database
@app.route('/finance/<trip_id>/add', methods=['POST'])
def add_expense(trip_id):
    try:
        data = request.get_json()
        required_fields = ['user_id', 'date', 'location', 'amount', 'base_currency', 'description', 'is_paid']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        try:
            new_expense = Expense(trip_id, **data)
            db.session.add(new_expense)
            db.session.commit()
        except:
            return jsonify(
            {
                "result": "fail",
                "data": {
                    "trip_id": trip_id
                },
                "message": "An error occured creating the expense."
            }
            ), 500
        # Successful addition
        return jsonify(
            {
                "result": "success",
                "data": new_expense.json(),
                "message": "Expense created successfully"
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Add route to update user payment status for a given trip once all users have paid
@app.route('/finance/update/<trip_id>', methods=['PUT'])
def update_payment_status(trip_id):
    try:
        stmt = db.update(Expense).where(Expense.trip_id == trip_id).values(is_paid=True)
        db.session.execute(stmt)
        db.session.commit()
        
        return jsonify({
            'result': "Success",
            'message': "Payment status successfully updated"
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)