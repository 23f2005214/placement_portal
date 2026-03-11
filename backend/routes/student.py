"""
Student routes - Handles student dashboard, profile, and application management.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from extensions import db, cache

# Import models - DO NOT define models here
from models import User, StudentProfile, PlacementDrive, Application
from utils.decorators import student_required
from utils.helpers import parse_date

# Create blueprint
student_bp = Blueprint('student', __name__)


def get_student_profile():
    """Helper to get current student profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user and user.student_profile:
        return user.student_profile
    return None


@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@student_required
def get_dashboard():
    """
    Get student dashboard with statistics and recommendations.
    
    Returns:
        Dashboard data including profile, stats, and eligible drives
    """
    try:
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get application statistics
        total_applications = student.applications.count()
        applied = student.applications.filter_by(status='applied').count()
        shortlisted = student.applications.filter_by(status='shortlisted').count()
        interview_scheduled = student.applications.filter_by(status='interview_scheduled').count()
        selected = student.applications.filter_by(status='selected').count()
        rejected = student.applications.filter_by(status='rejected').count()
        
        # Get active drives count (student is eligible)
        active_drives = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline > datetime.utcnow()
        ).all()
        
        eligible_drive_count = 0
        for drive in active_drives:
            is_eligible, _ = student.check_eligibility(drive)
            if is_eligible:
                eligible_drive_count += 1
        
        # Get upcoming interviews
        upcoming_interviews = student.applications.filter(
            Application.status == 'interview_scheduled',
            Application.interview_date > datetime.utcnow()
        ).order_by(Application.interview_date.asc()).limit(5).all()
        
        # Get recent applications
        recent_applications = student.applications.order_by(
            Application.applied_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'profile': student.to_dict(),
            'statistics': {
                'total_applications': total_applications,
                'applied': applied,
                'shortlisted': shortlisted,
                'interview_scheduled': interview_scheduled,
                'selected': selected,
                'rejected': rejected,
                'eligible_drives': eligible_drive_count
            },
            'upcoming_interviews': [a.to_dict() for a in upcoming_interviews],
            'recent_applications': [a.to_dict() for a in recent_applications]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/profile', methods=['GET'])
@jwt_required()
@student_required
def get_profile():
    """Get student profile."""
    try:
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        return jsonify({'profile': student.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
@student_required
def update_profile():
    """Update student profile."""
    try:
        data = request.get_json()
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Update allowed fields
        updatable_fields = [
            'first_name', 'last_name', 'phone', 'gender',
            'roll_number', 'branch', 'department', 'year_of_study',
            'graduation_year', 'cgpa', 'tenth_percentage', 'twelfth_percentage',
            'active_backlogs', 'history_of_backlogs', 'skills',
            'resume_url', 'linkedin_url', 'github_url', 'portfolio_url',
            'address', 'city', 'state', 'profile_picture_url'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(student, field, data[field])
        
        # Handle date of birth
        if 'date_of_birth' in data and data['date_of_birth']:
            dob = parse_date(data['date_of_birth'])
            if dob:
                student.date_of_birth = dob
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== DRIVE VIEWING ====================

@student_bp.route('/drives', methods=['GET'])
@jwt_required()
@student_required
def get_eligible_drives():
    """
    Get all approved placement drives with eligibility status.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - branch: Filter by branch
        - job_type: Filter by job type
        - search: Search by title or company
        - show_all: Show all drives including ineligible (default: false)
        - min_salary: Minimum salary filter
    
    Returns:
        Paginated list of drives with eligibility info
    """
    try:
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        branch = request.args.get('branch')
        job_type = request.args.get('job_type')
        search = request.args.get('search', '').strip()
        show_all = request.args.get('show_all', 'false').lower() == 'true'
        min_salary = request.args.get('min_salary', type=float)
        
        # Base query: approved drives with deadline not passed
        query = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline > datetime.utcnow()
        )
        
        # Filters
        if job_type:
            query = query.filter(PlacementDrive.job_type == job_type)
        
        if min_salary:
            query = query.filter(PlacementDrive.salary_min >= min_salary)
        
        if search:
            query = query.join(PlacementDrive.company).filter(
                or_(
                    PlacementDrive.job_title.ilike(f'%{search}%'),
                    PlacementDrive.job_description.ilike(f'%{search}%')
                )
            )
        
        # Order by deadline (nearest first)
        query = query.order_by(PlacementDrive.application_deadline.asc())
        
        # Get all drives for this page
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Add eligibility info to each drive
        drives_data = []
        for drive in pagination.items:
            is_eligible, reasons = student.check_eligibility(drive)
            
            # Check if already applied
            existing_application = Application.query.filter_by(
                student_id=student.id,
                drive_id=drive.id
            ).first()
            
            drive_dict = drive.to_dict()
            drive_dict['is_eligible'] = is_eligible
            drive_dict['eligibility_reasons'] = reasons
            drive_dict['has_applied'] = existing_application is not None
            drive_dict['application_status'] = existing_application.status if existing_application else None
            
            # Only include if eligible (or show_all is true)
            if show_all or is_eligible:
                drives_data.append(drive_dict)
        
        return jsonify({
            'drives': drives_data,
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


@student_bp.route('/drives/<int:drive_id>', methods=['GET'])
@jwt_required()
@student_required
def get_drive_details(drive_id):
    """Get details of a specific drive with eligibility check."""
    try:
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        drive = PlacementDrive.query.filter_by(
            id=drive_id,
            status='approved'
        ).first_or_404()
        
        # Check eligibility
        is_eligible, reasons = student.check_eligibility(drive)
        
        # Check if already applied
        existing_application = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        
        drive_dict = drive.to_dict()
        drive_dict['is_eligible'] = is_eligible
        drive_dict['eligibility_reasons'] = reasons
        drive_dict['has_applied'] = existing_application is not None
        drive_dict['application'] = existing_application.to_dict() if existing_application else None
        
        return jsonify({'drive': drive_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== APPLICATION MANAGEMENT ====================

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
@student_required
def get_applications():
    """
    Get all applications made by the student.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - status: Filter by status
    
    Returns:
        Paginated list of applications
    """
    try:
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = student.applications
        
        if status:
            query = query.filter(Application.status == status)
        
        query = query.order_by(Application.applied_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'applications': [a.to_dict() for a in pagination.items],
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


@student_bp.route('/applications/<int:application_id>', methods=['GET'])
@jwt_required()
@student_required
def get_application(application_id):
    """Get details of a specific application."""
    try:
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        application = Application.query.filter_by(
            id=application_id,
            student_id=student.id
        ).first_or_404()
        
        return jsonify({'application': application.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@jwt_required()
@student_required
def apply_to_drive(drive_id):
    """
    Apply to a placement drive.
    
    Request Body:
        - cover_letter: Cover letter text (optional)
    
    Returns:
        Created application object
    """
    try:
        data = request.get_json() or {}
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get the drive
        drive = PlacementDrive.query.filter_by(
            id=drive_id,
            status='approved'
        ).first_or_404()
        
        # Check if deadline has passed
        if drive.is_deadline_passed:
            return jsonify({'error': 'Application deadline has passed'}), 400
        
        # Check if already applied (prevent duplicate applications)
        existing = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        
        if existing:
            return jsonify({
                'error': 'You have already applied to this drive',
                'application': existing.to_dict()
            }), 409
        
        # Check eligibility
        is_eligible, reasons = student.check_eligibility(drive)
        
        if not is_eligible:
            return jsonify({
                'error': 'You are not eligible for this drive',
                'reasons': reasons
            }), 400
        
        # Check if student is blacklisted
        if student.user.is_blacklisted:
            return jsonify({'error': 'Your account is blacklisted'}), 403
        
        # Create application
        application = Application(
            student_id=student.id,
            drive_id=drive.id,
            cover_letter=data.get('cover_letter'),
            resume_snapshot_url=student.resume_url,  # Snapshot of current resume
            status='applied'
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@student_bp.route('/applications/<int:application_id>/withdraw', methods=['POST'])
@jwt_required()
@student_required
def withdraw_application(application_id):
    """Withdraw an application (only if status is 'applied' or 'shortlisted')."""
    try:
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        application = Application.query.filter_by(
            id=application_id,
            student_id=student.id
        ).first_or_404()
        
        # Only allow withdrawal if application is in early stages
        if application.status not in ['applied', 'under_review', 'shortlisted']:
            return jsonify({
                'error': 'Cannot withdraw application at this stage'
            }), 400
        
        application.status = 'withdrawn'
        db.session.commit()
        
        return jsonify({
            'message': 'Application withdrawn successfully',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@student_bp.route('/applications/<int:application_id>/respond-offer', methods=['POST'])
@jwt_required()
@student_required
def respond_to_offer(application_id):
    """
    Accept or decline an offer.
    
    Request Body:
        - response: 'accept' or 'decline' (required)
    """
    try:
        data = request.get_json()
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        response = data.get('response')
        if response not in ['accept', 'decline']:
            return jsonify({'error': "Response must be 'accept' or 'decline'"}), 400
        
        application = Application.query.filter_by(
            id=application_id,
            student_id=student.id
        ).first_or_404()
        
        if application.status != 'selected':
            return jsonify({'error': 'No offer to respond to'}), 400
        
        if response == 'accept':
            application.status = 'offer_accepted'
            student.is_placed = True
            student.placement_count += 1
        else:
            application.status = 'offer_declined'
        
        db.session.commit()
        
        return jsonify({
            'message': f'Offer {response}ed successfully',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== PLACEMENT HISTORY ====================

@student_bp.route('/placement-history', methods=['GET'])
@jwt_required()
@student_required
def get_placement_history():
    """Get complete placement history for the student."""
    try:
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get all applications ordered by date
        applications = student.applications.order_by(
            Application.applied_at.desc()
        ).all()
        
        # Categorize applications
        history = {
            'total_applications': len(applications),
            'selected': [],
            'rejected': [],
            'in_progress': [],
            'withdrawn': []
        }
        
        for app in applications:
            app_data = app.to_dict()
            
            if app.status in ['selected', 'offer_accepted']:
                history['selected'].append(app_data)
            elif app.status == 'rejected':
                history['rejected'].append(app_data)
            elif app.status == 'withdrawn':
                history['withdrawn'].append(app_data)
            else:
                history['in_progress'].append(app_data)
        
        return jsonify({
            'history': history,
            'is_placed': student.is_placed,
            'placement_count': student.placement_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/export-applications', methods=['POST'])
@jwt_required()
@student_required
def export_applications():
    """
    Trigger async export of applications to CSV.
    Returns a task ID that can be used to check status.
    """
    try:
        student = get_student_profile()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Import celery task
        try:
            from tasks.celery_tasks import export_student_applications
            
            # Trigger async export
            task = export_student_applications.delay(student.id)
            
            return jsonify({
                'message': 'Export started. You will be notified when complete.',
                'task_id': task.id
            }), 202
        except ImportError:
            # Celery not available, do synchronous export
            return jsonify({
                'message': 'Async export not available. Please try again later.',
                'task_id': None
            }), 503
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/export-applications/<task_id>/status', methods=['GET'])
@jwt_required()
@student_required
def check_export_status(task_id):
    """Check the status of an export task."""
    try:
        from celery.result import AsyncResult
        from tasks.celery_tasks import celery
        
        task = AsyncResult(task_id, app=celery)
        
        if task.state == 'PENDING':
            response = {'status': 'pending', 'message': 'Export is queued'}
        elif task.state == 'STARTED':
            response = {'status': 'processing', 'message': 'Export in progress'}
        elif task.state == 'SUCCESS':
            response = {
                'status': 'completed',
                'message': 'Export complete',
                'result': task.result
            }
        elif task.state == 'FAILURE':
            response = {
                'status': 'failed',
                'message': str(task.info)
            }
        else:
            response = {'status': task.state}
        
        return jsonify(response), 200
        
    except ImportError:
        return jsonify({
            'status': 'error',
            'message': 'Celery not available'
        }), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500