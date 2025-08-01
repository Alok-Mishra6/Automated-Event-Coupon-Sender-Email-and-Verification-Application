import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Dict, List, Callable, Optional
from jinja2 import Environment, FileSystemLoader, Template
import base64
import os
from dataclasses import dataclass
import threading
from queue import Queue


@dataclass
class EmailConfig:
    """Configuration for SMTP email service"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 30


@dataclass
class EmailResult:
    """Result of email sending operation"""
    success: bool
    recipient: str
    error_message: Optional[str] = None
    timestamp: Optional[str] = None


class EmailService:
    """SMTP email service with retry logic and template rendering"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.template_env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=True
        )
        
    def _create_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection with authentication"""
        try:
            if self.config.use_ssl:
                server = smtplib.SMTP_SSL(
                    self.config.smtp_server, 
                    self.config.smtp_port,
                    timeout=self.config.timeout
                )
            else:
                server = smtplib.SMTP(
                    self.config.smtp_server, 
                    self.config.smtp_port,
                    timeout=self.config.timeout
                )
                
            if self.config.use_tls and not self.config.use_ssl:
                server.starttls()
                
            server.login(self.config.username, self.config.password)
            return server
            
        except Exception as e:
            self.logger.error(f"Failed to create SMTP connection: {str(e)}")
            raise
    
    def _send_single_email(self, recipient: str, subject: str, html_content: str, 
                          max_retries: int = 3) -> EmailResult:
        """Send a single email with retry logic and exponential backoff"""
        
        for attempt in range(max_retries):
            try:
                # Create message
                msg = MIMEMultipart('alternative')
                msg['From'] = self.config.username
                msg['To'] = recipient
                msg['Subject'] = subject
                
                # Add HTML content
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
                
                # Send email
                with self._create_connection() as server:
                    server.send_message(msg)
                    
                self.logger.info(f"Email sent successfully to {recipient}")
                return EmailResult(
                    success=True,
                    recipient=recipient,
                    timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                )
                
            except Exception as e:
                wait_time = (2 ** attempt) * 1  # Exponential backoff: 1, 2, 4 seconds
                error_msg = f"Attempt {attempt + 1} failed for {recipient}: {str(e)}"
                self.logger.warning(error_msg)
                
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"All retry attempts failed for {recipient}")
                    return EmailResult(
                        success=False,
                        recipient=recipient,
                        error_message=str(e),
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                    )
        
        return EmailResult(
            success=False,
            recipient=recipient,
            error_message="Max retries exceeded"
        ) 
   
    def render_email_template(self, template_name: str, context: Dict) -> str:
        """Render email template with given context using Jinja2"""
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            self.logger.error(f"Failed to render template {template_name}: {str(e)}")
            raise
    
    def send_coupon_email(self, recipient: str, coupon_data: Dict, 
                         template_name: str = 'event.html') -> EmailResult:
        """Send a single coupon email with QR code"""
        try:
            # Render email content
            html_content = self.render_email_template(template_name, coupon_data)
            
            # Send email
            subject = coupon_data.get('subject', 'Your Digital Coupon')
            return self._send_single_email(recipient, subject, html_content)
            
        except Exception as e:
            self.logger.error(f"Failed to send coupon email to {recipient}: {str(e)}")
            return EmailResult(
                success=False,
                recipient=recipient,
                error_message=str(e)
            )
    
    def send_batch_emails(self, recipients: List[Dict], 
                         progress_callback: Optional[Callable] = None,
                         template_name: str = 'event.html') -> Dict:
        """Send emails to multiple recipients with progress tracking"""
        
        results = {
            'total': len(recipients),
            'sent': 0,
            'failed': 0,
            'results': [],
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.logger.info(f"Starting batch email send to {len(recipients)} recipients")
        
        for i, recipient_data in enumerate(recipients):
            recipient_email = recipient_data.get('email')
            if not recipient_email:
                self.logger.warning(f"Skipping recipient {i}: no email address")
                continue
                
            # Send individual email
            result = self.send_coupon_email(
                recipient_email, 
                recipient_data, 
                template_name
            )
            
            results['results'].append(result)
            
            if result.success:
                results['sent'] += 1
            else:
                results['failed'] += 1
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback({
                    'current': i + 1,
                    'total': len(recipients),
                    'sent': results['sent'],
                    'failed': results['failed'],
                    'last_result': result
                })
            
            # Small delay between emails to avoid overwhelming SMTP server
            time.sleep(0.1)
        
        results['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.logger.info(f"Batch email send completed: {results['sent']} sent, {results['failed']} failed")
        
        return results
    
    def test_connection(self) -> bool:
        """Test SMTP connection and authentication"""
        try:
            with self._create_connection() as server:
                self.logger.info("SMTP connection test successful")
                return True
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {str(e)}")
            return False


# Factory function for creating EmailService from environment variables
def create_email_service_from_env() -> EmailService:
    """Create EmailService instance from environment variables"""
    config = EmailConfig(
        smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        username=os.getenv('SMTP_USERNAME', ''),
        password=os.getenv('SMTP_PASSWORD', ''),
        use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
        use_ssl=os.getenv('SMTP_USE_SSL', 'false').lower() == 'true',
        timeout=int(os.getenv('SMTP_TIMEOUT', '30'))
    )
    
    return EmailService(config)