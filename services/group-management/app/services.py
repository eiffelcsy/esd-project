import os
import requests
from flask import current_app
import json
from app.message_broker import MessageBroker

class UserService:
    """Service to interact with the User microservice"""
    
    @staticmethod
    def validate_user(user_id):
        """
        Validates if a user exists by ID
        
        Args:
            user_id (int): The user ID to validate
            
        Returns:
            tuple: (bool, dict) - (is_valid, user_data or error_message)
        """
        user_service_url = os.getenv('USER_SERVICE_URL')
        
        try:
            response = requests.get(f"{user_service_url}/api/users/{user_id}")
            
            if response.status_code == 200:
                return True, response.json()
            elif response.status_code == 404:
                return False, {"error": f"User with ID {user_id} not found"}
            else:
                return False, {"error": f"Error validating user: {response.text}"}
                
        except requests.RequestException as e:
            current_app.logger.error(f"Error connecting to User service: {str(e)}")
            return False, {"error": f"Error connecting to User service: {str(e)}"}


class GroupService:
    """Service to interact with the Group microservice"""
    
    @staticmethod
    def create_group(name, description, created_by, users=None):
        """
        Creates a new group via the Group microservice
        
        Args:
            name (str): Group name
            description (str): Group description
            created_by (int): User ID of the creator
            users (list, optional): List of user IDs to be invited to the group
            
        Returns:
            tuple: (bool, dict) - (success, group_data or error_message)
        """
        group_service_url = os.getenv('GROUP_SERVICE_URL')
        
        # Print debug information
        print(f"DEBUG GroupService.create_group: URL={group_service_url}, name={name}, created_by={created_by}, invited_users={users}")
        
        # If no service URL is provided in testing, return a mock response
        if not group_service_url:
            current_app.logger.warning("GROUP_SERVICE_URL not set. Using mock response for testing.")
            return False, {"error": "GROUP_SERVICE_URL not configured"}
        
        payload = {
            "name": name,
            "description": description,
            "createdby": created_by,
        }
        
        try:
            print(f"DEBUG Sending request to group service: {group_service_url}/groups with payload: {json.dumps(payload)}")
            response = requests.post(
                f"{group_service_url}/groups", 
                json=payload
            )
            
            if response.status_code in (200, 201):
                response_data = response.json()
                print(f"DEBUG Group service response: {response.status_code} {json.dumps(response_data)}")
                
                # Extract the group ID
                # group_id = response_data.get('id') or response_data.get('group_id')
                group_id = response_data

                if group_id:
                    # Add the creator to the group immediately
                    success, add_creator_response = GroupService.add_user_to_group(group_id, created_by)
                    if not success:
                        print(f"WARNING: Failed to add creator to group: {add_creator_response}")
                
                return True, response_data
            else:
                error_message = f"Error creating group: {response.text}"
                print(f"DEBUG Group service error: {response.status_code} {error_message}")
                return False, {"error": error_message}
                
        except requests.RequestException as e:
            error_message = f"Error connecting to Group service: {str(e)}"
            print(f"DEBUG Request exception: {error_message}")
            current_app.logger.error(error_message)
            return False, {"error": error_message}

    @staticmethod
    def add_user_to_group(group_id, user_id):
        """
        Adds a user to an existing group via the Group microservice
        
        Args:
            group_id (int): ID of the group
            user_id (int): ID of the user to add
            
        Returns:
            tuple: (bool, dict) - (success, response_data or error_message)
        """
        group_service_url = os.getenv('GROUP_SERVICE_URL')
        
        try:
            response = requests.post(
                f"{group_service_url}/groups/{group_id}/users",
                json={"userId": user_id}
            )
            
            if response.status_code in (200, 201):
                return True, response.text
            else:
                return False, {"error": f"Error adding user to group: {response.text}"}
                
        except requests.RequestException as e:
            current_app.logger.error(f"Error connecting to Group service: {str(e)} {response.text} {response.status_code}")
            return False, {"error": f"Error connecting to Group service: {str(e)} {response.text} {response.status_code}"}

    @staticmethod
    def get_user_groups(user_id):
        """
        Fetches all groups a user is a member of via the Group microservice
        
        Args:
            user_id (int): User ID to get groups for
            
        Returns:
            tuple: (bool, list) - (success, list_of_groups or error_message)
        """
        group_service_url = os.getenv('GROUP_SERVICE_URL')
        
        # If no service URL is provided in testing, return a mock response
        if not group_service_url:
            current_app.logger.warning("GROUP_SERVICE_URL not set. Using mock response for testing.")
            return False, {"error": "GROUP_SERVICE_URL not configured"}
        
        try:
            response = requests.get(
                f"{group_service_url}/groups/by-user/{user_id}"
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"Error fetching user groups: {response.text}"}
                
        except requests.RequestException as e:
            current_app.logger.error(f"Error connecting to Group service: {str(e)}")
            return False, {"error": f"Error connecting to Group service: {str(e)}"}

    @staticmethod
    def get_group_by_id(group_id):
        """
        Fetches a group by its ID via the Group microservice
        
        Args:
            group_id (int): ID of the group to fetch
            
        Returns:
            tuple: (bool, dict) - (success, group_data or error_message)
        """
        group_service_url = os.getenv('GROUP_SERVICE_URL')
        
        # If no service URL is provided in testing, return a mock response
        if not group_service_url:
            current_app.logger.warning("GROUP_SERVICE_URL not set. Using mock response for testing.")
            return False, {"error": "GROUP_SERVICE_URL not configured"}
        
        try:
            response = requests.get(
                f"{group_service_url}/groups/{group_id}"
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"Error fetching group: {response.text}"}
                
        except requests.RequestException as e:
            current_app.logger.error(f"Error connecting to Group service: {str(e)}")
            return False, {"error": f"Error connecting to Group service: {str(e)}"}

    @staticmethod
    def delete_group(group_id):
        """
        Deletes a group via the Group microservice
        
        Args:
            group_id (int): ID of the group to delete
            
        Returns:
            tuple: (bool, dict) - (success, response_data or error_message)
        """
        group_service_url = os.getenv('GROUP_SERVICE_URL')
        
        # If no service URL is provided in testing, return a mock response
        if not group_service_url:
            current_app.logger.warning("GROUP_SERVICE_URL not set. Using mock response for testing.")
            return False, {"error": "GROUP_SERVICE_URL not configured"}
        
        try:
            response = requests.delete(
                f"{group_service_url}/groups/{group_id}"
            )
            
            if response.status_code in (200, 204):
                return True, {"message": f"Group {group_id} deleted successfully"}
            else:
                return False, {"error": f"Error deleting group: {response.text}"}
                
        except requests.RequestException as e:
            current_app.logger.error(f"Error connecting to Group service: {str(e)}")
            return False, {"error": f"Error connecting to Group service: {str(e)}"}


class CalendarService:
    """Service to interact with the Calendar microservice"""
    
    @staticmethod
    def create_calendar(group_id, start_date_range, end_date_range):
        """
        Creates a new calendar for a group
        
        Args:
            group_id (int): ID of the group
            start_date_range (str): Start date in ISO format
            end_date_range (str): End date in ISO format
            
        Returns:
            tuple: (bool, dict) - (success, calendar_data or error_message)
        """
        calendar_service_url = os.getenv('CALENDAR_SERVICE_URL')
        
        # If no service URL is provided in testing, return a mock response
        if not calendar_service_url:
            current_app.logger.warning("CALENDAR_SERVICE_URL not set. Using mock response for testing.")
            return True, {
                "id": group_id,
                "group_id": group_id,
                "start_date_range": start_date_range,
                "end_date_range": end_date_range,
                "note": "Mock calendar created in testing mode"
            }
        
        payload = {
            "group_id": group_id,
            "start_date_range": start_date_range,
            "end_date_range": end_date_range
        }
        
        try:
            response = requests.post(
                f"{calendar_service_url}/api/calendars", 
                json=payload
            )
            
            if response.status_code in (200, 201):
                return True, response.json()
            else:
                return False, {"error": f"Error creating calendar: {response.text}"}
                
        except requests.RequestException as e:
            current_app.logger.error(f"Error connecting to Calendar service: {str(e)}")
            return False, {"error": f"Error connecting to Calendar service: {str(e)}"}

    @staticmethod
    def delete_calendar(group_id):
        """
        Deletes a calendar for a group
        
        Args:
            group_id (int): ID of the group whose calendar to delete
            
        Returns:
            tuple: (bool, dict) - (success, response_data or error_message)
        """
        calendar_service_url = os.getenv('CALENDAR_SERVICE_URL')
        
        # If no service URL is provided in testing, return a mock response
        if not calendar_service_url:
            current_app.logger.warning("CALENDAR_SERVICE_URL not set. Using mock response for testing.")
            return True, {"message": "Calendar deletion bypassed - mock testing mode"}
        
        try:
            response = requests.delete(
                f"{calendar_service_url}/api/calendars/group/{group_id}"
            )
            
            if response.status_code in (200, 204):
                return True, {"message": f"Calendar for group {group_id} deleted successfully"}
            else:
                return False, {"error": f"Error deleting calendar: {response.text}"}
                
        except requests.RequestException as e:
            current_app.logger.error(f"Error connecting to Calendar service: {str(e)}")
            return False, {"error": f"Error connecting to Calendar service: {str(e)}"}
    
    @staticmethod
    def get_calendar_by_group_id(group_id):
        """
        Gets calendar information for a specific group
        
        Args:
            group_id (int): ID of the group
            
        Returns:
            tuple: (bool, dict) - (success, calendar_data or error_message)
        """
        calendar_service_url = os.getenv('CALENDAR_SERVICE_URL')
        
        # If no service URL is provided in testing, return a mock response
        if not calendar_service_url:
            current_app.logger.warning("CALENDAR_SERVICE_URL not set. Using mock response for testing.")
            return False, {"error": "CALENDAR_SERVICE_URL not configured"}
        
        try:
            response = requests.get(
                f"{calendar_service_url}/api/calendars/group/{group_id}"
            )
            
            if response.status_code == 200:
                return True, response.json()
            elif response.status_code == 404:
                return False, {"error": f"No calendar found for group {group_id}"}
            else:
                return False, {"error": f"Error fetching calendar: {response.text}"}
                
        except requests.RequestException as e:
            current_app.logger.error(f"Error connecting to Calendar service: {str(e)}")
            return False, {"error": f"Error connecting to Calendar service: {str(e)}"}
    
    @staticmethod
    def update_user_availability(calendar_id, user_id, available_dates):
        """
        Updates a user's availability in a calendar
        
        Args:
            calendar_id (int): ID of the calendar
            user_id (int): ID of the user
            available_dates (list): List of available date strings
            
        Returns:
            tuple: (bool, dict) - (success, response_data or error_message)
        """
        # Try direct API call first
        calendar_service_url = os.getenv('CALENDAR_SERVICE_URL')
        
        if calendar_service_url:
            try:
                payload = {
                    "user_id": user_id,
                    "available_dates": available_dates
                }
                
                response = requests.post(
                    f"{calendar_service_url}/api/calendars/{calendar_id}/availability",
                    json=payload
                )
                
                if response.status_code in (200, 201):
                    return True, response.json()
                else:
                    # If API call fails, try RabbitMQ as fallback
                    success = MessageBroker.publish_user_availability(calendar_id, user_id, available_dates)
                    if success:
                        return True, {"message": "Availability update queued via message broker", "queued": True}
                    else:
                        return False, {"error": f"Failed to update availability: {response.text}"}
            
            except requests.RequestException:
                # On connection error, try RabbitMQ
                success = MessageBroker.publish_user_availability(calendar_id, user_id, available_dates)
                if success:
                    return True, {"message": "Availability update queued via message broker", "queued": True}
                else:
                    return False, {"error": "Failed to update availability through all available methods"}
        else:
            # If no API URL is set, use RabbitMQ directly
            success = MessageBroker.publish_user_availability(calendar_id, user_id, available_dates)
            if success:
                return True, {"message": "Availability update queued via message broker", "queued": True}
            else:
                return False, {"error": "Failed to publish availability update to message queue"} 