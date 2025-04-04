import requests
import os
from typing import Dict, Optional, Any, List

class TripClient:
    @classmethod
    def get_trip_details(cls, trip_id):
        """
        Get details of a trip, including its group_id
        
        Args:
            trip_id: The ID of the trip
            
        Returns:
            Dict: Trip details including group_id if available
        """
        trip_service_url = os.getenv('TRIP_SERVICE_URL', 'http://trip-management:5005')
        
        try:
            # Call the trip service API
            response = requests.get(f"{trip_service_url}/api/trips/{trip_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trip details: {str(e)}")
            return None

class ExchangeRateClient:
    @classmethod
    def get_latest_rates(cls, base_currency: str, target_currencies: Optional[str] = None) -> Dict:
        # Obtain all environment variables
        BASE_URL = os.getenv('EXCHANGE_RATE_BASE_URL')
        API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')
        # Error handling if environment variables not loaded properly
        if not all([BASE_URL, API_KEY]):
            raise ValueError("Missing required environment variables: EXCHANGE_RATE_BASE_URL and EXCHANGE_RATE_API_KEY")
        # params = {
        #     'base': base_currency
        # }
        
        # if target_currencies:
        #     params['symbols'] = target_currencies
        response = requests.get(f"{BASE_URL}/{API_KEY}/latest/{base_currency}")
        response.raise_for_status()
        return response.json()

    @classmethod
    def convert_amount(cls, from_currency: str, to_currency: str, amount: float) -> float:
        rates = cls.get_latest_rates(from_currency, to_currency)
        rate = rates['conversion_rates'][to_currency]
        return amount * rate

class EmailClient:
    @classmethod
    def send_settlement_email(cls, to_email: str, subject: str, body: Dict[str, Any]) -> Dict:
        """
        Send email with settlement details to a user
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content as a dictionary
            
        Returns:
            Dict: The response from the email service
        """
        # Get email service URL from environment variables
        email_api_url = os.getenv('EMAIL_API_URL')
        if not email_api_url:
            raise ValueError("Missing required environment variable: EMAIL_API_URL")
        
        # Prepare email data
        email_data = {
            'to': to_email,
            'subject': subject,
            'body': body
        }
        
        try:
            # Send the request to the email service
            response = requests.post(
                email_api_url,
                json=email_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Check for successful response
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # If the request fails (email service unavailable), log the email details
            # and return a mock response - this is just for testing
            print(f"===== MOCK EMAIL SENT =====")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            print(f"===========================")
            
            # Return a mock response
            return {
                "status": "logged",
                "message": "Email logged (email service unavailable)",
                "id": f"mock-{hash(to_email + subject)}"
            }
    
    @classmethod
    def send_batch_settlement_emails(cls, trip_id: str, settlement_data: Dict, users: List) -> Dict:
        """
        Send settlement emails to all users in a trip
        
        Args:
            trip_id: The ID of the trip
            settlement_data: Settlement calculation data
            users: List of users to send emails to
            
        Returns:
            Dict: Results of the email sending operation
        """
        results = {
            'success': [],
            'failed': []
        }
        
        for user in users:
            # Skip if user has no email
            if not user.email:
                results['failed'].append({
                    'user_id': user.user_id,
                    'reason': 'No email address'
                })
                continue
            
            try:
                # Prepare user-specific settlement details
                user_id = user.user_id
                
                # Get what this user needs to pay to others
                to_pay = []
                if 'split_details' in settlement_data:
                    for recipient_id, details in settlement_data['split_details'].items():
                        if user_id in details.get('payers', []):
                            # This user needs to pay recipient_id
                            recipient_name = details.get('user_name', recipient_id)
                            to_pay.append({
                                'to': recipient_name,
                                'amount': details.get('split_amount', 0),
                                'currency': settlement_data.get('currency', 'SGD')
                            })
                
                # Get what others need to pay this user
                to_receive = []
                if 'split_details' in settlement_data and user_id in settlement_data['split_details']:
                    user_split_details = settlement_data['split_details'][user_id]
                    
                    # Match payer IDs with their names
                    payers = user_split_details.get('payers', [])
                    payer_names = user_split_details.get('payer_names', [])
                    
                    for i, payer_id in enumerate(payers):
                        payer_name = payer_names[i] if i < len(payer_names) else payer_id
                        to_receive.append({
                            'from': payer_name,
                            'amount': user_split_details.get('split_amount', 0),
                            'currency': settlement_data.get('currency', 'SGD')
                        })
                
                # Prepare email content
                email_body = {
                    'trip_id': trip_id,
                    'user_name': user.name,
                    'total_trip_amount': settlement_data.get('total_amount', 0),
                    'currency': settlement_data.get('currency', 'SGD'),
                    'to_pay': to_pay,
                    'to_receive': to_receive
                }
                
                # Send email
                cls.send_settlement_email(
                    to_email=user.email,
                    subject=f'Trip Settlement Details for {trip_id}',
                    body=email_body
                )
                
                results['success'].append(user.user_id)
                
            except Exception as e:
                results['failed'].append({
                    'user_id': user.user_id,
                    'reason': str(e)
                })
        
        return results 