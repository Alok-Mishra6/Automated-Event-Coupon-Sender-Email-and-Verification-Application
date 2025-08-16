#!/usr/bin/env python3
"""
OAuth Mobile Fix - Comprehensive solution for mobile authentication
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def get_network_ip():
    """Get the current network IP"""
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

def main():
    print("🔧 OAuth Mobile Authentication Fix")
    print("=" * 50)
    
    load_dotenv()
    
    # Get current configuration
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    network_ip = get_network_ip()
    
    if not client_id:
        print("❌ GOOGLE_CLIENT_ID not found in .env file")
        return
    
    if not network_ip:
        print("❌ Could not detect network IP")
        return
    
    print(f"📱 Network IP: {network_ip}")
    print(f"🔑 Client ID: {client_id}")
    
    print("\n🎯 CRITICAL FIX NEEDED:")
    print("=" * 50)
    print("The OAuth error occurs because your Google Cloud Console")
    print("redirect URIs don't match what the app is sending.")
    
    print("\n📋 STEP-BY-STEP FIX:")
    print("=" * 50)
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print(f"2. Find OAuth Client: {client_id}")
    print("3. Click 'EDIT' (pencil icon)")
    print("4. In 'Authorized redirect URIs', REPLACE with these EXACT URLs:")
    print("   ❌ Remove any existing URLs")
    print("   ✅ Add: http://localhost:5000/auth/callback")
    print(f"   ✅ Add: http://{network_ip}:5000/auth/callback")
    print("5. Click 'SAVE' and wait 5-10 minutes for changes to propagate")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("=" * 50)
    print("• The URLs must match EXACTLY (no trailing slashes)")
    print("• Both localhost AND network IP are required")
    print("• Changes can take 5-10 minutes to take effect")
    print("• Clear your browser cache after making changes")
    
    print("\n🧪 TESTING STEPS:")
    print("=" * 50)
    print("1. After updating Google Console, wait 5-10 minutes")
    print("2. Clear browser cache on your phone")
    print("3. Test localhost first: http://localhost:5000")
    print(f"4. Then test mobile: http://{network_ip}:5000")
    
    # Create a test script
    print("\n🔍 Creating OAuth test script...")
    
    test_script = f'''#!/usr/bin/env python3
"""OAuth Configuration Test"""

import requests
import os
from dotenv import load_dotenv

def test_oauth_endpoints():
    load_dotenv()
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    network_ip = "{network_ip}"
    
    print("🧪 Testing OAuth Endpoints...")
    print("-" * 40)
    
    # Test URLs that should be in Google Console
    test_urls = [
        "http://localhost:5000/auth/callback",
        f"http://{{network_ip}}:5000/auth/callback"
    ]
    
    print("✅ These URLs should be in your Google Console:")
    for url in test_urls:
        print(f"   • {{url}}")
    
    print("\\n🔗 OAuth Authorization URL:")
    auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={{client_id}}&redirect_uri=http://{{network_ip}}:5000/auth/callback&scope=openid%20email%20profile%20https://www.googleapis.com/auth/gmail.send&response_type=code&access_type=offline&prompt=consent"
    print(f"   {{auth_url}}")
    
    print("\\n📱 Test this URL on your phone after updating Google Console!")

if __name__ == '__main__':
    test_oauth_endpoints()
'''
    
    with open('test_oauth.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created test_oauth.py - run this after updating Google Console")
    
    print(f"\n🚀 AFTER FIXING GOOGLE CONSOLE:")
    print("=" * 50)
    print("1. Wait 5-10 minutes for changes to propagate")
    print("2. Run: python test_oauth.py")
    print("3. Clear browser cache on your phone")
    print("4. Test mobile access again")
    
    print(f"\n📱 Mobile URL: http://{network_ip}:5000")

if __name__ == '__main__':
    main()