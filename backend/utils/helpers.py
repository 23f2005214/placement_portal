"""
Helper functions for common operations across the application.
"""

import re
import csv
import io
import os
import requests
from datetime import datetime
from flask import current_app
from flask_mail import Message


def validate_email(email):
    """
    Validate email format using regex.
    Returns True if valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validate password strength.
    Requirements: min 8 chars, 1 uppercase, 1 lowercase, 1 digit.
    Returns tuple (is_valid, message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"


def send_email(subject, recipients, body, html_body=None):
    """
    Send email using Flask-Mail.
    Returns True if successful, False otherwise.
    """
    try:
        from extensions import mail
        
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            body=body,
            html=html_body
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {str(e)}")
        return False


def send_chat_notification(message, webhook_url=None):
    """
    Send notification to Google Chat using webhook.
    Returns True if successful, False otherwise.
    """
    try:
        if webhook_url is None:
            webhook_url = current_app.config.get('GOOGLE_CHAT_WEBHOOK_URL')
        
        if not webhook_url or 'YOUR_SPACE' in webhook_url:
            current_app.logger.warning("Google Chat webhook URL not configured")
            return False
        
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        return response.status_code == 200
    except Exception as e:
        current_app.logger.error(f"Chat notification failed: {str(e)}")
        return False


def generate_csv(data, headers, filename=None):
    """
    Generate CSV file from data.
    
    Args:
        data: List of dictionaries or list of lists
        headers: List of column headers
        filename: Optional filename for saving
    
    Returns:
        StringIO object containing CSV data
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(headers)
    
    # Write data rows
    for row in data:
        if isinstance(row, dict):
            writer.writerow([row.get(h, '') for h in headers])
        else:
            writer.writerow(row)
    
    output.seek(0)
    
    # Save to file if filename provided
    if filename:
        export_folder = current_app.config.get('EXPORT_FOLDER', 'exports')
        os.makedirs(export_folder, exist_ok=True)
        
        filepath = os.path.join(export_folder, filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            f.write(output.getvalue())
        
        output.seek(0)
    
    return output


def format_date(date_obj, format_str='%Y-%m-%d'):
    """Format date object to string."""
    if date_obj:
        return date_obj.strftime(format_str)
    return None


def format_datetime(dt_obj, format_str='%Y-%m-%d %H:%M:%S'):
    """Format datetime object to string."""
    if dt_obj:
        return dt_obj.strftime(format_str)
    return None


def parse_date(date_str, format_str='%Y-%m-%d'):
    """Parse date string to date object."""
    if date_str:
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            return None
    return None


def parse_datetime(dt_str, format_str='%Y-%m-%dT%H:%M:%S'):
    """Parse datetime string to datetime object."""
    if dt_str:
        try:
            # Handle ISO format with or without timezone
            if 'Z' in dt_str:
                dt_str = dt_str.replace('Z', '+00:00')
            if '+' in dt_str:
                dt_str = dt_str.split('+')[0]
            return datetime.fromisoformat(dt_str)
        except ValueError:
            try:
                return datetime.strptime(dt_str, format_str)
            except ValueError:
                return None
    return None


def generate_monthly_report_html(report_data):
    """
    Generate HTML content for monthly activity report.
    
    Args:
        report_data: Dictionary containing report statistics
    
    Returns:
        HTML string
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
            .stat-card {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-radius: 5px; }}
            .stat-number {{ font-size: 32px; font-weight: bold; color: #3498db; }}
            .stat-label {{ font-size: 14px; color: #666; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Monthly Placement Activity Report</h1>
            <p>{report_data.get('month_year', 'Monthly Report')}</p>
        </div>
        
        <div class="section">
            <h2>Summary Statistics</h2>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-number">{report_data.get('total_drives', 0)}</div>
                    <div class="stat-label">Total Drives</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{report_data.get('total_applications', 0)}</div>
                    <div class="stat-label">Total Applications</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{report_data.get('total_selections', 0)}</div>
                    <div class="stat-label">Students Selected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{report_data.get('new_companies', 0)}</div>
                    <div class="stat-label">New Companies</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{report_data.get('new_students', 0)}</div>
                    <div class="stat-label">New Students</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{report_data.get('placement_rate', 0):.1f}%</div>
                    <div class="stat-label">Placement Rate</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Top Recruiting Companies</h2>
            <table>
                <tr>
                    <th>Company</th>
                    <th>Drives</th>
                    <th>Applications</th>
                    <th>Selections</th>
                </tr>
                {''.join([f"<tr><td>{c['name']}</td><td>{c['drives']}</td><td>{c['applications']}</td><td>{c['selections']}</td></tr>" 
                         for c in report_data.get('top_companies', [])])}
            </table>
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p>Placement Portal - Institute Placement Cell</p>
        </div>
    </body>
    </html>
    """
    return html


def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed."""
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx'})
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions