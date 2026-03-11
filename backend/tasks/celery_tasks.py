"""
Celery tasks for background jobs.
Includes daily reminders, monthly reports, and CSV exports.
"""

import os
import csv
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab

# Initialize Celery
celery = Celery(
    'placement_portal',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/1'
)

# Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    beat_schedule={
        # Daily reminders at 9 AM
        'send-daily-reminders': {
            'task': 'tasks.celery_tasks.send_daily_reminders',
            'schedule': crontab(hour=9, minute=0),
        },
        # Monthly report on 1st of each month at 8 AM
        'generate-monthly-report': {
            'task': 'tasks.celery_tasks.generate_monthly_report',
            'schedule': crontab(day_of_month=1, hour=8, minute=0),
        },
    }
)


def get_flask_app():
    """Create and return Flask application context."""
    from app import create_app
    app = create_app()
    return app


@celery.task(bind=True)
def export_student_applications(self, student_id):
    """
    Export student's application history to CSV.
    This is a user-triggered async job.
    
    Args:
        student_id: ID of the student
    
    Returns:
        Dictionary with export status and file path
    """
    app = get_flask_app()
    
    with app.app_context():
        try:
            from models import StudentProfile, Application
            from utils.helpers import send_email
            
            student = StudentProfile.query.get(student_id)
            if not student:
                return {'error': 'Student not found', 'status': 'failed'}
            
            # Get all applications
            applications = student.applications.order_by(
                Application.applied_at.desc()
            ).all()
            
            # Prepare CSV data
            headers = [
                'Application ID',
                'Company Name',
                'Job Title',
                'Application Date',
                'Status',
                'Interview Date',
                'Offer Salary',
                'Last Updated'
            ]
            
            rows = []
            for app in applications:
                rows.append([
                    app.id,
                    app.drive.company.company_name if app.drive and app.drive.company else 'N/A',
                    app.drive.job_title if app.drive else 'N/A',
                    app.applied_at.strftime('%Y-%m-%d %H:%M') if app.applied_at else 'N/A',
                    app.status,
                    app.interview_date.strftime('%Y-%m-%d %H:%M') if app.interview_date else 'N/A',
                    app.offer_salary if app.offer_salary else 'N/A',
                    app.updated_at.strftime('%Y-%m-%d %H:%M') if app.updated_at else 'N/A'
                ])
            
            # Create export directory
            export_dir = app.config.get('EXPORT_FOLDER', 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f'applications_{student_id}_{timestamp}.csv'
            filepath = os.path.join(export_dir, filename)
            
            # Write CSV file
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            
            # Send email notification
            if student.user and student.user.email:
                send_email(
                    subject='Your Application Export is Ready',
                    recipients=[student.user.email],
                    body=f'''Dear {student.full_name},

Your placement application history has been exported successfully.

Total Applications: {len(applications)}
Export File: {filename}

You can download the file from your dashboard.

Best regards,
Placement Portal Team'''
                )
            
            return {
                'status': 'success',
                'message': 'Export completed successfully',
                'filename': filename,
                'filepath': filepath,
                'total_records': len(applications)
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }


@celery.task
def send_daily_reminders():
    """
    Send daily reminders to students about upcoming application deadlines.
    Scheduled to run daily at 9 AM.
    """
    app = get_flask_app()
    
    with app.app_context():
        try:
            from models import PlacementDrive, StudentProfile, Application
            from utils.helpers import send_email, send_chat_notification
            
            # Get drives with deadlines in next 3 days
            now = datetime.utcnow()
            deadline_threshold = now + timedelta(days=3)
            
            upcoming_drives = PlacementDrive.query.filter(
                PlacementDrive.status == 'approved',
                PlacementDrive.application_deadline > now,
                PlacementDrive.application_deadline <= deadline_threshold
            ).all()
            
            if not upcoming_drives:
                return {'message': 'No upcoming deadlines', 'reminders_sent': 0}
            
            # Get all active students
            students = StudentProfile.query.join(
                StudentProfile.user
            ).filter(
                StudentProfile.user.has(is_active=True, is_blacklisted=False)
            ).all()
            
            reminders_sent = 0
            
            for student in students:
                eligible_drives = []
                
                for drive in upcoming_drives:
                    is_eligible, _ = student.check_eligibility(drive)
                    
                    # Check if not already applied
                    existing = Application.query.filter_by(
                        student_id=student.id,
                        drive_id=drive.id
                    ).first()
                    
                    if is_eligible and not existing:
                        eligible_drives.append(drive)
                
                if eligible_drives:
                    # Prepare reminder message
                    drive_list = '\n'.join([
                        f"- {d.job_title} at {d.company.company_name} "
                        f"(Deadline: {d.application_deadline.strftime('%Y-%m-%d %H:%M')})"
                        for d in eligible_drives
                    ])
                    
                    message = f'''Dear {student.full_name},

This is a reminder about upcoming placement drive deadlines:

{drive_list}

Don't miss out! Apply now through the Placement Portal.

Best regards,
Placement Portal Team'''
                    
                    # Send email
                    if student.user and student.user.email:
                        send_email(
                            subject='Upcoming Placement Drive Deadlines',
                            recipients=[student.user.email],
                            body=message
                        )
                        reminders_sent += 1
            
            # Send summary to admin via chat
            send_chat_notification(
                f"📢 Daily Reminder Summary:\n"
                f"- Drives with upcoming deadlines: {len(upcoming_drives)}\n"
                f"- Reminders sent to students: {reminders_sent}"
            )
            
            return {
                'message': 'Daily reminders sent',
                'upcoming_drives': len(upcoming_drives),
                'reminders_sent': reminders_sent
            }
            
        except Exception as e:
            return {'error': str(e)}


@celery.task
def generate_monthly_report():
    """
    Generate monthly placement activity report for admin.
    Scheduled to run on 1st of each month at 8 AM.
    """
    app = get_flask_app()
    
    with app.app_context():
        try:
            from models import User, PlacementDrive, Application, CompanyProfile, StudentProfile
            from utils.helpers import send_email, generate_monthly_report_html
            from sqlalchemy import func
            
            # Calculate previous month's date range
            now = datetime.utcnow()
            first_of_current_month = datetime(now.year, now.month, 1)
            
            if now.month == 1:
                first_of_previous_month = datetime(now.year - 1, 12, 1)
            else:
                first_of_previous_month = datetime(now.year, now.month - 1, 1)
            
            last_of_previous_month = first_of_current_month - timedelta(days=1)
            
            # Gather statistics
            drives_query = PlacementDrive.query.filter(
                PlacementDrive.created_at >= first_of_previous_month,
                PlacementDrive.created_at < first_of_current_month
            )
            
            applications_query = Application.query.filter(
                Application.applied_at >= first_of_previous_month,
                Application.applied_at < first_of_current_month
            )
            
            companies_query = CompanyProfile.query.filter(
                CompanyProfile.created_at >= first_of_previous_month,
                CompanyProfile.created_at < first_of_current_month
            )
            
            students_query = StudentProfile.query.filter(
                StudentProfile.created_at >= first_of_previous_month,
                StudentProfile.created_at < first_of_current_month
            )
            
            # Calculate stats
            total_drives = drives_query.count()
            approved_drives = drives_query.filter_by(status='approved').count()
            total_applications = applications_query.count()
            total_selections = applications_query.filter_by(status='selected').count()
            new_companies = companies_query.count()
            new_students = students_query.count()
            
            placement_rate = (total_selections / total_applications * 100) if total_applications > 0 else 0
            
            # Get top recruiting companies
            top_companies_data = []
            companies = CompanyProfile.query.filter_by(approval_status='approved').all()
            
            for company in companies[:10]:  # Top 10
                company_drives = company.placement_drives.filter(
                    PlacementDrive.created_at >= first_of_previous_month,
                    PlacementDrive.created_at < first_of_current_month
                ).count()
                
                if company_drives > 0:
                    company_apps = 0
                    company_selections = 0
                    
                    for drive in company.placement_drives:
                        company_apps += drive.application_count
                        company_selections += drive.applications.filter_by(status='selected').count()
                    
                    top_companies_data.append({
                        'name': company.company_name,
                        'drives': company_drives,
                        'applications': company_apps,
                        'selections': company_selections
                    })
            
            # Sort by number of drives
            top_companies_data.sort(key=lambda x: x['drives'], reverse=True)
            top_companies_data = top_companies_data[:5]
            
            # Prepare report data
            report_data = {
                'month_year': first_of_previous_month.strftime('%B %Y'),
                'total_drives': total_drives,
                'approved_drives': approved_drives,
                'total_applications': total_applications,
                'total_selections': total_selections,
                'new_companies': new_companies,
                'new_students': new_students,
                'placement_rate': placement_rate,
                'top_companies': top_companies_data
            }
            
            # Generate HTML report
            html_report = generate_monthly_report_html(report_data)
            
            # Get admin email
            admin = User.query.filter_by(role='admin').first()
            
            if admin:
                send_email(
                    subject=f'Monthly Placement Report - {report_data["month_year"]}',
                    recipients=[admin.email],
                    body=f'''Monthly Placement Activity Report for {report_data["month_year"]}

Summary:
- Total Drives: {total_drives}
- Total Applications: {total_applications}
- Students Selected: {total_selections}
- New Companies: {new_companies}
- New Students: {new_students}
- Placement Rate: {placement_rate:.1f}%

Please find the detailed HTML report attached.

Best regards,
Placement Portal System''',
                    html_body=html_report
                )
            
            return {
                'message': 'Monthly report generated and sent',
                'month': report_data['month_year'],
                'stats': report_data
            }
            
        except Exception as e:
            return {'error': str(e)}


@celery.task
def send_interview_reminders():
    """
    Send reminders for upcoming interviews (next 24 hours).
    Can be scheduled to run every few hours.
    """
    app = get_flask_app()
    
    with app.app_context():
        try:
            from models import Application
            from utils.helpers import send_email
            
            now = datetime.utcnow()
            tomorrow = now + timedelta(hours=24)
            
            upcoming_interviews = Application.query.filter(
                Application.status == 'interview_scheduled',
                Application.interview_date > now,
                Application.interview_date <= tomorrow
            ).all()
            
            reminders_sent = 0
            
            for app in upcoming_interviews:
                if app.student and app.student.user:
                    interview_time = app.interview_date.strftime('%Y-%m-%d at %H:%M')
                    
                    message = f'''Dear {app.student.full_name},

This is a reminder for your upcoming interview:

Company: {app.drive.company.company_name if app.drive and app.drive.company else 'N/A'}
Position: {app.drive.job_title if app.drive else 'N/A'}
Date/Time: {interview_time}
Mode: {app.interview_mode or 'N/A'}
'''
                    
                    if app.interview_mode == 'online' and app.interview_link:
                        message += f'\nMeeting Link: {app.interview_link}'
                    elif app.interview_venue:
                        message += f'\nVenue: {app.interview_venue}'
                    
                    message += '''

Please ensure you are prepared and on time.

Best of luck!
Placement Portal Team'''
                    
                    send_email(
                        subject='Interview Reminder - Tomorrow',
                        recipients=[app.student.user.email],
                        body=message
                    )
                    reminders_sent += 1
            
            return {
                'message': 'Interview reminders sent',
                'reminders_sent': reminders_sent
            }
            
        except Exception as e:
            return {'error': str(e)}