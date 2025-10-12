#!/bin/bash

# Quick fix for deploy-simple.sh permissions
# Run this on your production server before running deploy-simple.sh

PRODUCTION_PATH="/var/www/vhosts/ungozu.com/techkids.ungozu.com"

echo "🔧 Applying quick permission fix..."

# Navigate to production directory
cd "$PRODUCTION_PATH"

# Fix permissions on the deployment script
chmod +x deploy-simple.sh 2>/dev/null || echo "deploy-simple.sh not found"

# Create deployments directory with proper permissions
mkdir -p deployments
chown -R www-data:www-data deployments
chmod 755 deployments

# Fix ownership of current directory
chown -R www-data:www-data .
chmod 755 .

echo "✅ Permissions fixed!"
echo ""
echo "Now you can run: sudo ./deploy-simple.sh"