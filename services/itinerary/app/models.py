from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize database
db = SQLAlchemy()

class Itinerary(db.Model):
    __tablename__ = 'itineraries'
    trip_id = db.Column(db.String, primary_key=True)
    destination = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    daily_activities = db.Column(db.JSON, nullable=False, default={})
    
    def to_dict(self):
        return {
            "tripId": self.trip_id,
            "destination": self.destination,
            "startDate": self.start_date.isoformat(),
            "endDate": self.end_date.isoformat(),
            "dailyActivities": self.daily_activities
        }

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    trip_id = db.Column(db.String, primary_key=True)
    destination = db.Column(db.String, nullable=False)
    attractions = db.Column(db.JSON, nullable=False, default=[])
    restaurants = db.Column(db.JSON, nullable=False, default=[])
    activities = db.Column(db.JSON, nullable=False, default=[])
    events = db.Column(db.JSON, nullable=False, default=[])
    tips = db.Column(db.JSON, nullable=False, default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "tripId": self.trip_id,
            "destination": self.destination,
            "recommendations": {
                "attractions": self.attractions,
                "restaurants": self.restaurants,
                "activities": self.activities,
                "events": self.events,
                "tips": self.tips
            }
        } 