from flask import request, jsonify
from datetime import datetime
from app.models import db, GroupRequest
from app.services import UserService, GroupService, CalendarService
import os
import requests

def register_routes(app):
    @app.route('/api/groups', methods=['POST'])
    def create_group():
        """
        Composite endpoint for group creation:
        1. Validates user exists
        2. Creates group (only creator is added, others are invited)
        3. Creates calendar for the group
        """
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'createdBy', 'startDateRange', 'endDateRange']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Extract data
        name = data['name']
        description = data.get('description', '')
        created_by = data['createdBy']
        
        # Get invited users (excluding the creator who will be added automatically)
        invited_users = []
        if 'users' in data and data['users']:
            # Convert users to integers where needed
            invited_users = [user for user in data['users'] if str(user) != str(created_by)]
        
        # Parse dates
        try:
            start_date_range = datetime.fromisoformat(data['startDateRange'])
            end_date_range = datetime.fromisoformat(data['endDateRange'])
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
            
        # Create a record of this request - store all users (creator + invited)
        users_to_store = [str(created_by)] + invited_users
        group_request = GroupRequest(
            name=name,
            description=description,
            created_by=created_by,
            users=users_to_store,
            joined_users=[created_by],  # Initialize with creator as joined
            start_date_range=start_date_range,
            end_date_range=end_date_range,
            status='pending'
        )
        
        db.session.add(group_request)
        db.session.commit()
        
        # Step 1: Validate user exists
        is_valid, user_data = UserService.validate_user(created_by)
        if not is_valid:
            group_request.status = 'failed'
            group_request.description = f"{description} - Failed: {user_data.get('error', 'User validation failed')}"
            db.session.commit()
            return jsonify(user_data), 400
            
        # Step 2: Create group in group service (only with creator)
        print(f"DEBUG Before GroupService.create_group: created_by={created_by}, invited_users={invited_users}")
        success, group_data = GroupService.create_group(
            name=name,
            description=description,
            created_by=created_by,
        )
        print(f"DEBUG After GroupService.create_group: success={success}, group_data={group_data}, type={type(group_data)}")
            
        # Get group ID from the response
        if isinstance(group_data, dict):
            print(f"DEBUG group_data is a dictionary: {group_data}")
            group_id = group_data.get('id') or group_data.get('group_id')
            if not group_id:
                group_id = group_request.id  # Use request ID as fallback
                group_data["id"] = group_id
                print(f"DEBUG Using request ID as fallback: {group_id}")
        else:
            # If group_data is an integer (or something else), assume it's the group ID
            print(f"DEBUG group_data is not a dictionary. Type: {type(group_data)}, Value: {group_data}")
            group_id = int(group_data) if group_data else group_request.id
            # Convert to dictionary
            group_data = {
                "id": group_id,
                "name": name,
                "description": description,
                "created_by": created_by,
                "invited_users": invited_users,
                "active_users": [created_by],  # Only creator is an active member
                "note": "Response converted from non-dictionary value"
            }
            print(f"DEBUG Created dictionary from non-dictionary value: {group_data}")
            
        # Ensure group_id is not null - use request id as absolute fallback
        if group_id is None:
            group_id = group_request.id
            print(f"DEBUG group_id was None, using request ID as absolute fallback: {group_id}")
            group_data["id"] = group_id
            
        # Update the request with the group ID
        print(f"DEBUG Setting group_request.group_id = {group_id}")
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
            'status': group_request.status,
            'invited_users': invited_users,  # Include list of invited users
            'active_users': [created_by]     # Only creator is active initially
        }
        
        return jsonify(response), 201
    
    @app.route('/api/groups/<int:group_id>/join', methods=['POST'])
    def join_group(group_id):
        """
        Endpoint for a user to join a group they've been invited to
        """
        data = request.get_json()
        
        # Validate required fields
        if 'user_id' not in data:
            return jsonify({'error': 'user_id is required'}), 400
            
        user_id = data['user_id']
        
        # First, verify the group exists in our records
        group_request = GroupRequest.query.filter_by(group_id=group_id).first()
        if not group_request:
            return jsonify({'error': f'Group with ID {group_id} not found in our records'}), 404
            
        # Check if user is in the invited list (convert to strings for comparison)
        users_list = [str(u) for u in group_request.users]
        if str(user_id) not in users_list:
            return jsonify({'error': 'User is not invited to this group'}), 403
            
        # Check if user has already joined
        if group_request.joined_users and str(user_id) in [str(u) for u in group_request.joined_users]:
            return jsonify({'message': 'User already joined this group', 'group_id': group_id, 'user_id': user_id}), 200
            
        # Validate user exists
        is_valid, user_data = UserService.validate_user(user_id)
        if not is_valid:
            return jsonify({'error': f'Invalid user: {user_data.get("error", "User validation failed")}'}), 400
            
        # Add user to the group
        success, response_data = GroupService.add_user_to_group(group_id, user_id)
        
        if success:
            # Update the joined_users list in the database
            if not group_request.joined_users:
                group_request.joined_users = [group_request.created_by, user_id]
            else:
                # Make sure we don't add duplicates
                joined_users = [str(u) for u in group_request.joined_users]
                if str(user_id) not in joined_users:
                    group_request.joined_users.append(user_id)
            
            # Remove user from the users list since they've now joined
            group_request.users = [u for u in group_request.users if str(u) != str(user_id)]
            
            db.session.commit()
            
            return jsonify({
                'message': f'User {user_id} successfully joined group {group_id}',
                'group_id': group_id,
                'user_id': user_id,
                'joined_users': group_request.joined_users
            }), 200
        else:
            return jsonify({
                'error': f'Failed to add user to group: {response_data.get("error", "Unknown error")}',
            }), 500
    
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
        Composite endpoint to delete a group and its associated resources
        1. Delete the group from group service
        2. Delete the group's calendar from calendar service
        3. Delete the record of the group request from our database
        """
        # First, verify the group exists in our records
        group_request = GroupRequest.query.filter_by(group_id=group_id).first()
        if not group_request:
            return jsonify({'error': f'Group with ID {group_id} not found in our records'}), 404
            
        # Step 1: Delete the group from group service
        group_success, group_response = GroupService.delete_group(group_id)
        
        # Step 2: Delete the group's calendar from calendar service
        calendar_success, calendar_response = CalendarService.delete_calendar(group_id)
        
        # Step 3: Delete the record from our database
        try:
            db.session.delete(group_request)
            db.session.commit()
            db_success = True
        except Exception as e:
            db_success = False
            db_error = str(e)
            db.session.rollback()
            
        # Determine overall success and response
        if group_success and calendar_success and db_success:
            return jsonify({'message': f'Group {group_id} and all associated resources deleted successfully'}), 200
        else:
            # Construct response with details of what failed
            response = {
                'status': 'partial',
                'message': 'Some operations failed while deleting the group',
                'details': {
                    'group_service': {'success': group_success, 'details': group_response},
                    'calendar_service': {'success': calendar_success, 'details': calendar_response},
                    'database': {'success': db_success}
                }
            }
            
            if not db_success:
                response['details']['database']['error'] = db_error
                
            return jsonify(response), 207  # 207 Multi-Status

    # Endpoint to verify if a user exists
    @app.route('/api/verify-user', methods=['GET'])
    def verify_user():
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'Email parameter is required'}), 400
        
        try:
            user_service_url = os.getenv('USER_SERVICE_URL', 'http://user:5001')
            response = requests.get(f"{user_service_url}/api/users/search?q={email}")
            
            if response.status_code == 200:
                users = response.json()
                exists = len(users) > 0
                # Only try to get userId if users exist
                userId = users[0]['id'] if exists and len(users) > 0 else None
                return jsonify({'exists': exists, 'userId': userId})
            else:
                return jsonify({'exists': False, 'error': f'User service returned status {response.status_code}'}), response.status_code
        except Exception as e:
            return jsonify({'exists': False, 'error': str(e)}), 500

    @app.route('/api/groups/user/<int:user_id>', methods=['GET'])
    def get_user_groups(user_id):
        """Get all groups a user is a member of"""
        success, response = GroupService.get_user_groups(user_id)
        
        if success:
            return jsonify(response), 200
        else:
            return jsonify(response), 400

    @app.route('/api/groups/cleanup/null-group-id', methods=['DELETE'])
    def delete_null_group_id_requests():
        """Cleanup endpoint to remove requests that have null group_id (failed creations)"""
        try:
            null_requests = GroupRequest.query.filter(GroupRequest.group_id.is_(None)).all()
            count = len(null_requests)
            
            for req in null_requests:
                db.session.delete(req)
            
            db.session.commit()
            return jsonify({'message': f'Successfully deleted {count} requests with null group_id'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error during cleanup: {str(e)}'}), 500

    @app.route('/api/groups/cleanup/all', methods=['DELETE'])
    def delete_all_requests():
        """Cleanup endpoint to remove all group requests - ONLY FOR TESTING"""
        if os.getenv('FLASK_ENV') != 'development':
            return jsonify({'error': 'This endpoint is only available in development mode'}), 403
            
        try:
            deleted = db.session.query(GroupRequest).delete()
            db.session.commit()
            return jsonify({'message': f'Successfully deleted all {deleted} group requests'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error during cleanup: {str(e)}'}), 500

    # Get invited groups (groups that a user is invited to but hasn't joined yet)
    @app.route('/api/groups/invited/<int:user_id>', methods=['GET'])
    def get_invited_groups(user_id):
        """Get all groups a user is invited to but hasn't joined yet"""
        try:
            # Convert user_id to string for comparison
            str_user_id = str(user_id)
            
            # Find group requests where:
            # 1. The user is in the users list (invited)
            # 2. The user is not in joined_users (hasn't accepted yet)
            # 3. The group has been created successfully
            invited_groups = []
            requests = GroupRequest.query.filter(
                GroupRequest.status.in_(['completed', 'partial'])  # Group creation succeeded or partially succeeded
            ).all()
            
            for req in requests:
                # Skip if user is not in the users list
                if str_user_id not in [str(u) for u in req.users]:
                    continue
                    
                # Skip if user has already joined
                if req.joined_users and str_user_id in [str(u) for u in req.joined_users]:
                    continue
                    
                # Get creator's email
                success, creator_data = UserService.validate_user(req.created_by)
                creator_email = creator_data.get('email', f'User {req.created_by}') if success else f'User {req.created_by}'
                
                # Get all member emails
                member_emails = []
                for member_id in req.users:
                    success, member_data = UserService.validate_user(member_id)
                    if success:
                        member_emails.append(member_data.get('email', f'User {member_id}'))
                    else:
                        member_emails.append(f'User {member_id}')
                
                # Format the response
                group_data = {
                    'group_id': req.group_id,
                    'id': req.group_id,  # For frontend compatibility
                    'name': req.name,
                    'description': req.description,
                    'created_by': req.created_by,
                    'created_by_email': creator_email,
                    'users': member_emails,
                    'start_date_range': req.start_date_range.isoformat() if req.start_date_range else None,
                    'end_date_range': req.end_date_range.isoformat() if req.end_date_range else None
                }
                invited_groups.append(group_data)
            
            return jsonify(invited_groups), 200
            
        except Exception as e:
            print(f"Error in get_invited_groups: {str(e)}")  # Log the error
            return jsonify({'error': f'Error getting invited groups: {str(e)}'}), 500

    @app.route('/api/groups/<int:group_id>/availability', methods=['POST'])
    def submit_availability(group_id):
        """
        Submit user availability for a group's calendar
        """
        data = request.get_json()
        
        # Validate required fields
        if 'user_id' not in data:
            return jsonify({'error': 'user_id is required'}), 400
        if 'available_dates' not in data:
            return jsonify({'error': 'available_dates is required'}), 400
            
        user_id = data['user_id']
        available_dates = data['available_dates']
        
        # First, verify the group exists in our records
        group_request = GroupRequest.query.filter_by(group_id=group_id).first()
        if not group_request:
            return jsonify({'error': f'Group with ID {group_id} not found in our records'}), 404
            
        # Check if user is part of the group
        users_list = [str(u) for u in group_request.users]
        if str(user_id) not in users_list:
            return jsonify({'error': 'User is not part of this group'}), 403
            
        # Get the calendar for this group
        success, calendar_data = CalendarService.get_calendar_by_group_id(group_id)
        
        if not success:
            # If the calendar doesn't exist, create it
            if 'No calendar found' in calendar_data.get('error', ''):
                create_success, calendar_data = CalendarService.create_calendar(
                    group_id=group_id,
                    start_date_range=group_request.start_date_range.isoformat(),
                    end_date_range=group_request.end_date_range.isoformat()
                )
                
                if not create_success:
                    return jsonify({'error': f'Failed to create calendar: {calendar_data.get("error", "Unknown error")}'}), 500
            else:
                return jsonify({'error': f'Failed to fetch calendar: {calendar_data.get("error", "Unknown error")}'}), 500
                
        # Get the calendar ID
        calendar_id = calendar_data.get('id')
        
        # Update user availability
        success, response_data = CalendarService.update_user_availability(
            calendar_id=calendar_id,
            user_id=user_id,
            available_dates=available_dates
        )
        
        if success:
            return jsonify({
                'message': 'Availability submitted successfully',
                'group_id': group_id,
                'calendar_id': calendar_id,
                'user_id': user_id,
                'data': response_data
            }), 200
        else:
            return jsonify({'error': f'Failed to update availability: {response_data.get("error", "Unknown error")}'}), 500 

    @app.route('/api/groups/<int:group_id>/availability', methods=['GET'])
    def get_group_availability(group_id):
        """
        Get availability for all users in a group
        """
        # First, verify the group exists in our records
        group_request = GroupRequest.query.filter_by(group_id=group_id).first()
        if not group_request:
            return jsonify({'error': f'Group with ID {group_id} not found in our records'}), 404
            
        # Get the calendar for this group
        success, calendar_data = CalendarService.get_calendar_by_group_id(group_id)
        
        if not success:
            # If calendar doesn't exist yet, return empty result
            if 'No calendar found' in calendar_data.get('error', ''):
                return jsonify({
                    'group_id': group_id,
                    'calendar': None,
                    'availabilities': [],
                    'message': 'No calendar or availability data found for this group'
                }), 200
            else:
                return jsonify({'error': f'Failed to fetch calendar: {calendar_data.get("error", "Unknown error")}'}), 500
                
        # Return the calendar data which includes all user availabilities
        return jsonify({
            'group_id': group_id,
            'calendar': calendar_data
        }), 200 

    @app.route('/api/groups/<int:group_id>', methods=['GET'])
    def get_group(group_id):
        """
        Get details for a specific group
        """
        # First, check if the group exists in our records
        group_request = GroupRequest.query.filter_by(group_id=group_id).first()
        if not group_request:
            return jsonify({'error': f'Group with ID {group_id} not found in our records'}), 404
            
        # Get the group details from the group service
        success, group_data = GroupService.get_group_by_id(group_id)
        
        if not success:
            return jsonify({'error': f'Failed to fetch group details: {group_data.get("error", "Unknown error")}'}), 500
            
        # Return the group data which should include the UserIds array
        return jsonify(group_data), 200 

    @app.route('/api/groups/<int:group_id>/decline', methods=['POST'])
    def decline_invitation(group_id):
        """
        Endpoint for a user to decline a group invitation
        """
        data = request.get_json()
        
        # Validate required fields
        if 'user_id' not in data:
            return jsonify({'error': 'user_id is required'}), 400
            
        user_id = data['user_id']
        
        # First, verify the group exists in our records
        group_request = GroupRequest.query.filter_by(group_id=group_id).first()
        if not group_request:
            return jsonify({'error': f'Group with ID {group_id} not found in our records'}), 404
            
        # Check if user is in the invited list (convert to strings for comparison)
        users_list = [str(u) for u in group_request.users]
        if str(user_id) not in users_list:
            return jsonify({'error': 'User is not invited to this group'}), 403
            
        # Check if user has already joined
        if group_request.joined_users and str(user_id) in [str(u) for u in group_request.joined_users]:
            return jsonify({'error': 'User has already joined this group'}), 400
            
        # Remove user from the users list
        group_request.users = [u for u in group_request.users if str(u) != str(user_id)]
        
        try:
            db.session.commit()
            return jsonify({
                'message': f'User {user_id} successfully declined invitation to group {group_id}',
                'group_id': group_id,
                'user_id': user_id
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error declining invitation: {str(e)}'}), 500 