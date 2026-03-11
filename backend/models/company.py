"""
Company Profile model - Stores company-specific information.
Linked to User model for authentication.
"""

from datetime import datetime
from extensions import db


class CompanyProfile(db.Model):
    """
    Company profile containing company-specific details.
    Each company has one user account for authentication.
    """
    
    __tablename__ = 'company_profiles'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Company details
    company_name = db.Column(db.String(200), nullable=False)
    company_description = db.Column(db.Text, nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    
    # Contact information
    hr_name = db.Column(db.String(100), nullable=True)
    hr_email = db.Column(db.String(120), nullable=True)
    hr_phone = db.Column(db.String(20), nullable=True)
    
    # Address
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), default='India')
    
    # Company size and type
    company_size = db.Column(db.String(50), nullable=True)  # e.g., "50-100", "500+"
    company_type = db.Column(db.String(50), nullable=True)  # e.g., "Private", "MNC", "Startup"
    
    # Logo
    logo_url = db.Column(db.String(500), nullable=True)
    
    # Approval status: 'pending', 'approved', 'rejected'
    approval_status = db.Column(db.String(20), default='pending')
    approval_date = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='company_profile')
    placement_drives = db.relationship(
        'PlacementDrive', 
        back_populates='company',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    def __init__(self, user_id, company_name, **kwargs):
        """Initialize company profile with required fields."""
        self.user_id = user_id
        self.company_name = company_name
        
        # Set optional fields from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def approve(self):
        """Approve the company registration."""
        self.approval_status = 'approved'
        self.approval_date = datetime.utcnow()
        self.rejection_reason = None
        db.session.commit()
    
    def reject(self, reason=None):
        """Reject the company registration with optional reason."""
        self.approval_status = 'rejected'
        self.rejection_reason = reason
        db.session.commit()
    
    def to_dict(self):
        """Convert company profile to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'company_description': self.company_description,
            'industry': self.industry,
            'website': self.website,
            'hr_name': self.hr_name,
            'hr_email': self.hr_email,
            'hr_phone': self.hr_phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'company_size': self.company_size,
            'company_type': self.company_type,
            'logo_url': self.logo_url,
            'approval_status': self.approval_status,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'email': self.user.email if self.user else None,
            'is_active': self.user.is_active if self.user else None,
            'is_blacklisted': self.user.is_blacklisted if self.user else None
        }
    
    def __repr__(self):
        return f'<CompanyProfile {self.company_name}>'