import os
import requests
from flask import current_app
import json

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
        user_service_url = os.environ.get('USER_SERVICE_URL')
        
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
    def create_group(name, description, created_by, users):
        """
        Creates a new group via the Group microservice
        
        Args:
            name (str): Group name
            description (str): Group description
            created_by (int): User ID of the creator
            users (list): List of user IDs in the group
            
        Returns:
            tuple: (bool, dict) - (success, group_data or error_message)
        """
        group_service_url = os.environ.get('GROUP_SERVICE_URL')
        
        # If no service URL is provided in testing, return a mock response
        if not group_service_url:
            current_app.logger.warning("GROUP_SERVICE_URL not set. Using mock response for testing.")
            return False, {"error": "GROUP_SERVICE_URL not configured"}
        
        payload = {
            "name": name,
            "description": description,
            "createdby": created_by,
            "users": users
        }
        
        try:
            response = requests.post(
                f"{group_service_url}/groups", 
                json=payload
            )
            
            if response.status_code in (200, 201):
                return True, response.json()
            else:
                return False, {"error": f"Error creating group: {response.text}"}
                
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
        group_service_url = os.environ.get('GROUP_SERVICE_URL')
        
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
        calendar_service_url = os.environ.get('CALENDAR_SERVICE_URL')
        
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
        calendar_service_url = os.environ.get('CALENDAR_SERVICE_URL')
        
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