#!/usr/bin/env python3
"""
Mobile OAuth Testing Script
"""

import requests
import subprocess
import time

def get_network_ip():
    """Get network IP"""
    try:
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'inet ' in line and ('192.168.' in line or '10.' in line or '172.' in line):
                if '127.0.0.1' not in line:
                    ip = line.strip().split()[1].split('/')[0]
                    return ip
    except:
        pass
    return None

def test_app_endpoints():
    """Test if app endpoints are working"""
    network_ip = get_network_ip()
    if not network_ip:
        print("❌ Could not get network IP")
        return False
    
    print(f"🌐 Testing endpoints for IP: {network_ip}")
    print("-" * 50)
    
    # Test endpoints
    endpoints = [
        f"http://localhost:5000/",
        f"http://{network_ip}:5000/",
        f"http://localhost:5000/scanner",
        f"http://{network_ip}:5000/scanner"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"⚠️  {response.status_code}"
            print(f"{status} - {endpoint}")
        except requests.exceptions.RequestException as e:
            print(f"❌ FAILED - {endpoint} - {str(e)}")
    
    return True

def main():
    print("📱 Mobile OAuth Testing")
    print("=" * 50)
    
    network_ip = get_network_ip()
    if not network_ip:
        print("❌ Could not detect network IP")
        return
    
    print(f"📍 Your network IP: {network_ip}")
    
    # Test app endpoints
    test_app_endpoints()
    
    print("\n🔧 Google Console Configuration:")
    print("-" * 50)
    print("Make sure these EXACT URLs are in your Google Console:")
    print(f"✅ http://localhost:5000/auth/callback")
    print(f"✅ http://{network_ip}:5000/auth/callback")
    
    print("\n📱 Mobile Testing Steps:")
    print("-" * 50)
    print("1. Update Google Console with the URLs above")
    print("2. Wait 5-10 minutes for changes to propagate")
    print("3. Clear browser cache on your phone")
    print(f"4. Open: http://{network_ip}:5000")
    print("5. Click 'Login with Google'")
    print("6. Complete authentication")
    print("7. You should see the device registration modal")
    
    print("\n🎯 Expected Flow:")
    print("-" * 50)
    print("1. Phone opens scanner page")
    print("2. Device registration modal appears")
    print("3. Fill in: Staff Email, Device Name, Event Name")
    print("4. Click 'Register Device'")
    print("5. Scanner becomes fully functional")
    
    print(f"\n🚀 Ready to test: http://{network_ip}:5000")

if __name__ == '__main__':
    main()