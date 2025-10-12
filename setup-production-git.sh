#!/bin/bash

# TechKids Production Git Setup Script
# This script converts a non-git production directory to a proper git repository

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PRODUCTION_PATH="/var/www/vhosts/ungozu.com/techkids.ungozu.com"
REPO_URL="https://github.com/iniakponode/techkids.git"
BACKUP_DIR="git-conversion-backup-$(date +%Y%m%d-%H%M%S)"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root or with sudo"
    exit 1
fi

print_status "🔧 Converting production directory to git repository"
echo "Production path: $PRODUCTION_PATH"
echo "Repository URL: $REPO_URL"
echo ""

# Navigate to production directory
if [ ! -d "$PRODUCTION_PATH" ]; then
    print_error "Production directory does not exist: $PRODUCTION_PATH"
    exit 1
fi

cd "$PRODUCTION_PATH"

# Check if already a git repository
if [ -d ".git" ]; then
    print_status "Directory is already a git repository. Checking status..."
    git status
    print_status "Git setup appears to be complete!"
    exit 0
fi

# Create backup of current files
print_step "1️⃣ Creating backup of current files..."
mkdir -p "../$BACKUP_DIR"
cp -r * "../$BACKUP_DIR/" 2>/dev/null || print_warning "Some files could not be backed up"
print_status "✅ Backup created: ../$BACKUP_DIR"

# Initialize git repository
print_step "2️⃣ Initializing git repository..."
sudo -u www-data git init
print_status "✅ Git repository initialized"

# Add remote origin
print_step "3️⃣ Adding remote repository..."
sudo -u www-data git remote add origin "$REPO_URL"
print_status "✅ Remote origin added"

# Fetch from remote
print_step "4️⃣ Fetching from remote repository..."
sudo -u www-data git fetch origin
print_status "✅ Remote data fetched"

# Check out main branch
print_step "5️⃣ Checking out main branch..."
sudo -u www-data git checkout -b main origin/main
print_status "✅ Main branch checked out"

# Show current status
print_step "6️⃣ Checking repository status..."
git status --porcelain

# Check if there are differences
if [ -n "$(git status --porcelain)" ]; then
    print_warning "There are differences between the current files and the repository."
    print_status "Differences found:"
    git status --short
    echo ""
    print_status "Options:"
    echo "1. Keep local changes: git add . && git commit -m 'Production local changes'"
    echo "2. Discard local changes: git reset --hard HEAD"
    echo "3. Review differences: git diff"
    echo ""
    read -p "Choose an option (1/2/3) or press Enter to continue with current state: " choice
    
    case $choice in
        1)
            print_step "Committing local changes..."
            sudo -u www-data git add .
            sudo -u www-data git commit -m "Production local changes during git conversion"
            ;;
        2)
            print_step "Discarding local changes..."
            sudo -u www-data git reset --hard HEAD
            ;;
        3)
            print_step "Showing differences..."
            git diff
            ;;
        *)
            print_status "Continuing with current state..."
            ;;
    esac
fi

# Set proper permissions
print_step "7️⃣ Setting proper permissions..."
chown -R www-data:www-data "$PRODUCTION_PATH"
chmod -R 755 "$PRODUCTION_PATH"
print_status "✅ Permissions set"

# Test git operations
print_step "8️⃣ Testing git operations..."
sudo -u www-data git log --oneline -3 || print_warning "Could not show git log"
sudo -u www-data git remote -v
print_status "✅ Git operations working"

print_status "🎉 Git repository setup complete!"
echo ""
print_status "📋 Summary:"
print_status "   • Production directory is now a git repository"
print_status "   • Remote origin: $REPO_URL"
print_status "   • Current branch: main"
print_status "   • Backup location: ../$BACKUP_DIR"
echo ""
print_status "🚀 You can now run the deployment script:"
print_status "   sudo ./deploy-production.sh"
echo ""
print_status "📝 Useful commands:"
print_status "   • Check status: git status"
print_status "   • Pull latest: git pull origin main"
print_status "   • View log: git log --oneline -5"