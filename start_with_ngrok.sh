#!/bin/bash
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
    
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('GOOGLE_REDIRECT_URI='):
            updated_lines.append(f'GOOGLE_REDIRECT_URI=$NGROK_URL/auth/callback')
        else:
            updated_lines.append(line)
    
    with open(env_path, 'w') as f:
        f.write('\n'.join(updated_lines))
    
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
