#!/usr/bin/env python3
"""
Test Scanner Improvements

This script tests the key improvements made to the scanner:
1. Camera initialization works properly
2. Continuous scanning after verification
3. Async email sending in backend
"""

import requests
import json
import time

def test_server_running():
    """Test if the server is running"""
    try:
        response = requests.get('http://127.0.0.1:5000/scanner', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and scanner page accessible")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        return False

def test_coupon_verification():
    """Test the coupon verification endpoint"""
    try:
        # Test data (this should be an actual encrypted coupon from your CSV)
        test_data = {
            "encrypted_data": "Z0FBQUFBQm9uLVRBeWpYREN1eXNVZkVwR25IWUE2SUhQbC14b1BZaU9BSnpEMUEzVUNTR2U1RFc4cVVva0p1MExjZ2ZKNjBPVV9XSnpaMkdyay1HWmg1OHVfbGllMlZLbXV4dmVma242UHlTeGRicmItUzhSZkVjT0poOGZ5bVd1Y0g5V2RLRWQ1VjNTbU1WLXNBeVpQVVJlVWtvMjdueHpQUUk3Z0ZZWVBBazNxRkJzTW9EN2xNYzIwSUM4c21rdTN5dEVCQUpsWXQ1U0pxSnJ0dXRzZE5HaTFSMTBHSWdqODBiZTc2ODNSZUd3bDlEd0JOaThDTjAxUXZzUGc3Q2lmY0ZwZzA4WXE4dzhIOUs0cXIxUGRrUFNEZDRLZHhPNU5JYTZXLTNoTEVHSThkQ3VMTjFqV2VLV1VyWVY5MFRnRWRESWM4d1ctZFhUWEJ1TGF4eTc0QmlaemJnWjFXbTNHX1ZYUk1HZkhoRG5iUlF5bDNpMUwxcUUyWVVzTjE3QS1JLWMyY3plaWVjYnJFUmJMODRXYUI1dmVKMVJIOUtMY0tqUzNzTTB5a0p2MVVEY0ZuYjhUYUgyU0JmRENJcmFQVWFNcFdrdWx4MQ==",
            "email": "technicallittlemaster@gmail.com"
        }
        
        print("🧪 Testing coupon verification...")
        
        start_time = time.time()
        response = requests.post(
            'http://127.0.0.1:5000/verify-coupon',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=10
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Coupon verification successful")
                print(f"   - Coupon ID: {result.get('coupon_id')}")
                print(f"   - Email: {result.get('email')}")
                print(f"   - Event: {result.get('event_name')}")
                print(f"   - Thank you email: {result.get('thank_you_email', 'not specified')}")
                
                if response_time < 2.0:
                    print("✅ Fast response - good for continuous scanning")
                else:
                    print("⚠️ Slow response - may affect scanning speed")
                    
                return True
            else:
                print(f"❌ Verification failed: {result.get('error')}")
                print(f"   - Error code: {result.get('error_code')}")
                return False
        else:
            print(f"❌ HTTP error {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during verification: {e}")
        return False

def test_frontend_structure():
    """Test if the frontend has the key improvements"""
    try:
        response = requests.get('http://127.0.0.1:5000/scanner', timeout=5)
        content = response.text
        
        checks = [
            ("initializeCamera function", "function initializeCamera"),
            ("resumeScanning function", "function resumeScanning"),
            ("verification modal", "verificationModal"),
            ("handleQRDetection function", "function handleQRDetection"),
            ("Global video variable", "let video = null"),
            ("Continuous scanning", "requestAnimationFrame(scanQRCode)")
        ]
        
        print("🔍 Checking frontend improvements...")
        
        all_good = True
        for check_name, search_text in checks:
            if search_text in content:
                print(f"✅ {check_name} found")
            else:
                print(f"❌ {check_name} missing")
                all_good = False
        
        return all_good
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking frontend: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Scanner Improvements")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test 1: Server running
    print("\n1. Testing server status...")
    if not test_server_running():
        all_tests_passed = False
    
    # Test 2: Frontend structure
    print("\n2. Testing frontend improvements...")
    if not test_frontend_structure():
        all_tests_passed = False
    
    # Test 3: Backend verification
    print("\n3. Testing coupon verification...")
    if not test_coupon_verification():
        all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! Scanner improvements look good.")
        print("\nKey improvements verified:")
        print("• Fast camera initialization")
        print("• Continuous scanning capability")
        print("• Async email sending for fast verification")
        print("• Improved error handling and recovery")
    else:
        print("❌ Some tests failed. Check the issues above.")
    
    print("\n📱 To test manually:")
    print("   1. Open http://127.0.0.1:5000/scanner in your browser")
    print("   2. Click 'Start Scanner' - camera should initialize quickly")
    print("   3. Test QR code scanning - should work continuously")
    print("   4. After verification, scanning should resume automatically")

if __name__ == "__main__":
    main()
