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
        Send email with settlement details to a user using Resend
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content as a dictionary
            
        Returns:
            Dict: The response from the email service
        """
        # Get Resend API key and domain from environment variables
        resend_api_key = os.getenv('RESEND_API_KEY')
        resend_domain = os.getenv('RESEND_DOMAIN')
        
        if not resend_api_key or not resend_domain:
            raise ValueError("Missing required environment variables: RESEND_API_KEY and RESEND_DOMAIN")
        
        try:
            import resend
            
            # Initialize Resend client
            resend.api_key = resend_api_key
            
            # Format the email body into HTML
            html_content = cls._format_settlement_email_html(body)
            
            # Send email using Resend
            response = resend.Emails.send({
                "from": f"Trip Settlement <settlement@{resend_domain}>",
                "to": to_email,
                "subject": subject,
                "html": html_content
            })
            
            return {
                "status": "success",
                "message": "Email sent successfully",
                "id": response["id"] if "id" in response else None
            }
        except ImportError:
            # If the resend library is not installed, log the message
            print(f"===== ERROR: Resend library not installed =====")
            return {
                "status": "error",
                "message": "Resend library not installed",
                "id": None
            }
        except Exception as e:
            # If the request fails, log the email details
            print(f"===== ERROR SENDING EMAIL =====")
            print(f"Error: {str(e)}")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"===========================")
            
            # Return error response
            return {
                "status": "error",
                "message": f"Error sending email: {str(e)}",
                "id": None
            }
    
    @classmethod
    def _format_settlement_email_html(cls, body: Dict[str, Any]) -> str:
        """
        Format settlement details into an HTML email
        
        Args:
            body: Settlement data dictionary
            
        Returns:
            str: HTML content for the email
        """
        trip_id = body.get('trip_id', 'Unknown Trip')
        user_name = body.get('user_name', 'Traveler')
        total_trip_amount = body.get('total_trip_amount', 0)
        currency = body.get('currency', 'SGD')
        user_balance = body.get('user_balance', 0)
        to_pay = body.get('to_pay', [])
        to_receive = body.get('to_receive', [])
        
        # Set balance status text and color
        if user_balance > 0:
            balance_status = f"You are owed {abs(user_balance)} {currency}"
            balance_color = "#34D399"  # Green
        elif user_balance < 0:
            balance_status = f"You owe {abs(user_balance)} {currency}"
            balance_color = "#F87171"  # Red
        else:
            balance_status = "Your balance is settled"
            balance_color = "#6B7280"  # Gray
        
        # Create HTML content
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .summary {{
                    background-color: #f9fafb;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .balance {{
                    font-size: 18px;
                    font-weight: bold;
                    color: {balance_color};
                    margin: 10px 0;
                }}
                .section {{
                    margin-bottom: 20px;
                }}
                h2 {{
                    border-bottom: 1px solid #e5e7eb;
                    padding-bottom: 8px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    border: 1px solid #e5e7eb;
                    padding: 8px 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f9fafb;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 14px;
                    color: #6B7280;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Trip Settlement Summary</h1>
                <p>Trip ID: {trip_id}</p>
            </div>
            
            <div class="summary">
                <p>Hello {user_name},</p>
                <p>Your trip expense settlement is ready. The total trip expenses were <strong>{total_trip_amount} {currency}</strong>.</p>
                <div class="balance">{balance_status}</div>
            </div>
        """
        
        # Add payments to make section if there are any
        if to_pay:
            html += f"""
            <div class="section">
                <h2>Payments to Make</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Pay To</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for payment in to_pay:
                html += f"""
                        <tr>
                            <td>{payment.get('to', 'Unknown')}</td>
                            <td>{payment.get('amount', 0)} {payment.get('currency', currency)}</td>
                        </tr>
                """
            
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        # Add payments to receive section if there are any
        if to_receive:
            html += f"""
            <div class="section">
                <h2>Payments to Receive</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Receive From</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for payment in to_receive:
                html += f"""
                        <tr>
                            <td>{payment.get('from', 'Unknown')}</td>
                            <td>{payment.get('amount', 0)} {payment.get('currency', currency)}</td>
                        </tr>
                """
            
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        # If no payments to make or receive
        if not to_pay and not to_receive:
            html += """
            <div class="section">
                <p>You have no pending transactions. Your expenses are already settled!</p>
            </div>
            """
        
        # Add footer
        html += """
            <div class="footer">
                <p>This is an automated email. Please do not reply to this message.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
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
                if 'settlements' in settlement_data:
                    for settlement in settlement_data['settlements']:
                        if settlement['from'] == user_id:
                            # This user needs to pay
                            to_pay.append({
                                'to': settlement['to_name'],
                                'amount': settlement['amount'],
                                'currency': settlement['currency']
                            })
                
                # Get what others need to pay this user
                to_receive = []
                if 'settlements' in settlement_data:
                    for settlement in settlement_data['settlements']:
                        if settlement['to'] == user_id:
                            # This user will receive payment
                            to_receive.append({
                                'from': settlement['from_name'],
                                'amount': settlement['amount'],
                                'currency': settlement['currency']
                            })
                
                # Get overall user balance
                user_balance = settlement_data.get('user_balances', {}).get(user_id, 0)
                
                # Prepare email content
                email_body = {
                    'trip_id': trip_id,
                    'user_name': user.name,
                    'total_trip_amount': settlement_data.get('total_amount', 0),
                    'currency': settlement_data.get('currency', 'SGD'),
                    'user_balance': user_balance,
                    'to_pay': to_pay,
                    'to_receive': to_receive
                }
                
                # Send email
                response = cls.send_settlement_email(
                    to_email=user.email,
                    subject=f'Trip Settlement Details for Trip #{trip_id}',
                    body=email_body
                )
                
                if response.get('status') == 'success':
                    results['success'].append(user.user_id)
                else:
                    results['failed'].append({
                        'user_id': user.user_id,
                        'reason': response.get('message', 'Unknown error')
                    })
                
            except Exception as e:
                results['failed'].append({
                    'user_id': user.user_id,
                    'reason': str(e)
                })
        
        return results 