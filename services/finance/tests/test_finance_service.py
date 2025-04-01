import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from finance_service.models import Expense, db
from finance_service.schemas import ExpenseCreate
from finance_service.services import ExpenseService
from finance_service.email_notifier import EmailNotifier
from sqlalchemy.exc import SQLAlchemyError

@pytest.fixture
def mock_expense():
    return Expense(
        trip_id='trip123',
        user_id='user456',
        date=date.today(),
        base_price=100.50,
        currency='SGD',
        description='Hotel',
        is_paid=False
    )

@pytest.fixture
def mock_db_session(mock_expense):
    with patch('expense_service.models.db.session') as mock_session:
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = [mock_expense]
        mock_session.query.return_value = mock_query
        yield mock_session

class TestExpenseService:
    def test_create_expense_success(self, mock_db_session):
        expense_data = ExpenseCreate(
            trip_id='trip123',
            user_id='user456',
            amount=100.50,
            currency='USD',
            description='Hotel'
        )
        
        result = ExpenseService.create_expense(expense_data)
        
        assert isinstance(result, Expense)
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_create_expense_db_error(self, mock_db_session):
        mock_db_session.commit.side_effect = SQLAlchemyError("DB error")
        expense_data = ExpenseCreate(
            trip_id='trip123',
            user_id='user456',
            amount=100.50
        )
        
        with pytest.raises(SQLAlchemyError):
            ExpenseService.create_expense(expense_data)

    def test_get_expenses_by_trip(self, mock_db_session, mock_expense):
        expenses = ExpenseService.get_expenses_by_trip('trip123')
        
        assert len(expenses) == 1
        assert expenses[0].user_id == 'user456'
        mock_db_session.query.assert_called_with(Expense)

    def test_get_total_spent(self, mock_db_session, mock_expense):
        total = ExpenseService.get_total_spent('trip123')
        
        assert total == 100.50

class TestEmailNotifier:
    @patch('expense_service.email_notifier.pika')
    def test_send_notification(self, mock_pika):
        notifier = EmailNotifier()
        notifier.send_notification('test@example.com', 'trip123', 150.75)
        
        mock_pika.URLParameters.assert_called()
        mock_pika.BlockingConnection.assert_called()
        
        # Verify message was published
        channel = mock_pika.BlockingConnection.return_value.channel.return_value
        channel.basic_publish.assert_called_once()