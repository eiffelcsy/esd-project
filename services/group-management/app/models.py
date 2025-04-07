from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class GroupRequest(db.Model):
    """
    Model for tracking group creation requests
    This is for the composite service to track the status of requests it processes
    """
    __tablename__ = 'group_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, nullable=False) # User ID
    users = db.Column(db.JSON, nullable=False) # Array of user IDs
    joined_users = db.Column(db.JSON, nullable=True, default=[]) # Array of user IDs that have joined
    start_date_range = db.Column(db.DateTime, nullable=False)
    end_date_range = db.Column(db.DateTime, nullable=False)
    group_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'users': self.users,
            'joined_users': self.joined_users if self.joined_users else [self.created_by],
            'pending_users': [u for u in self.users if str(u) != str(self.created_by) and (not self.joined_users or u not in self.joined_users)],
            'start_date_range': self.start_date_range.isoformat() if self.start_date_range else None,
            'end_date_range': self.end_date_range.isoformat() if self.end_date_range else None,
            'group_id': self.group_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 