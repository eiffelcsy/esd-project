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
    """Get calendar for a specific group"""
    calendar = Calendar.query.filter_by(group_id=group_id).first()
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    return jsonify(calendar.to_dict()), 200

@app.route('/api/calendars/group/<int:group_id>', methods=['DELETE'])
def delete_group_calendar(group_id):
    """Delete calendar for a specific group"""
    calendar = Calendar.query.filter_by(group_id=group_id).first()
    if not calendar:
        return jsonify({'error': 'Calendar not found'}), 404
    
    try:
        db.session.delete(calendar)
        db.session.commit()
        return jsonify({'message': f'Calendar for group {group_id} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5006))
    app.run(host='0.0.0.0', port=port, debug=True) 