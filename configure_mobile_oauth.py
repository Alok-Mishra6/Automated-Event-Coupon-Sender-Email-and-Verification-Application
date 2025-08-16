#!/usr/bin/env python3
"""
Mobile OAuth Configuration Helper
This script helps configure Google OAuth for mobile device access.
"""

import os
import subprocess
import sys

def get_network_ip():
    """Get the network IP address"""
    try:
        result = subprocess.run([
            'ip', 'addr', 'show'
        ], capture_output=True, text=True)
        
        for line in result.stdout.split('\n'):
            if 'inet ' in line and ('192.168.' in line or '10.' in line or '172.' in line):
                if '127.0.0.1' not in line:
                    ip = line.strip().split()[1].split('/')[0]
                    return ip
    except:
        pass
    
    return None

def main():
    print("🔧 Mobile OAuth Configuration Helper")
    print("=" * 50)
    
    # Get network IP
    network_ip = get_network_ip()
    if not network_ip:
        print("❌ Could not detect network IP address")
        return
    
    print(f"📱 Your network IP: {network_ip}")
    print(f"🌐 Mobile access URL: http://{network_ip}:5000")
    
    print("\n📋 Google OAuth Configuration Required:")
    print("=" * 50)
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Find your OAuth 2.0 Client ID")
    print("3. Click 'Edit' on your OAuth client")
    print("4. In 'Authorized redirect URIs', ADD these URLs:")
    print(f"   • http://localhost:5000/auth/callback")
    print(f"   • http://{network_ip}:5000/auth/callback")
    print("5. Click 'Save'")
    
    print("\n⚠️  Important Notes:")
    print("=" * 50)
    print("• Keep BOTH localhost AND network IP in redirect URIs")
    print("• Make sure your phone is on the same WiFi network")
    print("• Use HTTPS for production (required for camera access)")
    print("• Test on localhost first, then try mobile")
    
    print(f"\n🚀 After configuring OAuth, restart your app:")
    print("   python app.py")
    print(f"\n📱 Then access from your phone:")
    print(f"   http://{network_ip}:5000")
    
    # Update .env file
    env_path = '.env'
    if os.path.exists(env_path):
        print(f"\n🔄 Updating .env file with network IP...")
        
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Update redirect URI to use network IP
        updated_content = content.replace(
            'GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback',
            f'GOOGLE_REDIRECT_URI=http://{network_ip}:5000/auth/callback'
        )
        
        if updated_content != content:
            with open(env_path, 'w') as f:
                f.write(updated_content)
            print("✅ .env file updated with network IP")
        else:
            print("ℹ️  .env file already has correct configuration")

if __name__ == '__main__':
    main()