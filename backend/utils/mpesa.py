import requests
import json
import base64
from datetime import datetime
from config import Config

class MPESAError(Exception):
    pass

class MPESA:
    def __init__(self):
        self.consumer_key = Config.MPESA_CONSUMER_KEY
        self.consumer_secret = Config.MPESA_CONSUMER_SECRET
        self.passkey = Config.MPESA_PASSKEY
        self.shortcode = Config.MPESA_SHORTCODE
        self.callback_url = Config.MPESA_CALLBACK_URL
        
        # Sandbox URLs (change to production for live)
        self.auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        
    def get_access_token(self):
        """Get M-PESA access token"""
        if not self.consumer_key or not self.consumer_secret:
            raise MPESAError("M-PESA credentials not configured")
            
        credentials = base64.b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(self.auth_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('access_token')
            
        except requests.exceptions.RequestException as e:
            raise MPESAError(f"Failed to get access token: {str(e)}")
    
    def generate_password(self):
        """Generate M-PESA password"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        return password, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push request"""
        if not phone_number.startswith('254'):
            # Convert 07XXXXXXXX to 254XXXXXXXX
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            else:
                phone_number = '254' + phone_number
        
        access_token = self.get_access_token()
        password, timestamp = self.generate_password()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        try:
            response = requests.post(self.stk_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('ResponseCode') == '0':
                return {
                    'success': True,
                    'checkout_request_id': data.get('CheckoutRequestID'),
                    'merchant_request_id': data.get('MerchantRequestID'),
                    'response_code': data.get('ResponseCode'),
                    'response_description': data.get('ResponseDescription'),
                    'customer_message': data.get('CustomerMessage')
                }
            else:
                return {
                    'success': False,
                    'error': data.get('ResponseDescription', 'Unknown error'),
                    'response_code': data.get('ResponseCode')
                }
                
        except requests.exceptions.RequestException as e:
            raise MPESAError(f"STK Push failed: {str(e)}")
    
    def query_transaction_status(self, checkout_request_id):
        """Query the status of a transaction"""
        # TODO: Implement transaction status query
        # This would use the STK Push Query API
        pass
    
    def validate_callback(self, callback_data):
        """Validate and process M-PESA callback data"""
        try:
            # Extract callback data
            result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            result_desc = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
            checkout_request_id = callback_data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            
            if result_code == 0:
                # Payment successful
                callback_metadata = callback_data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])
                
                payment_data = {}
                for item in callback_metadata:
                    name = item.get('Name')
                    value = item.get('Value')
                    payment_data[name] = value
                
                return {
                    'success': True,
                    'checkout_request_id': checkout_request_id,
                    'amount': payment_data.get('Amount'),
                    'mpesa_receipt_number': payment_data.get('MpesaReceiptNumber'),
                    'transaction_date': payment_data.get('TransactionDate'),
                    'phone_number': payment_data.get('PhoneNumber')
                }
            else:
                # Payment failed
                return {
                    'success': False,
                    'checkout_request_id': checkout_request_id,
                    'result_code': result_code,
                    'result_desc': result_desc
                }
                
        except Exception as e:
            raise MPESAError(f"Failed to validate callback: {str(e)}")

# Convenience functions
def initiate_payment(phone_number, amount, plan_name):
    """Initiate M-PESA payment for internet access"""
    mpesa = MPESA()
    
    account_reference = f"BYTEBILL_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    transaction_desc = f"ByteBill {plan_name} Internet Access"
    
    return mpesa.stk_push(phone_number, amount, account_reference, transaction_desc)

def process_payment_callback(callback_data):
    """Process M-PESA payment callback"""
    mpesa = MPESA()
    return mpesa.validate_callback(callback_data)
