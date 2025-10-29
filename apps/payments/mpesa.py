import requests
import base64
from datetime import datetime
from django.conf import settings
import json
import logging
import uuid

logger = logging.getLogger(__name__)


class MpesaAPI:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        self.environment = settings.MPESA_ENVIRONMENT
        
        # Check if we're in test mode (when credentials are not properly set or forced)
        test_mode_setting = getattr(settings, 'MPESA_TEST_MODE', False)
        self.test_mode = test_mode_setting in [True, 'true', 'True'] or self._is_test_mode()
        self.demo_mode = test_mode_setting in ['demo', 'Demo', 'DEMO']
        
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def _is_test_mode(self):
        """Check if we should run in test mode (for development without real M-Pesa credentials)"""
        test_indicators = [
            'your-consumer-key',
            'your-consumer-secret', 
            'your-shortcode',
            'your-passkey',
            'test',
            'demo'
        ]
        
        credentials = [
            self.consumer_key.lower() if self.consumer_key else '',
            self.consumer_secret.lower() if self.consumer_secret else '',
            str(self.shortcode).lower() if self.shortcode else '',
            self.passkey.lower() if self.passkey else ''
        ]
        
        return any(indicator in credential for credential in credentials for indicator in test_indicators)
    
    def get_access_token(self):
        """Get OAuth access token from Safaricom"""
        if self.test_mode:
            logger.info("Running in test mode - returning mock access token")
            return "mock_access_token_for_testing"
        
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        # Validate credentials
        if not self.consumer_key or not self.consumer_secret:
            logger.error("M-Pesa consumer key or secret not configured")
            return None
        
        # Create basic auth header
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        try:
            logger.info(f"Requesting access token from: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            access_token = result.get('access_token')
            if access_token:
                logger.info("Successfully obtained access token")
                return access_token
            else:
                logger.error(f"No access token in response: {result}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Timeout while requesting access token")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting access token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return None
    
    def generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        return password, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push payment"""
        
        # Test mode simulation
        if self.test_mode:
            logger.info("Running in test mode - simulating STK Push")
            return {
                'success': True,
                'checkout_request_id': f'ws_CO_TEST_{uuid.uuid4().hex[:10]}',
                'merchant_request_id': f'TEST_{uuid.uuid4().hex[:8]}',
                'message': 'Test STK Push sent successfully (simulated)'
            }
        
        # Demo mode - simulates real STK push with success
        if self.demo_mode:
            logger.info("Running in demo mode - simulating successful STK Push")
            return {
                'success': True,
                'checkout_request_id': f'ws_CO_DEMO_{uuid.uuid4().hex[:10]}',
                'merchant_request_id': f'DEMO_{uuid.uuid4().hex[:8]}',
                'message': f'Demo STK Push sent to {phone_number} (simulated success)'
            }
        
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False, 
                'message': 'Failed to get access token. Please check your M-Pesa credentials.'
            }
        
        password, timestamp = self.generate_password()
        
        # Format phone number (remove + and ensure it starts with 254)
        formatted_phone = self._format_phone_number(phone_number)
        if not formatted_phone:
            return {
                'success': False,
                'message': 'Invalid phone number format. Please use format: +254XXXXXXXXX'
            }
        
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': formatted_phone,
            'PartyB': self.shortcode,
            'PhoneNumber': formatted_phone,
            'CallBackURL': self.callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        
        try:
            logger.info(f"Sending STK Push to: {url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"STK Push response status: {response.status_code}")
            logger.info(f"STK Push response: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('ResponseCode') == '0':
                return {
                    'success': True,
                    'checkout_request_id': result.get('CheckoutRequestID'),
                    'merchant_request_id': result.get('MerchantRequestID'),
                    'message': result.get('ResponseDescription', 'STK Push sent successfully')
                }
            else:
                error_message = result.get('ResponseDescription', 'STK Push failed')
                logger.error(f"STK Push failed: {error_message}")
                return {
                    'success': False,
                    'message': error_message
                }
        
        except requests.exceptions.Timeout:
            logger.error("Timeout while sending STK Push")
            return {
                'success': False,
                'message': 'Request timeout. Please try again.'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during STK Push: {e}")
            
            # Handle specific error cases
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 403:
                    return {
                        'success': False,
                        'message': 'M-Pesa API access denied. This may be due to callback URL restrictions or IP whitelisting in sandbox environment.'
                    }
                elif e.response.status_code == 400:
                    return {
                        'success': False,
                        'message': 'Invalid request parameters. Please check your M-Pesa configuration.'
                    }
            
            return {
                'success': False,
                'message': f'Network error: {str(e)}'
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from STK Push: {e}")
            return {
                'success': False,
                'message': 'Invalid response from M-Pesa API'
            }
    
    def _format_phone_number(self, phone_number):
        """Format phone number to Kenyan format"""
        if not phone_number:
            return None
        
        # Remove all non-digit characters except +
        phone = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Remove + if present
        if phone.startswith('+'):
            phone = phone[1:]
        
        # Convert local format to international
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('7') or phone.startswith('1'):
            phone = '254' + phone
        
        # Validate Kenyan number format
        if phone.startswith('254') and len(phone) == 12:
            return phone
        
        return None
    
    def get_credentials_status(self):
        """Get status of M-Pesa credentials configuration"""
        if self.test_mode:
            return {
                'status': 'test_mode',
                'message': 'Running in test mode with simulated responses',
                'configured': True
            }
        
        missing = []
        if not self.consumer_key:
            missing.append('Consumer Key')
        if not self.consumer_secret:
            missing.append('Consumer Secret')
        if not self.shortcode:
            missing.append('Shortcode')
        if not self.passkey:
            missing.append('Passkey')
        if not self.callback_url:
            missing.append('Callback URL')
        
        if missing:
            return {
                'status': 'incomplete',
                'message': f'Missing: {", ".join(missing)}',
                'configured': False
            }
        
        # Test access token
        access_token = self.get_access_token()
        if access_token:
            return {
                'status': 'configured',
                'message': 'M-Pesa credentials are properly configured',
                'configured': True
            }
        else:
            return {
                'status': 'invalid',
                'message': 'M-Pesa credentials are invalid or API is unreachable',
                'configured': False
            }