#!/bin/bash

# TechKids Emergency Rollback Script
# Usage: sudo ./rollback-production.sh [backup-directory]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PRODUCTION_PATH="/var/www/vhosts/ungozu.com/techkids.ungozu.com"
SERVICE_NAME="fastapi-techkids"
LOG_FILE="/var/log/techkids-rollback.log"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root or with sudo"
    exit 1
fi

cd "$PRODUCTION_PATH"

# If backup directory is provided as argument, use it
if [ -n "$1" ]; then
    BACKUP_DIR="$1"
else
    # Find the most recent backup
    if [ -d "deployments" ]; then
        BACKUP_DIR=$(ls -t deployments/ | head -n 1)
        BACKUP_DIR="deployments/$BACKUP_DIR"
    else
        print_error "No deployments directory found!"
        exit 1
    fi
fi

# Check if backup exists
if [ ! -d "$BACKUP_DIR" ]; then
    print_error "Backup directory not found: $BACKUP_DIR"
    print_status "Available backups:"
    ls -la deployments/ 2>/dev/null || echo "No backups found"
    exit 1
fi

print_status "🔄 Starting emergency rollback to: $BACKUP_DIR"
echo "Rollback started at $(date)" >> "$LOG_FILE"

# Stop service
print_step "1️⃣ Stopping $SERVICE_NAME service..."
systemctl stop $SERVICE_NAME || print_status "Service was not running"

# Create emergency backup of current state
print_step "2️⃣ Creating emergency backup of current state..."
EMERGENCY_BACKUP="deployments/emergency-$(date +%Y%m%d-%H%M%S)"
sudo -u www-data mkdir -p "$EMERGENCY_BACKUP"
sudo -u www-data cp -r backend frontend main.py requirements.txt "$EMERGENCY_BACKUP/" 2>/dev/null || true

# Restore from backup
print_step "3️⃣ Restoring from backup..."
sudo -u www-data cp -r "$BACKUP_DIR"/* ./
print_status "✅ Files restored from backup"

# Set permissions
print_step "4️⃣ Setting permissions..."
chown -R www-data:www-data "$PRODUCTION_PATH"
chmod -R 755 "$PRODUCTION_PATH"
chmod 600 "$PRODUCTION_PATH/.env.production" 2>/dev/null || true

# Start service
print_step "5️⃣ Starting service..."
systemctl start $SERVICE_NAME

# Wait and check
sleep 5
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "🎉 Rollback successful! Service is running."
    systemctl status $SERVICE_NAME --no-pager --lines=5
else
    print_error "❌ Rollback failed! Service is not running."
    journalctl -u $SERVICE_NAME --since "2 minutes ago" --no-pager | tail -10
    exit 1
fi

print_success "✅ Emergency rollback completed!"
print_status "Current state backed up to: $EMERGENCY_BACKUP"
echo "Rollback completed at $(date)" >> "$LOG_FILE"