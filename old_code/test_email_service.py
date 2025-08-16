import unittest
from unittest.mock import Mock, patch, MagicMock
import smtplib
import time
from email_service import EmailService, EmailConfig, EmailResult
import tempfile
import os


class TestEmailService(unittest.TestCase):
    """Unit tests for EmailService with mock SMTP server"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = EmailConfig(
            smtp_server='smtp.test.com',
            smtp_port=587,
            username='test@example.com',
            password='testpass',
            use_tls=True,
            timeout=30
        )
        
        # Create temporary template directory
        self.temp_dir = tempfile.mkdtemp()
        self.template_path = os.path.join(self.temp_dir, 'test_template.html')
        
        # Create a simple test template
        with open(self.template_path, 'w') as f:
            f.write('<html><body>Hello {{name}}! Your coupon: {{coupon_id}}</body></html>')
        
        # Mock the template loader to use our temp directory
        with patch('email_service.FileSystemLoader') as mock_loader:
            mock_loader.return_value.get_source.return_value = (
                '<html><body>Hello {{name}}! Your coupon: {{coupon_id}}</body></html>',
                None,
                lambda: True
            )
            self.email_service = EmailService(self.config)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.template_path):
            os.remove(self.template_path)
        os.rmdir(self.temp_dir)
    
    @patch('email_service.smtplib.SMTP')
    def test_create_connection_success(self, mock_smtp):
        """Test successful SMTP connection creation"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        connection = self.email_service._create_connection()
        
        mock_smtp.assert_called_once_with('smtp.test.com', 587, timeout=30)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'testpass')
        self.assertEqual(connection, mock_server)
    
    @patch('email_service.smtplib.SMTP')
    def test_create_connection_ssl(self, mock_smtp):
        """Test SMTP connection with SSL"""
        self.config.use_ssl = True
        self.config.use_tls = False
        
        with patch('email_service.smtplib.SMTP_SSL') as mock_smtp_ssl:
            mock_server = Mock()
            mock_smtp_ssl.return_value = mock_server
            
            connection = self.email_service._create_connection()
            
            mock_smtp_ssl.assert_called_once_with('smtp.test.com', 587, timeout=30)
            mock_server.starttls.assert_not_called()
            mock_server.login.assert_called_once_with('test@example.com', 'testpass')
    
    @patch('email_service.smtplib.SMTP')
    def test_create_connection_failure(self, mock_smtp):
        """Test SMTP connection failure"""
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")
        
        with self.assertRaises(smtplib.SMTPException):
            self.email_service._create_connection()
    
    @patch('email_service.smtplib.SMTP')
    def test_send_single_email_success(self, mock_smtp):
        """Test successful single email sending"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__ = Mock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = Mock(return_value=None)
        
        result = self.email_service._send_single_email(
            'recipient@test.com',
            'Test Subject',
            '<html><body>Test content</body></html>'
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.recipient, 'recipient@test.com')
        self.assertIsNone(result.error_message)
        mock_server.send_message.assert_called_once()
    
    @patch('email_service.smtplib.SMTP')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_send_single_email_retry_logic(self, mock_sleep, mock_smtp):
        """Test email retry logic with exponential backoff"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__ = Mock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = Mock(return_value=None)
        
        # First two attempts fail, third succeeds
        mock_server.send_message.side_effect = [
            smtplib.SMTPException("Temporary failure"),
            smtplib.SMTPException("Another failure"),
            None  # Success
        ]
        
        result = self.email_service._send_single_email(
            'recipient@test.com',
            'Test Subject',
            '<html><body>Test content</body></html>',
            max_retries=3
        )
        
        self.assertTrue(result.success)
        self.assertEqual(mock_server.send_message.call_count, 3)
        # Check exponential backoff: sleep(1), sleep(2)
        mock_sleep.assert_any_call(1)
        mock_sleep.assert_any_call(2)
    
    @patch('email_service.smtplib.SMTP')
    @patch('time.sleep')
    def test_send_single_email_max_retries_exceeded(self, mock_sleep, mock_smtp):
        """Test email sending when max retries are exceeded"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__ = Mock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = Mock(return_value=None)
        
        # All attempts fail
        mock_server.send_message.side_effect = smtplib.SMTPException("Persistent failure")
        
        result = self.email_service._send_single_email(
            'recipient@test.com',
            'Test Subject',
            '<html><body>Test content</body></html>',
            max_retries=2
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.recipient, 'recipient@test.com')
        self.assertIn("Persistent failure", result.error_message)
        self.assertEqual(mock_server.send_message.call_count, 2)