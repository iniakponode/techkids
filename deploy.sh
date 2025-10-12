#!/bin/bash

# TechKids Production Deployment Script
# This script helps deploy the FastAPI application to production

set -e  # Exit on any error

echo "🚀 Starting TechKids deployment..."

# Configuration
PRODUCTION_PATH="/var/www/vhosts/ungozu.com/techkids.ungozu.com"
SERVICE_NAME="fastapi-techkids"
PYTHON_VERSION="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root or with sudo"
    exit 1
fi

# 1. Stop the service
print_status "Stopping $SERVICE_NAME service..."
systemctl stop $SERVICE_NAME || print_warning "Service was not running"

# 2. Navigate to production directory
print_status "Navigating to production directory: $PRODUCTION_PATH"
cd $PRODUCTION_PATH

# 3. Backup current deployment (optional)
if [ -d "backup" ]; then
    rm -rf backup
fi
mkdir -p backup
print_status "Creating backup of current deployment..."
cp -r backend main.py requirements.txt backup/ 2>/dev/null || print_warning "Some files were not found for backup"

# 4. Pull latest changes from repository
print_status "Pulling latest changes from git..."
sudo -u www-data git pull origin main

# 5. Activate virtual environment and install dependencies
print_status "Activating virtual environment and installing dependencies..."
sudo -u www-data bash -c "
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
"

# 6. Run database migrations
print_status "Running database migrations..."
sudo -u www-data bash -c "
    source venv/bin/activate
    alembic upgrade head
"

# 7. Run any additional setup if needed
print_status "Running additional setup..."
sudo -u www-data bash -c "
    source venv/bin/activate
    python -c 'from backend.core.database import init_db; init_db()'
"

# 8. Set proper permissions
print_status "Setting proper permissions..."
chown -R www-data:www-data $PRODUCTION_PATH
chmod -R 755 $PRODUCTION_PATH

# 9. Start the service
print_status "Starting $SERVICE_NAME service..."
systemctl start $SERVICE_NAME

# 10. Enable service to start on boot
systemctl enable $SERVICE_NAME

# 11. Check service status
sleep 3
if systemctl is-active --quiet $SERVICE_NAME; then
    print_status "✅ Deployment successful! Service is running."
    systemctl status $SERVICE_NAME --no-pager
else
    print_error "❌ Deployment failed! Service is not running."
    print_error "Check the logs with: journalctl -u $SERVICE_NAME -f"
    exit 1
fi

# 12. Test the endpoint
print_status "Testing the application..."
sleep 5
if curl -f -s http://localhost:8002/ > /dev/null; then
    print_status "✅ Application is responding on port 8002"
else
    print_warning "⚠️  Application might not be responding yet. Check logs if needed."
fi

print_status "🎉 Deployment completed!"
print_status "To check logs: journalctl -u $SERVICE_NAME -f"
print_status "To restart service: systemctl restart $SERVICE_NAME"