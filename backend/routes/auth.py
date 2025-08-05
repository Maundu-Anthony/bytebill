from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import hashlib
import sqlite3
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Admin credentials (in production, store hashed in database)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = hashlib.sha256('admin123'.encode()).hexdigest()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH:
        access_token = create_access_token(identity=username)
        return jsonify({
            'access_token': access_token,
            'user': {'username': username, 'role': 'admin'}
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/user-login', methods=['POST'])
def user_login():
    """User captive portal login endpoint"""
    data = request.get_json()
    voucher_code = data.get('voucher_code')
    mpesa_code = data.get('mpesa_code')
    mac_address = data.get('mac_address')
    ip_address = data.get('ip_address')
    
    if voucher_code:
        # Validate voucher
        return handle_voucher_login(voucher_code, mac_address, ip_address)
    elif mpesa_code:
        # Validate M-PESA payment
        return handle_mpesa_login(mpesa_code, mac_address, ip_address)
    else:
        return jsonify({'error': 'Voucher code or M-PESA code required'}), 400

def handle_voucher_login(voucher_code, mac_address, ip_address):
    """Handle voucher-based login"""
    # TODO: Implement voucher validation logic
    return jsonify({
        'success': True,
        'session_id': f'session_{voucher_code}',
        'expires_at': datetime.now().isoformat()
    })

def handle_mpesa_login(mpesa_code, mac_address, ip_address):
    """Handle M-PESA based login"""
    # TODO: Implement M-PESA validation logic
    return jsonify({
        'success': True,
        'session_id': f'session_{mpesa_code}',
        'expires_at': datetime.now().isoformat()
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Admin logout endpoint"""
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/user-logout', methods=['POST'])
def user_logout():
    """User logout endpoint"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    # TODO: Implement session termination logic
    return jsonify({'message': 'Session terminated'})
