"""
Database models for roadside assistance service.
Uses SQLAlchemy ORM for database operations.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid

db = SQLAlchemy()


class User(db.Model):
    """User model for tracking user behavior and misuse detection."""
    __tablename__ = 'users'
    
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(200))
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requests = db.relationship('Request', backref='user', lazy=True)
    
    def get_recent_request_count(self, minutes=10):
        """Get number of requests in the last N minutes."""
        time_threshold = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return Request.query.filter(
            Request.user_id == self.id,
            Request.created_at >= time_threshold
        ).count()
    
    def get_cancel_count_today(self):
        """Get number of cancelled requests today."""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return Request.query.filter(
            Request.user_id == self.id,
            Request.status == 'cancelled',
            Request.cancelled_at >= today_start
        ).count()
    
    def increment_cancel_count(self):
        """Increment cancel count (tracked via cancelled_at timestamp)."""
        pass  # Handled by updating request status
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Mechanic(db.Model):
    """Mechanic model for tracking available mechanics."""
    __tablename__ = 'mechanics'
    
    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(200))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)
    current_request_id = db.Column(db.String(100), db.ForeignKey('requests.id'), nullable=True)
    specialization = db.Column(db.String(100))  # e.g., 'towing', 'battery', 'all'
    rating = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'location': {'lat': self.latitude, 'lon': self.longitude},
            'available': self.available,
            'specialization': self.specialization,
            'rating': self.rating
        }


class ServiceCenter(db.Model):
    """Service center model for repair facilities."""
    __tablename__ = 'service_centers'
    
    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(200))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, default=10)
    current_load = db.Column(db.Integer, default=0)
    services = db.Column(db.String(500))  # Comma-separated list
    rating = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'location': {'lat': self.latitude, 'lon': self.longitude},
            'capacity': self.capacity,
            'current_load': self.current_load,
            'services': self.services.split(',') if self.services else [],
            'rating': self.rating
        }


class Request(db.Model):
    """Service request model."""
    __tablename__ = 'requests'
    
    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    
    # Issue details
    issue_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    
    # Emergency and scoring
    emergency_score = db.Column(db.Integer, default=0)
    emergency_flag = db.Column(db.Boolean, default=False)
    suspicious = db.Column(db.Boolean, default=False)
    
    # Dispatch decision
    priority = db.Column(db.String(20))  # 'emergency', 'normal', 'low'
    response_type = db.Column(db.String(50))  # 'mechanic', 'ambulance_police_and_mechanic', 'request_location'
    
    # Location
    user_latitude = db.Column(db.Float)
    user_longitude = db.Column(db.Float)
    
    # Assignment
    selected_mechanic_id = db.Column(db.String(100), db.ForeignKey('mechanics.id'))
    selected_service_center_id = db.Column(db.String(100), db.ForeignKey('service_centers.id'))
    
    # Status and tracking
    status = db.Column(db.String(50), default='assigned')  # 'assigned', 'on_the_way', 'arriving', 'arrived', 'completed', 'cancelled'
    eta_minutes = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Relationships
    mechanic = db.relationship('Mechanic', foreign_keys=[selected_mechanic_id], backref='assigned_requests')
    service_center = db.relationship('ServiceCenter', backref='requests')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'issue_type': self.issue_type,
            'description': self.description,
            'emergency_score': self.emergency_score,
            'emergency_flag': self.emergency_flag,
            'suspicious': self.suspicious,
            'priority': self.priority,
            'response_type': self.response_type,
            'location': {
                'lat': self.user_latitude,
                'lon': self.user_longitude
            } if self.user_latitude and self.user_longitude else None,
            'selected_mechanic_id': self.selected_mechanic_id,
            'selected_service_center_id': self.selected_service_center_id,
            'status': self.status,
            'eta_minutes': self.eta_minutes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class RequestHistory(db.Model):
    """Track status changes and events for requests."""
    __tablename__ = 'request_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.String(100), db.ForeignKey('requests.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'status_change', 'location_update', 'assignment', etc.
    old_value = db.Column(db.String(200))
    new_value = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    request = db.relationship('Request', backref='history')
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'event_type': self.event_type,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
