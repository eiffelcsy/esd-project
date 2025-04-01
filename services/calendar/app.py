from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure the database
database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@calendar-db:5432/calendar_db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Calendar model
class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False)
    start_date_range = db.Column(db.DateTime, nullable=False)
    end_date_range = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'start_date_range': self.start_date_range.isoformat(),
            'end_date_range': self.end_date_range.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# User Availability model
class UserAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendar.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    available_dates = db.Column(db.JSON, nullable=False)  # Store dates as ISO strings in an array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'calendar_id': self.calendar_id,
            'user_id': self.user_id,
            'available_dates': self.available_dates,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Create tables
with app.app_context():
    db.create_all()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "calendar"}), 200

@app.route('/api/calendars', methods=['POST'])
def create_calendar():
    """Create a new calendar for a group"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['group_id', 'start_date_range', 'end_date_range']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        # Parse dates
        start_date = datetime.fromisoformat(data['start_date_range'])
        end_date = datetime.fromisoformat(data['end_date_range'])
        
        # Create calendar
        calendar = Calendar(
            group_id=data['group_id'],
            start_date_range=start_date,
            end_date_range=end_date
        )
        
        db.session.add(calendar)
        db.session.commit()
        
        return jsonify(calendar.to_dict()), 201
        
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendars/group/<int:group_id>', methods=['GET'])
def get_group_calendar(group_id):
    """Get calendar and all user availabilities for a specific group"""
    calendar = Calendar.query.filter_by(group_id=group_id).first()
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404

    # Get all user availabilities for this calendar
    availabilities = UserAvailability.query.filter_by(calendar_id=calendar.id).all()
    
    response = {
        **calendar.to_dict(),
        'user_availabilities': [avail.to_dict() for avail in availabilities]
    }
    
    return jsonify(response), 200

@app.route('/api/calendars/group/<int:group_id>', methods=['DELETE'])
def delete_group_calendar(group_id):
    """Delete calendar and all associated user availabilities for a specific group"""
    calendar = Calendar.query.filter_by(group_id=group_id).first()
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    
    try:
        # Delete associated user availabilities first
        UserAvailability.query.filter_by(calendar_id=calendar.id).delete()
        
        # Delete the calendar
        db.session.delete(calendar)
        db.session.commit()
        return jsonify({'message': f'Calendar for group {group_id} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendars/<int:calendar_id>/availability', methods=['GET'])
def get_calendar_availability(calendar_id):
    """Get all user availabilities for a specific calendar"""
    calendar = Calendar.query.get_or_404(calendar_id)
    availabilities = UserAvailability.query.filter_by(calendar_id=calendar_id).all()
    
    return jsonify({
        'calendar': calendar.to_dict(),
        'availabilities': [avail.to_dict() for avail in availabilities]
    }), 200

@app.route('/api/calendars/<int:calendar_id>/availability', methods=['POST'])
def update_calendar_availability(calendar_id):
    """Update user availability for a specific calendar"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['user_id', 'available_dates']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        # Update or create user availability
        availability = UserAvailability.query.filter_by(
            calendar_id=calendar_id,
            user_id=data['user_id']
        ).first()

        if availability:
            availability.available_dates = data['available_dates']
        else:
            availability = UserAvailability(
                calendar_id=calendar_id,
                user_id=data['user_id'],
                available_dates=data['available_dates']
            )
            db.session.add(availability)

        db.session.commit()
        return jsonify(availability.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5006))
    app.run(host='0.0.0.0', port=port) 