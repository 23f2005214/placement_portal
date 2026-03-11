"""
Flask extensions initialization.
Centralizes all extension objects for clean imports across the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from flask_mail import Mail

# Database ORM
db = SQLAlchemy()

# JWT Authentication Manager
jwt = JWTManager()

# Cross-Origin Resource Sharing
cors = CORS()

# Redis Cache
cache = Cache()

# Email functionality
mail = Mail()