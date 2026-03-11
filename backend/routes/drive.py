"""
Public drive routes - For viewing drives without authentication (if needed).
Also includes shared drive-related utilities.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required
from sqlalchemy import or_
from extensions import db, cache
from models import PlacementDrive, CompanyProfile

# Create blueprint
drive_bp = Blueprint('drive', __name__)


@drive_bp.route('/', methods=['GET'])
@cache.cached(timeout=120, query_string=True)
def get_public_drives():
    """
    Get all approved and active placement drives (public endpoint).
    This can be used for public viewing without authentication.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - search: Search by job title or company name
        - job_type: Filter by job type
        - branch: Filter by eligible branch
    
    Returns:
        Paginated list of active drives
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').strip()
        job_type = request.args.get('job_type')
        branch = request.args.get('branch')
        
        # Base query: approved drives with deadline not passed
        query = PlacementDrive.query.join(CompanyProfile).filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline > datetime.utcnow(),
            CompanyProfile.approval_status == 'approved'
        )
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    PlacementDrive.job_title.ilike(f'%{search}%'),
                    CompanyProfile.company_name.ilike(f'%{search}%'),
                    PlacementDrive.job_description.ilike(f'%{search}%')
                )
            )
        
        if job_type:
            query = query.filter(PlacementDrive.job_type == job_type)
        
        if branch:
            query = query.filter(
                or_(
                    PlacementDrive.eligible_branches.ilike(f'%{branch}%'),
                    PlacementDrive.eligible_branches.ilike('%all%')
                )
            )
        
        # Order by deadline (nearest first)
        query = query.order_by(PlacementDrive.application_deadline.asc())
        
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


@drive_bp.route('/<int:drive_id>', methods=['GET'])
@cache.cached(timeout=60)
def get_drive_public(drive_id):
    """Get public details of a specific drive."""
    try:
        drive = PlacementDrive.query.filter_by(
            id=drive_id,
            status='approved'
        ).first_or_404()
        
        return jsonify({'drive': drive.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drive_bp.route('/stats', methods=['GET'])
@cache.cached(timeout=300)
def get_drive_stats():
    """Get overall placement drive statistics (public)."""
    try:
        total_drives = PlacementDrive.query.filter_by(status='approved').count()
        active_drives = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline > datetime.utcnow()
        ).count()
        total_companies = CompanyProfile.query.filter_by(approval_status='approved').count()
        
        # Get job type distribution
        job_types = db.session.query(
            PlacementDrive.job_type,
            db.func.count(PlacementDrive.id)
        ).filter(
            PlacementDrive.status == 'approved'
        ).group_by(PlacementDrive.job_type).all()
        
        return jsonify({
            'stats': {
                'total_drives': total_drives,
                'active_drives': active_drives,
                'total_companies': total_companies,
                'job_type_distribution': {jt[0]: jt[1] for jt in job_types}
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drive_bp.route('/upcoming', methods=['GET'])
@cache.cached(timeout=60)
def get_upcoming_drives():
    """Get upcoming drives with nearest deadlines."""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        drives = PlacementDrive.query.join(CompanyProfile).filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline > datetime.utcnow(),
            CompanyProfile.approval_status == 'approved'
        ).order_by(
            PlacementDrive.application_deadline.asc()
        ).limit(limit).all()
        
        return jsonify({
            'drives': [d.to_dict() for d in drives]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@drive_bp.route('/branches', methods=['GET'])
@cache.cached(timeout=600)
def get_available_branches():
    """Get list of all branches with active drives."""
    try:
        # Get all eligible branches from active drives
        drives = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline > datetime.utcnow()
        ).all()
        
        branches = set()
        for drive in drives:
            if drive.eligible_branches:
                for branch in drive.eligible_branches.split(','):
                    branch = branch.strip()
                    if branch.lower() != 'all':
                        branches.add(branch)
        
        return jsonify({
            'branches': sorted(list(branches))
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500