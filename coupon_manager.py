"""
Coupon Manager for the Email Coupon System.
Handles coupon generation, QR code creation, and validation.
"""

import uuid
import qrcode
import base64
from io import BytesIO
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging
import json

from encryption_service import EncryptionService
from csv_manager import CSVManager, CouponRecord


class CouponManager:
    """Manages coupon generation, encryption, and validation"""
    
    def __init__(self, secret_key: Optional[str] = None, csv_manager: Optional[CSVManager] = None):
        self.encryption_service = EncryptionService(secret_key)
        self.csv_manager = csv_manager or CSVManager()
        self.logger = logging.getLogger(__name__)
    
    def generate_coupon_id(self) -> str:
        """Generate unique coupon ID using UUID4"""
        return str(uuid.uuid4())
    
    def create_qr_code(self, data: str) -> str:
        """
        Generate QR code from data and return as base64 string
        
        Args:
            data: String data to encode in QR code
            
        Returns:
            Base64 encoded PNG image of QR code
        """
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            self.logger.error(f"Error creating QR code: {str(e)}")
            raise
    
    def generate_coupon(self, email: str, event_name: str = "Special Event") -> Dict[str, Any]:
        """
        Generate a complete coupon with encrypted data and QR code
        
        Args:
            email: Recipient email address
            event_name: Name of the event for the coupon
            
        Returns:
            Dictionary containing coupon data
        """
        try:
            # Generate unique coupon ID
            coupon_id = self.generate_coupon_id()
            
            # Create coupon data
            coupon_data = {
                'coupon_id': coupon_id,
                'email': email.lower(),
                'event_name': event_name,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'valid': True
            }
            
            # Encrypt coupon data
            encrypted_data = self.encryption_service.encrypt_coupon_data(coupon_data, email)
            
            # Create QR code data with both email and encrypted data for fast scanning
            qr_data = {
                'email': email.lower(),
                'data': encrypted_data,
                'coupon_id': coupon_id
            }
            qr_code_base64 = self.create_qr_code(json.dumps(qr_data))
            
            # Create coupon record
            coupon_record = CouponRecord(
                coupon_id=coupon_id,
                email=email.lower(),
                encrypted_data=encrypted_data,
                qr_code_data=qr_code_base64,
                status='generated'
            )
            
            # Save to CSV
            if self.csv_manager.save_coupon(coupon_record):
                self.logger.info(f"Generated coupon {coupon_id} for {email}")
                
                return {
                    'coupon_id': coupon_id,
                    'email': email,
                    'event_name': event_name,
                    'qr_code_base64': qr_code_base64,
                    'encrypted_data': encrypted_data,
                    'success': True
                }
            else:
                raise Exception("Failed to save coupon to database")
                
        except Exception as e:
            self.logger.error(f"Error generating coupon for {email}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_coupons_batch(self, recipients: List[Dict[str, str]], 
                              event_name: str = "Special Event") -> Dict[str, Any]:
        """
        Generate coupons for multiple recipients
        
        Args:
            recipients: List of recipient dictionaries with 'email' key
            event_name: Name of the event
            
        Returns:
            Dictionary with generation results
        """
        results = {
            'total': len(recipients),
            'generated': 0,
            'failed': 0,
            'coupons': [],
            'errors': []
        }
        
        coupon_records = []
        
        for recipient in recipients:
            email = recipient.get('email', '').strip()
            if not email:
                results['failed'] += 1
                results['errors'].append("Empty email address")
                continue
            
            try:
                # Generate coupon data
                coupon_id = self.generate_coupon_id()
                
                coupon_data = {
                    'coupon_id': coupon_id,
                    'email': email.lower(),
                    'event_name': event_name,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'valid': True
                }
                
                # Encrypt and create QR code
                encrypted_data = self.encryption_service.encrypt_coupon_data(coupon_data, email)
                
                # Create QR code data with both email and encrypted data for fast scanning
                qr_data = {
                    'email': email.lower(),
                    'data': encrypted_data,
                    'coupon_id': coupon_id
                }
                qr_code_base64 = self.create_qr_code(json.dumps(qr_data))
                
                # Create record
                coupon_record = CouponRecord(
                    coupon_id=coupon_id,
                    email=email.lower(),
                    encrypted_data=encrypted_data,
                    qr_code_data=qr_code_base64,
                    status='generated'
                )
                
                coupon_records.append(coupon_record)
                
                # Add to results
                results['coupons'].append({
                    'coupon_id': coupon_id,
                    'email': email,
                    'event_name': event_name,
                    'qr_code_base64': qr_code_base64,
                    'encrypted_data': encrypted_data
                })
                
                results['generated'] += 1
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Failed to generate coupon for {email}: {str(e)}")
                self.logger.error(f"Error generating coupon for {email}: {str(e)}")
        
        # Save all coupons in batch
        if coupon_records:
            if not self.csv_manager.save_coupons_batch(coupon_records):
                self.logger.error("Failed to save coupon batch to database")
                # Note: coupons are still generated in memory, just not persisted
        
        self.logger.info(f"Generated {results['generated']} coupons, {results['failed']} failed")
        return results
    
    def validate_coupon(self, encrypted_data: str, email: str) -> Dict[str, Any]:
        """
        Validate a coupon by decrypting and checking its status
        
        Args:
            encrypted_data: Encrypted coupon data from QR code
            email: Email address for validation
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Decrypt coupon data
            decrypted_data = self.encryption_service.decrypt_coupon_data(encrypted_data, email)
            
            # Validate timestamp (24 hours validity)
            if not self.encryption_service.validate_timestamp(decrypted_data, max_age_hours=24):
                return {
                    'valid': False,
                    'error': 'Coupon has expired',
                    'error_code': 'EXPIRED'
                }
            
            # Get coupon ID and check database status
            coupon_id = decrypted_data.get('coupon_id')
            if not coupon_id:
                return {
                    'valid': False,
                    'error': 'Invalid coupon data',
                    'error_code': 'INVALID_DATA'
                }
            
            # Check coupon record in database
            coupon_record = self.csv_manager.find_coupon(coupon_id)
            if not coupon_record:
                return {
                    'valid': False,
                    'error': 'Coupon not found in database',
                    'error_code': 'NOT_FOUND'
                }
            
            # Check if already used
            if coupon_record.status == 'used':
                return {
                    'valid': False,
                    'error': 'Coupon has already been used',
                    'error_code': 'ALREADY_USED',
                    'used_at': coupon_record.used_at
                }
            
            # Coupon is valid
            return {
                'valid': True,
                'coupon_id': coupon_id,
                'email': decrypted_data.get('email'),
                'event_name': decrypted_data.get('event_name'),
                'created_at': decrypted_data.get('created_at'),
                'status': coupon_record.status
            }
            
        except ValueError as e:
            self.logger.warning(f"Coupon validation failed: {str(e)}")
            return {
                'valid': False,
                'error': 'Invalid or corrupted coupon data',
                'error_code': 'DECRYPTION_FAILED'
            }
        except Exception as e:
            self.logger.error(f"Unexpected error during coupon validation: {str(e)}")
            return {
                'valid': False,
                'error': 'System error during validation',
                'error_code': 'SYSTEM_ERROR'
            }
    
    def mark_coupon_used(self, coupon_id: str) -> bool:
        """
        Mark a coupon as used
        
        Args:
            coupon_id: ID of the coupon to mark as used
            
        Returns:
            True if successfully marked as used, False otherwise
        """
        try:
            used_at = datetime.now(timezone.utc).isoformat()
            success = self.csv_manager.update_coupon_status(coupon_id, 'used', used_at)
            
            if success:
                self.logger.info(f"Marked coupon {coupon_id} as used")
            else:
                self.logger.error(f"Failed to mark coupon {coupon_id} as used")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error marking coupon {coupon_id} as used: {str(e)}")
            return False
    
    def mark_coupon_sent(self, coupon_id: str) -> bool:
        """
        Mark a coupon as sent via email
        
        Args:
            coupon_id: ID of the coupon to mark as sent
            
        Returns:
            True if successfully marked as sent, False otherwise
        """
        try:
            sent_at = datetime.now(timezone.utc).isoformat()
            # Update the coupon record with sent timestamp
            coupon_record = self.csv_manager.find_coupon(coupon_id)
            if coupon_record:
                coupon_record.sent_at = sent_at
                coupon_record.status = 'sent'
                success = self.csv_manager.update_coupon_status(coupon_id, 'sent', None)
                
                if success:
                    self.logger.info(f"Marked coupon {coupon_id} as sent")
                return success
            else:
                self.logger.error(f"Coupon {coupon_id} not found for marking as sent")
                return False
                
        except Exception as e:
            self.logger.error(f"Error marking coupon {coupon_id} as sent: {str(e)}")
            return False
    
    def get_coupon_status(self, coupon_id: str) -> Dict[str, Any]:
        """
        Get the current status of a coupon
        
        Args:
            coupon_id: ID of the coupon to check
            
        Returns:
            Dictionary with coupon status information
        """
        try:
            coupon_record = self.csv_manager.find_coupon(coupon_id)
            
            if not coupon_record:
                return {
                    'found': False,
                    'error': 'Coupon not found'
                }
            
            return {
                'found': True,
                'coupon_id': coupon_record.coupon_id,
                'email': coupon_record.email,
                'status': coupon_record.status,
                'sent_at': coupon_record.sent_at,
                'used_at': coupon_record.used_at
            }
            
        except Exception as e:
            self.logger.error(f"Error getting coupon status for {coupon_id}: {str(e)}")
            return {
                'found': False,
                'error': f'System error: {str(e)}'
            }