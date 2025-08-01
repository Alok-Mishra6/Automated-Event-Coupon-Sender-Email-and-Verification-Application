"""
Unit tests for the EncryptionService class.
Tests encryption/decryption functionality, timestamp validation, and security features.
"""

import unittest
import os
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from encryption_service import EncryptionService


class TestEncryptionService(unittest.TestCase):
    """Test cases for EncryptionService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_secret_key = "test-secret-key-for-encryption-testing"
        self.test_email = "test@example.com"
        self.test_data = {
            "coupon_id": "test-coupon-123",
            "event_name": "Test Event",
            "value": "50% off"
        }
        self.encryption_service = EncryptionService(self.test_secret_key)
    
    def test_initialization_with_secret_key(self):
        """Test initialization with provided secret key."""
        service = EncryptionService("custom-secret")
        self.assertEqual(service.secret_key, "custom-secret")
    
    @patch.dict(os.environ, {'COUPON_SECRET_KEY': 'env-secret-key'})
    def test_initialization_from_environment(self):
        """Test initialization loading secret key from environment."""
        service = EncryptionService()
        self.assertEqual(service.secret_key, "env-secret-key")
    
    def test_initialization_without_secret_key_raises_error(self):
        """Test that initialization without secret key raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                EncryptionService()
            self.assertIn("Secret key must be provided", str(context.exception))
    
    def test_create_email_hash(self):
        """Test email hash creation."""
        hash1 = self.encryption_service._create_email_hash("test@example.com")
        hash2 = self.encryption_service._create_email_hash("TEST@EXAMPLE.COM")
        hash3 = self.encryption_service._create_email_hash("different@example.com")
        
        # Same email (case insensitive) should produce same hash
        self.assertEqual(hash1, hash2)
        # Different emails should produce different hashes
        self.assertNotEqual(hash1, hash3)
        # Hash should be 16 characters
        self.assertEqual(len(hash1), 16)
    
    def test_derive_key_consistency(self):
        """Test that key derivation is consistent for same email."""
        key1 = self.encryption_service._derive_key(self.test_email)
        key2 = self.encryption_service._derive_key(self.test_email)
        key3 = self.encryption_service._derive_key("different@example.com")
        
        # Same email should produce same key
        self.assertEqual(key1, key2)
        # Different emails should produce different keys
        self.assertNotEqual(key1, key3)
    
    def test_encrypt_coupon_data(self):
        """Test coupon data encryption."""
        encrypted = self.encryption_service.encrypt_coupon_data(self.test_data, self.test_email)
        
        # Should return a base64 encoded string
        self.assertIsInstance(encrypted, str)
        self.assertTrue(len(encrypted) > 0)
        
        # Should be different each time due to Fernet's built-in randomness
        encrypted2 = self.encryption_service.encrypt_coupon_data(self.test_data, self.test_email)
        self.assertNotEqual(encrypted, encrypted2)
    
    def test_decrypt_coupon_data(self):
        """Test coupon data decryption."""
        encrypted = self.encryption_service.encrypt_coupon_data(self.test_data, self.test_email)
        decrypted = self.encryption_service.decrypt_coupon_data(encrypted, self.test_email)
        
        # Original data should be preserved
        for key, value in self.test_data.items():
            self.assertEqual(decrypted[key], value)
        
        # Additional security fields should be present
        self.assertIn('timestamp', decrypted)
        self.assertIn('email_hash', decrypted)
        self.assertIn('email', decrypted)
        self.assertEqual(decrypted['email'], self.test_email.lower())
    
    def test_decrypt_with_wrong_email_fails(self):
        """Test that decryption with wrong email fails."""
        encrypted = self.encryption_service.encrypt_coupon_data(self.test_data, self.test_email)
        
        with self.assertRaises(ValueError) as context:
            self.encryption_service.decrypt_coupon_data(encrypted, "wrong@example.com")
        self.assertIn("Decryption failed", str(context.exception))
    
    def test_decrypt_invalid_data_fails(self):
        """Test that decryption of invalid data fails."""
        with self.assertRaises(ValueError) as context:
            self.encryption_service.decrypt_coupon_data("invalid-encrypted-data", self.test_email)
        self.assertIn("Decryption failed", str(context.exception))
    
    def test_validate_timestamp_recent(self):
        """Test timestamp validation for recent timestamps."""
        # Create data with current timestamp
        data = {'timestamp': datetime.now(timezone.utc).isoformat()}
        self.assertTrue(self.encryption_service.validate_timestamp(data))
    
    def test_validate_timestamp_old(self):
        """Test timestamp validation for old timestamps."""
        # Create data with old timestamp (25 hours ago)
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        data = {'timestamp': old_time.isoformat()}
        self.assertFalse(self.encryption_service.validate_timestamp(data))
    
    def test_validate_timestamp_custom_max_age(self):
        """Test timestamp validation with custom max age."""
        # Create data with timestamp 2 hours ago
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        data = {'timestamp': old_time.isoformat()}
        
        # Should fail with 1 hour max age
        self.assertFalse(self.encryption_service.validate_timestamp(data, max_age_hours=1))
        # Should pass with 3 hour max age
        self.assertTrue(self.encryption_service.validate_timestamp(data, max_age_hours=3))
    
    def test_validate_timestamp_missing(self):
        """Test timestamp validation with missing timestamp."""
        data = {}
        self.assertFalse(self.encryption_service.validate_timestamp(data))
    
    def test_validate_timestamp_invalid_format(self):
        """Test timestamp validation with invalid timestamp format."""
        data = {'timestamp': 'invalid-timestamp'}
        self.assertFalse(self.encryption_service.validate_timestamp(data))
    
    def test_generate_secure_token(self):
        """Test secure token generation."""
        token1 = self.encryption_service.generate_secure_token()
        token2 = self.encryption_service.generate_secure_token()
        
        # Tokens should be different
        self.assertNotEqual(token1, token2)
        # Tokens should be strings
        self.assertIsInstance(token1, str)
        self.assertIsInstance(token2, str)
        # Tokens should have reasonable length
        self.assertTrue(len(token1) > 0)
    
    def test_generate_secure_token_custom_length(self):
        """Test secure token generation with custom length."""
        token = self.encryption_service.generate_secure_token(length=16)
        # Token length should be related to input length (base64 encoding affects final length)
        self.assertTrue(len(token) > 0)
    
    def test_end_to_end_encryption_decryption(self):
        """Test complete encryption/decryption workflow."""
        # Encrypt data
        encrypted = self.encryption_service.encrypt_coupon_data(self.test_data, self.test_email)
        
        # Decrypt data
        decrypted = self.encryption_service.decrypt_coupon_data(encrypted, self.test_email)
        
        # Validate timestamp
        self.assertTrue(self.encryption_service.validate_timestamp(decrypted))
        
        # Verify original data integrity
        for key, value in self.test_data.items():
            self.assertEqual(decrypted[key], value)
    
    def test_case_insensitive_email_handling(self):
        """Test that email handling is case insensitive."""
        # Encrypt with lowercase email
        encrypted = self.encryption_service.encrypt_coupon_data(self.test_data, "test@example.com")
        
        # Should decrypt successfully with uppercase email
        decrypted = self.encryption_service.decrypt_coupon_data(encrypted, "TEST@EXAMPLE.COM")
        
        # Data should be intact
        for key, value in self.test_data.items():
            self.assertEqual(decrypted[key], value)


if __name__ == '__main__':
    unittest.main()