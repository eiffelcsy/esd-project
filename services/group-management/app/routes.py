from flask import request, jsonify
from datetime import datetime
from app.models import db, GroupRequest
from app.services import UserService, GroupService, CalendarService

def register_routes(app):
    @app.route('/api/groups', methods=['POST'])
    def create_group():
        """
        Composite endpoint for group creation:
        1. Validates/creates users from emails
        2. Creates group
        3. Creates calendar for the group
        """
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'members', 'startDateRange', 'endDateRange']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Extract data
        name = data['name']
        description = data.get('description', '')
        member_emails = data['members']
        
        if not member_emails:
            return jsonify({'error': 'At least one member email is required'}), 400
        
        # Parse dates
        try:
            start_date_range = datetime.fromisoformat(data['startDateRange'])
            end_date_range = datetime.fromisoformat(data['endDateRange'])
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
            
        # Step 1: Validate/create all users
        user_ids = []
        creator_id = None
        
        for email in member_emails:
            is_valid, user_data = UserService.validate_or_create_user(email)
            if not is_valid:
                return jsonify(user_data), 400
            user_ids.append(user_data['user_id'])
            if not creator_id:  # First user becomes the creator
                creator_id = user_data['user_id']
            
        # Create a record of this request
        group_request = GroupRequest(
            name=name,
            description=description,
            created_by=creator_id,
            users=user_ids,
            start_date_range=start_date_range,
            end_date_range=end_date_range,
            status='pending'
        )
        
        db.session.add(group_request)
        db.session.commit()
        
        # Step 2: Create group in group service
        success, group_data = GroupService.create_group(
            name=name,
            description=description,
            created_by=creator_id,
            users=user_ids
        )
        
        # For testing purposes, create a mock group response if service is not available
        if not success and 'GROUP_SERVICE_URL not configured' in group_data.get('error', ''):
            group_data = {
                "id": group_request.id, 
                "name": name,
                "description": description,
                "created_by": creator_id,
                "users": user_ids
            }
            success = True
            
        if not success:
            group_request.status = 'failed'
            group_request.description = f"{description} - Failed: {group_data.get('error', 'Group creation failed')}"
            db.session.commit()
            return jsonify(group_data), 400
            
        # Get group ID from the response
        group_id = group_data.get('id', group_request.id)
        group_request.group_id = group_id
            
        # Step 3: Create calendar for the group
        success, calendar_data = CalendarService.create_calendar(
            group_id=group_id,
            start_date_range=data['startDateRange'],
            end_date_range=data['endDateRange']
        )
        
        if not success:
            group_request.status = 'partial'
            group_request.description = f"{description} - Partial: {calendar_data.get('error', 'Calendar creation failed')}"
            db.session.commit()
            # We don't return error here as the group was created successfully
            # Just include warning in the response
            response = {
                **group_data,
                'warning': calendar_data.get('error', 'Calendar creation failed'),
                'status': 'partial'
            }
            return jsonify(response), 201
            
        # Everything succeeded
        group_request.status = 'completed'
        db.session.commit()
        
        # Combine responses for a complete picture
        response = {
            **group_data,
            'calendar': calendar_data,
            'status': 'completed'
        }
        
        return jsonify(response), 201
    
    @app.route('/api/groups/requests', methods=['GET'])
    def get_group_requests():
        """Get all group creation requests with their status"""
        requests = GroupRequest.query.all()
        return jsonify([req.to_dict() for req in requests]), 200
    
    @app.route('/api/groups/requests/<int:request_id>', methods=['GET'])
    def get_group_request(request_id):
        """Get a specific group creation request by ID"""
        group_request = GroupRequest.query.get_or_404(request_id)
        return jsonify(group_request.to_dict()), 200
        
    @app.route('/api/groups/<int:group_id>', methods=['DELETE'])
    def delete_group(group_id):
        """
        Composite endpoint for group deletion:
        1. Delete group from Group service
        2. Delete calendar from Calendar service
        3. Delete the local group request record if both services succeed
        """
        # First find the group request in our database
        group_request = GroupRequest.query.filter_by(group_id=group_id).first()
        
        if not group_request:
            return jsonify({'error': f'Group with ID {group_id} not found in our records'}), 404
            
        # Step 1: Delete the calendar from Calendar service first
        calendar_success, calendar_response = CalendarService.delete_calendar(group_id)
        
        # Step 2: Delete the group from Group service
        group_success, group_response = GroupService.delete_group(group_id)
        
        # Prepare the response based on the results
        if group_success and calendar_success:
            # Both services successfully deleted the group and calendar
            # Now we can delete the record from our database
            db.session.delete(group_request)
            db.session.commit()
            
            return jsonify({
                'message': f'Group {group_id} and its calendar successfully deleted',
                'group_response': group_response,
                'calendar_response': calendar_response
            }), 200
            
        elif group_success and not calendar_success:
            # Group was deleted but calendar deletion failed
            # Mark as partially deleted but don't remove the record
            group_request.status = 'partial_deleted'
            db.session.commit()
            
            return jsonify({
                'message': f'Group {group_id} deleted but calendar deletion failed',
                'group_response': group_response,
                'calendar_response': calendar_response,
                'warning': 'Calendar deletion failed, may need manual cleanup'
            }), 207  # Multi-Status
            
        elif not group_success and calendar_success:
            # Calendar was deleted but group deletion failed
            # Mark as partially deleted but don't remove the record
            group_request.status = 'calendar_deleted'
            db.session.commit()
            
            return jsonify({
                'error': f'Failed to delete group {group_id} but calendar was deleted',
                'group_response': group_response,
                'calendar_response': calendar_response
            }), 500
            
        else:
            # Both deletions failed
            return jsonify({
                'error': 'Failed to delete both group and calendar',
                'group_response': group_response, 
                'calendar_response': calendar_response
            }), 500 