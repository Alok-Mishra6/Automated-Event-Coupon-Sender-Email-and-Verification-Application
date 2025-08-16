#!/usr/bin/env python3
"""OAuth Configuration Test"""

import requests
import os
from dotenv import load_dotenv

def test_oauth_endpoints():
    load_dotenv()
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    network_ip = "172.24.154.140"
    
    print("🧪 Testing OAuth Endpoints...")
    print("-" * 40)
    
    # Test URLs that should be in Google Console
    test_urls = [
        "http://localhost:5000/auth/callback",
        f"http://{network_ip}:5000/auth/callback"
    ]
    
    print("✅ These URLs should be in your Google Console:")
    for url in test_urls:
        print(f"   • {url}")
    
    print("\n🔗 OAuth Authorization URL:")
    auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={client_id}&redirect_uri=http://{network_ip}:5000/auth/callback&scope=openid%20email%20profile%20https://www.googleapis.com/auth/gmail.send&response_type=code&access_type=offline&prompt=consent"
    print(f"   {auth_url}")
    
    print("\n📱 Test this URL on your phone after updating Google Console!")

if __name__ == '__main__':
    test_oauth_endpoints()
