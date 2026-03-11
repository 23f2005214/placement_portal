"""
Configuration settings for the Placement Portal Application.
Contains database, JWT, Redis, Celery, and Mail configurations.
"""

import os
from datetime import timedelta

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class with common settings."""
    
    # Secret key for session management and JWT
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-in-production')
    
    # SQLite Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(BASE_DIR, "placement_portal.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL debugging
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Redis Configuration (for caching and Celery broker)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Flask-Caching Configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default cache timeout
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    CELERY_TIMEZONE = 'Asia/Kolkata'
    CELERY_ENABLE_UTC = True
    
    # Mail Configuration (for sending emails)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your-app-password')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'placement@institute.edu')
    
    # Google Chat Webhook (for notifications)
    GOOGLE_CHAT_WEBHOOK_URL = os.environ.get(
        'GOOGLE_CHAT_WEBHOOK_URL', 
        'https://chat.googleapis.com/v1/spaces/YOUR_SPACE/messages?key=YOUR_KEY'
    )
    
    # Admin credentials (pre-created admin)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@placement.edu')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    ADMIN_NAME = os.environ.get('ADMIN_NAME', 'Placement Admin')
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    # Export folder for CSV files
    EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary for easy access
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}