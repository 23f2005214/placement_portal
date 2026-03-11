"""
Authentication routes - Handles user registration, login, and token management.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from extensions import db, cache
from models import User, CompanyProfile, StudentProfile
from utils.helpers import validate_email, validate_password

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    """
    Register a new student account.
    
    Request Body:
        - email: Student email (required)
        - password: Password (required)
        - first_name: First name (required)
        - last_name: Last name (optional)
        - branch: Branch of study (required)
        - year_of_study: Current year (required)
        - graduation_year: Expected graduation year (required)
        - cgpa: Current CGPA (required)
        - phone: Phone number (optional)
        - roll_number: Roll number (optional)
    
    Returns:
        JSON response with success message or error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'branch', 
                          'year_of_study', 'graduation_year', 'cgpa']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email'].lower()).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user account
        user = User(
            email=data['email'],
            password=data['password'],
            role='student'
        )
        user.is_verified = True  # Auto-verify students for simplicity
        
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Create student profile
        student_profile = StudentProfile(
            user_id=user.id,
            first_name=data['first_name'],
            last_name=data.get('last_name'),
            branch=data['branch'],
            year_of_study=int(data['year_of_study']),
            graduation_year=int(data['graduation_year']),
            cgpa=float(data['cgpa']),
            phone=data.get('phone'),
            roll_number=data.get('roll_number'),
            tenth_percentage=data.get('tenth_percentage'),
            twelfth_percentage=data.get('twelfth_percentage'),
            active_backlogs=data.get('active_backlogs', 0),
            skills=data.get('skills'),
            gender=data.get('gender'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state')
        )
        
        db.session.add(student_profile)
        db.session.commit()
        
        # Generate tokens (identity must be string to avoid invalid subject errors)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Student registered successfully',
            'user': user.to_dict(),
            'profile': student_profile.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    """
    Register a new company account.
    
    Request Body:
        - email: Company email (required)
        - password: Password (required)
        - company_name: Company name (required)
        - company_description: Description (optional)
        - industry: Industry type (optional)
        - website: Company website (optional)
        - hr_name: HR contact name (optional)
        - hr_email: HR email (optional)
        - hr_phone: HR phone (optional)
        - address, city, state, country: Location details (optional)
        - company_size: Size range (optional)
        - company_type: Type (Private, MNC, etc.) (optional)
    
    Returns:
        JSON response with success message or error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'company_name']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email'].lower()).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user account
        user = User(
            email=data['email'],
            password=data['password'],
            role='company'
        )
        
        db.session.add(user)
        db.session.flush()
        
        # Create company profile (pending approval)
        company_profile = CompanyProfile(
            user_id=user.id,
            company_name=data['company_name'],
            company_description=data.get('company_description'),
            industry=data.get('industry'),
            website=data.get('website'),
            hr_name=data.get('hr_name'),
            hr_email=data.get('hr_email'),
            hr_phone=data.get('hr_phone'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country', 'India'),
            company_size=data.get('company_size'),
            company_type=data.get('company_type'),
            approval_status='pending'  # Requires admin approval
        )
        
        db.session.add(company_profile)
        db.session.commit()
        
        # Generate tokens (use string identity)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Company registered successfully. Awaiting admin approval.',
            'user': user.to_dict(),
            'profile': company_profile.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login for all roles (admin, company, student).
    
    Request Body:
        - email: User email (required)
        - password: User password (required)
    
    Returns:
        JSON response with tokens and user info or error
    """
    try:
        data = request.get_json()
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated. Please contact admin.'}), 403
        
        # Check if user is blacklisted
        if user.is_blacklisted:
            return jsonify({'error': 'Account is blacklisted. Please contact admin.'}), 403
        
        # Update last login
        user.update_last_login()
        
        # Generate tokens (string identity to satisfy JWT subject requirement)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Prepare response based on role
        response_data = {
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        
        # Include profile data based on role
        if user.role == 'student' and user.student_profile:
            response_data['profile'] = user.student_profile.to_dict()
        elif user.role == 'company' and user.company_profile:
            response_data['profile'] = user.company_profile.to_dict()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh access token using refresh token.
    
    Returns:
        New access token
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'Invalid user'}), 401
        
        # ID from jwt is a string already; ensure we pass string
        access_token = create_access_token(identity=str(user_id))
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user's information.
    
    Returns:
        User data with profile
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        response_data = {
            'user': user.to_dict()
        }
        
        # Include profile based on role
        if user.role == 'student' and user.student_profile:
            response_data['profile'] = user.student_profile.to_dict()
        elif user.role == 'company' and user.company_profile:
            response_data['profile'] = user.company_profile.to_dict()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password.
    
    Request Body:
        - current_password: Current password (required)
        - new_password: New password (required)
    
    Returns:
        Success message or error
    """
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new password are required'}), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client should remove tokens).
    
    Returns:
        Success message
    """
    # In a production app, you might want to blacklist the token
    # For now, we just return success and let client handle token removal
    return jsonify({'message': 'Logged out successfully'}), 200