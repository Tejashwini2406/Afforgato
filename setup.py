#!/usr/bin/env python3
"""
Afforgato Cafe Setup Script
This script helps set up the database and initial data for the Afforgato Cafe application.
"""

import os
import sys
import subprocess
from werkzeug.security import generate_password_hash

def print_banner():
    """Print the setup banner"""
    print("=" * 60)
    print("🍵 AFFORGATO CAFE SETUP 🍵")
    print("=" * 60)
    print("Setting up your cafe order system...")
    print()

def check_requirements():
    """Check if required packages are installed"""
    print("📋 Checking requirements...")
    
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import pymysql
        print("✅ All Python packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_mariadb():
    """Check if MariaDB is accessible"""
    print("🗄️ Checking MariaDB connection...")
    
    try:
        import pymysql
        
        # Try to connect to MariaDB
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',  # Default empty password
            charset='utf8mb4'
        )
        connection.close()
        print("✅ MariaDB connection successful")
        return True
    except Exception as e:
        print(f"❌ MariaDB connection failed: {e}")
        print("Please ensure MariaDB is running and accessible")
        return False

def create_database():
    """Create the database and tables"""
    print("🏗️ Creating database and tables...")
    
    try:
        import pymysql
        
        # Read the SQL file
        with open('database.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split SQL commands
        sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        # Connect and execute
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        for command in sql_commands:
            if command:
                cursor.execute(command)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Database and tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def create_env_file():
    """Create a .env file with default configuration"""
    print("⚙️ Creating environment configuration...")
    
    env_content = """# Afforgato Cafe Environment Configuration
SECRET_KEY=afforgato-cafe-secret-key-2024
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=afforgato_cafe
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Environment file created (.env)")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def generate_demo_passwords():
    """Generate password hashes for demo accounts"""
    print("🔐 Generating demo account passwords...")
    
    admin_hash = generate_password_hash('admin123')
    demo_hash = generate_password_hash('demo123')
    
    print(f"Admin password hash: {admin_hash}")
    print(f"Demo password hash: {demo_hash}")
    print("✅ Demo passwords generated")
    
    return admin_hash, demo_hash

def run_flask_app():
    """Start the Flask application"""
    print("🚀 Starting Flask application...")
    print("The application will be available at: http://localhost:5000")
    print()
    print("Demo Accounts:")
    print("👨‍💼 Admin: username='admin', password='admin123'")
    print("👤 User: username='demo', password='demo123'")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        os.system('python app.py')
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thank you for using Afforgato Cafe!")

def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check MariaDB
    if not check_mariadb():
        print("\n💡 Tips for MariaDB setup:")
        print("1. Install MariaDB: https://mariadb.org/download/")
        print("2. Start MariaDB service")
        print("3. Ensure root user has no password (default)")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        sys.exit(1)
    
    # Create database
    if not create_database():
        sys.exit(1)
    
    # Generate demo passwords
    generate_demo_passwords()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5000")
    print("3. Login with demo accounts")
    print()
    
    # Ask if user wants to start the app
    start_app = input("Would you like to start the application now? (y/n): ").lower().strip()
    if start_app in ['y', 'yes']:
        run_flask_app()
    else:
        print("👍 You can start the application later with: python app.py")

if __name__ == "__main__":
    main()
