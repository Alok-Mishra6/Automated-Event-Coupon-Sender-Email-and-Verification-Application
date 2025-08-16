#!/usr/bin/env python3
"""
Mobile OAuth Solutions - Multiple approaches to fix Google OAuth on mobile
"""

import os
import subprocess
import sys

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

def main():
    print("🔧 Mobile OAuth Solutions")
    print("=" * 60)
    
    network_ip = get_network_ip()
    print(f"📱 Your network IP: {network_ip}")
    
    print("\n❌ THE PROBLEM:")
    print("-" * 60)
    print("Google OAuth doesn't allow private IP addresses (192.168.x.x, 10.x.x.x, 172.x.x.x)")
    print("as redirect URIs. They must use public domains (.com, .org, etc.)")
    
    print("\n✅ SOLUTION OPTIONS:")
    print("=" * 60)
    
    print("\n🎯 OPTION 1: Use ngrok (RECOMMENDED - Quick & Easy)")
    print("-" * 60)
    print("ngrok creates a public tunnel to your local server")
    print("Steps:")
    print("1. Install ngrok: https://ngrok.com/download")
    print("2. Run: ngrok http 5000")
    print("3. Copy the https URL (e.g., https://abc123.ngrok.io)")
    print("4. Add to Google Console: https://abc123.ngrok.io/auth/callback")
    print("5. Update .env: GOOGLE_REDIRECT_URI=https://abc123.ngrok.io/auth/callback")
    print("6. Access from phone: https://abc123.ngrok.io")
    print("✅ Pros: Works immediately, HTTPS included, mobile camera access")
    print("❌ Cons: URL changes each restart (free version)")
    
    print("\n🎯 OPTION 2: Use localhost.run (Free Alternative)")
    print("-" * 60)
    print("Another tunneling service, no installation required")
    print("Steps:")
    print("1. Run: ssh -R 80:localhost:5000 nokey@localhost.run")
    print("2. Copy the provided URL")
    print("3. Add to Google Console as redirect URI")
    print("4. Update .env with the new URL")
    print("✅ Pros: No installation, free")
    print("❌ Cons: Less reliable than ngrok")
    
    print("\n🎯 OPTION 3: Disable OAuth for Scanner (Quick Fix)")
    print("-" * 60)
    print("Make scanner work without Google authentication")
    print("Steps:")
    print("1. Modify scanner to work without login")
    print("2. Keep admin features with OAuth on localhost")
    print("3. Staff can scan tickets without Google login")
    print("✅ Pros: Works immediately, no external dependencies")
    print("❌ Cons: No real-time sync, less secure")
    
    print("\n🎯 OPTION 4: Use a Custom Domain (Advanced)")
    print("-" * 60)
    print("Set up a domain that points to your local IP")
    print("Steps:")
    print("1. Buy a domain (e.g., myevent.com)")
    print("2. Set up DNS to point to your local IP")
    print("3. Use domain in Google Console")
    print("✅ Pros: Professional, permanent solution")
    print("❌ Cons: Costs money, more complex setup")
    
    print("\n🚀 RECOMMENDED QUICK FIX:")
    print("=" * 60)
    print("Use ngrok for immediate testing:")
    print("1. Download ngrok: https://ngrok.com/download")
    print("2. Run: ./ngrok http 5000")
    print("3. Use the https URL for Google OAuth")
    print("4. Mobile users access the ngrok URL")
    
    print(f"\n📋 Current Status:")
    print("-" * 60)
    print(f"• Local access: http://localhost:5000 ✅")
    print(f"• Network access: http://{network_ip}:5000 ❌ (OAuth blocked)")
    print("• Need public domain for mobile OAuth")

if __name__ == '__main__':
    main()