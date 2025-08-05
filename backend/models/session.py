from database import db
from datetime import datetime
from sqlalchemy import Enum
import enum

class SessionStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    PAUSED = "paused"

class PaymentMethod(enum.Enum):
    VOUCHER = "voucher"
    MPESA = "mpesa"
    FREE = "free"

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    voucher_id = db.Column(db.Integer, db.ForeignKey('vouchers.id'), nullable=True)
    
    # Session details
    status = db.Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    payment_method = db.Column(Enum(PaymentMethod), nullable=False)
    payment_reference = db.Column(db.String(100), nullable=True)  # Voucher code or M-PESA code
    
    # Time tracking
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    duration_limit = db.Column(db.Integer, nullable=False)  # In seconds
    time_used = db.Column(db.Integer, default=0)  # In seconds
    
    # Data tracking
    data_limit = db.Column(db.BigInteger, nullable=True)  # In bytes, NULL for unlimited
    bytes_uploaded = db.Column(db.BigInteger, default=0)
    bytes_downloaded = db.Column(db.BigInteger, default=0)
    
    # Network details
    ip_address = db.Column(db.String(45), nullable=False)
    mac_address = db.Column(db.String(17), nullable=False)
    
    # Billing
    amount_paid = db.Column(db.Numeric(10, 2), default=0.00)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def total_data_used(self):
        """Calculate total data used"""
        return self.bytes_uploaded + self.bytes_downloaded
    
    @property
    def time_remaining(self):
        """Calculate remaining time in seconds"""
        if self.status != SessionStatus.ACTIVE:
            return 0
        
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        remaining = max(0, self.duration_limit - elapsed)
        return int(remaining)
    
    @property
    def data_remaining(self):
        """Calculate remaining data in bytes"""
        if not self.data_limit:
            return None  # Unlimited
        
        remaining = max(0, self.data_limit - self.total_data_used)
        return remaining
    
    def is_expired(self):
        """Check if session has expired"""
        if self.status != SessionStatus.ACTIVE:
            return True
            
        # Check time limit
        if self.time_remaining <= 0:
            return True
            
        # Check data limit
        if self.data_limit and self.data_remaining <= 0:
            return True
            
        return False
    
    def terminate(self, reason="manual"):
        """Terminate the session"""
        self.status = SessionStatus.TERMINATED
        self.end_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'voucher_id': self.voucher_id,
            'status': self.status.value,
            'payment_method': self.payment_method.value,
            'payment_reference': self.payment_reference,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'duration_limit': self.duration_limit,
            'time_used': self.time_used,
            'time_remaining': self.time_remaining,
            'data_limit': self.data_limit,
            'data_remaining': self.data_remaining,
            'bytes_uploaded': self.bytes_uploaded,
            'bytes_downloaded': self.bytes_downloaded,
            'total_data_used': self.total_data_used,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'amount_paid': float(self.amount_paid),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Session {self.session_id}>'
