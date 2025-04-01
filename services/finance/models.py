from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Expense(db.Model):
    __tablename__ = 'expenses'

    trip_id = db.Column(db.String(64), primary_key=True, nullable=False)
    user_id = db.Column(db.String(64), primary_key=True, nullable=False)
    date = db.Column(db.Date, server_default=db.func.now(), primary_key=True, nullable=False)
    location = db.Column(db.String(64), primary_key=True, nullable=False)
    amount = db.Column(db.Float, primary_key=True, nullable=False)
    base_currency = db.Column(db.String(3), primary_key=True, nullable=False, default='SGD')
    description = db.Column(db.String(64))
    is_paid = db.Column(db.Boolean, default=False)

    def __init__(self, trip_id, user_id, date, location, amount, base_currency, description, is_paid):
        self.trip_id = trip_id
        self.user_id = user_id
        self.date = date
        self.location = location
        self.amount = amount
        self.base_currency = base_currency
        self.description = description
        self.is_paid = is_paid

    def json(self):
        return {
            "trip_id": self.trip_id, 
            "user_id": self.user_id, 
            "date": self.date.isoformat() if self.date else None, 
            "location": self.location,
            "amount": self.amount, 
            "base_currency": self.base_currency, 
            "description": self.description, 
            "is_paid": self.is_paid
        }