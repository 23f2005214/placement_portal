"""
Application model - Represents a student's application to a placement drive.
Tracks application status throughout the recruitment process.
"""

from datetime import datetime
from extensions import db


class Application(db.Model):
    """
    Application model tracking student applications to placement drives.
    Includes status tracking through various stages of recruitment.
    """
    
    __tablename__ = 'applications'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    
    # Application status
    # 'applied', 'under_review', 'shortlisted', 'interview_scheduled', 
    # 'interviewed', 'selected', 'rejected', 'offer_accepted', 'offer_declined', 'withdrawn'
    status = db.Column(db.String(30), default='applied')
    
    # Application details
    cover_letter = db.Column(db.Text, nullable=True)
    resume_snapshot_url = db.Column(db.String(500), nullable=True)  # Resume at time of application
    
    # Company feedback
    company_remarks = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 rating by company
    
    # Interview details
    interview_date = db.Column(db.DateTime, nullable=True)
    interview_mode = db.Column(db.String(50), nullable=True)  # 'online', 'offline', 'telephonic'
    interview_link = db.Column(db.String(500), nullable=True)
    interview_venue = db.Column(db.String(300), nullable=True)
    interview_feedback = db.Column(db.Text, nullable=True)
    
    # Offer details (for selected candidates)
    offer_salary = db.Column(db.Float, nullable=True)
    offer_position = db.Column(db.String(200), nullable=True)
    offer_location = db.Column(db.String(200), nullable=True)
    offer_letter_url = db.Column(db.String(500), nullable=True)
    offer_deadline = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shortlisted_at = db.Column(db.DateTime, nullable=True)
    selected_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    
    # Unique constraint to prevent duplicate applications
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive_application'),
    )
    
    # Relationships
    student = db.relationship('StudentProfile', back_populates='applications')
    drive = db.relationship('PlacementDrive', back_populates='applications')
    
    def __init__(self, student_id, drive_id, **kwargs):
        """Initialize application with student and drive IDs."""
        self.student_id = student_id
        self.drive_id = drive_id
        
        # Set optional fields from kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_status(self, new_status, remarks=None):
        """
        Update application status with timestamp tracking.
        """
        self.status = new_status
        
        if remarks:
            self.company_remarks = remarks
        
        # Update specific timestamps based on status
        if new_status == 'shortlisted':
            self.shortlisted_at = datetime.utcnow()
        elif new_status == 'selected':
            self.selected_at = datetime.utcnow()
            # Update student's placement status
            if self.student:
                self.student.is_placed = True
                self.student.placement_count += 1
        elif new_status == 'rejected':
            self.rejected_at = datetime.utcnow()
        
        db.session.commit()
    
    def schedule_interview(self, date, mode, link=None, venue=None):
        """Schedule an interview for the application."""
        self.status = 'interview_scheduled'
        self.interview_date = date
        self.interview_mode = mode
        self.interview_link = link
        self.interview_venue = venue
        db.session.commit()
    
    def to_dict(self, include_student=True, include_drive=True):
        """Convert application to dictionary."""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'drive_id': self.drive_id,
            'status': self.status,
            'cover_letter': self.cover_letter,
            'resume_snapshot_url': self.resume_snapshot_url,
            'company_remarks': self.company_remarks,
            'rating': self.rating,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_mode': self.interview_mode,
            'interview_link': self.interview_link,
            'interview_venue': self.interview_venue,
            'interview_feedback': self.interview_feedback,
            'offer_salary': self.offer_salary,
            'offer_position': self.offer_position,
            'offer_location': self.offer_location,
            'offer_letter_url': self.offer_letter_url,
            'offer_deadline': self.offer_deadline.isoformat() if self.offer_deadline else None,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'shortlisted_at': self.shortlisted_at.isoformat() if self.shortlisted_at else None,
            'selected_at': self.selected_at.isoformat() if self.selected_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None
        }
        
        if include_student and self.student:
            data['student'] = {
                'id': self.student.id,
                'full_name': self.student.full_name,
                'email': self.student.user.email if self.student.user else None,
                'roll_number': self.student.roll_number,
                'branch': self.student.branch,
                'cgpa': self.student.cgpa,
                'graduation_year': self.student.graduation_year,
                'phone': self.student.phone,
                'resume_url': self.student.resume_url
            }
        
        if include_drive and self.drive:
            data['drive'] = {
                'id': self.drive.id,
                'job_title': self.drive.job_title,
                'company_name': self.drive.company.company_name if self.drive.company else None,
                'company_logo': self.drive.company.logo_url if self.drive.company else None,
                'application_deadline': self.drive.application_deadline.isoformat() if self.drive.application_deadline else None,
                'salary_display': self.drive.get_salary_display()
            }
        
        return data
    
    @staticmethod
    def get_status_display(status):
        """Get human-readable status display."""
        status_map = {
            'applied': 'Applied',
            'under_review': 'Under Review',
            'shortlisted': 'Shortlisted',
            'interview_scheduled': 'Interview Scheduled',
            'interviewed': 'Interviewed',
            'selected': 'Selected',
            'rejected': 'Rejected',
            'offer_accepted': 'Offer Accepted',
            'offer_declined': 'Offer Declined',
            'withdrawn': 'Withdrawn'
        }
        return status_map.get(status, status.replace('_', ' ').title())
    
    def __repr__(self):
        return f'<Application {self.id}: Student {self.student_id} -> Drive {self.drive_id}>'