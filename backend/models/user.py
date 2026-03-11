"""
User model - Unified user model for all roles (Admin, Company, Student).
Handles authentication and role-based access control.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model):
    """
    Unified User model for Admin, Company, and Student roles.
    Uses role field to differentiate between user types.
    """
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Authentication fields
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Role: 'admin', 'company', 'student'
    role = db.Column(db.String(20), nullable=False, default='student')
    
    # User status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships (back_populates for bidirectional)
    company_profile = db.relationship(
        'CompanyProfile', 
        back_populates='user', 
        uselist=False,
        cascade='all, delete-orphan'
    )
    student_profile = db.relationship(
        'StudentProfile', 
        back_populates='user', 
        uselist=False,
        cascade='all, delete-orphan'
    )
    
    def __init__(self, email, password, role='student'):
        """Initialize a new user with email, password, and role."""
        self.email = email.lower().strip()
        self.set_password(password)
        self.role = role
        
        # Admin is auto-verified
        if role == 'admin':
            self.is_verified = True
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify the provided password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert user object to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


def create_admin_user(app):
    """
    Create the pre-existing admin user programmatically.
    Called during application initialization.
    """
    with app.app_context():
        from extensions import db
        
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@placement.edu')
        admin_password = app.config.get('ADMIN_PASSWORD', 'Admin@123')
        admin_name = app.config.get('ADMIN_NAME', 'Placement Admin')
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if not existing_admin:
            admin = User(
                email=admin_email,
                password=admin_password,
                role='admin'
            )
            admin.is_verified = True
            admin.is_active = True
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"Admin user created: {admin_email}")
        else:
            print(f"Admin user already exists: {admin_email}")