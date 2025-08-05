from database import db
from datetime import datetime
from sqlalchemy import Enum
from decimal import Decimal
import enum

class PlanType(enum.Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    UNLIMITED = "unlimited"

class Plan(db.Model):
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(Enum(PlanType), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in seconds
    data_limit = db.Column(db.BigInteger, nullable=True)  # Data limit in bytes, NULL for unlimited
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vouchers = db.relationship('Voucher', backref='plan', lazy=True)
    sessions = db.relationship('Session', backref='plan', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'duration': self.duration,
            'data_limit': self.data_limit,
            'price': float(self.price),
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Plan {self.name}>'
