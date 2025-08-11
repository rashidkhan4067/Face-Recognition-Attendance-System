#!/usr/bin/env python
"""
Startup script for the Face Recognition Attendance System
"""
import os
import sys
import argparse

def start_server(production=False):
    print("🚀 Starting Face Recognition Attendance System...")
    print("=" * 60)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected!")
        print("Please activate the virtual environment first:")
        print("   face_recognition_env\\Scripts\\activate")
        print("   Then run: python start_server.py")
        return
    
    print("✅ Virtual environment is active")
    
    # Set Django settings
    if production:
        print("🔧 Using production settings")
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_recognition_system.settings_production')
        manage_script = 'manage_production.py'
    else:
        print("🔧 Using development settings")
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_recognition_system.settings')
        manage_script = 'manage.py'
    
    try:
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        from django.urls import reverse
        from django.conf import settings
        
        print("✅ Django configuration loaded")
        
        # Display URL information
        print("\n📋 Available URLs:")
        print(f"   🌐 Root: http://127.0.0.1:8000/ (redirects to login)")
        print(f"   🔐 Login: http://127.0.0.1:8000/auth/login/")
        print(f"   📝 Register: http://127.0.0.1:8000/auth/register/")
        print(f"   📊 Dashboard: http://127.0.0.1:8000/auth/dashboard/ (requires login)")
        print(f"   ⚙️  Admin: http://127.0.0.1:8000/admin/")
        
        if not production:
            print("\n🎯 The login and register pages now have:")
            print("   ✨ Beautiful gradient backgrounds")
            print("   🎨 Modern glass morphism design")
            print("   📱 Mobile responsive layout")
            print("   ⚡ Interactive form validation")
            print("   🔄 Loading animations")
            print("   ♿ Accessibility features")
        
        print("\n" + "=" * 60)
        if production:
            print("🌟 Starting production server...")
            print("⚠️  Note: For production, use a proper WSGI server like Gunicorn")
        else:
            print("🌟 Starting development server...")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Start the development server
        execute_from_command_line([manage_script, 'runserver', '8000'])
        
    except ImportError as e:
        print(f"❌ Error importing Django: {e}")
        print("Please make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    parser = argparse.ArgumentParser(description='Start the Face Recognition Attendance System')
    parser.add_argument('--production', action='store_true', 
                        help='Run with production settings')
    
    args = parser.parse_args()
    start_server(production=args.production)

if __name__ == "__main__":
    main()
