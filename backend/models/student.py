"""
Student Profile model - Stores student-specific information.
Linked to User model for authentication.
"""

from datetime import datetime
from extensions import db


class StudentProfile(db.Model):
    """
    Student profile containing student-specific academic and personal details.
    Each student has one user account for authentication.
    """
    
    __tablename__ = 'student_profiles'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Personal details
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    
    # Academic details
    roll_number = db.Column(db.String(50), unique=True, nullable=True)
    branch = db.Column(db.String(100), nullable=False)  # e.g., "Computer Science", "Electronics"
    department = db.Column(db.String(100), nullable=True)
    year_of_study = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    graduation_year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    
    # 10th and 12th marks
    tenth_percentage = db.Column(db.Float, nullable=True)
    twelfth_percentage = db.Column(db.Float, nullable=True)
    
    # Backlogs
    active_backlogs = db.Column(db.Integer, default=0)
    history_of_backlogs = db.Column(db.Integer, default=0)
    
    # Skills and resume
    skills = db.Column(db.Text, nullable=True)  # Comma-separated skills
    resume_url = db.Column(db.String(500), nullable=True)
    linkedin_url = db.Column(db.String(300), nullable=True)
    github_url = db.Column(db.String(300), nullable=True)
    portfolio_url = db.Column(db.String(300), nullable=True)
    
    # Address
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    
    # Placement status
    is_placed = db.Column(db.Boolean, default=False)
    placement_count = db.Column(db.Integer, default=0)  # Number of offers received
    
    # Profile picture
    profile_picture_url = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='student_profile')
    applications = db.relationship(
        'Application', 
        back_populates='student',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    def __init__(self, user_id, first_name, branch, year_of_study, graduation_year, cgpa, **kwargs):
        """Initialize student profile with required fields."""
        self.user_id = user_id
        self.first_name = first_name
        self.branch = branch
        self.year_of_study = year_of_study
        self.graduation_year = graduation_year
        self.cgpa = cgpa
        
        # Set optional fields from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def full_name(self):
        """Return the full name of the student."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def get_skills_list(self):
        """Return skills as a list."""
        if self.skills:
            return [s.strip() for s in self.skills.split(',')]
        return []
    
    def check_eligibility(self, drive):
        """
        Check if student is eligible for a placement drive.
        Returns tuple (is_eligible, reasons).
        """
        reasons = []
        is_eligible = True
        
        # Check CGPA
        if drive.min_cgpa and self.cgpa < drive.min_cgpa:
            is_eligible = False
            reasons.append(f"CGPA {self.cgpa} is below minimum required {drive.min_cgpa}")
        
        # Check branch
        if drive.eligible_branches:
            branches = [b.strip().lower() for b in drive.eligible_branches.split(',')]
            if self.branch.lower() not in branches and 'all' not in branches:
                is_eligible = False
                reasons.append(f"Branch '{self.branch}' is not eligible")
        
        # Check graduation year
        if drive.eligible_graduation_years:
            years = [int(y.strip()) for y in drive.eligible_graduation_years.split(',')]
            if self.graduation_year not in years:
                is_eligible = False
                reasons.append(f"Graduation year {self.graduation_year} is not eligible")
        
        # Check backlogs
        if drive.max_backlogs is not None and self.active_backlogs > drive.max_backlogs:
            is_eligible = False
            reasons.append(f"Active backlogs ({self.active_backlogs}) exceed maximum allowed ({drive.max_backlogs})")
        
        # Check 10th percentage
        if drive.min_tenth_percentage and self.tenth_percentage:
            if self.tenth_percentage < drive.min_tenth_percentage:
                is_eligible = False
                reasons.append(f"10th percentage below minimum required")
        
        # Check 12th percentage
        if drive.min_twelfth_percentage and self.twelfth_percentage:
            if self.twelfth_percentage < drive.min_twelfth_percentage:
                is_eligible = False
                reasons.append(f"12th percentage below minimum required")
        
        return is_eligible, reasons
    
    def to_dict(self):
        """Convert student profile to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'roll_number': self.roll_number,
            'branch': self.branch,
            'department': self.department,
            'year_of_study': self.year_of_study,
            'graduation_year': self.graduation_year,
            'cgpa': self.cgpa,
            'tenth_percentage': self.tenth_percentage,
            'twelfth_percentage': self.twelfth_percentage,
            'active_backlogs': self.active_backlogs,
            'history_of_backlogs': self.history_of_backlogs,
            'skills': self.get_skills_list(),
            'resume_url': self.resume_url,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'is_placed': self.is_placed,
            'placement_count': self.placement_count,
            'profile_picture_url': self.profile_picture_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'email': self.user.email if self.user else None,
            'is_active': self.user.is_active if self.user else None,
            'is_blacklisted': self.user.is_blacklisted if self.user else None
        }
    
    def __repr__(self):
        return f'<StudentProfile {self.full_name} ({self.roll_number})>'