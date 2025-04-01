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

    def to_dict(self):
        return {
            'trip_id': self.trip_id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'location': self.location,
            'amount': self.amount,
            'base_currency': self.base_currency,
            'description': self.description,
            'is_paid': self.is_paid
        }