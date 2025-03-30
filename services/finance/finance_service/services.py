from models import db, Expense
from schemas import ExpenseCreate
from typing import List

class ExpenseService:
    @staticmethod
    def create_expense(expense_data: ExpenseCreate) -> Expense:
        new_expense = Expense(**expense_data.model_dump())
        db.session.add(new_expense)
        db.session.commit()
        return new_expense

    @staticmethod
    def get_expenses_by_trip(trip_id: str) -> List[Expense]:
        return Expense.query.filter_by(trip_id=trip_id).all()

    @staticmethod
    def get_total_spent(trip_id: str) -> float:
        expenses = Expense.query.filter_by(trip_id=trip_id).all()
        return sum(expense.amount for expense in expenses)