"""
Custom decorators for role-based access control and other common patterns.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User, CompanyProfile


def get_current_user():
    """Get the current authenticated user from JWT."""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def admin_required(fn):
    """
    Decorator to restrict access to admin users only.
    Must be used after @jwt_required() decorator.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        return fn(*args, **kwargs)
    return wrapper


def company_required(fn):
    """
    Decorator to restrict access to company users only.
    Must be used after @jwt_required() decorator.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'company':
            return jsonify({'error': 'Company access required'}), 403
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        if user.is_blacklisted:
            return jsonify({'error': 'Account is blacklisted'}), 403
        
        return fn(*args, **kwargs)
    return wrapper


def approved_company_required(fn):
    """
    Decorator to restrict access to approved company users only.
    Company must be approved by admin to access certain features.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'company':
            return jsonify({'error': 'Company access required'}), 403
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        if user.is_blacklisted:
            return jsonify({'error': 'Account is blacklisted'}), 403
        
        # Check if company profile is approved
        company_profile = CompanyProfile.query.filter_by(user_id=user.id).first()
        if not company_profile:
            return jsonify({'error': 'Company profile not found'}), 404
        
        # Prefer boolean flag when available, fall back to status text
        is_approved = getattr(company_profile, 'is_approved', None)
        if is_approved is None:
            is_approved = company_profile.approval_status == 'approved'
        
        if not is_approved:
            return jsonify({
                'error': 'Company not approved',
                'message': 'Your company registration is pending admin approval',
                'approval_status': company_profile.approval_status
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def student_required(fn):
    """
    Decorator to restrict access to student users only.
    Must be used after @jwt_required() decorator.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        if user.is_blacklisted:
            return jsonify({'error': 'Account is blacklisted'}), 403
        
        return fn(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """
    Generic decorator to restrict access to specific roles.
    Usage: @role_required('admin', 'company')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user.role not in roles:
                return jsonify({'error': f'Access restricted to: {", ".join(roles)}'}), 403
            
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator