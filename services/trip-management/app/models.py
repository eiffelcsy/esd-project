from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

# Initialize database
db = SQLAlchemy()

class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, nullable=True)
    city = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    itinerary_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'city': self.city,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'itinerary_id': self.itinerary_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    recommendations_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationship with Trip
    trip = db.relationship('Trip', backref=db.backref('recommendations', lazy=True))
    
    @property
    def recommendations(self):
        """Get the recommendations object from JSON"""
        try:
            return json.loads(self.recommendations_json)
        except (json.JSONDecodeError, TypeError):
            return {}
            
    @recommendations.setter
    def recommendations(self, value):
        """Store the recommendations object as JSON"""
        if value is None:
            self.recommendations_json = '{}'
        elif isinstance(value, dict) or isinstance(value, list):
            self.recommendations_json = json.dumps(value)
        elif isinstance(value, str):
            # Make sure it's valid JSON
            try:
                json.loads(value)
                self.recommendations_json = value
            except json.JSONDecodeError:
                self.recommendations_json = '{}'
        else:
            self.recommendations_json = '{}'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 