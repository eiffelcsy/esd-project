from flask import request, jsonify
from app.models import db, Expense, UserReadiness
from app.client import ExchangeRateClient, EmailClient, TripClient
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_routes(app):
    # Routes to check health
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({"message": "Finance Service API. Use /health for health check."}), 200

    # Gets conversion rates for local currency
    @app.route('/api/finance/rates', methods=['GET'])
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
    @app.route('/api/finance/convert/<string:from_currency>/<string:to_currency>/<float:amount>', methods=['GET'])
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

    # Add a new endpoint to get all expenses for a trip without calculations
    @app.route('/api/finance/expenses/<trip_id>', methods=['GET'])
    def get_expenses_without_calculation(trip_id):
        try:
            # Get all expenses for the specified trip
            stmt = db.select(Expense).where(Expense.trip_id == trip_id)
            expenses = db.session.scalars(stmt).all()
            
            if not expenses:
                return jsonify({
                    'trip_id': trip_id,
                    'message': 'No expenses found for this trip',
                    'expenses': []
                }), 200
            
            # Convert expenses to JSON format
            result = [expense.json() for expense in expenses]
            
            return jsonify({
                'trip_id': trip_id,
                'expenses': result
            }), 200
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # Gets the total amount spent for a trip and splits the total according to the users in the trip
    @app.route('/api/finance/calculate/<trip_id>', methods=['GET'])
    def get_all_expenses(trip_id):
        try:
            # Get the base currency from query params, default to SGD
            base_currency = request.args.get('base', 'SGD')

            stmt = db.select(Expense).where(Expense.trip_id == trip_id)
            expenses = db.session.scalars(stmt).all()  
                
            if not expenses:
                return jsonify({
                    'trip_id': trip_id,
                    'message': 'No expenses found for this trip',
                    'total_amount': 0,
                    'currency': base_currency
                }), 200 
            
            # Initialize total amount
            total_amount = 0
            
            # Get the list of users for a given trip
            users = []
            for e in expenses:
                if e.user_id not in users:
                    users.append(e.user_id)
                if e.payee_id and e.payee_id not in users:
                    users.append(e.payee_id)
                
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
            
            # Get user names/emails from the UserReadiness model for better display
            users_info = {}
            try:
                stmt = db.select(UserReadiness).where(UserReadiness.trip_id == trip_id)
                user_readiness_records = db.session.scalars(stmt).all()
                for record in user_readiness_records:
                    users_info[record.user_id] = {
                        'name': record.name or f"User {record.user_id}",
                        'email': record.email
                    }
            except Exception as e:
                print(f"Error getting user readiness records: {str(e)}")
                
            # Create balance sheet to track how much each user has spent and owes
            balances = {user_id: 0 for user_id in users}
            
            # Calculate each user's expenditure and who they paid for
            for expense in expenses:
                # Convert amount to base currency if needed
                if expense.base_currency == base_currency:
                    amount = expense.amount
                else:
                    amount = ExchangeRateClient.convert_amount(
                        from_currency=expense.base_currency,
                        to_currency=base_currency,
                        amount=expense.amount
                    )
                
                # If expense has a specific payee, it means the payer (user_id) paid for the payee
                if expense.payee_id and expense.payee_id != 'all':
                    # Increase payer's balance (they are owed money)
                    balances[expense.user_id] += amount
                    # Decrease payee's balance (they owe money)
                    balances[expense.payee_id] -= amount
                else:
                    # If no specific payee or payee_id is 'all', split among all users evenly
                    payer_share = amount / len(users)
                    # The payer paid the full amount but only owes their share
                    balances[expense.user_id] += amount - payer_share
                    
                    # Everyone else owes their share to the payer
                    for user_id in users:
                        if user_id != expense.user_id:
                            balances[user_id] -= payer_share
            
            # Create settlement plan - who pays whom
            settlements = []
            # Sort users by balance (negative balances owe money, positive are owed money)
            sorted_users = sorted(users, key=lambda u: balances[u])
            
            # Simple approach: users with negative balances pay to users with positive balances
            i, j = 0, len(sorted_users) - 1
            while i < j:
                debtor = sorted_users[i]  # User who owes money (negative balance)
                creditor = sorted_users[j]  # User who is owed money (positive balance)
                
                if abs(balances[debtor]) < 0.01 or abs(balances[creditor]) < 0.01:
                    # Skip users with negligible balances
                    if abs(balances[debtor]) < 0.01:
                        i += 1
                    if abs(balances[creditor]) < 0.01:
                        j -= 1
                    continue
                
                # Amount to transfer is the minimum of what debtor owes and creditor is owed
                amount = min(abs(balances[debtor]), balances[creditor])
                
                if amount > 0:
                    # Create a settlement transaction
                    settlements.append({
                        'from': debtor,
                        'from_name': users_info.get(debtor, {}).get('name', f"User {debtor}"),
                        'to': creditor,
                        'to_name': users_info.get(creditor, {}).get('name', f"User {creditor}"),
                        'amount': round(amount, 2),
                        'currency': base_currency
                    })
                
                    # Update balances
                    balances[debtor] += amount
                    balances[creditor] -= amount
                
                # Move pointers if balances are settled
                if abs(balances[debtor]) < 0.01:
                    i += 1
                if abs(balances[creditor]) < 0.01:
                    j -= 1
            
            # Prepare response with settlement details
            response_data = {
                'trip_id': trip_id,
                'total_amount': round(total_amount, 2),
                'currency': base_currency,
                'users': len(users),
                'user_balances': {user_id: round(balance, 2) for user_id, balance in balances.items()},
                'user_names': {user_id: users_info.get(user_id, {}).get('name', f"User {user_id}") for user_id in users},
                'settlements': settlements
            }
            
            return jsonify(response_data), 200
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        
    # Add route to add expense into database
    @app.route('/api/finance/<trip_id>/add', methods=['POST'])
    def add_expense(trip_id):
        try:
            data = request.get_json()
            required_fields = ['user_id', 'date', 'location', 'amount', 'base_currency', 'description', 'is_paid', 'category']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

            # Ensure payee_id is present in data even if null
            if 'payee_id' not in data:
                data['payee_id'] = None

            try:
                new_expense = Expense(**data)
                db.session.add(new_expense)
                db.session.commit()
            except Exception as e:
                return jsonify(
                {
                    "result": "fail",
                    "data": {
                        "trip_id": trip_id
                    },
                    "message": "An error occured creating the expense. " + str(e) + " " + str(trip_id) + " " + str(data)
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
    @app.route('/api/finance/update/<trip_id>', methods=['PUT'])
    def update_payment_status(trip_id):
        try:
            # Get user ID from request body or query parameter
            data = request.get_json() or {}
            user_id = data.get('user_id') or request.args.get('user_id')
            
            if not user_id:
                return jsonify({
                    'error': 'Missing user_id parameter. Please provide a user_id in the request body or as a query parameter.'
                }), 400
            
            # Update user readiness status by calling the dedicated endpoint
            return update_readiness_status(trip_id, user_id)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        
    # Get all users and their readiness status for a trip
    @app.route('/api/finance/readiness/<trip_id>', methods=['GET'])
    def get_readiness_status(trip_id):
        try:
            print(f"Getting readiness status for trip: {trip_id}")
            # Get all user readiness records for the specified trip
            stmt = db.select(UserReadiness).where(UserReadiness.trip_id == trip_id)
            users = db.session.scalars(stmt).all()
            
            logger.info(f"Initial users query result: {users}")
            
            if not users:
                # If no users are found, try to fetch them from the group service
                try:
                    logger.info(f"No users found in database, trying to fetch from group service")
                    
                    # Get the trip details to get the group_id
                    trip_details = TripClient.get_trip_details(trip_id)
                    
                    if trip_details and 'group_id' in trip_details and trip_details['group_id']:
                        group_id = trip_details['group_id']
                        logger.info(f"Found group_id: {group_id} for trip_id: {trip_id}")
                        
                        # Use group_id to fetch users from group service
                        group_service_url = f"https://personal-ekdcuwio.outsystemscloud.com/GroupMicroservice/rest/GroupService/groups/{group_id}/users"
                        logger.info(f"Calling group service: {group_service_url}")
                        response = requests.get(group_service_url)
                        logger.info(f"Group service response status: {response.status_code}")
                        
                        if response.ok:
                            group_members = response.json()
                            logger.info(f"Group members from service: {group_members}")
                            
                            # Add each group member to our database
                            for member in group_members:
                                user_id = member
                                logger.info(f"Processing member: {user_id}")
                                
                                # Fetch user details from the user service
                                try:
                                    user_service_url = f"http://user-service:5001/api/users/{user_id}"
                                    logger.info(f"Calling user service: {user_service_url}")
                                    user_response = requests.get(user_service_url)
                                    logger.info(f"User service response status: {user_response.status_code}")
                                    
                                    user_data = {}
                                    if user_response.ok:
                                        user_data = user_response.json()
                                        logger.info(f"User data: {user_data}")
                                except Exception as e:
                                    logger.error(f"Error fetching user details from user service: {str(e)}")
                                    user_data = {}
                                
                                user_readiness = UserReadiness(
                                    trip_id=trip_id,
                                    user_id=user_id,
                                    name=user_data.get('first_name') + " " + user_data.get('last_name'),
                                    email=user_data.get('email', f"{user_id}@example.com"),  # Get email from user service
                                    ready=False
                                )
                                db.session.add(user_readiness)
                            
                            db.session.commit()
                            logger.info("Added users to database and committed")
                            
                            # Fetch the newly added users
                            stmt = db.select(UserReadiness).where(UserReadiness.trip_id == trip_id)
                            users = db.session.scalars(stmt).all()
                            logger.info(f"Users after adding to database: {users}")
                        else:
                            logger.error(f"Group service returned error: {response.text}")
                            return jsonify({
                                'trip_id': trip_id,
                                'message': f'No users found for this trip and could not fetch from group service. Status: {response.status_code}',
                                'users': []
                            }), 404
                    else:
                        logger.info(f"No group_id found for trip_id: {trip_id}")
                        return jsonify({
                            'trip_id': trip_id,
                            'message': 'No group_id associated with this trip',
                            'users': []
                        }), 404
                        
                except Exception as e:
                    logger.error(f"Exception during group service call: {str(e)}")
                    return jsonify({
                        'trip_id': trip_id,
                        'message': f'Error fetching users from group service: {str(e)}',
                        'users': []
                    }), 500
            
            # Convert users to JSON format
            result = [user.json() for user in users]
            logger.info(f"Final result: {result}")
            
            # Check if all users are ready
            all_ready = all(user.ready for user in users) if users else False
            
            return jsonify({
                'trip_id': trip_id,
                'users': result,
                'all_ready': all_ready
            }), 200
                
        except Exception as e:
            logger.error(f"Exception in get_readiness_status: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Update a user's readiness status
    @app.route('/api/finance/readiness/<trip_id>/<user_id>', methods=['PUT'])
    def update_readiness_status(trip_id, user_id):
        try:
            # Check if the user exists
            stmt = db.select(UserReadiness).where(UserReadiness.trip_id == trip_id, UserReadiness.user_id == user_id)
            user = db.session.scalars(stmt).first()
            
            if not user:
                # Try to get user info from request body
                data = request.get_json() or {}
                
                # Fetch user details from the user service
                try:
                    user_response = requests.get(f"http://user-service:5001/api/users/{user_id}")
                    user_data = {}
                    if user_response.ok:
                        user_data = user_response.json()
                except Exception as e:
                    print(f"Error fetching user details from user service: {str(e)}")
                    user_data = {}
                
                name = user_data.get('name', data.get('name', f"User {user_id}"))
                email = user_data.get('email', data.get('email', f"{user_id}@example.com"))
                
                # Create new user readiness record
                user = UserReadiness(
                    trip_id=trip_id,
                    user_id=user_id,
                    name=name,
                    email=email,
                    ready=True  # Set as ready since this is an update request
                )
                db.session.add(user)
            else:
                # Update existing user readiness status
                user.ready = True
            
            db.session.commit()
            
            # Check if all users are ready for this trip
            stmt = db.select(UserReadiness).where(UserReadiness.trip_id == trip_id)
            all_users = db.session.scalars(stmt).all()
            all_ready = all(u.ready for u in all_users) if all_users else False
            
            response_data = {
                'trip_id': trip_id,
                'user_id': user_id,
                'ready': True,
                'all_ready': all_ready
            }
            
            # If all users are ready, trigger settlement calculation and email notification
            if all_ready:
                try:
                    # Get settlement details
                    settlement_response = get_all_expenses(trip_id)
                    
                    # Check if the response has settlement data
                    if settlement_response and hasattr(settlement_response, '__getitem__') and settlement_response[1] == 200:
                        settlement_data = settlement_response[0].json
                        
                        # Send email notification with settlement details
                        email_sent = send_settlement_email(trip_id, settlement_data, all_users)
                        response_data['email_sent'] = email_sent
                except Exception as e:
                    response_data['settlement_error'] = str(e)
            
            return jsonify(response_data), 200
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Send email notification with settlement details
    def send_settlement_email(trip_id, settlement_data, users):
        try:
            # Use the EmailClient to send batch emails
            result = EmailClient.send_batch_settlement_emails(trip_id, settlement_data, users)
            
            # Return True if at least one email was sent successfully
            return len(result['success']) > 0
            
        except Exception as e:
            logger.error(f"Error sending settlement email: {str(e)}")
            return False

    # Get all trips for a user
    @app.route('/api/finance/test-trip-group/<trip_id>', methods=['GET'])
    def test_trip_group(trip_id):
        """Test endpoint to get a trip's group_id"""
        try:
            # Get the trip details
            trip_details = TripClient.get_trip_details(trip_id)
            
            if not trip_details:
                return jsonify({
                    'error': 'Failed to retrieve trip details'
                }), 404
                
            if 'group_id' not in trip_details or not trip_details['group_id']:
                return jsonify({
                    'trip_id': trip_id,
                    'message': 'No group_id associated with this trip',
                    'trip_details': trip_details
                }), 200
            
            group_id = trip_details['group_id']
            
            # Try to get group members
            try:
                group_service_url = f"https://personal-ekdcuwio.outsystemscloud.com/GroupMicroservice/rest/GroupService/groups/{group_id}/users"
                response = requests.get(group_service_url)
                
                if response.ok:
                    group_members = response.json()
                    return jsonify({
                        'trip_id': trip_id,
                        'group_id': group_id,
                        'group_members': group_members,
                        'trip_details': trip_details
                    }), 200
                else:
                    return jsonify({
                        'trip_id': trip_id,
                        'group_id': group_id,
                        'error': f'Failed to retrieve group members. Status: {response.status_code}',
                        'trip_details': trip_details
                    }), 200
            except Exception as e:
                return jsonify({
                    'trip_id': trip_id,
                    'group_id': group_id,
                    'error': f'Error retrieving group members: {str(e)}',
                    'trip_details': trip_details
                }), 200
            
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500 

    # Test endpoint to manually trigger a settlement email for a specific user
    @app.route('/api/finance/test-email/<trip_id>/<user_id>', methods=['GET'])
    def test_settlement_email(trip_id, user_id):
        try:
            # Get settlement details
            settlement_response = get_all_expenses(trip_id)
            
            if not settlement_response or not hasattr(settlement_response, '__getitem__') or settlement_response[1] != 200:
                return jsonify({
                    'error': 'Could not calculate settlement'
                }), 500
            
            settlement_data = settlement_response[0].json
            
            # Get user readiness record
            stmt = db.select(UserReadiness).where(UserReadiness.trip_id == trip_id, UserReadiness.user_id == user_id)
            user = db.session.scalars(stmt).first()
            
            if not user:
                return jsonify({
                    'error': f'User {user_id} not found for trip {trip_id}'
                }), 404
            
            # Prepare user-specific settlement details
            to_pay = []
            if 'settlements' in settlement_data:
                for settlement in settlement_data['settlements']:
                    if settlement['from'] == user_id:
                        # This user needs to pay
                        to_pay.append({
                            'to': settlement['to_name'],
                            'amount': settlement['amount'],
                            'currency': settlement['currency']
                        })
            
            # Get what others need to pay this user
            to_receive = []
            if 'settlements' in settlement_data:
                for settlement in settlement_data['settlements']:
                    if settlement['to'] == user_id:
                        # This user will receive payment
                        to_receive.append({
                            'from': settlement['from_name'],
                            'amount': settlement['amount'],
                            'currency': settlement['currency']
                        })
            
            # Get overall user balance
            user_balance = settlement_data.get('user_balances', {}).get(user_id, 0)
            
            # Prepare email content
            email_body = {
                'trip_id': trip_id,
                'user_name': user.name,
                'total_trip_amount': settlement_data.get('total_amount', 0),
                'currency': settlement_data.get('currency', 'SGD'),
                'user_balance': user_balance,
                'to_pay': to_pay,
                'to_receive': to_receive
            }
            
            # Send email
            response = EmailClient.send_settlement_email(
                to_email=user.email,
                subject=f'Trip Settlement Details for Trip #{trip_id} (TEST)',
                body=email_body
            )
            
            return jsonify({
                'message': 'Settlement email sent',
                'email_result': response,
                'email_content': email_body
            }), 200
            
        except Exception as e:
            logger.error(f"Error sending test settlement email: {str(e)}")
            return jsonify({'error': str(e)}), 500 