#!/usr/bin/env python3
"""
Setup script for Email Coupon System
Creates necessary directories and initializes the system
"""

import os
import secrets
from dotenv import load_dotenv

def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'static/css',
        'static/js',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            # Generate secure keys
            secret_key = secrets.token_urlsafe(32)
            coupon_key = secrets.token_urlsafe(64)
            
            with open('.env.example', 'r') as f:
                content = f.read()
            
            # Replace placeholder values
            content = content.replace('your-secret-key-here-change-in-production', secret_key)
            content = content.replace('your-encryption-secret-key-here-make-it-long-and-random', coupon_key)
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print("✅ Created .env file with generated keys")
            print("⚠️  Please update SMTP settings in .env file before running the application")
        else:
            print("❌ .env.example file not found")
    else:
        print("ℹ️  .env file already exists")

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import flask
        import cryptography
        import qrcode
        import PIL
        from dotenv import load_dotenv
        print("✅ All required modules are available")
        return True
    except ImportError as e:
        print(f"❌ Missing module: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_google_oauth_instructions():
    """Display Google OAuth setup instructions"""
    print("\n🔧 Google OAuth Setup Instructions:")
    print("=" * 50)
    print("To enable Google authentication and Gmail sending:")
    print("\n1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable the following APIs:")
    print("   - Gmail API")
    print("   - Google+ API (for user info)")
    print("\n4. Create OAuth 2.0 credentials:")
    print("   - Go to 'Credentials' → 'Create Credentials' → 'OAuth 2.0 Client ID'")
    print("   - Application type: Web application")
    print("   - Authorized redirect URIs: http://localhost:5000/auth/callback")
    print("\n5. Update your .env file with:")
    print("   GOOGLE_CLIENT_ID=your-client-id-here")
    print("   GOOGLE_CLIENT_SECRET=your-client-secret-here")
    print("\n6. For production, update the redirect URI to your domain")

def main():
    print("🚀 Setting up Email Coupon System with Google OAuth...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Test imports
    if test_imports():
        print("\n✅ Setup completed successfully!")
        
        # Show Google OAuth setup instructions
        setup_google_oauth_instructions()
        
        print("\n🚀 Next steps:")
        print("1. Complete Google OAuth setup (see instructions above)")
        print("2. Add recipient emails to 'responses - Sheet1.csv'")
        print("3. Run: python app.py")
        print("4. Open http://localhost:5000 in your browser")
        print("5. Sign in with your Google account")
        print("6. Send beautiful coupon emails from your Gmail!")
    else:
        print("\n❌ Setup incomplete. Please install requirements first.")

if __name__ == "__main__":
    main()