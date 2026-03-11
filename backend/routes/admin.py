"""
Admin routes - Handles admin dashboard, approvals, and management functions.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, or_

from extensions import db, cache
from models import (
    User,
    CompanyProfile,
    StudentProfile,
    PlacementDrive,
    Application,
)
from utils.decorators import admin_required

# Create blueprint
admin_bp = Blueprint('admin', __name__)


# ==================== DASHBOARD ====================

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard():
    """
    Get admin dashboard statistics.
    
    Returns:
        Dashboard statistics including counts and recent activities
    """
    try:
        # Get counts (use User roles to be robust even if profiles missing)
        total_students = User.query.filter_by(role='student').count()
        total_companies = User.query.filter_by(role='company').count()
        total_drives = PlacementDrive.query.count()
        total_applications = Application.query.count()

        # Pending approvals
        pending_companies = CompanyProfile.query.filter_by(approval_status='pending').count()
        pending_drives = PlacementDrive.query.filter_by(status='pending').count()

        # Approved companies and drives
        approved_companies = CompanyProfile.query.filter_by(approval_status='approved').count()
        approved_drives = PlacementDrive.query.filter_by(status='approved').count()

        # Placement statistics
        placed_students = StudentProfile.query.filter_by(is_placed=True).count()
        selected_applications = Application.query.filter_by(status='selected').count()

        # Recent registrations (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_students_week = StudentProfile.query.filter(StudentProfile.created_at >= week_ago).count()
        new_companies_week = CompanyProfile.query.filter(CompanyProfile.created_at >= week_ago).count()
        new_applications_week = Application.query.filter(Application.applied_at >= week_ago).count()

        # Recent activities
        recent_applications = Application.query.order_by(
            Application.applied_at.desc()
        ).limit(5).all()

        recent_drives = PlacementDrive.query.order_by(
            PlacementDrive.created_at.desc()
        ).limit(5).all()

        return jsonify({
            'statistics': {
                'total_students': total_students,
                'total_companies': total_companies,
                'total_drives': total_drives,
                'total_applications': total_applications,
                'pending_companies': pending_companies,
                'pending_drives': pending_drives,
                'approved_companies': approved_companies,
                'approved_drives': approved_drives,
                'placed_students': placed_students,
                'selected_applications': selected_applications,
                'placement_rate': round((placed_students / total_students * 100), 2) if total_students > 0 else 0
            },
            'weekly': {
                'new_students': new_students_week,
                'new_companies': new_companies_week,
                'new_applications': new_applications_week
            },
            'recent_applications': [app.to_dict() for app in recent_applications],
            'recent_drives': [drive.to_dict() for drive in recent_drives]
        }), 200

    except Exception as e:
        # Unexpected error -> 500
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== COMPANY MANAGEMENT ====================

@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
@admin_required
def get_companies():
    """
    Get all companies with optional filtering and search.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - status: Filter by approval status
        - search: Search by company name or email
        - sort: Sort field (default: created_at)
        - order: Sort order (asc/desc, default: desc)
    
    Returns:
        Paginated list of companies
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        query = CompanyProfile.query.join(User)

        # Filter by status
        if status:
            query = query.filter(CompanyProfile.approval_status == status)  # type: ignore

        # Search
        if search:
            query = query.filter(  # type: ignore
                or_(
                    CompanyProfile.company_name.ilike(f'%{search}%'),  # type: ignore
                    User.email.ilike(f'%{search}%'),
                    CompanyProfile.industry.ilike(f'%{search}%')
                )
            )

        # Sorting
        sort_column = getattr(CompanyProfile, sort_by, CompanyProfile.created_at)
        if order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'companies': [c.to_dict() for c in pagination.items],
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


@admin_bp.route('/companies/<int:company_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_company(company_id):
    """Get a single company by ID."""
    try:
        company = CompanyProfile.query.get_or_404(company_id)

        # Include additional stats
        total_drives = company.placement_drives.count()
        approved_drives = company.placement_drives.filter_by(status='approved').count()
        total_applications = 0
        total_selections = 0

        for drive in company.placement_drives:
            total_applications += drive.application_count
            total_selections += drive.applications.filter_by(status='selected').count()

        return jsonify({
            'company': company.to_dict(),
            'stats': {
                'total_drives': total_drives,
                'approved_drives': approved_drives,
                'total_applications': total_applications,
                'total_selections': total_selections
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/companies/<int:company_id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_company(company_id):
    """Approve a company registration."""
    try:
        company = CompanyProfile.query.get_or_404(company_id)

        if company.approval_status == 'approved' or getattr(company, 'is_approved', False):
            return jsonify({'error': 'Company is already approved'}), 400

        company.approve()
        company.user.is_verified = True
        db.session.commit()

        # Clear cache if used
        try:
            cache.delete_memoized(get_companies)
        except Exception:
            pass

        return jsonify({
            'message': 'Company approved successfully',
            'company': company.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/companies/<int:company_id>/reject', methods=['POST'])
@jwt_required()
@admin_required
def reject_company(company_id):
    """Reject a company registration."""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Registration rejected by admin')

        company = CompanyProfile.query.get_or_404(company_id)
        company.reject(reason)
        db.session.commit()

        try:
            cache.delete_memoized(get_companies)
        except Exception:
            pass

        return jsonify({
            'message': 'Company rejected',
            'company': company.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['POST'])
@jwt_required()
@admin_required
def toggle_company_blacklist(company_id):
    """Toggle blacklist status of a company."""
    try:
        company = CompanyProfile.query.get_or_404(company_id)

        company.user.is_blacklisted = not company.user.is_blacklisted
        db.session.commit()

        status = 'blacklisted' if company.user.is_blacklisted else 'unblacklisted'

        return jsonify({
            'message': f'Company {status} successfully',
            'company': company.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/companies/<int:company_id>/deactivate', methods=['POST'])
@jwt_required()
@admin_required
def toggle_company_status(company_id):
    """Toggle active status of a company."""
    try:
        company = CompanyProfile.query.get_or_404(company_id)

        company.user.is_active = not company.user.is_active
        db.session.commit()

        status = 'activated' if company.user.is_active else 'deactivated'

        return jsonify({
            'message': f'Company {status} successfully',
            'company': company.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== STUDENT MANAGEMENT ====================

@admin_bp.route('/students', methods=['GET'])
@jwt_required()
@admin_required
def get_students():
    """
    Get all students with optional filtering and search.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - branch: Filter by branch
        - graduation_year: Filter by graduation year
        - is_placed: Filter by placement status (true/false)
        - search: Search by name, email, or roll number
        - sort: Sort field (default: created_at)
        - order: Sort order (asc/desc, default: desc)
    
    Returns:
        Paginated list of students
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        branch = request.args.get('branch')
        graduation_year = request.args.get('graduation_year', type=int)
        is_placed = request.args.get('is_placed')
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        query = StudentProfile.query.join(User)

        # Filters
        if branch:
            query = query.filter(StudentProfile.branch == branch)  # type: ignore

        if graduation_year:
            query = query.filter(StudentProfile.graduation_year == graduation_year)  # type: ignore

        if is_placed is not None:
            is_placed_bool = is_placed.lower() == 'true'
            query = query.filter(StudentProfile.is_placed == is_placed_bool)

        # Search
        if search:
            query = query.filter(  # type: ignore
                or_(
                    StudentProfile.first_name.ilike(f'%{search}%'),  # type: ignore
                    StudentProfile.last_name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    StudentProfile.roll_number.ilike(f'%{search}%')
                )
            )

        # Sorting
        sort_column = getattr(StudentProfile, sort_by, StudentProfile.created_at)
        if order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'students': [s.to_dict() for s in pagination.items],
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


@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_student(student_id):
    """Get a single student by ID with application history."""
    try:
        student = StudentProfile.query.get_or_404(student_id)

        # Get application statistics
        total_applications = student.applications.count()
        selected = student.applications.filter_by(status='selected').count()
        rejected = student.applications.filter_by(status='rejected').count()
        pending = student.applications.filter(
            Application.status.in_(['applied', 'under_review', 'shortlisted', 'interview_scheduled'])  # type: ignore
        ).count()

        # Get recent applications
        recent_applications = student.applications.order_by(
            Application.applied_at.desc()
        ).limit(10).all()

        return jsonify({
            'student': student.to_dict(),
            'stats': {
                'total_applications': total_applications,
                'selected': selected,
                'rejected': rejected,
                'pending': pending
            },
            'recent_applications': [app.to_dict() for app in recent_applications]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/students/<int:student_id>/blacklist', methods=['POST'])
@jwt_required()
@admin_required
def toggle_student_blacklist(student_id):
    """Toggle blacklist status of a student."""
    try:
        student = StudentProfile.query.get_or_404(student_id)

        student.user.is_blacklisted = not student.user.is_blacklisted
        db.session.commit()

        status = 'blacklisted' if student.user.is_blacklisted else 'unblacklisted'

        return jsonify({
            'message': f'Student {status} successfully',
            'student': student.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/students/<int:student_id>/deactivate', methods=['POST'])
@jwt_required()
@admin_required
def toggle_student_status(student_id):
    """Toggle active status of a student."""
    try:
        student = StudentProfile.query.get_or_404(student_id)

        student.user.is_active = not student.user.is_active
        db.session.commit()

        status = 'activated' if student.user.is_active else 'deactivated'

        return jsonify({
            'message': f'Student {status} successfully',
            'student': student.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== DRIVE MANAGEMENT ====================

@admin_bp.route('/drives', methods=['GET'])
@jwt_required()
@admin_required
def get_all_drives():
    """
    Get all placement drives with optional filtering.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - status: Filter by status (pending/approved/rejected/completed)
        - company_id: Filter by company
        - search: Search by job title or company name
    
    Returns:
        Paginated list of drives
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        company_id = request.args.get('company_id', type=int)
        search = request.args.get('search', '').strip()

        query = PlacementDrive.query.join(CompanyProfile)

        # Filters
        if status:
            query = query.filter(PlacementDrive.status == status)  # type: ignore

        if company_id:
            query = query.filter(PlacementDrive.company_id == company_id)  # type: ignore

        # Search
        if search:
            query = query.filter(  # type: ignore
                or_(
                    PlacementDrive.job_title.ilike(f'%{search}%'),  # type: ignore
                    CompanyProfile.company_name.ilike(f'%{search}%')  # type: ignore
                )
            )

        # Order by created_at desc
        query = query.order_by(PlacementDrive.created_at.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'drives': [d.to_dict() for d in pagination.items],
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


@admin_bp.route('/drives/<int:drive_id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_drive(drive_id):
    """Approve a placement drive."""
    try:
        data = request.get_json() or {}
        remarks = data.get('remarks')

        drive = PlacementDrive.query.get_or_404(drive_id)

        if drive.status == 'approved':
            return jsonify({'error': 'Drive is already approved'}), 400

        drive.approve(remarks)
        db.session.commit()

        return jsonify({
            'message': 'Drive approved successfully',
            'drive': drive.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/drives/<int:drive_id>/reject', methods=['POST'])
@jwt_required()
@admin_required
def reject_drive(drive_id):
    """Reject a placement drive."""
    try:
        data = request.get_json() or {}
        remarks = data.get('remarks', 'Drive rejected by admin')

        drive = PlacementDrive.query.get_or_404(drive_id)
        drive.reject(remarks)
        db.session.commit()

        return jsonify({
            'message': 'Drive rejected',
            'drive': drive.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== APPLICATIONS ====================

@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
@admin_required
def get_all_applications():
    """
    Get all applications with optional filtering.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - status: Filter by status
        - drive_id: Filter by drive
        - student_id: Filter by student
    
    Returns:
        Paginated list of applications
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        drive_id = request.args.get('drive_id', type=int)
        student_id = request.args.get('student_id', type=int)

        query = Application.query

        # Filters
        if status:
            query = query.filter(Application.status == status)  # type: ignore

        if drive_id:
            query = query.filter(Application.drive_id == drive_id)  # type: ignore

        if student_id:
            query = query.filter(Application.student_id == student_id)  # type: ignore

        # Order by applied_at desc
        query = query.order_by(Application.applied_at.desc())

        # Paginate
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


# ==================== REPORTS ====================

@admin_bp.route('/reports/monthly', methods=['GET'])
@jwt_required()
@admin_required
def get_monthly_report():
    """
    Generate monthly placement activity report.
    
    Query Parameters:
        - month: Month number (1-12, default: current month)
        - year: Year (default: current year)
    
    Returns:
        Monthly statistics and report data
    """
    try:
        from utils.helpers import generate_monthly_report_html

        now = datetime.utcnow()
        month = request.args.get('month', now.month, type=int)
        year = request.args.get('year', now.year, type=int)

        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Get statistics for the month
        drives_query = PlacementDrive.query.filter(
            PlacementDrive.created_at >= start_date,
            PlacementDrive.created_at < end_date
        )

        applications_query = Application.query.filter(
            Application.applied_at >= start_date,
            Application.applied_at < end_date
        )

        companies_query = CompanyProfile.query.filter(
            CompanyProfile.created_at >= start_date,
            CompanyProfile.created_at < end_date
        )

        students_query = StudentProfile.query.filter(
            StudentProfile.created_at >= start_date,
            StudentProfile.created_at < end_date
        )

        total_drives = drives_query.count()
        approved_drives = drives_query.filter_by(status='approved').count()
        total_applications = applications_query.count()
        total_selections = applications_query.filter_by(status='selected').count()
        new_companies = companies_query.count()
        new_students = students_query.count()

        # Calculate placement rate
        placement_rate = (total_selections / total_applications * 100) if total_applications > 0 else 0

        # Get top recruiting companies
        top_companies = db.session.query(
            CompanyProfile.company_name,  # type: ignore
            func.count(PlacementDrive.id).label('drive_count'),
            func.count(Application.id).label('app_count')
        ).join(PlacementDrive).outerjoin(Application).filter(
            PlacementDrive.created_at >= start_date,
            PlacementDrive.created_at < end_date
        ).group_by(CompanyProfile.id).order_by(
            func.count(PlacementDrive.id).desc()
        ).limit(5).all()

        report_data = {
            'month_year': start_date.strftime('%B %Y'),
            'total_drives': total_drives,
            'approved_drives': approved_drives,
            'total_applications': total_applications,
            'total_selections': total_selections,
            'new_companies': new_companies,
            'new_students': new_students,
            'placement_rate': placement_rate,
            'top_companies': [
                {'name': c[0], 'drives': c[1], 'applications': c[2], 'selections': 0}
                for c in top_companies
            ]
        }

        # Generate HTML report
        html_report = generate_monthly_report_html(report_data)

        return jsonify({
            'report_data': report_data,
            'html_report': html_report
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/stats/branches', methods=['GET'])
@jwt_required()
@admin_required
def get_branch_stats():
    """Get statistics by branch."""
    try:
        branch_stats = db.session.query(
            StudentProfile.branch,  # type: ignore
            func.count(StudentProfile.id).label('total_students'),
            func.sum(StudentProfile.is_placed.cast(db.Integer)).label('placed_students')
        ).group_by(StudentProfile.branch).all()  # type: ignore

        return jsonify({
            'branches': [
                {
                    'branch': b[0],
                    'total_students': b[1],
                    'placed_students': b[2] or 0,
                    'placement_rate': round((b[2] or 0) / b[1] * 100, 2) if b[1] > 0 else 0
                }
                for b in branch_stats
            ]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500