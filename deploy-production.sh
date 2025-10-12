#!/bin/bash

# TechKids Automated Production Deployment Script
# Usage: sudo ./deploy-production.sh [--quick] [--force] [--help]
# 
# Options:
#   --quick    Skip database migrations and dependency updates (faster for frontend-only changes)
#   --force    Force deployment even if there are uncommitted changes on server
#   --help     Show this help message

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_PATH="/var/www/vhosts/ungozu.com/techkids.ungozu.com"
SERVICE_NAME="fastapi-techkids"
BACKUP_DIR="deployments/backup-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="/var/log/techkids-deployment.log"

# Parse command line arguments
QUICK_DEPLOY=false
FORCE_DEPLOY=false
SHOW_HELP=false

for arg in "$@"; do
    case $arg in
        --quick)
            QUICK_DEPLOY=true
            shift
            ;;
        --force)
            FORCE_DEPLOY=true
            shift
            ;;
        --help)
            SHOW_HELP=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            SHOW_HELP=true
            ;;
    esac
done

# Show help
if [ "$SHOW_HELP" = true ]; then
    echo -e "${CYAN}TechKids Production Deployment Script${NC}"
    echo ""
    echo "Usage: sudo ./deploy-production.sh [options]"
    echo ""
    echo "Options:"
    echo "  --quick    Skip database migrations and pip installs (for frontend-only changes)"
    echo "  --force    Deploy even if there are local changes on server"
    echo "  --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  sudo ./deploy-production.sh                    # Full deployment"
    echo "  sudo ./deploy-production.sh --quick            # Quick deployment (CSS/JS changes)"
    echo "  sudo ./deploy-production.sh --force            # Force deployment"
    echo ""
    exit 0
fi

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
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

# Create log file
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

print_status "🚀 Starting TechKids production deployment..."
echo "Deployment started at $(date)" >> "$LOG_FILE"

# Check if production directory exists
if [ ! -d "$PRODUCTION_PATH" ]; then
    print_error "Production directory does not exist: $PRODUCTION_PATH"
    exit 1
fi

# Navigate to production directory
cd "$PRODUCTION_PATH"
print_status "📁 Working in: $(pwd)"

# Check git status
print_step "1️⃣ Checking git repository status..."
if [ "$FORCE_DEPLOY" = false ]; then
    if ! git diff-index --quiet HEAD --; then
        print_error "There are uncommitted changes in the production directory!"
        print_warning "Use --force to deploy anyway, or commit/stash changes first:"
        git status --porcelain
        exit 1
    fi
fi

# Fetch latest changes
print_step "2️⃣ Fetching latest changes from repository..."
sudo -u www-data git fetch origin

# Check if there are updates
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    print_warning "No new changes to deploy. Local and remote are in sync."
    if [ "$FORCE_DEPLOY" = false ]; then
        print_status "Use --force to restart services anyway."
        exit 0
    fi
else
    print_status "New changes detected:"
    git log --oneline HEAD..origin/main
fi

# Create backup
print_step "3️⃣ Creating backup..."
mkdir -p "deployments"
sudo -u www-data mkdir -p "$BACKUP_DIR"
sudo -u www-data cp -r backend frontend main.py requirements.txt "$BACKUP_DIR/" 2>/dev/null || print_warning "Some files were not found for backup"
print_status "✅ Backup created: $BACKUP_DIR"

# Stop the service
print_step "4️⃣ Stopping $SERVICE_NAME service..."
systemctl stop $SERVICE_NAME || print_warning "Service was not running"
print_status "✅ Service stopped"

# Pull latest changes
print_step "5️⃣ Pulling latest changes..."
sudo -u www-data git pull origin main
print_status "✅ Code updated to latest version"

if [ "$QUICK_DEPLOY" = false ]; then
    # Update dependencies
    print_step "6️⃣ Installing/updating Python dependencies..."
    sudo -u www-data bash -c "
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    "
    print_status "✅ Dependencies updated"

    # Run database migrations
    print_step "7️⃣ Running database migrations..."
    sudo -u www-data bash -c "
        source venv/bin/activate
        export DATABASE_URL='mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/aitechkids'
        export ENVIRONMENT='production'
        alembic upgrade head
    " 2>&1 | tee -a "$LOG_FILE"
    print_status "✅ Database migrations completed"

    # Run any additional setup
    print_step "8️⃣ Running additional setup..."
    sudo -u www-data bash -c "
        source venv/bin/activate
        export DATABASE_URL='mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/aitechkids'
        export ENVIRONMENT='production'
        python -c 'from backend.core.database import init_db; init_db()' || echo 'Database init skipped'
    " 2>&1 | tee -a "$LOG_FILE"
    print_status "✅ Additional setup completed"
else
    print_warning "⚡ Quick deployment mode - skipping migrations and dependencies"
fi

# Set proper permissions
print_step "9️⃣ Setting proper file permissions..."
chown -R www-data:www-data "$PRODUCTION_PATH"
chmod -R 755 "$PRODUCTION_PATH"
# Ensure the environment file is secure
chmod 600 "$PRODUCTION_PATH/.env.production" 2>/dev/null || print_warning "No .env.production file found"
print_status "✅ Permissions set"

# Start the service
print_step "🔟 Starting $SERVICE_NAME service..."
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME
print_status "✅ Service started and enabled"

# Wait for service to stabilize
print_status "⏳ Waiting for service to stabilize..."
sleep 5

# Check service status
print_step "1️⃣1️⃣ Verifying deployment..."
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

# Cleanup old backups (keep last 5)
print_step "1️⃣2️⃣ Cleaning up old backups..."
cd deployments
ls -t | tail -n +6 | xargs -r rm -rf
cd "$PRODUCTION_PATH"
print_status "✅ Old backups cleaned up"

# Final status
print_success "🚀 Deployment completed successfully!"
echo ""
print_status "📊 Deployment Summary:"
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
echo "Deployment completed successfully at $(date)" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"