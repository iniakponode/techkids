#!/usr/bin/env python3
"""
Production Database Configuration Diagnostic
Run this script on your production server to debug the database connection issue.
"""

import os
import sys
from pathlib import Path

print("🔍 TechKids Database Configuration Diagnostic")
print("=" * 50)

# 1. Check current working directory
print(f"📁 Current working directory: {os.getcwd()}")
print(f"📁 Script location: {Path(__file__).resolve().parent}")

# 2. Check environment variables
print("\n🌍 Environment Variables:")
database_url = os.getenv("DATABASE_URL")
environment = os.getenv("ENVIRONMENT")

print(f"DATABASE_URL: {database_url}")
print(f"ENVIRONMENT: {environment}")

if database_url:
    if "mysql" in database_url.lower():
        print("✅ DATABASE_URL points to MySQL - CORRECT")
    elif "sqlite" in database_url.lower():
        print("⚠️  DATABASE_URL points to SQLite - This might be the issue")
    else:
        print("❓ DATABASE_URL format not recognized")
else:
    print("❌ DATABASE_URL is not set!")

# 3. Check if we can import the application modules
print("\n🐍 Python Module Import Test:")
try:
    sys.path.insert(0, os.getcwd())
    from backend.core.database import DB_URL, _raw_db_url, _default_db_url
    print(f"✅ Successfully imported database module")
    print(f"   _default_db_url: {_default_db_url}")
    print(f"   _raw_db_url: {_raw_db_url}")
    print(f"   Final DB_URL: {DB_URL}")
    
    if "mysql" in DB_URL.lower():
        print("✅ Application will use MySQL - CORRECT")
    else:
        print("❌ Application will use SQLite - THIS IS THE PROBLEM")
        
except Exception as e:
    print(f"❌ Failed to import database module: {e}")

# 4. Test MySQL connection
print("\n🗄️  MySQL Connection Test:")
try:
    import pymysql
    print("✅ PyMySQL module is available")
    
    # Parse the DATABASE_URL if it exists
    if database_url and "mysql" in database_url.lower():
        # Extract connection details from URL
        # Format: mysql+pymysql://user:password@host:port/database
        url_parts = database_url.replace("mysql+pymysql://", "").split("/")
        if len(url_parts) >= 2:
            user_host = url_parts[0]
            database = url_parts[1]
            
            if "@" in user_host:
                user_pass, host_port = user_host.split("@")
                if ":" in user_pass:
                    user, password = user_pass.split(":", 1)
                else:
                    user, password = user_pass, ""
                
                if ":" in host_port:
                    host, port = host_port.split(":")
                    port = int(port)
                else:
                    host, port = host_port, 3306
                
                print(f"   Connecting to: {user}@{host}:{port}/{database}")
                
                try:
                    connection = pymysql.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database
                    )
                    print("✅ MySQL connection successful!")
                    connection.close()
                except Exception as e:
                    print(f"❌ MySQL connection failed: {e}")
            else:
                print("❌ Invalid DATABASE_URL format")
        else:
            print("❌ Could not parse DATABASE_URL")
    else:
        print("⚠️  DATABASE_URL not set or not MySQL format")
        
except ImportError:
    print("❌ PyMySQL module not found - install with: pip install PyMySQL")
except Exception as e:
    print(f"❌ Error testing MySQL: {e}")

# 5. Check systemd environment
print("\n⚙️  Systemd Service Environment Check:")
service_file = "/etc/systemd/system/fastapi-techkids.service"
if os.path.exists(service_file):
    print(f"✅ Service file exists: {service_file}")
    try:
        with open(service_file, 'r') as f:
            content = f.read()
            if 'DATABASE_URL=' in content:
                lines = [line.strip() for line in content.split('\n') if 'DATABASE_URL=' in line]
                for line in lines:
                    print(f"   Found: {line}")
                    if 'mysql' in line.lower():
                        print("   ✅ MySQL URL found in service file")
                    else:
                        print("   ❌ Non-MySQL URL in service file")
            else:
                print("   ❌ No DATABASE_URL found in service file")
    except Exception as e:
        print(f"   ❌ Error reading service file: {e}")
else:
    print(f"❌ Service file not found: {service_file}")

print("\n🎯 DIAGNOSIS COMPLETE")
print("\nIf you see 'Application will use SQLite' above, that's your problem!")
print("The environment variable is not being read properly by the application.")