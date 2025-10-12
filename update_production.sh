#!/bin/bash

# TechKids Production Deployment Script
# Run this script after pushing changes to deploy updates

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_PATH="/var/www/vhosts/ungozu.com/techkids.ungozu.com"
SERVICE_NAME="fastapi-techkids"
ENV_USER="www-data"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root or with sudo"
    exit 1
fi

print_status "🚀 Starting TechKids Production Deployment..."
echo "================================================="

# Step 1: Navigate to production directory
print_step "📁 Navigating to production directory"
cd "$PRODUCTION_PATH" || {
    print_error "Failed to navigate to $PRODUCTION_PATH"
    exit 1
}
print_status "Current directory: $(pwd)"

# Step 2: Check git status
print_step "📋 Checking git repository status"
sudo -u "$ENV_USER" git status --porcelain
if [ $? -ne 0 ]; then
    print_error "Git repository has issues"
    exit 1
fi

# Step 3: Pull latest changes
print_step "⬇️  Pulling latest changes from git"
sudo -u "$ENV_USER" git pull origin main
if [ $? -eq 0 ]; then
    print_status "✅ Git pull successful"
else
    print_error "❌ Git pull failed"
    exit 1
fi

# Step 4: Check if requirements.txt changed
print_step "📦 Checking for dependency changes"
if git diff HEAD~1 HEAD --name-only | grep -q "requirements.txt"; then
    print_status "📦 requirements.txt changed, updating dependencies..."
    sudo -u "$ENV_USER" bash -c "
        cd '$PRODUCTION_PATH'
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    "
    if [ $? -eq 0 ]; then
        print_status "✅ Dependencies updated successfully"
    else
        print_error "❌ Failed to update dependencies"
        exit 1
    fi
else
    print_status "📦 No dependency changes detected"
fi

# Step 5: Check for database migrations
print_step "🗄️  Checking for database migrations"
if find alembic/versions -name "*.py" -newer .last_migration 2>/dev/null | grep -q .; then
    print_status "🗄️  Running database migrations..."
    sudo -u "$ENV_USER" bash -c "
        cd '$PRODUCTION_PATH'
        source venv/bin/activate
        export DATABASE_URL='mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/aitechkids'
        export ENVIRONMENT='production'
        alembic upgrade head
    "
    if [ $? -eq 0 ]; then
        print_status "✅ Database migrations completed"
        touch .last_migration
    else
        print_error "❌ Database migrations failed"
        exit 1
    fi
else
    print_status "🗄️  No new migrations to apply"
fi

# Step 6: Check current service status
print_step "⚙️  Checking current service status"
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_status "⚡ Service is currently running"
    RESTART_NEEDED=true
else
    print_warning "⚠️  Service is not running"
    RESTART_NEEDED=true
fi

# Step 7: Restart the service
if [ "$RESTART_NEEDED" = true ]; then
    print_step "🔄 Restarting $SERVICE_NAME service"
    systemctl restart "$SERVICE_NAME"
    
    # Wait a moment for service to start
    sleep 3
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "✅ Service restarted successfully"
    else
        print_error "❌ Service failed to restart"
        print_error "Check logs with: journalctl -u $SERVICE_NAME -f"
        exit 1
    fi
fi

# Step 8: Verify deployment
print_step "🔍 Verifying deployment"

# Test local endpoint
if curl -f -s http://localhost:8002/ > /dev/null; then
    print_status "✅ Local endpoint responding"
else
    print_warning "⚠️  Local endpoint not responding"
fi

# Test public endpoint
if curl -f -s https://techkids.ungozu.com/ > /dev/null; then
    print_status "✅ Public endpoint responding"
else
    print_warning "⚠️  Public endpoint not responding (check proxy configuration)"
fi

# Step 9: Show recent logs
print_step "📋 Recent service logs"
journalctl -u "$SERVICE_NAME" --since "2 minutes ago" --no-pager | tail -10

# Step 10: Final status
print_status "🎉 Deployment completed successfully!"
print_status "Service status: $(systemctl is-active $SERVICE_NAME)"
print_status "To monitor logs: journalctl -u $SERVICE_NAME -f"
print_status "To check status: systemctl status $SERVICE_NAME"

echo ""
print_status "✨ TechKids is now running the latest version!"