from database import db
from datetime import datetime
from sqlalchemy import Enum
import enum
import random
import string

class VoucherStatus(enum.Enum):
    UNUSED = "unused"
    USED = "used"
    EXPIRED = "expired"
    DISABLED = "disabled"

class Voucher(db.Model):
    __tablename__ = 'vouchers'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    status = db.Column(Enum(VoucherStatus), default=VoucherStatus.UNUSED)
    created_by = db.Column(db.String(100), nullable=False)  # Admin username
    used_by_mac = db.Column(db.String(17), nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    batch_id = db.Column(db.String(50), nullable=True)  # For bulk generation
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('Session', backref='voucher', lazy=True)
    
    @staticmethod
    def generate_code(length=10):
        """Generate a unique voucher code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not Voucher.query.filter_by(code=code).first():
                return code
    
    def is_valid(self):
        """Check if voucher is valid for use"""
        return (self.status == VoucherStatus.UNUSED and 
                self.expires_at > datetime.utcnow())
    
    def redeem(self, mac_address):
        """Redeem the voucher"""
        if not self.is_valid():
            return False
        
        self.status = VoucherStatus.USED
        self.used_by_mac = mac_address
        self.used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'plan_id': self.plan_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'status': self.status.value,
            'created_by': self.created_by,
            'used_by_mac': self.used_by_mac,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'batch_id': self.batch_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Voucher {self.code}>'
