from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
import string
from datetime import datetime, timedelta

vouchers_bp = Blueprint('vouchers', __name__)

def generate_voucher_code(length=10):
    """Generate a random voucher code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@vouchers_bp.route('/', methods=['GET'])
@jwt_required()
def get_vouchers():
    """Get all vouchers with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', 'all')  # all, unused, used, expired
    
    # TODO: Implement database query with filters
    mock_vouchers = [
        {
            'id': 1,
            'code': 'BYTE123456',
            'plan': 'hourly',
            'duration': 3600,
            'data_limit': None,
            'created_at': '2024-01-01T09:00:00',
            'expires_at': '2024-01-07T09:00:00',
            'status': 'unused',
            'used_by': None,
            'used_at': None
        },
        {
            'id': 2,
            'code': 'BYTE789012',
            'plan': 'daily',
            'duration': 86400,
            'data_limit': 1073741824,  # 1GB
            'created_at': '2024-01-01T10:00:00',
            'expires_at': '2024-01-08T10:00:00',
            'status': 'used',
            'used_by': '00:11:22:33:44:55',
            'used_at': '2024-01-01T11:30:00'
        }
    ]
    
    return jsonify({
        'vouchers': mock_vouchers,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': 2,
            'pages': 1
        }
    })

@vouchers_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_vouchers():
    """Generate single or bulk vouchers"""
    data = request.get_json()
    
    count = data.get('count', 1)
    plan = data.get('plan', 'hourly')
    duration = data.get('duration', 3600)  # seconds
    data_limit = data.get('data_limit')  # bytes
    expires_in_days = data.get('expires_in_days', 7)
    
    vouchers = []
    for i in range(count):
        voucher = {
            'code': generate_voucher_code(),
            'plan': plan,
            'duration': duration,
            'data_limit': data_limit,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=expires_in_days)).isoformat(),
            'status': 'unused'
        }
        vouchers.append(voucher)
        # TODO: Save to database
    
    return jsonify({
        'message': f'{count} voucher(s) generated successfully',
        'vouchers': vouchers
    })

@vouchers_bp.route('/<voucher_code>', methods=['GET'])
def get_voucher(voucher_code):
    """Get voucher details (public endpoint for validation)"""
    # TODO: Implement database query
    mock_voucher = {
        'code': voucher_code,
        'plan': 'hourly',
        'duration': 3600,
        'data_limit': None,
        'status': 'unused',
        'expires_at': '2024-01-07T09:00:00'
    }
    return jsonify(mock_voucher)

@vouchers_bp.route('/<voucher_code>/redeem', methods=['POST'])
def redeem_voucher(voucher_code):
    """Redeem a voucher"""
    data = request.get_json()
    mac_address = data.get('mac_address')
    ip_address = data.get('ip_address')
    
    # TODO: Implement voucher redemption logic
    return jsonify({
        'success': True,
        'session_id': f'session_{voucher_code}',
        'expires_at': datetime.now().isoformat()
    })

@vouchers_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_voucher_stats():
    """Get voucher statistics"""
    stats = {
        'total_generated': 150,
        'total_used': 89,
        'total_expired': 12,
        'total_unused': 49,
        'revenue_generated': 45000.00,
        'popular_plans': [
            {'plan': 'hourly', 'count': 67},
            {'plan': 'daily', 'count': 45},
            {'plan': 'weekly', 'count': 23}
        ]
    }
    return jsonify(stats)
