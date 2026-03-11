"""
Company routes - Handles company dashboard, drives, and application management.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from extensions import db, cache
from models import User, CompanyProfile, PlacementDrive, Application, StudentProfile
from utils.decorators import company_required, approved_company_required
from utils.helpers import parse_datetime

# Create blueprint
company_bp = Blueprint('company', __name__)


def get_company_profile():
    """Helper to get current company profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user and user.company_profile:
        return user.company_profile
    return None


@company_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@company_required
def get_dashboard():
    """
    Get company dashboard with statistics and recent activities.
    
    Returns:
        Dashboard data including company info, stats, and recent activities
    """
    try:
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        # Get drive statistics
        total_drives = company.placement_drives.count()
        approved_drives = company.placement_drives.filter_by(status='approved').count()
        pending_drives = company.placement_drives.filter_by(status='pending').count()
        active_drives = company.placement_drives.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline > datetime.utcnow()
        ).count()
        
        # Get application statistics
        total_applications = 0
        shortlisted = 0
        selected = 0
        
        for drive in company.placement_drives:
            total_applications += drive.application_count
            shortlisted += drive.applications.filter_by(status='shortlisted').count()
            selected += drive.applications.filter_by(status='selected').count()
        
        # Get recent drives
        recent_drives = company.placement_drives.order_by(
            PlacementDrive.created_at.desc()
        ).limit(5).all()
        
        # Get recent applications
        recent_applications = Application.query.join(PlacementDrive).filter(
            PlacementDrive.company_id == company.id
        ).order_by(Application.applied_at.desc()).limit(10).all()
        
        return jsonify({
            'company': company.to_dict(),
            'statistics': {
                'total_drives': total_drives,
                'approved_drives': approved_drives,
                'pending_drives': pending_drives,
                'active_drives': active_drives,
                'total_applications': total_applications,
                'shortlisted': shortlisted,
                'selected': selected
            },
            'recent_drives': [d.to_dict(include_company=False) for d in recent_drives],
            'recent_applications': [a.to_dict(include_drive=False) for a in recent_applications]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@company_bp.route('/profile', methods=['GET'])
@jwt_required()
@company_required
def get_profile():
    """Get company profile."""
    try:
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        return jsonify({'company': company.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@company_bp.route('/profile', methods=['PUT'])
@jwt_required()
@company_required
def update_profile():
    """Update company profile."""
    try:
        data = request.get_json()
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        # Update allowed fields
        updatable_fields = [
            'company_name', 'company_description', 'industry', 'website',
            'hr_name', 'hr_email', 'hr_phone', 'address', 'city', 'state',
            'country', 'company_size', 'company_type', 'logo_url'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(company, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'company': company.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== DRIVE MANAGEMENT ====================

@company_bp.route('/drives', methods=['GET'])
@jwt_required()
@company_required
def get_company_drives():
    """
    Get all drives created by the company.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - status: Filter by status
    
    Returns:
        Paginated list of drives
    """
    try:
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = company.placement_drives
        
        if status:
            query = query.filter(PlacementDrive.status == status)
        
        query = query.order_by(PlacementDrive.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'drives': [d.to_dict(include_company=False) for d in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@company_bp.route('/drives', methods=['POST'])
@jwt_required()
@approved_company_required
def create_drive():
    """
    Create a new placement drive.
    
    Request Body:
        - job_title: Job title (required)
        - job_description: Job description (required)
        - application_deadline: Deadline datetime (required)
        - job_type: Full-time, Internship, Part-time (optional)
        - job_location: Location (optional)
        - work_mode: On-site, Remote, Hybrid (optional)
        - salary_min, salary_max: Salary range (optional)
        - eligible_branches: Comma-separated branches (optional)
        - eligible_graduation_years: Comma-separated years (optional)
        - min_cgpa: Minimum CGPA (optional)
        - max_backlogs: Maximum backlogs allowed (optional)
        - required_skills: Required skills (optional)
        - number_of_positions: Number of openings (optional)
        - selection_process: Description of selection process (optional)
    
    Returns:
        Created drive object
    """
    try:
        data = request.get_json()
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        # Validate required fields
        required_fields = ['job_title', 'job_description', 'application_deadline']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse deadline
        deadline = parse_datetime(data['application_deadline'])
        if not deadline:
            return jsonify({'error': 'Invalid application_deadline format'}), 400
        
        if deadline <= datetime.utcnow():
            return jsonify({'error': 'Application deadline must be in the future'}), 400
        
        # Create drive
        drive = PlacementDrive(
            company_id=company.id,
            job_title=data['job_title'],
            job_description=data['job_description'],
            application_deadline=deadline,
            job_type=data.get('job_type', 'Full-time'),
            job_location=data.get('job_location'),
            work_mode=data.get('work_mode', 'On-site'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            salary_currency=data.get('salary_currency', 'INR'),
            salary_period=data.get('salary_period', 'per annum'),
            eligible_branches=data.get('eligible_branches'),
            eligible_graduation_years=data.get('eligible_graduation_years'),
            min_cgpa=data.get('min_cgpa'),
            min_tenth_percentage=data.get('min_tenth_percentage'),
            min_twelfth_percentage=data.get('min_twelfth_percentage'),
            max_backlogs=data.get('max_backlogs'),
            required_skills=data.get('required_skills'),
            number_of_positions=data.get('number_of_positions', 1),
            drive_date=parse_datetime(data.get('drive_date')) if data.get('drive_date') else None,
            drive_venue=data.get('drive_venue'),
            selection_process=data.get('selection_process'),
            number_of_rounds=data.get('number_of_rounds'),
            status='pending'  # Requires admin approval
        )
        
        db.session.add(drive)
        db.session.commit()
        
        return jsonify({
            'message': 'Drive created successfully. Awaiting admin approval.',
            'drive': drive.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/drives/<int:drive_id>', methods=['GET'])
@jwt_required()
@company_required
def get_drive(drive_id):
    """Get a specific drive with application statistics."""
    try:
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        drive = PlacementDrive.query.filter_by(
            id=drive_id, 
            company_id=company.id
        ).first_or_404()
        
        # Get application breakdown
        applied = drive.applications.filter_by(status='applied').count()
        under_review = drive.applications.filter_by(status='under_review').count()
        shortlisted = drive.applications.filter_by(status='shortlisted').count()
        interview_scheduled = drive.applications.filter_by(status='interview_scheduled').count()
        selected = drive.applications.filter_by(status='selected').count()
        rejected = drive.applications.filter_by(status='rejected').count()
        
        return jsonify({
            'drive': drive.to_dict(include_company=False),
            'application_breakdown': {
                'total': drive.application_count,
                'applied': applied,
                'under_review': under_review,
                'shortlisted': shortlisted,
                'interview_scheduled': interview_scheduled,
                'selected': selected,
                'rejected': rejected
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@company_bp.route('/drives/<int:drive_id>', methods=['PUT'])
@jwt_required()
@company_required
def update_drive(drive_id):
    """Update a placement drive (only if pending or approved)."""
    try:
        data = request.get_json()
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        drive = PlacementDrive.query.filter_by(
            id=drive_id, 
            company_id=company.id
        ).first_or_404()
        
        # Only allow updates if drive is pending or approved
        if drive.status not in ['pending', 'approved']:
            return jsonify({'error': 'Cannot update drive with current status'}), 400
        
        # Update allowed fields
        updatable_fields = [
            'job_title', 'job_description', 'job_type', 'job_location', 'work_mode',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period',
            'eligible_branches', 'eligible_graduation_years', 'min_cgpa',
            'min_tenth_percentage', 'min_twelfth_percentage', 'max_backlogs',
            'required_skills', 'number_of_positions', 'drive_venue',
            'selection_process', 'number_of_rounds'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(drive, field, data[field])
        
        # Handle deadline update
        if 'application_deadline' in data:
            deadline = parse_datetime(data['application_deadline'])
            if deadline:
                drive.application_deadline = deadline
        
        # Handle drive date update
        if 'drive_date' in data:
            drive_date = parse_datetime(data['drive_date'])
            if drive_date:
                drive.drive_date = drive_date
        
        db.session.commit()
        
        return jsonify({
            'message': 'Drive updated successfully',
            'drive': drive.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/drives/<int:drive_id>/close', methods=['POST'])
@jwt_required()
@company_required
def close_drive(drive_id):
    """Close a placement drive (mark as completed)."""
    try:
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        drive = PlacementDrive.query.filter_by(
            id=drive_id, 
            company_id=company.id
        ).first_or_404()
        
        drive.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'message': 'Drive closed successfully',
            'drive': drive.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== APPLICATION MANAGEMENT ====================

@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
@company_required
def get_drive_applications(drive_id):
    """
    Get all applications for a specific drive.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - status: Filter by application status
        - search: Search by student name or email
    
    Returns:
        Paginated list of applications
    """
    try:
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        drive = PlacementDrive.query.filter_by(
            id=drive_id, 
            company_id=company.id
        ).first_or_404()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        query = drive.applications.join(StudentProfile).join(User)
        
        if status:
            query = query.filter(Application.status == status)
        
        if search:
            query = query.filter(
                or_(
                    StudentProfile.first_name.ilike(f'%{search}%'),
                    StudentProfile.last_name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    StudentProfile.roll_number.ilike(f'%{search}%')
                )
            )
        
        query = query.order_by(Application.applied_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'drive': drive.to_dict(include_company=False),
            'applications': [a.to_dict(include_drive=False) for a in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@company_bp.route('/applications/<int:application_id>/status', methods=['PUT'])
@jwt_required()
@company_required
def update_application_status(application_id):
    """
    Update the status of an application.
    
    Request Body:
        - status: New status (required)
        - remarks: Company remarks (optional)
        - rating: Rating 1-5 (optional)
    
    Valid status values:
        'under_review', 'shortlisted', 'interview_scheduled', 
        'interviewed', 'selected', 'rejected'
    """
    try:
        data = request.get_json()
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = [
            'under_review', 'shortlisted', 'interview_scheduled',
            'interviewed', 'selected', 'rejected'
        ]
        
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        # Get application and verify it belongs to company's drive
        application = Application.query.join(PlacementDrive).filter(
            Application.id == application_id,
            PlacementDrive.company_id == company.id
        ).first_or_404()
        
        application.update_status(new_status, data.get('remarks'))
        
        if data.get('rating'):
            application.rating = data['rating']
            db.session.commit()
        
        return jsonify({
            'message': 'Application status updated',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/applications/<int:application_id>/schedule-interview', methods=['POST'])
@jwt_required()
@company_required
def schedule_interview(application_id):
    """
    Schedule an interview for an application.
    
    Request Body:
        - interview_date: Interview datetime (required)
        - interview_mode: 'online', 'offline', 'telephonic' (required)
        - interview_link: Link for online interview (optional)
        - interview_venue: Venue for offline interview (optional)
    """
    try:
        data = request.get_json()
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        # Validate required fields
        if not data.get('interview_date') or not data.get('interview_mode'):
            return jsonify({'error': 'interview_date and interview_mode are required'}), 400
        
        interview_date = parse_datetime(data['interview_date'])
        if not interview_date:
            return jsonify({'error': 'Invalid interview_date format'}), 400
        
        # Get application and verify
        application = Application.query.join(PlacementDrive).filter(
            Application.id == application_id,
            PlacementDrive.company_id == company.id
        ).first_or_404()
        
        application.schedule_interview(
            date=interview_date,
            mode=data['interview_mode'],
            link=data.get('interview_link'),
            venue=data.get('interview_venue')
        )
        
        return jsonify({
            'message': 'Interview scheduled successfully',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/applications/<int:application_id>/offer', methods=['POST'])
@jwt_required()
@company_required
def create_offer(application_id):
    """
    Create an offer for a selected candidate.
    
    Request Body:
        - offer_salary: Offered salary (optional)
        - offer_position: Position offered (optional)
        - offer_location: Work location (optional)
        - offer_deadline: Deadline to accept offer (optional)
    """
    try:
        data = request.get_json()
        company = get_company_profile()
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        # Get application and verify
        application = Application.query.join(PlacementDrive).filter(
            Application.id == application_id,
            PlacementDrive.company_id == company.id
        ).first_or_404()
        
        # Verify application is selected
        if application.status not in ['selected', 'offer_accepted']:
            return jsonify({'error': 'Application must be selected before creating offer'}), 400
        
        # Update offer details
        if data.get('offer_salary'):
            application.offer_salary = data['offer_salary']
        
        if data.get('offer_position'):
            application.offer_position = data['offer_position']
        
        if data.get('offer_location'):
            application.offer_location = data['offer_location']
        
        if data.get('offer_deadline'):
            application.offer_deadline = parse_datetime(data['offer_deadline'])
        
        if data.get('offer_letter_url'):
            application.offer_letter_url = data['offer_letter_url']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Offer details updated',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500