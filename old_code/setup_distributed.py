#!/usr/bin/env python3
"""
Setup script for distributed event ticket system.
Handles database setup, Redis configuration, and multi-device deployment.
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def run_command(command, description=""):
    """Run a command and handle errors"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error {description}: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_dependencies():
    """Check if required system dependencies are installed"""
    print_step("1", "Checking System Dependencies")
    
    dependencies = {
        'python3': 'Python 3.8+',
        'pip': 'Python package manager',
        'psql': 'PostgreSQL client (optional for database setup)',
        'redis-cli': 'Redis client (optional for Redis setup)'
    }
    
    missing = []
    for cmd, desc in dependencies.items():
        if not run_command(f"which {cmd}", f"checking {desc}"):
            missing.append(f"{cmd} ({desc})")
    
    if missing:
        print(f"⚠️  Missing optional dependencies: {', '.join(missing)}")
        print("The system will work without them, but setup may require manual configuration.")
    else:
        print("✅ All system dependencies found")

def install_python_dependencies():
    """Install Python dependencies"""
    print_step("2", "Installing Python Dependencies")
    
    if run_command("pip install -r requirements.txt", "installing Python packages"):
        print("✅ Python dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install Python dependencies")
        return False

def setup_environment():
    """Set up environment variables"""
    print_step("3", "Setting Up Environment Configuration")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("ℹ️  .env file already exists")
        response = input("Do you want to update it? (y/N): ").lower()
        if response != 'y':
            return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    # Read template
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Generate secure keys
    secret_key = secrets.token_urlsafe(32)
    coupon_key = secrets.token_urlsafe(64)
    
    # Replace placeholder values
    content = content.replace('your-secret-key-here-change-in-production', secret_key)
    content = content.replace('your-encryption-secret-key-here-make-it-long-and-random', coupon_key)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Environment file created with secure keys")
    print("⚠️  Please update the following in .env:")
    print("   - GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
    print("   - DATABASE_URL (if using PostgreSQL)")
    print("   - REDIS_URL (if using Redis)")
    
    return True

def setup_database():
    """Set up PostgreSQL database"""
    print_step("4", "Database Setup")
    
    print("Choose database option:")
    print("1. Use CSV files (single device, simple setup)")
    print("2. Set up PostgreSQL (multi-device, distributed)")
    print("3. Skip database setup (configure manually)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        print("✅ Using CSV files - no additional setup needed")
        print("Note: This limits you to single-device operation")
        return True
    
    elif choice == "2":
        print("Setting up PostgreSQL for distributed operation...")
        
        # Check if PostgreSQL is available
        if not run_command("which psql", "checking PostgreSQL"):
            print("❌ PostgreSQL not found. Please install PostgreSQL first:")
            print("   Ubuntu/Debian: sudo apt install postgresql postgresql-contrib")
            print("   macOS: brew install postgresql")
            print("   Windows: Download from https://www.postgresql.org/download/")
            return False
        
        # Create database
        db_name = "event_tickets"
        print(f"Creating database: {db_name}")
        
        if run_command(f'sudo -u postgres createdb {db_name}', "creating database"):
            print(f"✅ Database '{db_name}' created successfully")
        else:
            print("⚠️  Database creation failed - it may already exist")
        
        # Create user (optional)
        print("Database setup completed. Update DATABASE_URL in .env file.")
        return True
    
    else:
        print("⚠️  Database setup skipped - configure manually")
        return True

def setup_redis():
    """Set up Redis for real-time features"""
    print_step("5", "Redis Setup (Optional)")
    
    print("Redis enables real-time synchronization across multiple devices.")
    print("Choose Redis option:")
    print("1. Skip Redis (basic functionality only)")
    print("2. Use local Redis (install if needed)")
    print("3. Use cloud Redis (configure manually)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        print("⚠️  Redis skipped - real-time features will be limited")
        return True
    
    elif choice == "2":
        print("Setting up local Redis...")
        
        # Check if Redis is available
        if not run_command("which redis-server", "checking Redis"):
            print("❌ Redis not found. Please install Redis first:")
            print("   Ubuntu/Debian: sudo apt install redis-server")
            print("   macOS: brew install redis")
            print("   Windows: Use Docker or WSL")
            return False
        
        # Start Redis
        if run_command("redis-cli ping", "testing Redis connection"):
            print("✅ Redis is running and accessible")
        else:
            print("Starting Redis server...")
            if run_command("sudo systemctl start redis", "starting Redis"):
                print("✅ Redis started successfully")
            else:
                print("⚠️  Could not start Redis automatically")
                print("Please start Redis manually: sudo systemctl start redis")
        
        return True
    
    else:
        print("⚠️  Using cloud Redis - update REDIS_URL in .env file")
        return True

def create_directories():
    """Create necessary directories"""
    print_step("6", "Creating Directory Structure")
    
    directories = [
        'uploads',
        'logs',
        'backups',
        'static/css',
        'static/js',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_system():
    """Test the system components"""
    print_step("7", "Testing System Components")
    
    try:
        # Test imports
        print("Testing Python imports...")
        import flask
        import psycopg2
        import redis
        import flask_socketio
        print("✅ All required packages imported successfully")
        
        # Test database connection (if configured)
        try:
            from database_models import DatabaseManager
            print("✅ Database models loaded successfully")
        except Exception as e:
            print(f"⚠️  Database connection test skipped: {e}")
        
        # Test encryption service
        try:
            from encryption_service import EncryptionService
            encryption = EncryptionService('test-key')
            test_data = {'test': 'data'}
            encrypted = encryption.encrypt_coupon_data(test_data, 'test@example.com')
            decrypted = encryption.decrypt_coupon_data(encrypted, 'test@example.com')
            assert decrypted['test'] == 'data'
            print("✅ Encryption service working correctly")
        except Exception as e:
            print(f"❌ Encryption service test failed: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def print_deployment_guide():
    """Print deployment guide"""
    print_header("🚀 DEPLOYMENT GUIDE")
    
    print("""
📋 SINGLE DEVICE DEPLOYMENT (Simple):
1. Keep CSV-based storage (current setup)
2. Run: python app.py
3. Access: http://localhost:5000
4. Perfect for small events with 1-2 staff members

📋 MULTI-DEVICE DEPLOYMENT (Distributed):
1. Set up PostgreSQL database
2. Configure Redis for real-time sync
3. Update .env with database and Redis URLs
4. Run: python app.py
5. Each device accesses the same URL
6. Perfect for large events with multiple staff

📋 PRODUCTION DEPLOYMENT:
1. Use a production WSGI server: gunicorn app:app
2. Set up reverse proxy (Nginx)
3. Use managed database (AWS RDS, Google Cloud SQL)
4. Use managed Redis (AWS ElastiCache, Redis Cloud)
5. Enable HTTPS for OAuth and camera access
6. Set up monitoring and logging

📋 CLOUD DEPLOYMENT OPTIONS:
- Heroku: Easy deployment with add-ons
- AWS: EC2 + RDS + ElastiCache
- Google Cloud: App Engine + Cloud SQL + Memorystore
- DigitalOcean: Droplets + Managed Databases
- Docker: Containerized deployment anywhere

📋 NETWORK SETUP FOR EVENTS:
- Ensure all devices are on the same network
- Use a reliable WiFi connection
- Consider mobile hotspot backup
- Test connectivity before the event
- Have offline backup procedures ready
""")

def main():
    """Main setup function"""
    print_header("🎫 EVENT TICKET SYSTEM - DISTRIBUTED SETUP")
    
    print("""
This setup script will help you configure the Event Ticket Management System
for either single-device or multi-device distributed operation.

Choose your deployment type:
- Single Device: Simple CSV-based storage, one person checking tickets
- Multi-Device: PostgreSQL + Redis, multiple staff members with real-time sync
""")
    
    # Check dependencies
    check_dependencies()
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Setup failed at dependency installation")
        return False
    
    # Set up environment
    if not setup_environment():
        print("❌ Setup failed at environment configuration")
        return False
    
    # Set up database
    if not setup_database():
        print("❌ Setup failed at database configuration")
        return False
    
    # Set up Redis
    setup_redis()
    
    # Create directories
    create_directories()
    
    # Test system
    if not test_system():
        print("❌ System tests failed")
        return False
    
    # Print deployment guide
    print_deployment_guide()
    
    print_header("✅ SETUP COMPLETED SUCCESSFULLY!")
    
    print("""
🎉 Your Event Ticket Management System is ready!

NEXT STEPS:
1. Configure Google OAuth credentials in .env
2. Update database/Redis URLs if using distributed mode
3. Add attendee emails to CSV or database
4. Run: python app.py
5. Access: http://localhost:5000

For distributed deployment:
- Each staff device should access the same server URL
- All devices will sync in real-time
- Monitor the admin dashboard for device activity

Need help? Check the README.md or CONTRIBUTING.md files.
""")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during setup: {e}")
        sys.exit(1)