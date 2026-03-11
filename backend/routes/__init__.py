"""
Routes package initialization.
Registers all blueprints with the Flask application.
"""

from flask import Blueprint

# Import all route blueprints
from .auth import auth_bp
from .admin import admin_bp
from .company import company_bp
from .student import student_bp
from .drive import drive_bp


def register_routes(app):
    """
    Register all API route blueprints with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(drive_bp, url_prefix='/api/drives')
    
    # Log registered routes in debug mode
    if app.debug:
        print("\n=== Registered Routes ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.methods} {rule.rule}")
        print("========================\n")