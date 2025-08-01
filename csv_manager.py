"""
CSV Manager for the Email Coupon System.
Handles reading and writing coupon data with file locking for concurrent access.
"""

import csv
import os
import fcntl
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import logging


@dataclass
class CouponRecord:
    """Data structure for coupon records in CSV"""
    coupon_id: str
    email: str
    encrypted_data: str
    qr_code_data: str
    sent_at: Optional[str] = None
    used_at: Optional[str] = None
    status: str = 'generated'  # generated, sent, used, expired
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV writing"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CouponRecord':
        """Create from dictionary loaded from CSV"""
        return cls(**data)


class CSVManager:
    """Manages CSV file operations with file locking for concurrent access"""
    
    def __init__(self, coupons_file: str = 'coupons.csv', recipients_file: str = 'responses - Sheet1.csv'):
        self.coupons_file = coupons_file
        self.recipients_file = recipients_file
        self.logger = logging.getLogger(__name__)
        
        # Ensure coupons file exists with headers
        self._initialize_coupons_file()
    
    def _initialize_coupons_file(self):
        """Initialize coupons CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.coupons_file):
            headers = ['coupon_id', 'email', 'encrypted_data', 'qr_code_data', 
                      'sent_at', 'used_at', 'status']
            with open(self.coupons_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            self.logger.info(f"Created coupons file: {self.coupons_file}")
    
    @contextmanager
    def _file_lock(self, file_path: str, mode: str = 'r'):
        """Context manager for file locking"""
        try:
            f = open(file_path, mode, newline='', encoding='utf-8')
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            yield f
        except Exception as e:
            self.logger.error(f"File lock error for {file_path}: {str(e)}")
            raise
        finally:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                f.close()
            except:
                pass
    
    def read_recipients(self) -> List[Dict[str, str]]:
        """Read recipient emails from CSV file"""
        recipients = []
        try:
            with self._file_lock(self.recipients_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('email'):
                        recipients.append({'email': row['email'].strip()})
            
            self.logger.info(f"Read {len(recipients)} recipients from {self.recipients_file}")
            return recipients
            
        except FileNotFoundError:
            self.logger.error(f"Recipients file not found: {self.recipients_file}")
            return []
        except Exception as e:
            self.logger.error(f"Error reading recipients: {str(e)}")
            return []
    
    def save_coupon(self, coupon: CouponRecord) -> bool:
        """Save a single coupon record to CSV"""
        try:
            with self._file_lock(self.coupons_file, 'a') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'coupon_id', 'email', 'encrypted_data', 'qr_code_data',
                    'sent_at', 'used_at', 'status'
                ])
                writer.writerow(coupon.to_dict())
            
            self.logger.info(f"Saved coupon {coupon.coupon_id} for {coupon.email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving coupon {coupon.coupon_id}: {str(e)}")
            return False
    
    def save_coupons_batch(self, coupons: List[CouponRecord]) -> bool:
        """Save multiple coupon records in batch"""
        try:
            with self._file_lock(self.coupons_file, 'a') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'coupon_id', 'email', 'encrypted_data', 'qr_code_data',
                    'sent_at', 'used_at', 'status'
                ])
                for coupon in coupons:
                    writer.writerow(coupon.to_dict())
            
            self.logger.info(f"Saved {len(coupons)} coupons in batch")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving coupon batch: {str(e)}")
            return False
    
    def find_coupon(self, coupon_id: str) -> Optional[CouponRecord]:
        """Find a coupon by ID"""
        try:
            with self._file_lock(self.coupons_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('coupon_id') == coupon_id:
                        return CouponRecord.from_dict(row)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding coupon {coupon_id}: {str(e)}")
            return None
    
    def update_coupon_status(self, coupon_id: str, status: str, used_at: Optional[str] = None) -> bool:
        """Update coupon status and usage timestamp"""
        try:
            # Read all coupons
            coupons = []
            updated = False
            
            with self._file_lock(self.coupons_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('coupon_id') == coupon_id:
                        row['status'] = status
                        if used_at:
                            row['used_at'] = used_at
                        updated = True
                    coupons.append(row)
            
            if not updated:
                self.logger.warning(f"Coupon {coupon_id} not found for status update")
                return False
            
            # Write back all coupons
            with self._file_lock(self.coupons_file, 'w') as f:
                if coupons:
                    writer = csv.DictWriter(f, fieldnames=coupons[0].keys())
                    writer.writeheader()
                    writer.writerows(coupons)
            
            self.logger.info(f"Updated coupon {coupon_id} status to {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating coupon {coupon_id}: {str(e)}")
            return False
    
    def get_coupon_stats(self) -> Dict[str, int]:
        """Get statistics about coupon usage"""
        stats = {
            'total': 0,
            'generated': 0,
            'sent': 0,
            'used': 0,
            'expired': 0
        }
        
        try:
            with self._file_lock(self.coupons_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stats['total'] += 1
                    status = row.get('status', 'generated')
                    if status in stats:
                        stats[status] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting coupon stats: {str(e)}")
            return stats
    
    def validate_email_format(self, email: str) -> bool:
        """Basic email format validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None
    
    def validate_recipients_file(self, file_path: str) -> Dict[str, Any]:
        """Validate recipients CSV file and return statistics"""
        result = {
            'valid': False,
            'total_rows': 0,
            'valid_emails': 0,
            'invalid_emails': 0,
            'errors': []
        }
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                if 'email' not in reader.fieldnames:
                    result['errors'].append("CSV must have 'email' column")
                    return result
                
                for i, row in enumerate(reader, 1):
                    result['total_rows'] += 1
                    email = row.get('email', '').strip()
                    
                    if not email:
                        result['invalid_emails'] += 1
                        continue
                    
                    if self.validate_email_format(email):
                        result['valid_emails'] += 1
                    else:
                        result['invalid_emails'] += 1
                        result['errors'].append(f"Invalid email format at row {i}: {email}")
            
            result['valid'] = result['valid_emails'] > 0
            
        except Exception as e:
            result['errors'].append(f"Error reading file: {str(e)}")
        
        return result