#!/usr/bin/env python3
"""
Mobile Access Diagnostic Tool
"""

import requests
import socket
import subprocess
import os
from dotenv import load_dotenv

def test_network_connectivity():
    """Test if the server is accessible from network"""
    print("🌐 Testing Network Connectivity...")
    print("-" * 40)
    
    # Get network IP
    try:
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'inet ' in line and ('192.168.' in line or '10.' in line or '172.' in line):
                if '127.0.0.1' not in line:
                    ip = line.strip().split()[1].split('/')[0]
                    print(f"📱 Network IP: {ip}")
                    break
    except:
        print("❌ Could not get network IP")
        return False
    
    # Test if port 5000 is accessible
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, 5000))
        sock.close()
        
        if result == 0:
            print("✅ Port 5000 is accessible on network")
            return True
        else:
            print("❌ Port 5000 is not accessible on network")
            return False
    except Exception as e:
        print(f"❌ Network test failed: {e}")
        return False

def test_oauth_config():
    """Test OAuth configuration"""
    print("\n🔐 Testing OAuth Configuration...")
    print("-" * 40)
    
    load_dotenv()
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    
    if not client_id:
        print("❌ GOOGLE_CLIENT_ID not set")
        return False
    
    if not client_secret:
        print("❌ GOOGLE_CLIENT_SECRET not set")
        return False
    
    if not redirect_uri:
        print("❌ GOOGLE_REDIRECT_URI not set")
        return False
    
    print(f"✅ Client ID: {client_id}")
    print(f"✅ Client Secret: {'*' * len(client_secret)}")
    print(f"✅ Redirect URI: {redirect_uri}")
    
    # Check if redirect URI uses network IP
    if 'localhost' in redirect_uri:
        print("⚠️  Warning: Redirect URI uses localhost (won't work on mobile)")
        return False
    
    return True

def test_app_startup():
    """Test if the app can start"""
    print("\n🚀 Testing App Startup...")
    print("-" * 40)
    
    try:
        from app import app
        print("✅ Flask app imports successfully")
        
        # Test database connection
        from database_models import DatabaseManager
        db = DatabaseManager()
        print("✅ Database connection works")
        
        # Test Redis connection
        import redis
        r = redis.from_url('redis://localhost:6379/0')
        r.ping()
        print("✅ Redis connection works")
        
        return True
        
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

def main():
    print("🔍 Mobile Access Diagnostic Tool")
    print("=" * 50)
    
    network_ok = test_network_connectivity()
    oauth_ok = test_oauth_config()
    app_ok = test_app_startup()
    
    print("\n📋 Diagnostic Summary:")
    print("=" * 50)
    print(f"Network Access: {'✅ OK' if network_ok else '❌ FAILED'}")
    print(f"OAuth Config: {'✅ OK' if oauth_ok else '❌ FAILED'}")
    print(f"App Startup: {'✅ OK' if app_ok else '❌ FAILED'}")
    
    if network_ok and oauth_ok and app_ok:
        print("\n🎉 All tests passed! Mobile access should work.")
        print("\n📱 Next steps:")
        print("1. Make sure you updated Google OAuth redirect URIs")
        print("2. Restart the app: python app.py")
        print("3. Access from phone: http://172.24.154.140:5000")
    else:
        print("\n❌ Some tests failed. Check the issues above.")

if __name__ == '__main__':
    main()