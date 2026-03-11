"""
Placement Drive model - Represents a recruitment drive created by a company.
Contains job details, eligibility criteria, and status tracking.
"""

from datetime import datetime
from extensions import db


class PlacementDrive(db.Model):
    """
    Placement Drive model for company recruitment events.
    Includes job details, eligibility criteria, and drive status.
    """
    
    __tablename__ = 'placement_drives'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to Company
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    
    # Job details
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.String(50), default='Full-time')  # Full-time, Internship, Part-time
    job_location = db.Column(db.String(200), nullable=True)
    work_mode = db.Column(db.String(50), default='On-site')  # On-site, Remote, Hybrid
    
    # Compensation
    salary_min = db.Column(db.Float, nullable=True)
    salary_max = db.Column(db.Float, nullable=True)
    salary_currency = db.Column(db.String(10), default='INR')
    salary_period = db.Column(db.String(20), default='per annum')  # per annum, per month
    
    # Eligibility criteria
    eligible_branches = db.Column(db.String(500), nullable=True)  # Comma-separated: "CSE,IT,ECE"
    eligible_graduation_years = db.Column(db.String(100), nullable=True)  # Comma-separated: "2024,2025"
    min_cgpa = db.Column(db.Float, nullable=True)
    min_tenth_percentage = db.Column(db.Float, nullable=True)
    min_twelfth_percentage = db.Column(db.Float, nullable=True)
    max_backlogs = db.Column(db.Integer, nullable=True)
    required_skills = db.Column(db.Text, nullable=True)  # Comma-separated skills
    
    # Drive details
    number_of_positions = db.Column(db.Integer, default=1)
    application_deadline = db.Column(db.DateTime, nullable=False)
    drive_date = db.Column(db.DateTime, nullable=True)
    drive_venue = db.Column(db.String(300), nullable=True)
    
    # Selection process
    selection_process = db.Column(db.Text, nullable=True)  # Description of rounds
    number_of_rounds = db.Column(db.Integer, nullable=True)
    
    # Status: 'pending', 'approved', 'rejected', 'ongoing', 'completed', 'cancelled'
    status = db.Column(db.String(20), default='pending')
    admin_remarks = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    company = db.relationship('CompanyProfile', back_populates='placement_drives')
    applications = db.relationship(
        'Application',
        back_populates='drive',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    
    def __init__(self, company_id, job_title, job_description, application_deadline, **kwargs):
        """Initialize placement drive with required fields."""
        self.company_id = company_id
        self.job_title = job_title
        self.job_description = job_description
        self.application_deadline = application_deadline
        
        # Set optional fields from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def is_deadline_passed(self):
        """Check if the application deadline has passed."""
        return datetime.utcnow() > self.application_deadline
    
    @property
    def is_active(self):
        """Check if the drive is currently active and accepting applications."""
        return (
            self.status == 'approved' and 
            not self.is_deadline_passed
        )
    
    @property
    def application_count(self):
        """Get the total number of applications."""
        return self.applications.count()
    
    def get_eligible_branches_list(self):
        """Return eligible branches as a list."""
        if self.eligible_branches:
            return [b.strip() for b in self.eligible_branches.split(',')]
        return []
    
    def get_required_skills_list(self):
        """Return required skills as a list."""
        if self.required_skills:
            return [s.strip() for s in self.required_skills.split(',')]
        return []
    
    def get_salary_display(self):
        """Return formatted salary string."""
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f} {self.salary_period}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,.0f} {self.salary_period}"
        elif self.salary_max:
            return f"Up to {self.salary_currency} {self.salary_max:,.0f} {self.salary_period}"
        return "Not disclosed"
    
    def approve(self, remarks=None):
        """Approve the placement drive."""
        self.status = 'approved'
        self.approved_at = datetime.utcnow()
        self.admin_remarks = remarks
        db.session.commit()
    
    def reject(self, remarks=None):
        """Reject the placement drive."""
        self.status = 'rejected'
        self.admin_remarks = remarks
        db.session.commit()
    
    def to_dict(self, include_company=True):
        """Convert placement drive to dictionary."""
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'job_title': self.job_title,
            'job_description': self.job_description,
            'job_type': self.job_type,
            'job_location': self.job_location,
            'work_mode': self.work_mode,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'salary_period': self.salary_period,
            'salary_display': self.get_salary_display(),
            'eligible_branches': self.get_eligible_branches_list(),
            'eligible_graduation_years': self.eligible_graduation_years,
            'min_cgpa': self.min_cgpa,
            'min_tenth_percentage': self.min_tenth_percentage,
            'min_twelfth_percentage': self.min_twelfth_percentage,
            'max_backlogs': self.max_backlogs,
            'required_skills': self.get_required_skills_list(),
            'number_of_positions': self.number_of_positions,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'drive_date': self.drive_date.isoformat() if self.drive_date else None,
            'drive_venue': self.drive_venue,
            'selection_process': self.selection_process,
            'number_of_rounds': self.number_of_rounds,
            'status': self.status,
            'admin_remarks': self.admin_remarks,
            'is_deadline_passed': self.is_deadline_passed,
            'is_active': self.is_active,
            'application_count': self.application_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }
        
        if include_company and self.company:
            data['company'] = {
                'id': self.company.id,
                'company_name': self.company.company_name,
                'industry': self.company.industry,
                'logo_url': self.company.logo_url,
                'website': self.company.website
            }
        
        return data
    
    def __repr__(self):
        return f'<PlacementDrive {self.job_title} by Company {self.company_id}>'