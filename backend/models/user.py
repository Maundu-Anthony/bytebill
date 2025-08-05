from database import db
from datetime import datetime
from sqlalchemy import Enum
import enum

class UserStatus(enum.Enum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    BLOCKED = "blocked"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)  # Supports IPv6
    mac_address = db.Column(db.String(17), nullable=False, unique=True)
    device_name = db.Column(db.String(255), nullable=True)
    status = db.Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    total_sessions = db.Column(db.Integer, default=0)
    total_data_used = db.Column(db.BigInteger, default=0)  # Total data used in bytes
    is_blocked = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'device_name': self.device_name,
            'status': self.status.value,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'total_sessions': self.total_sessions,
            'total_data_used': self.total_data_used,
            'is_blocked': self.is_blocked,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.mac_address}>'
