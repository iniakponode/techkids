#!/bin/bash

# Production Database Debug and Fix Script
# This script helps diagnose and fix database connection issues

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

print_status "🔍 TechKids Database Connection Diagnostics"
echo "================================================="

# 1. Check if we're in the right directory
EXPECTED_PATH="/var/www/vhosts/ungozu.com/techkids.ungozu.com"
CURRENT_PATH=$(pwd)

if [ "$CURRENT_PATH" != "$EXPECTED_PATH" ]; then
    print_warning "Current directory: $CURRENT_PATH"
    print_warning "Expected directory: $EXPECTED_PATH"
    if [ -d "$EXPECTED_PATH" ]; then
        print_status "Changing to expected directory..."
        cd "$EXPECTED_PATH"
    else
        print_error "Expected directory does not exist!"
        exit 1
    fi
fi

# 2. Check systemd service file
print_status "📋 Checking systemd service configuration..."
SERVICE_FILE="/etc/systemd/system/fastapi-techkids.service"

if [ -f "$SERVICE_FILE" ]; then
    print_debug "Service file exists: $SERVICE_FILE"
    
    # Check DATABASE_URL in service file
    if grep -q "DATABASE_URL.*mysql" "$SERVICE_FILE"; then
        print_status "✅ MySQL DATABASE_URL found in service file"
        DATABASE_URL_LINE=$(grep "DATABASE_URL" "$SERVICE_FILE")
        print_debug "Current DATABASE_URL line: $DATABASE_URL_LINE"
        
        # Check if the line is complete
        if [[ "$DATABASE_URL_LINE" == *">"* ]] || [[ ${#DATABASE_URL_LINE} -lt 80 ]]; then
            print_error "❌ DATABASE_URL appears to be truncated!"
            print_status "The DATABASE_URL should be:"
            echo 'Environment="DATABASE_URL=mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/aitechkids"'
        fi
    else
        print_error "❌ MySQL DATABASE_URL not found in service file"
    fi
else
    print_error "❌ Service file not found: $SERVICE_FILE"
fi

# 3. Check MySQL connection
print_status "🗄️  Testing MySQL database connection..."
if command -v mysql &> /dev/null; then
    print_debug "MySQL client is available"
    
    # Test connection (this will prompt for password)
    print_status "Testing connection to MySQL database 'aitechkids'..."
    print_warning "You will be prompted for the MySQL password for user 'techkids'"
    
    if mysql -u techkids -p -h localhost -e "USE aitechkids; SELECT 'Connection successful!' as status;" 2>/dev/null; then
        print_status "✅ MySQL connection successful!"
    else
        print_error "❌ Failed to connect to MySQL database"
        print_status "Please ensure:"
        echo "  1. MySQL server is running: sudo systemctl status mysql"
        echo "  2. Database 'aitechkids' exists"
        echo "  3. User 'techkids' has access to database"
    fi
else
    print_warning "MySQL client not found. Install with: apt install mysql-client"
fi

# 4. Check Python environment and dependencies
print_status "🐍 Checking Python environment..."
if [ -f "venv/bin/activate" ]; then
    print_status "Virtual environment found"
    
    # Test if PyMySQL is installed
    if venv/bin/python -c "import pymysql; print('PyMySQL version:', pymysql.__version__)" 2>/dev/null; then
        print_status "✅ PyMySQL is installed and working"
    else
        print_error "❌ PyMySQL is not installed or not working"
        print_status "Install with: venv/bin/pip install PyMySQL"
    fi
    
    # Test database URL parsing
    print_status "Testing DATABASE_URL parsing..."
    venv/bin/python -c "
import os
os.environ['DATABASE_URL'] = 'mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/aitechkids'
from backend.core.database import DB_URL
print('Parsed DATABASE_URL:', DB_URL)
print('Database type:', 'MySQL' if 'mysql' in DB_URL.lower() else 'SQLite')
" 2>/dev/null || print_error "❌ Failed to parse DATABASE_URL"
    
else
    print_error "❌ Virtual environment not found at venv/"
fi

# 5. Check current service status
print_status "⚙️  Checking service status..."
if systemctl is-active --quiet fastapi-techkids; then
    print_warning "⚠️  Service is currently running (but with errors)"
    print_status "Recent service logs:"
    journalctl -u fastapi-techkids --since "5 minutes ago" --no-pager | tail -10
else
    print_error "❌ Service is not running"
fi

echo ""
print_status "🔧 RECOMMENDED FIXES:"
echo "1. Edit the systemd service file to fix the DATABASE_URL:"
echo "   sudo nano /etc/systemd/system/fastapi-techkids.service"
echo ""
echo "2. Ensure this line is complete and correct:"
echo '   Environment="DATABASE_URL=mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/aitechkids"'
echo ""
echo "3. Reload and restart the service:"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl restart fastapi-techkids"
echo ""
echo "4. Monitor the logs:"
echo "   sudo journalctl -u fastapi-techkids -f"

print_status "🎯 Diagnostic complete!"