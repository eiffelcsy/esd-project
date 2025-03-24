from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(100), nullable=False, unique=True)
    recommendations = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, trip_id, recommendations=None):
        self.trip_id = trip_id
        self.recommendations = recommendations
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 