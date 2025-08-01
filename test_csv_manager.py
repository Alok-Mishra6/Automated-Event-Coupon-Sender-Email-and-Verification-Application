#!/usr/bin/env python3
"""
Unit tests for CSV Manager
Tests CSV operations, file locking, data validation, and error handling
"""

import unittest
import tempfile
import os
import csv
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open
import threading
import time

from csv_manager import CSVManager, Coupon


class TestCoupon(unittest.TestCase):
    """Test Coupon data class"""
    
    def test_coupon_creation(self):
        """Test basic coupon creation"""
        coupon = Coupon(
            coupon_id="test-123",
            email="test@example.com",
            encrypted_data="encrypted",
            qr_code_data="qr_data"
        )
        
        self.assertEqual(coupon.coupon_id, "test-123")
        self.assertEqual(coupon.email, "test@example.com")
        self.assertEqual(coupon.status, "generated")
        self.assertIsNone(coupon.sent_at)
        self.assertIsNone(coupon.used_at)
    
    def test_coupon_to_dict(self):
        """Test coupon to dictionary conversion"""
        coupon = Coupon(
            coupon_id="test-123",
            email="test@example.com",
            encrypted_data="encrypted",
            qr_code_data="qr_data",
            status="sent"
        )
        
        data = coupon.to_dict()
        expected = {
            'coupon_id': 'test-123',
            'email': 'test@example.com',
            'encrypted_data': 'encrypted',
            'qr_code_data': 'qr_data',
            'sent_at': None,
            'used_at': None,
            'status': 'sent'
        }
        
        self.assertEqual(data, expected)
    
    def test_coupon_from_dict(self):
        """Test coupon creation from dictionary"""
        data = {
            'coupon_id': 'test-123',
            'email': 'test@example.com',
            'encrypted_data': 'encrypted',
            'qr_code_data': 'qr_data',
            'sent_at': '2024-01-01T10:00:00',
            'used_at': None,
            'status': 'sent'
        }
        
        coupon = Coupon.from_dict(data)
        
        self.assertEqual(coupon.coupon_id, 'test-123')
        self.assertEqual(coupon.email, 'test@example.com')
        self.assertEqual(coupon.sent_at, '2024-01-01T10:00:00')
        self.assertEqual(coupon.status, 'sent')


class TestCSVManager(unittest.TestCase):
    """Test CSV Manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.recipients_file = os.path.join(self.test_dir, "recipients.csv")
        self.coupons_file = os.path.join(self.test_dir, "coupons.csv")
        
        # Create test recipients file
        with open(self.recipients_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['email'])
            writer.writerow(['test1@example.com'])
            writer.writerow(['test2@example.com'])
            writer.writerow(['invalid-email'])  # Invalid email for testing
            writer.writerow([''])  # Empty email for testing
        
        self.manager = CSVManager(self.recipients_file, self.coupons_file)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test CSV manager initialization"""
        self.assertTrue(os.path.exists(self.coupons_file))
        
        # Check that headers were created
        with open(self.coupons_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected_headers = ['coupon_id', 'email', 'encrypted_data', 'qr_code_data', 
                              'sent_at', 'used_at', 'status']
            self.assertEqual(headers, expected_headers)
    
    def test_email_validation(self):
        """Test email validation"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'test123@test-domain.com'
        ]
        
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'test@',
            '',
            None,
            'test@domain',
            'test.domain.com'
        ]
        
        for email in valid_emails:
            self.assertTrue(self.manager.validate_email(email), f"Should be valid: {email}")
        
        for email in invalid_emails:
            self.assertFalse(self.manager.validate_email(email), f"Should be invalid: {email}")
    
    def test_data_sanitization(self):
        """Test data sanitization"""
        dirty_data = {
            'field1': 'normal text',
            'field2': 'text\nwith\nnewlines',
            'field3': 'text\rwith\rcarriage\rreturns',
            'field4': None,
            'field5': 123
        }
        
        clean_data = self.manager.sanitize_data(dirty_data)
        
        self.assertEqual(clean_data['field1'], 'normal text')
        self.assertEqual(clean_data['field2'], 'text with newlines')
        self.assertEqual(clean_data['field3'], 'text with carriage returns')
        self.assertEqual(clean_data['field4'], '')
        self.assertEqual(clean_data['field5'], '123')
    
    def test_read_recipients(self):
        """Test reading recipients from CSV"""
        recipients = self.manager.read_recipients()
        
        # Should only include valid emails
        self.assertEqual(len(recipients), 2)
        self.assertEqual(recipients[0]['email'], 'test1@example.com')
        self.assertEqual(recipients[1]['email'], 'test2@example.com')
    
    def test_read_recipients_file_not_found(self):
        """Test reading recipients when file doesn't exist"""
        manager = CSVManager("nonexistent.csv", self.coupons_file)
        
        with self.assertRaises(FileNotFoundError):
            manager.read_recipients()
    
    def test_read_recipients_invalid_format(self):
        """Test reading recipients with invalid CSV format"""
        # Create invalid CSV (no email column)
        invalid_file = os.path.join(self.test_dir, "invalid.csv")
        with open(invalid_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name'])  # Wrong header
            writer.writerow(['John'])
        
        manager = CSVManager(invalid_file, self.coupons_file)
        
        with self.assertRaises(ValueError):
            manager.read_recipients()
    
    def test_write_single_coupon(self):
        """Test writing a single coupon"""
        coupon = Coupon(
            coupon_id="test-123",
            email="test@example.com",
            encrypted_data="encrypted",
            qr_code_data="qr_data"
        )
        
        result = self.manager.write_coupon(coupon)
        self.assertTrue(result)
        
        # Verify coupon was written
        coupons = self.manager.read_coupons()
        self.assertEqual(len(coupons), 1)
        self.assertEqual(coupons[0].coupon_id, "test-123")
        self.assertEqual(coupons[0].email, "test@example.com")
    
    def test_write_coupon_duplicate_id(self):
        """Test writing coupon with duplicate ID"""
        coupon1 = Coupon(
            coupon_id="test-123",
            email="test1@example.com",
            encrypted_data="encrypted",
            qr_code_data="qr_data"
        )
        
        coupon2 = Coupon(
            coupon_id="test-123",  # Same ID
            email="test2@example.com",
            encrypted_data="encrypted",
            qr_code_data="qr_data"
        )
        
        self.manager.write_coupon(coupon1)
        
        with self.assertRaises(ValueError):
            self.manager.write_coupon(coupon2)
    
    def test_write_coupon_invalid_email(self):
        """Test writing coupon with invalid email"""
        coupon = Coupon(
            coupon_id="test-123",
            email="invalid-email",
            encrypted_data="encrypted",
            qr_code_data="qr_data"
        )
        
        with self.assertRaises(ValueError):
            self.manager.write_coupon(coupon) 
   
    def test_write_coupons_batch(self):
        """Test batch writing of coupons"""
        coupons = [
            Coupon(
                coupon_id="test-1",
                email="test1@example.com",
                encrypted_data="encrypted1",
                qr_code_data="qr_data1"
            ),
            Coupon(
                coupon_id="test-2",
                email="test2@example.com",
                encrypted_data="encrypted2",
                qr_code_data="qr_data2"
            ),
            Coupon(
                coupon_id="test-3",
                email="invalid-email",  # Invalid email
                encrypted_data="encrypted3",
                qr_code_data="qr_data3"
            )
        ]
        
        written_count = self.manager.write_coupons_batch(coupons)
        
        # Should write 2 valid coupons, skip 1 invalid
        self.assertEqual(written_count, 2)
        
        # Verify coupons were written
        saved_coupons = self.manager.read_coupons()
        self.assertEqual(len(saved_coupons), 2)
        self.assertEqual(saved_coupons[0].coupon_id, "test-1")
        self.assertEqual(saved_coupons[1].coupon_id, "test-2")
    
    def test_get_coupon_by_id(self):
        """Test getting coupon by ID"""
        coupon = Coupon(
            coupon_id="test-123",
            email="test@example.com",
            encrypted_data="encrypted",
            qr_code_data="qr_data"
        )
        
        self.manager.write_coupon(coupon)
        
        # Test finding existing coupon
        found_coupon = self.manager.get_coupon_by_id("test-123")
        self.assertIsNotNone(found_coupon)
        self.assertEqual(found_coupon.coupon_id, "test-123")
        
        # Test finding non-existent coupon
        not_found = self.manager.get_coupon_by_id("nonexistent")
        self.assertIsNone(not_found)
        
        # Test with empty ID
        empty_result = self.manager.get_coupon_by_id("")
        self.assertIsNone(empty_result)
    
    def test_update_coupon_status(self):
        """Test updating coupon status"""
        coupon = Coupon(
            coupon_id="test-123",
            email="test@example.com",
            encrypted_data="encrypted",
            qr_code_data="qr_data"
        )
        
        self.manager.write_coupon(coupon)
        
        # Update to sent status
        result = self.manager.update_coupon_status("test-123", "sent")
        self.assertTrue(result)
        
        # Verify update
        updated_coupon = self.manager.get_coupon_by_id("test-123")
        self.assertEqual(updated_coupon.status, "sent")
        
        # Update to used status (should set used_at timestamp)
        result = self.manager.update_coupon_status("test-123", "used")
        self.assertTrue(result)
        
        updated_coupon = self.manager.get_coupon_by_id("test-123")
        self.assertEqual(updated_coupon.status, "used")
        self.assertIsNotNone(updated_coupon.used_at)
    
    def test_update_coupon_status_invalid(self):
        """Test updating coupon with invalid status"""
        coupon = Coupon(
            coupon_id="test-123",
            email="test@example.com",
            encrypted_data="encrypted",
            qr_code_data="qr_data"
        )
        
        self.manager.write_coupon(coupon)
        
        with self.assertRaises(ValueError):
            self.manager.update_coupon_status("test-123", "invalid_status")
    
    def test_update_nonexistent_coupon(self):
        """Test updating non-existent coupon"""
        result = self.manager.update_coupon_status("nonexistent", "sent")
        self.assertFalse(result)
    
    def test_get_coupon_stats(self):
        """Test getting coupon statistics"""
        coupons = [
            Coupon("id1", "test1@example.com", "enc1", "qr1", status="generated"),
            Coupon("id2", "test2@example.com", "enc2", "qr2", status="sent"),
            Coupon("id3", "test3@example.com", "enc3", "qr3", status="used"),
            Coupon("id4", "test4@example.com", "enc4", "qr4", status="expired")
        ]
        
        self.manager.write_coupons_batch(coupons)
        
        stats = self.manager.get_coupon_stats()
        
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['generated'], 1)
        self.assertEqual(stats['sent'], 1)
        self.assertEqual(stats['used'], 1)
        self.assertEqual(stats['expired'], 1)
    
    def test_cleanup_expired_coupons(self):
        """Test cleanup of expired coupons"""
        # Create coupons with different timestamps
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        coupons = [
            Coupon("id1", "test1@example.com", "enc1", "qr1", 
                  sent_at=old_time, status="sent"),
            Coupon("id2", "test2@example.com", "enc2", "qr2", 
                  sent_at=recent_time, status="sent"),
            Coupon("id3", "test3@example.com", "enc3", "qr3", 
                  status="used")  # Already used, shouldn't be affected
        ]
        
        self.manager.write_coupons_batch(coupons)
        
        # Cleanup with 24-hour expiry
        expired_count = self.manager.cleanup_expired_coupons(24)
        
        self.assertEqual(expired_count, 1)  # Only one should be expired
        
        # Verify the correct coupon was expired
        coupon1 = self.manager.get_coupon_by_id("id1")
        coupon2 = self.manager.get_coupon_by_id("id2")
        coupon3 = self.manager.get_coupon_by_id("id3")
        
        self.assertEqual(coupon1.status, "expired")
        self.assertEqual(coupon2.status, "sent")  # Should remain sent
        self.assertEqual(coupon3.status, "used")  # Should remain used
    
    def test_read_empty_coupons_file(self):
        """Test reading from empty coupons file"""
        # Remove the coupons file
        os.remove(self.coupons_file)
        
        coupons = self.manager.read_coupons()
        self.assertEqual(len(coupons), 0)


class TestConcurrentAccess(unittest.TestCase):
    """Test concurrent access and file locking"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.recipients_file = os.path.join(self.test_dir, "recipients.csv")
        self.coupons_file = os.path.join(self.test_dir, "coupons.csv")
        
        # Create test recipients file
        with open(self.recipients_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['email'])
            writer.writerow(['test@example.com'])
        
        self.manager = CSVManager(self.recipients_file, self.coupons_file)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_concurrent_writes(self):
        """Test concurrent coupon writes"""
        results = []
        errors = []
        
        def write_coupon(thread_id):
            try:
                coupon = Coupon(
                    coupon_id=f"test-{thread_id}",
                    email=f"test{thread_id}@example.com",
                    encrypted_data=f"encrypted{thread_id}",
                    qr_code_data=f"qr_data{thread_id}"
                )
                result = self.manager.write_coupon(coupon)
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads to write concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=write_coupon, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All writes should succeed
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))
        self.assertEqual(len(errors), 0)
        
        # Verify all coupons were written
        coupons = self.manager.read_coupons()
        self.assertEqual(len(coupons), 5)
    
    def test_concurrent_read_write(self):
        """Test concurrent reads and writes"""
        # Write initial coupon
        initial_coupon = Coupon(
            coupon_id="initial",
            email="initial@example.com",
            encrypted_data="encrypted",
            qr_code_data="qr_data"
        )
        self.manager.write_coupon(initial_coupon)
        
        read_results = []
        write_results = []
        
        def read_coupons():
            try:
                coupons = self.manager.read_coupons()
                read_results.append(len(coupons))
            except Exception as e:
                read_results.append(f"Error: {e}")
        
        def write_coupon(thread_id):
            try:
                coupon = Coupon(
                    coupon_id=f"concurrent-{thread_id}",
                    email=f"concurrent{thread_id}@example.com",
                    encrypted_data=f"encrypted{thread_id}",
                    qr_code_data=f"qr_data{thread_id}"
                )
                result = self.manager.write_coupon(coupon)
                write_results.append(result)
            except Exception as e:
                write_results.append(f"Error: {e}")
        
        # Create mixed read/write threads
        threads = []
        for i in range(3):
            read_thread = threading.Thread(target=read_coupons)
            write_thread = threading.Thread(target=write_coupon, args=(i,))
            threads.extend([read_thread, write_thread])
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All operations should complete without errors
        self.assertEqual(len(read_results), 3)
        self.assertEqual(len(write_results), 3)
        
        # Check that reads returned valid counts
        for result in read_results:
            self.assertIsInstance(result, int)
            self.assertGreaterEqual(result, 1)  # At least the initial coupon
        
        # Check that writes succeeded
        for result in write_results:
            self.assertTrue(result)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)