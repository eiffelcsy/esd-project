from flask_sqlalchemy import SQLAlchemy
import json

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
    category = db.Column(db.String(64))
    payee_id = db.Column(db.String(64), nullable=True)
    payees_json = db.Column(db.Text, nullable=True)  # Store payees as JSON array

    def __init__(self, trip_id, user_id, date, location, amount, base_currency, description, is_paid, category, payee_id=None, payees=None):
        self.trip_id = trip_id
        self.user_id = user_id
        self.date = date
        self.location = location
        self.amount = amount
        self.base_currency = base_currency
        self.description = description
        self.is_paid = is_paid
        self.category = category
        self.payee_id = payee_id  # Keep for backward compatibility
        
        # Handle new payees list
        if payees:
            if isinstance(payees, list):
                self.payees_json = json.dumps(payees)
            elif isinstance(payees, str):
                # In case a single payee is passed as string
                self.payees_json = json.dumps([payees])
        else:
            # If no payees provided but payee_id exists, convert it to payees format
            if payee_id and payee_id != "all":
                self.payees_json = json.dumps([payee_id])
            elif payee_id == "all" or not payee_id:
                self.payees_json = json.dumps(["all"])

    @property
    def payees(self):
        # Get payees as Python list
        if self.payees_json:
            try:
                return json.loads(self.payees_json)
            except:
                pass
        # Fallback to payee_id for backward compatibility
        if self.payee_id:
            return [self.payee_id]
        return ["all"]  # Default

    def json(self):
        return {
            "trip_id": self.trip_id, 
            "user_id": self.user_id, 
            "date": self.date.isoformat() if self.date else None, 
            "location": self.location,
            "amount": self.amount, 
            "base_currency": self.base_currency, 
            "description": self.description, 
            "is_paid": self.is_paid,
            "category": self.category,
            "payee_id": self.payee_id,
            "payees": self.payees
        }

class UserReadiness(db.Model):
    __tablename__ = 'user_readiness'
    
    trip_id = db.Column(db.String(64), primary_key=True, nullable=False)
    user_id = db.Column(db.String(64), primary_key=True, nullable=False)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128))
    ready = db.Column(db.Boolean, default=False)
    
    def __init__(self, trip_id, user_id, name=None, email=None, ready=False):
        self.trip_id = trip_id
        self.user_id = user_id
        self.name = name
        self.email = email
        self.ready = ready
        
    def json(self):
        return {
            "trip_id": self.trip_id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "ready": self.ready
        } 