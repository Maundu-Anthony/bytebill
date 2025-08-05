from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.session import Session, SessionStatus
from models.user import User
from datetime import datetime

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get all sessions with pagination and filters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', 'all')  # all, active, expired, terminated
    
    query = Session.query
    
    if status != 'all':
        if status == 'active':
            query = query.filter(Session.status == SessionStatus.ACTIVE)
        elif status == 'expired':
            query = query.filter(Session.status == SessionStatus.EXPIRED)
        elif status == 'terminated':
            query = query.filter(Session.status == SessionStatus.TERMINATED)
    
    query = query.order_by(Session.created_at.desc())
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    sessions = [session.to_dict() for session in pagination.items]
    
    return jsonify({
        'sessions': sessions,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })

@sessions_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_sessions():
    """Get only active sessions"""
    sessions = Session.query.filter(Session.status == SessionStatus.ACTIVE).all()
    
    # Update expired sessions
    expired_count = 0
    for session in sessions:
        if session.is_expired():
            session.status = SessionStatus.EXPIRED
            session.end_time = datetime.utcnow()
            expired_count += 1
    
    if expired_count > 0:
        db.session.commit()
        # Re-fetch active sessions
        sessions = Session.query.filter(Session.status == SessionStatus.ACTIVE).all()
    
    return jsonify({
        'sessions': [session.to_dict() for session in sessions],
        'count': len(sessions)
    })

@sessions_bp.route('/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """Get specific session details"""
    session = Session.query.get_or_404(session_id)
    return jsonify(session.to_dict())

@sessions_bp.route('/<int:session_id>/terminate', methods=['POST'])
@jwt_required()
def terminate_session(session_id):
    """Terminate a specific session"""
    session = Session.query.get_or_404(session_id)
    
    if session.status == SessionStatus.ACTIVE:
        session.terminate("admin_terminated")
        db.session.commit()
        
        # TODO: Implement actual network disconnection logic here
        # This would involve iptables rules or CoovaChilli commands
        
        return jsonify({
            'message': f'Session {session_id} terminated successfully',
            'session': session.to_dict()
        })
    else:
        return jsonify({'error': 'Session is not active'}), 400

@sessions_bp.route('/terminate-expired', methods=['POST'])
@jwt_required()
def terminate_expired_sessions():
    """Terminate all expired sessions"""
    active_sessions = Session.query.filter(Session.status == SessionStatus.ACTIVE).all()
    
    terminated_count = 0
    for session in active_sessions:
        if session.is_expired():
            session.terminate("expired")
            terminated_count += 1
    
    if terminated_count > 0:
        db.session.commit()
    
    return jsonify({
        'message': f'{terminated_count} expired sessions terminated',
        'terminated_count': terminated_count
    })

@sessions_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_session_stats():
    """Get session statistics"""
    total_sessions = Session.query.count()
    active_sessions = Session.query.filter(Session.status == SessionStatus.ACTIVE).count()
    expired_sessions = Session.query.filter(Session.status == SessionStatus.EXPIRED).count()
    terminated_sessions = Session.query.filter(Session.status == SessionStatus.TERMINATED).count()
    
    # Calculate total data usage
    total_data_query = db.session.query(
        db.func.sum(Session.bytes_uploaded + Session.bytes_downloaded)
    ).scalar()
    total_data_used = total_data_query or 0
    
    # Calculate total revenue
    total_revenue_query = db.session.query(
        db.func.sum(Session.amount_paid)
    ).scalar()
    total_revenue = float(total_revenue_query or 0)
    
    stats = {
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'expired_sessions': expired_sessions,
        'terminated_sessions': terminated_sessions,
        'total_data_used': total_data_used,
        'total_revenue': total_revenue,
        'session_breakdown': {
            'active': active_sessions,
            'expired': expired_sessions,
            'terminated': terminated_sessions
        }
    }
    
    return jsonify(stats)
