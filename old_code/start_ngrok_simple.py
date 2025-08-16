#!/usr/bin/env python3
"""
Simple ngrok starter for the event system
"""

import subprocess
import time
import requests
import json
import os

def start_ngrok():
    """Start ngrok and get the public URL"""
    print("🌐 Starting ngrok tunnel...")
    
    # Start ngrok
    try:
        process = subprocess.Popen(['ngrok', 'http', '5000'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for ngrok to start
        print("⏳ Waiting for ngrok to initialize...")
        time.sleep(5)
        
        # Get the tunnel URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            data = response.json()
            
            https_url = None
            for tunnel in data.get('tunnels', []):
                if tunnel.get('proto') == 'https':
                    https_url = tunnel.get('public_url')
                    break
            
            if https_url:
                print(f"✅ ngrok tunnel active!")
                print(f"🔗 Public URL: {https_url}")
                print(f"📱 Mobile access: {https_url}")
                
                # Update .env file
                update_env_file(https_url)
                
                print(f"\n📋 NEXT STEPS:")
                print(f"1. Update Google Console redirect URI:")
                print(f"   {https_url}/auth/callback")
                print(f"2. Start your Flask app: python app.py")
                print(f"3. Access from mobile: {https_url}")
                print(f"\n⚠️  Keep this terminal open to maintain the tunnel!")
                
                # Keep running
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping ngrok...")
                    process.terminate()
                    
            else:
                print("❌ Could not get ngrok URL")
                process.terminate()
                
        except requests.exceptions.RequestException:
            print("❌ Could not connect to ngrok API")
            print("💡 Make sure ngrok is properly authenticated")
            print("   Run: ngrok config add-authtoken YOUR_TOKEN")
            process.terminate()
            
    except FileNotFoundError:
        print("❌ ngrok not found")
        print("📦 Install ngrok from: https://ngrok.com/download")

def update_env_file(ngrok_url):
    """Update .env file with ngrok URL"""
    env_path = '.env'
    if not os.path.exists(env_path):
        print("⚠️  .env file not found")
        return
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Update redirect URI
        redirect_uri = f"{ngrok_url}/auth/callback"
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('GOOGLE_REDIRECT_URI='):
                updated_lines.append(f'GOOGLE_REDIRECT_URI={redirect_uri}')
            else:
                updated_lines.append(line)
        
        with open(env_path, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"✅ Updated .env with redirect URI: {redirect_uri}")
        
    except Exception as e:
        print(f"⚠️  Could not update .env file: {e}")

def main():
    print("🚀 Event Ticket System - ngrok Setup")
    print("=" * 50)
    
    # Check if ngrok is authenticated
    print("🔍 Checking ngrok authentication...")
    
    start_ngrok()

if __name__ == '__main__':
    main()