"""
Celery tasks package initialization.
"""

from .celery_tasks import celery, export_student_applications, send_daily_reminders, generate_monthly_report

__all__ = [
    'celery',
    'export_student_applications',
    'send_daily_reminders',
    'generate_monthly_report'
]