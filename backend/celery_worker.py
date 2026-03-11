"""
Celery worker startup script.
Run with: celery -A celery_worker.celery worker --loglevel=info
"""

from app import create_app
from tasks.celery_tasks import celery

# Create Flask app for context
app = create_app()

# Push app context
app.app_context().push()

if __name__ == '__main__':
    celery.start()