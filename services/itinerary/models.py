from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Itinerary(db.Model):
    __tablename__ = 'itineraries'
    trip_id = db.Column(db.String, primary_key=True)
    destination = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    daily_activities = db.Column(db.JSON, nullable=False, default={})
