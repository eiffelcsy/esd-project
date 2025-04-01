from flask import Blueprint, request, jsonify
from services import ExpenseService
from schemas import ExpenseCreate, ExpenseResponse
from email_notifier import EmailNotifier
from pydantic import ValidationError

# Create a blueprint to automatically assign the url prefix to all routes
bp = Blueprint('expense', __name__, url_prefix='/expenses')

# Register required routes
@bp.route('/', methods=['POST'])
def add_expense():
    try:
        expense_data = ExpenseCreate(**request.json)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    expense = ExpenseService.create_expense(expense_data)
    return jsonify(ExpenseResponse(**expense.to_dict()).model_dump()), 201

@bp.route('/<trip_id>', methods=['GET'])
def get_trip_expenses(trip_id: str):
    expenses = ExpenseService.get_expenses_by_trip(trip_id)
    return jsonify([ExpenseResponse(**exp.to_dict()).model_dump() for exp in expenses])

@bp.route('/<trip_id>/total', methods=['GET'])
def get_trip_total(trip_id: str):
    total = ExpenseService.get_total_spent(trip_id)
    return jsonify({'trip_id': trip_id, 'total_amount': total})

@bp.route('/<trip_id>/notify', methods=['POST'])
def notify_payment(trip_id: str):
    user_email = request.json.get('email')
    if not user_email:
        return jsonify({'error': 'Email is required'}), 400
    
    total = ExpenseService.get_total_spent(trip_id)
    notifier = EmailNotifier()
    notifier.send_notification(user_email, trip_id, total)
    
    return jsonify({'message': 'Notification sent successfully'})