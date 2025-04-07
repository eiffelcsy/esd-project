from flask import request, jsonify, session
from app.models import db, Calendar, UserAvailability
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_routes(app):
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
            start_date_str = data['start_date_range']
            end_date_str = data['end_date_range']
            
            # Remove 'Z' suffix if present (UTC indicator in ISO format)
            if isinstance(start_date_str, str) and start_date_str.endswith('Z'):
                start_date_str = start_date_str[:-1]
            if isinstance(end_date_str, str) and end_date_str.endswith('Z'):
                end_date_str = end_date_str[:-1]
            
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
            
            # Create calendar
            calendar = Calendar(
                group_id=data['group_id'],
                start_date_range=start_date,
                end_date_range=end_date
            )
            
            db.session.add(calendar)
            db.session.commit()
            
            return jsonify(calendar.to_dict()), 201
            
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        except Exception as e:
            logger.error(f"Error creating calendar: {e}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/calendars', methods=['GET'])
    def get_all_calendars():
        """Get all calendars (temporary route)"""
        try:
            calendars = Calendar.query.all()
            return jsonify([calendar.to_dict() for calendar in calendars]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/calendars/group/<int:group_id>', methods=['GET'])
    def get_group_calendar(group_id):
        """Get calendar and all user availabilities for a specific group"""
        try:
            logger.info(f"Fetching calendar for group {group_id}")
            calendar = Calendar.query.filter_by(group_id=group_id).first()
            
            # If no calendar exists, create one with default date range
            if not calendar:
                logger.info(f"No calendar found for group {group_id}, creating default calendar")
                today = datetime.utcnow()
                calendar = Calendar(
                    group_id=group_id,
                    start_date_range=today,
                    end_date_range=today.replace(month=today.month + 1)
                )
                db.session.add(calendar)
                db.session.commit()

            # Get all user availabilities for this calendar
            availabilities = UserAvailability.query.filter_by(calendar_id=calendar.id).all()
            
            response = {
                **calendar.to_dict(),
                'user_availabilities': [avail.to_dict() for avail in availabilities]
            }
            
            logger.info(f"Successfully retrieved calendar for group {group_id}")
            return jsonify(response), 200

        except Exception as e:
            logger.error(f"Error fetching calendar for group {group_id}: {e}")
            return jsonify({'error': f'Error fetching calendar: {str(e)}'}), 500

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
