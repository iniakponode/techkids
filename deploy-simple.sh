#!/bin/bash

# TechKids Simple Production Deployment (No Git Required)
# Usage: sudo ./deploy-simple.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PRODUCTION_PATH="/var/www/vhosts/ungozu.com/techkids.ungozu.com"
SERVICE_NAME="fastapi-techkids"
BACKUP_DIR="deployments/backup-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="/var/log/techkids-deployment.log"
TEMP_REPO="/tmp/techkids-deploy-$(date +%Y%m%d-%H%M%S)"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root or with sudo"
    exit 1
fi

# Create log file
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

print_status "🚀 Starting TechKids simple deployment (no git required)..."
echo "Deployment started at $(date)" >> "$LOG_FILE"

# Check if production directory exists
if [ ! -d "$PRODUCTION_PATH" ]; then
    print_error "Production directory does not exist: $PRODUCTION_PATH"
    exit 1
fi

cd "$PRODUCTION_PATH"

# Create backup
print_step "1️⃣ Creating backup..."
# Create deployments directory as root first, then change ownership
mkdir -p "deployments"
chown -R www-data:www-data "deployments"
# Create backup directory
mkdir -p "$BACKUP_DIR"
chown -R www-data:www-data "$BACKUP_DIR"
# Copy files to backup
cp -r backend frontend main.py requirements.txt "$BACKUP_DIR/" 2>/dev/null || print_warning "Some files were not found for backup"
chown -R www-data:www-data "$BACKUP_DIR"
print_status "✅ Backup created: $BACKUP_DIR"

# Clone repository to temporary location
print_step "2️⃣ Downloading latest code..."
rm -rf "$TEMP_REPO"
git clone https://github.com/iniakponode/techkids.git "$TEMP_REPO"
cd "$TEMP_REPO"
LATEST_COMMIT=$(git log --oneline -1)
print_status "Latest commit: $LATEST_COMMIT"

# Stop the service
print_step "3️⃣ Stopping $SERVICE_NAME service..."
systemctl stop $SERVICE_NAME || print_warning "Service was not running"
print_status "✅ Service stopped"

# Copy new files to production
print_step "4️⃣ Updating production files..."
cd "$PRODUCTION_PATH"

# Copy backend files
if [ -d "$TEMP_REPO/backend" ]; then
    sudo -u www-data cp -r "$TEMP_REPO/backend" ./
    print_status "✅ Backend files updated"
fi

# Copy frontend files
if [ -d "$TEMP_REPO/frontend" ]; then
    sudo -u www-data cp -r "$TEMP_REPO/frontend" ./
    print_status "✅ Frontend files updated"
fi

# Copy main files
for file in main.py requirements.txt alembic.ini; do
    if [ -f "$TEMP_REPO/$file" ]; then
        sudo -u www-data cp "$TEMP_REPO/$file" ./
        print_status "✅ $file updated"
    fi
done

# Copy alembic directory
if [ -d "$TEMP_REPO/alembic" ]; then
    sudo -u www-data cp -r "$TEMP_REPO/alembic" ./
    print_status "✅ Alembic files updated"
fi

# Update dependencies
print_step "5️⃣ Installing/updating Python dependencies..."
sudo -u www-data bash -c "
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
"
print_status "✅ Dependencies updated"

# Run database migrations
print_step "6️⃣ Running database migrations..."
sudo -u www-data bash -c "
    source venv/bin/activate
    export DATABASE_URL='mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/aitechkids'
    export ENVIRONMENT='production'
    alembic upgrade head
" 2>&1 | tee -a "$LOG_FILE"
print_status "✅ Database migrations completed"

# Set proper permissions
print_step "7️⃣ Setting proper file permissions..."
chown -R www-data:www-data "$PRODUCTION_PATH"
chmod -R 755 "$PRODUCTION_PATH"
chmod 600 "$PRODUCTION_PATH/.env.production" 2>/dev/null || print_warning "No .env.production file found"
print_status "✅ Permissions set"

# Start the service
print_step "8️⃣ Starting $SERVICE_NAME service..."
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME
print_status "✅ Service started and enabled"

# Wait for service to stabilize
print_status "⏳ Waiting for service to stabilize..."
sleep 5

# Check service status
print_step "9️⃣ Verifying deployment..."
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "🎉 Deployment successful! Service is running."
    
    # Test the application
    if curl -f -s http://localhost:8002/ > /dev/null; then
        print_success "✅ Application is responding on port 8002"
    else
        print_warning "⚠️ Application might not be responding yet. Check logs if needed."
    fi
    
    # Show service status
    print_status "Service status:"
    systemctl status $SERVICE_NAME --no-pager --lines=5
    
else
    print_error "❌ Deployment failed! Service is not running."
    print_error "Check the logs with: journalctl -u $SERVICE_NAME -f"
    
    # Show recent logs
    print_status "Recent service logs:"
    journalctl -u $SERVICE_NAME --since "2 minutes ago" --no-pager | tail -20
    
    # Offer to restore backup
    echo ""
    read -p "Would you like to restore the backup? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Restoring backup from $BACKUP_DIR..."
        sudo -u www-data cp -r "$BACKUP_DIR"/* ./
        systemctl start $SERVICE_NAME
        print_status "Backup restored. Check service status."
    fi
    
    exit 1
fi

# Cleanup
print_step "🔟 Cleaning up..."
rm -rf "$TEMP_REPO"
# Cleanup old backups (keep last 5)
if [ -d "deployments" ]; then
    cd deployments
    ls -t | tail -n +6 | xargs -r rm -rf
    cd "$PRODUCTION_PATH"
fi
print_status "✅ Cleanup completed"

# Final status
print_success "🚀 Simple deployment completed successfully!"
echo ""
print_status "📊 Deployment Summary:"
print_status "   • Latest commit: $LATEST_COMMIT"
print_status "   • Service: $SERVICE_NAME is running"
print_status "   • URL: https://techkids.ungozu.com"
print_status "   • Backup: $BACKUP_DIR"
print_status "   • Logs: $LOG_FILE"
echo ""
print_status "📝 Useful commands:"
print_status "   • Check logs: sudo journalctl -u $SERVICE_NAME -f"
print_status "   • Restart service: sudo systemctl restart $SERVICE_NAME"
print_status "   • Service status: sudo systemctl status $SERVICE_NAME"
echo ""

# Log completion
echo "Simple deployment completed successfully at $(date)" >> "$LOG_FILE"
echo "Latest commit: $LATEST_COMMIT" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"