# TechKids Production Deployment Guide

## Overview

This guide covers the automated deployment system for TechKids production server. The system includes automated deployment, rollback capabilities, and monitoring tools.

## Files

- `deploy-production.sh` - Main deployment script
- `rollback-production.sh` - Emergency rollback script
- `DEPLOYMENT.md` - Detailed deployment documentation

## Quick Start

### 1. Regular Deployment

```bash
# Copy scripts to production server
scp deploy-production.sh rollback-production.sh user@techkids.ungozu.com:/var/www/vhosts/ungozu.com/techkids.ungozu.com/

# SSH to production server
ssh user@techkids.ungozu.com

# Navigate to project directory
cd /var/www/vhosts/ungozu.com/techkids.ungozu.com

# Run full deployment
sudo ./deploy-production.sh
```

### 2. Quick Deployment (Frontend changes only)

```bash
# For CSS, JavaScript, or template changes only
sudo ./deploy-production.sh --quick
```

### 3. Force Deployment

```bash
# Deploy even if there are uncommitted changes
sudo ./deploy-production.sh --force
```

## Deployment Script Features

### ✅ Full Deployment (`./deploy-production.sh`)

1. **Pre-deployment checks**
   - Verifies git repository status
   - Checks for uncommitted changes
   - Fetches latest changes from remote

2. **Backup creation**
   - Creates timestamped backup of current code
   - Stored in `deployments/backup-YYYYMMDD-HHMMSS/`

3. **Service management**
   - Stops FastAPI service gracefully
   - Restarts after deployment
   - Verifies service is running

4. **Code deployment**
   - Pulls latest changes from git
   - Updates Python dependencies
   - Runs database migrations
   - Sets proper file permissions

5. **Verification**
   - Tests service is responding
   - Shows service status
   - Provides helpful commands

### ⚡ Quick Deployment (`--quick`)

Skips time-consuming steps for frontend-only changes:
- ❌ Skip pip install
- ❌ Skip database migrations
- ✅ Update code
- ✅ Restart service

### 🔧 Force Deployment (`--force`)

- Deploys even with uncommitted changes
- Useful for hotfixes or emergency deployments

## Rollback System

### Emergency Rollback

```bash
# Rollback to most recent backup
sudo ./rollback-production.sh

# Rollback to specific backup
sudo ./rollback-production.sh deployments/backup-20241012-143000
```

### List Available Backups

```bash
ls -la deployments/
```

## Monitoring and Troubleshooting

### Check Service Status

```bash
# Service status
sudo systemctl status fastapi-techkids

# Live logs
sudo journalctl -u fastapi-techkids -f

# Recent logs
sudo journalctl -u fastapi-techkids --since "10 minutes ago"
```

### Application Health Check

```bash
# Test application response
curl -f http://localhost:8002/

# Check specific endpoints
curl -f http://localhost:8002/health
```

### Deployment Logs

```bash
# View deployment logs
sudo tail -f /var/log/techkids-deployment.log

# View rollback logs
sudo tail -f /var/log/techkids-rollback.log
```

## Deployment Workflow

### Development to Production

1. **Development**
   ```bash
   # Make changes locally
   git add .
   git commit -m "feat: new feature"
   git push origin main
   ```

2. **Testing**
   ```bash
   # Test locally first
   python -m pytest
   ```

3. **Deployment**
   ```bash
   # SSH to production
   ssh user@techkids.ungozu.com
   cd /var/www/vhosts/ungozu.com/techkids.ungozu.com
   
   # Deploy
   sudo ./deploy-production.sh
   ```

4. **Verification**
   ```bash
   # Check the website
   curl -f https://techkids.ungozu.com
   
   # Monitor logs
   sudo journalctl -u fastapi-techkids -f
   ```

### Hotfix Deployment

```bash
# For urgent fixes
sudo ./deploy-production.sh --force

# For frontend-only fixes
sudo ./deploy-production.sh --quick
```

## Security Notes

1. **File Permissions**
   - Scripts run as root/sudo for service management
   - Application files owned by www-data
   - Environment files secured with 600 permissions

2. **Backup Security**
   - Backups contain sensitive data
   - Automatically cleaned (keeps last 5)
   - Stored in production directory

3. **Database**
   - Migrations run automatically
   - Connection secured via environment variables
   - Production database isolated

## Troubleshooting Common Issues

### 1. Service Won't Start

```bash
# Check detailed status
sudo systemctl status fastapi-techkids -l

# Check configuration
sudo journalctl -u fastapi-techkids --since "5 minutes ago"

# Test configuration
sudo -u www-data bash -c "source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8002"
```

### 2. Database Connection Issues

```bash
# Test database connection
sudo -u www-data bash -c "
source venv/bin/activate
export DATABASE_URL='mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/aitechkids'
python -c 'from backend.core.database import engine; print(engine.execute(\"SELECT 1\").scalar())'
"
```

### 3. Permission Issues

```bash
# Fix permissions
sudo chown -R www-data:www-data /var/www/vhosts/ungozu.com/techkids.ungozu.com
sudo chmod -R 755 /var/www/vhosts/ungozu.com/techkids.ungozu.com
sudo chmod 600 /var/www/vhosts/ungozu.com/techkids.ungozu.com/.env.production
```

### 4. Git Issues

```bash
# Reset git state
sudo -u www-data git reset --hard HEAD

# Clean untracked files
sudo -u www-data git clean -fd

# Force pull
sudo -u www-data git fetch --all
sudo -u www-data git reset --hard origin/main
```

## Emergency Procedures

### 1. Complete Service Failure

```bash
# Immediate rollback
sudo ./rollback-production.sh

# If rollback fails, manual restore
sudo systemctl stop fastapi-techkids
sudo -u www-data cp -r deployments/backup-[LATEST]/* ./
sudo systemctl start fastapi-techkids
```

### 2. Database Issues

```bash
# Check database status
sudo systemctl status mysql

# Restart database
sudo systemctl restart mysql

# Check database connectivity
mysql -u techkids -p aitechkids
```

### 3. High Load Issues

```bash
# Check system resources
htop
df -h
free -m

# Check application processes
ps aux | grep uvicorn
sudo systemctl status fastapi-techkids
```

## Best Practices

1. **Always test locally first**
2. **Use quick deploy for frontend changes**
3. **Monitor logs after deployment**
4. **Keep backups for at least 24 hours**
5. **Use rollback immediately if issues detected**
6. **Verify SSL certificates monthly**
7. **Update dependencies regularly**

## Scheduled Maintenance

### Weekly Tasks
- Check disk space
- Review error logs
- Update system packages
- Verify backups

### Monthly Tasks
- Database optimization
- SSL certificate renewal check
- Security updates
- Performance monitoring

## Support Commands

```bash
# Quick health check
curl -f https://techkids.ungozu.com && echo "✅ Site is up"

# Service restart
sudo systemctl restart fastapi-techkids

# View all logs
sudo journalctl -u fastapi-techkids --since "1 hour ago"

# Check database
echo "SELECT COUNT(*) FROM users;" | mysql -u techkids -p aitechkids

# Disk usage
du -sh /var/www/vhosts/ungozu.com/techkids.ungozu.com
```