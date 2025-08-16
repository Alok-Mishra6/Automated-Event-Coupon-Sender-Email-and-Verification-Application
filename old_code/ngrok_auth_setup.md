# 🌐 Ngrok Authentication Setup

## Step 1: Get Your Ngrok Auth Token

1. **Go to**: https://dashboard.ngrok.com/signup
2. **Sign up** for a free account (or login if you have one)
3. **Go to**: https://dashboard.ngrok.com/get-started/your-authtoken
4. **Copy your authtoken** (looks like: `2abc123def456ghi789jkl`)

## Step 2: Configure Ngrok

Run this command with your actual token:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Example:
```bash
ngrok config add-authtoken 2abc123def456ghi789jkl
```

## Step 3: Start Ngrok Tunnel

```bash
python start_ngrok_simple.py
```

This will:
- Start ngrok tunnel on port 5000
- Get the public HTTPS URL
- Update your .env file automatically
- Show you the next steps

## Step 4: Update Google Console

1. **Go to**: https://console.cloud.google.com/apis/credentials
2. **Find your OAuth client**: `828548429562-0mdeb99fn0rh6ov6f25lvoq0he0e4qtc.apps.googleusercontent.com`
3. **Click "Edit"**
4. **In "Authorized redirect URIs", replace with**:
   - `https://YOUR-NGROK-URL.ngrok.io/auth/callback`
   - (The script will show you the exact URL)
5. **Click "Save"**

## Step 5: Start Your App

In a **new terminal**:
```bash
python app.py
```

## Step 6: Test Mobile Access

**On your phone**:
- Open: `https://YOUR-NGROK-URL.ngrok.io`
- Login with Google (should work now!)
- Complete device registration
- Start scanning tickets!

## 🎯 Benefits of This Setup

✅ **Public HTTPS URL** - Works with Google OAuth
✅ **Mobile Camera Access** - HTTPS enables camera
✅ **Access from Anywhere** - Not limited to local network
✅ **SSL Certificate** - Automatic HTTPS encryption
✅ **No Network Config** - Bypasses firewalls/routers

## ⚠️ Important Notes

- **Keep ngrok running** - Don't close the terminal
- **Free URLs change** - Each restart gives new URL
- **Update Google Console** - When URL changes
- **For production** - Consider ngrok paid plan for static URLs

## 🔧 Troubleshooting

**If ngrok fails to start:**
1. Check if you added the authtoken correctly
2. Make sure port 5000 isn't already in use
3. Try: `ngrok http 5000` manually first

**If OAuth still fails:**
1. Wait 5-10 minutes after updating Google Console
2. Clear browser cache
3. Make sure the redirect URI matches exactly