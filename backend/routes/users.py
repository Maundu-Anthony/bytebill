from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sqlite3
from datetime import datetime

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all active users"""
    # TODO: Implement database query for active users
    mock_users = [
        {
            'id': 1,
            'ip': '192.168.88.10',
            'mac': '00:11:22:33:44:55',
            'session_start': '2024-01-01T10:00:00',
            'data_used': 50000000,  # 50MB
            'time_remaining': 2700,  # 45 minutes
            'plan': 'hourly'
        },
        {
            'id': 2,
            'ip': '192.168.88.11',
            'mac': '66:77:88:99:AA:BB',
            'session_start': '2024-01-01T11:00:00',
            'data_used': 100000000,  # 100MB
            'time_remaining': 1800,  # 30 minutes
            'plan': 'daily'
        }
    ]
    return jsonify({'users': mock_users})

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user details"""
    # TODO: Implement database query for specific user
    mock_user = {
        'id': user_id,
        'ip': '192.168.88.10',
        'mac': '00:11:22:33:44:55',
        'session_start': '2024-01-01T10:00:00',
        'data_used': 50000000,
        'time_remaining': 2700,
        'plan': 'hourly',
        'voucher_code': 'BYTE123456'
    }
    return jsonify(mock_user)

@users_bp.route('/<int:user_id>/disconnect', methods=['POST'])
@jwt_required()
def disconnect_user(user_id):
    """Disconnect a specific user"""
    # TODO: Implement user disconnection logic
    return jsonify({'message': f'User {user_id} disconnected successfully'})

@users_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user statistics"""
    stats = {
        'total_active': 15,
        'total_today': 45,
        'peak_concurrent': 23,
        'bandwidth_usage': {
            'upload': 150000000,  # 150MB
            'download': 2000000000  # 2GB
        }
    }
    return jsonify(stats)
