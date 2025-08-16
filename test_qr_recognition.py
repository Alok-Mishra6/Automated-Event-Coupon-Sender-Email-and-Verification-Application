#!/usr/bin/env python3
"""
Test script to debug QR code recognition issues
"""

import sys
import json
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from pyzbar import pyzbar

def test_qr_recognition():
    """Test QR code recognition with the existing coupon data"""
    
    print("🔍 Testing QR Code Recognition...")
    
    # Read sample coupon from CSV
    try:
        with open('coupons.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) < 1:
                print("❌ No coupons found in database")
                return
                
            # Parse first coupon
            parts = lines[0].strip().split(',')
            if len(parts) < 4:
                print("❌ Invalid coupon format")
                return
                
            coupon_id = parts[0]
            email = parts[1]
            encrypted_data = parts[2]
            qr_base64 = parts[3]
            
            print(f"📧 Testing coupon for: {email}")
            print(f"🆔 Coupon ID: {coupon_id}")
            print(f"📊 Encrypted data length: {len(encrypted_data)} chars")
            print(f"🖼️ QR code data length: {len(qr_base64)} chars")
            
    except Exception as e:
        print(f"❌ Error reading coupon data: {e}")
        return
    
    # Decode QR code image
    try:
        # Decode base64 image
        image_data = base64.b64decode(qr_base64)
        image = Image.open(BytesIO(image_data))
        
        print(f"🖼️ QR image size: {image.size}")
        print(f"🎨 QR image mode: {image.mode}")
        
        # Convert to OpenCV format
        if image.mode == '1':  # 1-bit pixels, black and white
            image = image.convert('L')  # Convert to grayscale first
        elif image.mode == 'P':  # 8-bit pixels, mapped to any other mode using a color palette
            image = image.convert('RGB')
            
        image_array = np.array(image)
        
        # Handle different image modes
        if len(image_array.shape) == 3:  # RGB
            opencv_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:  # Grayscale
            opencv_image = image_array
        
        # Try to decode with pyzbar
        decoded_objects = pyzbar.decode(opencv_image)
        
        if decoded_objects:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                print(f"✅ QR Data decoded successfully!")
                print(f"📝 QR Data length: {len(qr_data)} chars")
                print(f"📝 QR Data (first 200 chars): {qr_data[:200]}...")
                
                # Try to parse as JSON
                try:
                    parsed_data = json.loads(qr_data)
                    print(f"✅ QR Data is valid JSON:")
                    print(f"   📧 Email: {parsed_data.get('email', 'N/A')}")
                    print(f"   🆔 Coupon ID: {parsed_data.get('coupon_id', 'N/A')}")
                    print(f"   📊 Data length: {len(parsed_data.get('data', ''))}")
                    
                    # Test if the data matches
                    if parsed_data.get('email') == email:
                        print("✅ Email matches!")
                    else:
                        print(f"❌ Email mismatch: {parsed_data.get('email')} vs {email}")
                        
                    if parsed_data.get('coupon_id') == coupon_id:
                        print("✅ Coupon ID matches!")
                    else:
                        print(f"❌ Coupon ID mismatch: {parsed_data.get('coupon_id')} vs {coupon_id}")
                        
                    if parsed_data.get('data') == encrypted_data:
                        print("✅ Encrypted data matches!")
                    else:
                        print("❌ Encrypted data mismatch")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ QR Data is not valid JSON: {e}")
                    print("🔄 Treating as legacy format (encrypted data only)")
                    
        else:
            print("❌ No QR code found in the image")
            
            # Try different decoding strategies
            print("🔄 Trying alternative decoding methods...")
            
            # Convert to grayscale
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            decoded_objects = pyzbar.decode(gray)
            
            if decoded_objects:
                print("✅ Decoded with grayscale conversion!")
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    print(f"📝 QR Data: {qr_data[:200]}...")
            else:
                print("❌ Still no QR code found")
                
                # Try with different image processing
                # Increase contrast
                enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
                decoded_objects = pyzbar.decode(enhanced)
                
                if decoded_objects:
                    print("✅ Decoded with contrast enhancement!")
                    for obj in decoded_objects:
                        qr_data = obj.data.decode('utf-8')
                        print(f"📝 QR Data: {qr_data[:200]}...")
                else:
                    print("❌ No QR code found even with enhancement")
                    
    except Exception as e:
        print(f"❌ Error processing QR image: {e}")
        return
    
    print("\n" + "="*50)
    print("🧪 Testing with Backend Verification...")
    
    # Test backend verification
    try:
        from coupon_manager import CouponManager
        from csv_manager import CSVManager
        
        csv_manager = CSVManager()
        coupon_manager = CouponManager(csv_manager=csv_manager)
        
        print("✅ Backend components loaded")
        
        # Test validation
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode('utf-8')
            try:
                parsed_data = json.loads(qr_data)
                test_email = parsed_data.get('email')
                test_encrypted = parsed_data.get('data')
                
                print(f"🧪 Testing validation with email: {test_email}")
                result = coupon_manager.validate_coupon(test_encrypted, test_email)
                
                if result.get('valid'):
                    print("✅ Backend validation successful!")
                    print(f"   Status: {result}")
                else:
                    print(f"❌ Backend validation failed: {result}")
                    
            except json.JSONDecodeError:
                print("❌ Could not parse QR data for backend test")
        else:
            print("❌ No QR data to test with backend")
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")

if __name__ == "__main__":
    test_qr_recognition()
