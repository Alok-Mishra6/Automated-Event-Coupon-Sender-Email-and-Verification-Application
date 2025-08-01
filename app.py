#!/usr/bin/env python3
"""
Email Coupon System - Flask Application
Main application entry point with integrated services
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import secrets

# Import our services
from email_service import create_email_service_from_env, EmailService
from coupon_manager import CouponManager
from csv_manager import CSVManager
from google_auth_service import GoogleAuthService, GmailEmailService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services
try:
    email_service = create_email_service_from_env()
    csv_manager = CSVManager()
    coupon_manager = CouponManager(csv_manager=csv_manager)
    google_auth_service = GoogleAuthService()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    email_service = None
    csv_manager = None
    coupon_manager = None
    google_auth_service = None

# Authentication helper functions
def login_required(f):
    """Decorator to require Google authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current authenticated user from session"""
    return session.get('user')

# Authentication routes
@app.route('/login')
def login():
    """Show login page or initiate Google OAuth login"""
    # If user is already logged in, redirect to dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    # If OAuth is initiated (has 'start' parameter), begin OAuth flow
    if request.args.get('start') == 'true':
        if not google_auth_service or not google_auth_service.is_configured():
            return render_template('login_error.html', 
                                 error="Google OAuth is not configured. Please check your environment variables.")
        
        try:
            authorization_url, state = google_auth_service.get_authorization_url()
            session['oauth_state'] = state
            return redirect(authorization_url)
        except Exception as e:
            logger.error(f"Error initiating OAuth: {e}")
            return render_template('login_error.html', error=str(e))
    
    # Show login page
    return render_template('login.html')

@app.route('/auth/callback')
def auth_callback():
    """Handle Google OAuth callback"""
    if not google_auth_service:
        return render_template('login_error.html', error="Google OAuth service not available")
    
    try:
        # Get authorization code from callback
        authorization_code = request.args.get('code')
        state = request.args.get('state')
        
        if not authorization_code:
            return render_template('login_error.html', error="Authorization code not received")
        
        # Verify state parameter
        if state != session.get('oauth_state'):
            return render_template('login_error.html', error="Invalid state parameter")
        
        # Exchange code for tokens
        token_data = google_auth_service.exchange_code_for_tokens(authorization_code, state)
        
        # Store user data in session
        session['user'] = token_data['user_info']
        session['oauth_tokens'] = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'token_uri': token_data['token_uri'],
            'client_id': token_data['client_id'],
            'client_secret': token_data['client_secret'],
            'scopes': token_data['scopes']
        }
        
        # Clear state
        session.pop('oauth_state', None)
        
        logger.info(f"User {token_data['user_info']['email']} logged in successfully")
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        return render_template('login_error.html', error=str(e))

@app.route('/logout')
def logout():
    """Logout user and clear session"""
    user_email = session.get('user', {}).get('email', 'Unknown')
    session.clear()
    logger.info(f"User {user_email} logged out")
    return redirect(url_for('login'))

# Main routes
@app.route('/')
@login_required
def dashboard():
    """Main dashboard route - requires authentication"""
    user = get_current_user()
    return render_template('sender.html', user=user)

@app.route('/sender')
@login_required
def sender():
    """Sender interface route - requires authentication"""
    user = get_current_user()
    return render_template('sender.html', user=user)

@app.route('/scanner')
def scanner():
    """QR scanner interface route - no authentication required"""
    return render_template('scanner.html')

# API endpoints
@app.route('/send-emails', methods=['POST'])
@login_required
def send_emails():
    """Send email campaign with coupon generation using authenticated user's Gmail"""
    if not all([coupon_manager, csv_manager, google_auth_service]):
        return jsonify({'success': False, 'error': 'Services not initialized'}), 500
    
    try:
        # Get current user and their OAuth tokens
        user = get_current_user()
        oauth_tokens = session.get('oauth_tokens')
        
        if not user or not oauth_tokens:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Create Gmail service with user's credentials
        credentials = google_auth_service.create_credentials_from_session(oauth_tokens)
        if not credentials:
            return jsonify({'success': False, 'error': 'Failed to create credentials'}), 401
        
        gmail_service = GmailEmailService(credentials)
        
        data = request.get_json()
        event_name = data.get('event_name', 'Special Event')
        
        # Read recipients from CSV
        recipients = csv_manager.read_recipients()
        if not recipients:
            return jsonify({'success': False, 'error': 'No recipients found'}), 400
        
        # Generate coupons for all recipients
        logger.info(f"Generating coupons for {len(recipients)} recipients")
        coupon_results = coupon_manager.generate_coupons_batch(recipients, event_name)
        
        if coupon_results['generated'] == 0:
            return jsonify({'success': False, 'error': 'Failed to generate any coupons'}), 500
        
        # Prepare email data with coupon information
        email_recipients = []
        for coupon in coupon_results['coupons']:
            email_recipients.append({
                'email': coupon['email'],
                'coupon_id': coupon['coupon_id'],
                'event_name': coupon['event_name'],
                'qr_code_base64': coupon['qr_code_base64'],
                'subject': f'Your Digital Coupon for {event_name}'
            })
        
        # Send emails with progress tracking using Gmail API
        def progress_callback(progress):
            logger.info(f"Gmail email progress: {progress['current']}/{progress['total']}")
        
        # Create template renderer function
        def template_renderer(template_name, context):
            return render_template(template_name, **context)
        
        sender_email = user['email']
        logger.info(f"Sending emails from {sender_email} to {len(email_recipients)} recipients via Gmail API")
        
        email_results = gmail_service.send_batch_emails(
            sender_email, 
            email_recipients, 
            template_renderer,
            progress_callback
        )
        
        # Update coupon status for successfully sent emails
        for result in email_results['results']:
            if result.success:
                # Find the coupon for this recipient and mark as sent
                for coupon in coupon_results['coupons']:
                    if coupon['email'] == result.recipient:
                        coupon_manager.mark_coupon_sent(coupon['coupon_id'])
                        break
        
        # Update OAuth tokens in session if they were refreshed
        updated_credentials = gmail_service.credentials
        if updated_credentials.token != oauth_tokens.get('access_token'):
            session['oauth_tokens']['access_token'] = updated_credentials.token
        
        return jsonify({
            'success': True,
            'sender_email': sender_email,
            'coupons_generated': coupon_results['generated'],
            'emails_sent': email_results['sent'],
            'emails_failed': email_results['failed'],
            'total_recipients': len(recipients),
            'start_time': email_results['start_time'],
            'end_time': email_results['end_time']
        })
        
    except Exception as e:
        logger.error(f"Error in send_emails: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/verify-coupon', methods=['POST'])
def verify_coupon():
    """Verify QR coupon and mark as used"""
    if not coupon_manager:
        return jsonify({'success': False, 'error': 'Coupon manager not initialized'}), 500
    
    try:
        data = request.get_json()
        encrypted_data = data.get('encrypted_data')
        email = data.get('email')
        
        if not encrypted_data or not email:
            return jsonify({
                'success': False, 
                'error': 'Missing encrypted_data or email',
                'error_code': 'MISSING_DATA'
            }), 400
        
        # Validate the coupon
        validation_result = coupon_manager.validate_coupon(encrypted_data, email)
        
        if not validation_result.get('valid'):
            return jsonify({
                'success': False,
                'error': validation_result.get('error', 'Invalid coupon'),
                'error_code': validation_result.get('error_code', 'INVALID'),
                'used_at': validation_result.get('used_at')
            })
        
        # Mark coupon as used
        coupon_id = validation_result['coupon_id']
        if coupon_manager.mark_coupon_used(coupon_id):
            return jsonify({
                'success': True,
                'message': 'Coupon verified and marked as used',
                'coupon_id': coupon_id,
                'email': validation_result['email'],
                'event_name': validation_result['event_name'],
                'created_at': validation_result['created_at']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to mark coupon as used',
                'error_code': 'UPDATE_FAILED'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in verify_coupon: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'System error during verification',
            'error_code': 'SYSTEM_ERROR'
        }), 500

@app.route('/coupon-status/<coupon_id>')
def coupon_status(coupon_id):
    """Get coupon status by ID"""
    if not coupon_manager:
        return jsonify({'success': False, 'error': 'Coupon manager not initialized'}), 500
    
    try:
        status_result = coupon_manager.get_coupon_status(coupon_id)
        
        if not status_result.get('found'):
            return jsonify({
                'success': False,
                'error': status_result.get('error', 'Coupon not found')
            }), 404
        
        return jsonify({
            'success': True,
            'coupon_id': status_result['coupon_id'],
            'email': status_result['email'],
            'status': status_result['status'],
            'sent_at': status_result['sent_at'],
            'used_at': status_result['used_at']
        })
        
    except Exception as e:
        logger.error(f"Error getting coupon status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    """Handle CSV file uploads and validation"""
    if not csv_manager:
        return jsonify({'success': False, 'error': 'CSV manager not initialized'}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be a CSV'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validate the CSV file
        validation_result = csv_manager.validate_recipients_file(filepath)
        
        if not validation_result['valid']:
            os.remove(filepath)  # Clean up invalid file
            return jsonify({
                'success': False,
                'error': 'Invalid CSV file',
                'details': validation_result
            }), 400
        
        # If valid, replace the current recipients file
        import shutil
        shutil.move(filepath, csv_manager.recipients_file)
        
        return jsonify({
            'success': True,
            'message': 'CSV file uploaded successfully',
            'total_rows': validation_result['total_rows'],
            'valid_emails': validation_result['valid_emails'],
            'invalid_emails': validation_result['invalid_emails']
        })
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/stats')
@login_required
def get_stats():
    """Get system statistics - requires authentication"""
    if not csv_manager:
        return jsonify({'success': False, 'error': 'CSV manager not initialized'}), 500
    
    try:
        coupon_stats = csv_manager.get_coupon_stats()
        recipients = csv_manager.read_recipients()
        user = get_current_user()
        
        return jsonify({
            'success': True,
            'recipients_count': len(recipients),
            'coupon_stats': coupon_stats,
            'user_email': user.get('email') if user else None
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/recipients')
@login_required
def get_recipients():
    """Get detailed recipient list with status markers"""
    if not all([csv_manager, coupon_manager]):
        return jsonify({'success': False, 'error': 'Services not initialized'}), 500
    
    try:
        # Get all recipients from CSV
        recipients = csv_manager.read_recipients()
        
        # Get all coupons to match with recipients
        coupon_stats = csv_manager.get_coupon_stats()
        
        # Create detailed recipient list with status
        detailed_recipients = []
        
        for recipient in recipients:
            email = recipient['email'].lower()
            
            # Find matching coupon for this recipient
            coupon_record = None
            try:
                # This is a simplified approach - in a real system you'd want a more efficient lookup
                import csv as csv_module
                with open(csv_manager.coupons_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv_module.DictReader(f)
                    for row in reader:
                        if row.get('email', '').lower() == email:
                            coupon_record = row
                            break
            except:
                pass
            
            # Determine status
            status = 'pending'  # Default status
            coupon_id = None
            sent_at = None
            used_at = None
            
            if coupon_record:
                coupon_id = coupon_record.get('coupon_id')
                status = coupon_record.get('status', 'generated')
                sent_at = coupon_record.get('sent_at')
                used_at = coupon_record.get('used_at')
            
            detailed_recipients.append({
                'email': recipient['email'],
                'status': status,
                'coupon_id': coupon_id,
                'sent_at': sent_at,
                'used_at': used_at
            })
        
        return jsonify({
            'success': True,
            'recipients': detailed_recipients,
            'total_count': len(detailed_recipients)
        })
        
    except Exception as e:
        logger.error(f"Error getting recipients: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/preview-send', methods=['POST'])
@login_required
def preview_send():
    """Preview the list of recipients before sending emails"""
    if not csv_manager:
        return jsonify({'success': False, 'error': 'CSV manager not initialized'}), 500
    
    try:
        data = request.get_json()
        event_name = data.get('event_name', 'Special Event')
        
        # Read recipients from CSV
        recipients = csv_manager.read_recipients()
        if not recipients:
            return jsonify({'success': False, 'error': 'No recipients found'}), 400
        
        # Filter out recipients who already have tickets (optional)
        include_existing = data.get('include_existing', True)
        
        preview_recipients = []
        for recipient in recipients:
            email = recipient['email'].lower()
            
            # Check if recipient already has a ticket
            has_ticket = False
            ticket_status = 'new'
            
            try:
                import csv as csv_module
                with open(csv_manager.coupons_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv_module.DictReader(f)
                    for row in reader:
                        if row.get('email', '').lower() == email:
                            has_ticket = True
                            ticket_status = row.get('status', 'generated')
                            break
            except:
                pass
            
            # Include based on filter
            if include_existing or not has_ticket:
                preview_recipients.append({
                    'email': recipient['email'],
                    'has_existing_ticket': has_ticket,
                    'ticket_status': ticket_status
                })
        
        return jsonify({
            'success': True,
            'event_name': event_name,
            'recipients': preview_recipients,
            'total_count': len(preview_recipients),
            'new_recipients': len([r for r in preview_recipients if not r['has_existing_ticket']]),
            'existing_recipients': len([r for r in preview_recipients if r['has_existing_ticket']])
        })
        
    except Exception as e:
        logger.error(f"Error previewing send: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )