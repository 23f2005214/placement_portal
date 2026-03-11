"""
Models package initialization.
Imports all models for easy access and ensures they are registered with SQLAlchemy.
"""

from .user import User
from .company import CompanyProfile
from .student import StudentProfile
from .drive import PlacementDrive
from .application import Application

# Export all models
__all__ = [
    'User',
    'CompanyProfile', 
    'StudentProfile',
    'PlacementDrive',
    'Application'
]