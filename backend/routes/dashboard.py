from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.session import Session, SessionStatus
from models.voucher import Voucher, VoucherStatus
from models.user import User
from models.plan import Plan
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    """Get main dashboard overview statistics"""
    
    # User statistics
    total_users = User.query.count()
    active_sessions = Session.query.filter(Session.status == SessionStatus.ACTIVE).count()
    
    # Update expired sessions before counting
    expired_sessions_updated = 0
    active_session_objects = Session.query.filter(Session.status == SessionStatus.ACTIVE).all()
    for session in active_session_objects:
        if session.is_expired():
            session.status = SessionStatus.EXPIRED
            session.end_time = datetime.utcnow()
            expired_sessions_updated += 1
    
    if expired_sessions_updated > 0:
        db.session.commit()
        active_sessions = Session.query.filter(Session.status == SessionStatus.ACTIVE).count()
    
    # Voucher statistics
    total_vouchers = Voucher.query.count()
    unused_vouchers = Voucher.query.filter(Voucher.status == VoucherStatus.UNUSED).count()
    used_vouchers = Voucher.query.filter(Voucher.status == VoucherStatus.USED).count()
    
    # Revenue statistics (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    revenue_query = db.session.query(
        func.sum(Session.amount_paid)
    ).filter(Session.created_at >= thirty_days_ago).scalar()
    monthly_revenue = float(revenue_query or 0)
    
    # Today's revenue
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue_query = db.session.query(
        func.sum(Session.amount_paid)
    ).filter(Session.created_at >= today_start).scalar()
    today_revenue = float(today_revenue_query or 0)
    
    # Data usage statistics
    total_data_query = db.session.query(
        func.sum(Session.bytes_uploaded + Session.bytes_downloaded)
    ).scalar()
    total_data_used = total_data_query or 0
    
    # Today's data usage
    today_data_query = db.session.query(
        func.sum(Session.bytes_uploaded + Session.bytes_downloaded)
    ).filter(Session.created_at >= today_start).scalar()
    today_data_used = today_data_query or 0
    
    overview = {
        'users': {
            'total': total_users,
            'active_sessions': active_sessions,
            'peak_concurrent': 25  # TODO: Calculate from historical data
        },
        'vouchers': {
            'total': total_vouchers,
            'unused': unused_vouchers,
            'used': used_vouchers,
            'expired': total_vouchers - unused_vouchers - used_vouchers
        },
        'revenue': {
            'today': today_revenue,
            'this_month': monthly_revenue,
            'total': monthly_revenue  # TODO: Calculate total from all sessions
        },
        'data_usage': {
            'today_bytes': today_data_used,
            'today_mb': round(today_data_used / (1024 * 1024), 2),
            'total_bytes': total_data_used,
            'total_gb': round(total_data_used / (1024 * 1024 * 1024), 2)
        },
        'system': {
            'uptime': '2 days, 5 hours',  # TODO: Get actual system uptime
            'load_balancing': True,
            'captive_portal': True
        }
    }
    
    return jsonify(overview)

@dashboard_bp.route('/charts/sessions', methods=['GET'])
@jwt_required()
def get_session_charts():
    """Get session data for charts"""
    period = request.args.get('period', '7d')  # 24h, 7d, 30d
    
    if period == '24h':
        start_time = datetime.utcnow() - timedelta(hours=24)
        interval = timedelta(hours=1)
    elif period == '7d':
        start_time = datetime.utcnow() - timedelta(days=7)
        interval = timedelta(days=1)
    elif period == '30d':
        start_time = datetime.utcnow() - timedelta(days=30)
        interval = timedelta(days=1)
    else:
        start_time = datetime.utcnow() - timedelta(days=7)
        interval = timedelta(days=1)
    
    # Generate time series data
    sessions_over_time = []
    current_time = start_time
    
    while current_time <= datetime.utcnow():
        next_time = current_time + interval
        
        session_count = Session.query.filter(
            Session.created_at >= current_time,
            Session.created_at < next_time
        ).count()
        
        sessions_over_time.append({
            'timestamp': current_time.isoformat(),
            'sessions': session_count
        })
        
        current_time = next_time
    
    return jsonify({
        'period': period,
        'sessions_over_time': sessions_over_time
    })

@dashboard_bp.route('/charts/revenue', methods=['GET'])
@jwt_required()
def get_revenue_charts():
    """Get revenue data for charts"""
    period = request.args.get('period', '30d')
    
    if period == '7d':
        start_time = datetime.utcnow() - timedelta(days=7)
        interval = timedelta(days=1)
    elif period == '30d':
        start_time = datetime.utcnow() - timedelta(days=30)
        interval = timedelta(days=1)
    else:
        start_time = datetime.utcnow() - timedelta(days=30)
        interval = timedelta(days=1)
    
    # Generate revenue time series data
    revenue_over_time = []
    current_time = start_time
    
    while current_time <= datetime.utcnow():
        next_time = current_time + interval
        
        revenue_query = db.session.query(
            func.sum(Session.amount_paid)
        ).filter(
            Session.created_at >= current_time,
            Session.created_at < next_time
        ).scalar()
        
        daily_revenue = float(revenue_query or 0)
        
        revenue_over_time.append({
            'timestamp': current_time.isoformat(),
            'revenue': daily_revenue
        })
        
        current_time = next_time
    
    return jsonify({
        'period': period,
        'revenue_over_time': revenue_over_time
    })

@dashboard_bp.route('/charts/data-usage', methods=['GET'])
@jwt_required()
def get_data_usage_charts():
    """Get data usage charts"""
    period = request.args.get('period', '7d')
    
    if period == '24h':
        start_time = datetime.utcnow() - timedelta(hours=24)
        interval = timedelta(hours=1)
    elif period == '7d':
        start_time = datetime.utcnow() - timedelta(days=7)
        interval = timedelta(days=1)
    else:
        start_time = datetime.utcnow() - timedelta(days=7)
        interval = timedelta(days=1)
    
    # Generate data usage time series
    data_usage_over_time = []
    current_time = start_time
    
    while current_time <= datetime.utcnow():
        next_time = current_time + interval
        
        upload_query = db.session.query(
            func.sum(Session.bytes_uploaded)
        ).filter(
            Session.created_at >= current_time,
            Session.created_at < next_time
        ).scalar()
        
        download_query = db.session.query(
            func.sum(Session.bytes_downloaded)
        ).filter(
            Session.created_at >= current_time,
            Session.created_at < next_time
        ).scalar()
        
        upload_bytes = upload_query or 0
        download_bytes = download_query or 0
        
        data_usage_over_time.append({
            'timestamp': current_time.isoformat(),
            'upload_mb': round(upload_bytes / (1024 * 1024), 2),
            'download_mb': round(download_bytes / (1024 * 1024), 2),
            'total_mb': round((upload_bytes + download_bytes) / (1024 * 1024), 2)
        })
        
        current_time = next_time
    
    return jsonify({
        'period': period,
        'data_usage_over_time': data_usage_over_time
    })

@dashboard_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_system_alerts():
    """Get system alerts and notifications"""
    
    alerts = []
    
    # Check for expired vouchers
    expired_vouchers = Voucher.query.filter(
        Voucher.expires_at < datetime.utcnow(),
        Voucher.status == VoucherStatus.UNUSED
    ).count()
    
    if expired_vouchers > 0:
        alerts.append({
            'type': 'warning',
            'title': 'Expired Vouchers',
            'message': f'{expired_vouchers} unused vouchers have expired',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Check for low voucher stock
    unused_vouchers = Voucher.query.filter(Voucher.status == VoucherStatus.UNUSED).count()
    if unused_vouchers < 10:
        alerts.append({
            'type': 'info',
            'title': 'Low Voucher Stock',
            'message': f'Only {unused_vouchers} vouchers remaining',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Check for high concurrent users (mock)
    active_sessions = Session.query.filter(Session.status == SessionStatus.ACTIVE).count()
    if active_sessions > 20:
        alerts.append({
            'type': 'warning',
            'title': 'High Concurrent Users',
            'message': f'{active_sessions} active sessions - monitor bandwidth',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return jsonify({'alerts': alerts})
