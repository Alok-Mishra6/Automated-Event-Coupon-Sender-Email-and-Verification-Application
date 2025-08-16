#!/usr/bin/env python3
"""
Ngrok Setup Guide and Configuration Helper
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ngrok is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ ngrok is not installed")
    return False

def install_ngrok_instructions():
    """Provide installation instructions"""
    print("\n📦 INSTALL NGROK:")
    print("=" * 50)
    print("Option 1 - Download directly:")
    print("1. Go to: https://ngrok.com/download")
    print("2. Download Linux 64-bit version")
    print("3. Extract: tar -xzf ngrok-v3-stable-linux-amd64.tgz")
    print("4. Move to PATH: sudo mv ngrok /usr/local/bin/")
    print()
    print("Option 2 - Using snap:")
    print("sudo snap install ngrok")
    print()
    print("Option 3 - Using apt (if available):")
    print("curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null")
    print("echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list")
    print("sudo apt update && sudo apt install ngrok")

def setup_ngrok_config():
    """Create ngrok configuration"""
    print("\n🔧 NGROK SETUP STEPS:")
    print("=" * 50)
    print("1. Sign up at: https://dashboard.ngrok.com/signup")
    print("2. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. Run: ngrok config add-authtoken YOUR_TOKEN_HERE")
    print("4. Start tunnel: ngrok http 5000")
    print("5. Copy the https URL (e.g., https://abc123.ngrok.io)")

def update_env_for_ngrok(ngrok_url):
    """Update .env file with ngrok URL"""
    if not ngrok_url:
        print("\n⚠️  Please provide the ngrok URL to update .env file")
        return
    
    # Read current .env
    env_path = '.env'
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        return
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Update redirect URI
    redirect_uri = f"{ngrok_url}/auth/callback"
    
    # Replace the redirect URI line
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('GOOGLE_REDIRECT_URI='):
            updated_lines.append(f'GOOGLE_REDIRECT_URI={redirect_uri}')
            print(f"✅ Updated redirect URI to: {redirect_uri}")
        else:
            updated_lines.append(line)
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"✅ .env file updated with ngrok URL")

def create_ngrok_startup_script():
    """Create a startup script for ngrok"""
    script_content = '''#!/bin/bash
# Ngrok Startup Script for Event Ticket System

echo "🚀 Starting Event Ticket System with ngrok"
echo "=" * 50

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed. Please install it first."
    exit 1
fi

# Start ngrok in background
echo "🌐 Starting ngrok tunnel..."
ngrok http 5000 --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 3

# Get the public URL
echo "🔍 Getting ngrok URL..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for tunnel in data['tunnels']:
        if tunnel['proto'] == 'https':
            print(tunnel['public_url'])
            break
except:
    pass
")

if [ -z "$NGROK_URL" ]; then
    echo "❌ Could not get ngrok URL. Check ngrok.log for errors."
    kill $NGROK_PID 2>/dev/null
    exit 1
fi

echo "✅ ngrok tunnel active: $NGROK_URL"
echo "📱 Mobile access: $NGROK_URL"
echo "🔧 Admin access: $NGROK_URL"

# Update .env file
python3 -c "
import os
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('GOOGLE_REDIRECT_URI='):
            updated_lines.append(f'GOOGLE_REDIRECT_URI=$NGROK_URL/auth/callback')
        else:
            updated_lines.append(line)
    
    with open(env_path, 'w') as f:
        f.write('\\n'.join(updated_lines))
    
    print('✅ Updated .env with ngrok URL')
"

echo ""
echo "📋 NEXT STEPS:"
echo "1. Update Google Console with: $NGROK_URL/auth/callback"
echo "2. Start your Flask app: python app.py"
echo "3. Access from any device: $NGROK_URL"
echo ""
echo "Press Ctrl+C to stop ngrok tunnel"

# Keep script running
trap "echo '🛑 Stopping ngrok...'; kill $NGROK_PID 2>/dev/null; exit 0" INT
wait $NGROK_PID
'''
    
    with open('start_with_ngrok.sh', 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod('start_with_ngrok.sh', 0o755)
    print("✅ Created start_with_ngrok.sh script")

def main():
    print("🌐 Ngrok Setup for Event Ticket System")
    print("=" * 60)
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        install_ngrok_instructions()
        print("\n⚠️  Please install ngrok first, then run this script again")
        return
    
    # Create startup script
    create_ngrok_startup_script()
    
    print("\n🚀 USAGE INSTRUCTIONS:")
    print("=" * 60)
    print("1. Install ngrok (if not done already)")
    print("2. Get authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. Run: ngrok config add-authtoken YOUR_TOKEN")
    print("4. Run: ./start_with_ngrok.sh")
    print("5. Update Google Console with the provided URL")
    print("6. Start your Flask app: python app.py")
    print("7. Access from mobile: use the ngrok URL")
    
    print("\n📱 BENEFITS OF NGROK:")
    print("=" * 60)
    print("✅ Public HTTPS URL (works with Google OAuth)")
    print("✅ Mobile camera access (HTTPS required)")
    print("✅ Access from anywhere on internet")
    print("✅ No firewall/network configuration needed")
    print("✅ Automatic SSL certificate")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("=" * 60)
    print("• Free ngrok URLs change on restart")
    print("• Update Google Console each time URL changes")
    print("• Keep ngrok running while using the system")
    print("• For production, consider ngrok paid plan for static URLs")

if __name__ == '__main__':
    main()