# Production Deployment Checklist for TechKids

## Before Deployment

### 1. Environment Variables (✓ Already configured in systemd service)
- [x] `ENVIRONMENT=production`
- [x] `DATABASE_URL=mysql+pymysql://techkids:ProgressIniks2018@localhost:3306/techkids`
- [x] `PAYSTACK_SECRET_KEY` (live key)
- [x] `PAYSTACK_PUBLIC_KEY` (live key)
- [x] `PAYSTACK_BASE_URL=https://api.paystack.co`
- [x] `PAYSTACK_CALLBACK_URL=https://techkids.ungozu.com/api/paystack/verify`
- [x] `SECRET_KEY` (production secret)
- [x] `ACCESS_TOKEN_EXPIRE_MINUTES=30`
- [x] `ALGORITHM=HS256`

### 2. Database Setup
- [ ] Ensure MySQL database `techkids` exists
- [ ] Verify database user `techkids` has proper permissions
- [ ] Test database connection: `mysql -u techkids -p -h localhost techkids`
- [ ] Run migrations: `alembic upgrade head`

### 3. File Permissions & Ownership
- [ ] Ensure `/var/www/vhosts/ungozu.com/techkids.ungozu.com` is owned by `www-data:www-data`
- [ ] Verify virtual environment exists at `/var/www/vhosts/ungozu.com/techkids.ungozu.com/venv`
- [ ] Check that `www-data` can execute the application

### 4. Dependencies
- [ ] Verify all packages in `requirements.txt` are installed in production venv
- [ ] Specifically ensure `PyMySQL==1.1.1` is installed for MySQL connectivity
- [ ] Test Python can import all required modules

### 5. Network & Security
- [ ] Verify port 8002 is available and not blocked by firewall
- [ ] Ensure reverse proxy (Nginx/Apache) is configured to forward to port 8002
- [ ] Test HTTPS certificate is valid for `techkids.ungozu.com`

## Deployment Steps

### 1. Stop Current Service
```bash
sudo systemctl stop fastapi-techkids
```

### 2. Deploy New Code
```bash
cd /var/www/vhosts/ungozu.com/techkids.ungozu.com
sudo -u www-data git pull origin main
```

### 3. Update Dependencies
```bash
sudo -u www-data bash -c "source venv/bin/activate && pip install -r requirements.txt"
```

### 4. Run Database Migrations
```bash
sudo -u www-data bash -c "source venv/bin/activate && alembic upgrade head"
```

### 5. Start Service
```bash
sudo systemctl start fastapi-techkids
sudo systemctl enable fastapi-techkids
```

### 6. Verify Deployment
```bash
# Check service status
sudo systemctl status fastapi-techkids

# Check application logs
sudo journalctl -u fastapi-techkids -f

# Test endpoint
curl http://localhost:8002/
curl https://techkids.ungozu.com/
```

## Post-deployment Testing

### 1. Basic Functionality
- [ ] Root endpoint (`/`) returns welcome message
- [ ] API endpoints are accessible under `/api/`
- [ ] Static files are served correctly from `/static/`

### 2. Database Connectivity
- [ ] Application can connect to MySQL database
- [ ] Database queries are working (check logs for SQL errors)

### 3. Paystack Integration
- [ ] Paystack endpoints are accessible
- [ ] Payment initialization works with live keys
- [ ] Callback URL is correctly configured

### 4. Authentication
- [ ] User registration/login works
- [ ] JWT tokens are generated correctly
- [ ] Protected endpoints require authentication

## Troubleshooting Commands

```bash
# Check service status
sudo systemctl status fastapi-techkids

# View service logs
sudo journalctl -u fastapi-techkids -f

# View recent logs
sudo journalctl -u fastapi-techkids --since "10 minutes ago"

# Test database connection
mysql -u techkids -p -h localhost techkids

# Test application directly
cd /var/www/vhosts/ungozu.com/techkids.ungozu.com
sudo -u www-data bash -c "source venv/bin/activate && python -c 'from main import app; print(\"App imported successfully\")'"

# Check listening ports
sudo netstat -tlnp | grep :8002

# Check file permissions
ls -la /var/www/vhosts/ungozu.com/techkids.ungozu.com/
```

## Common Issues & Solutions

### 1. Service Won't Start
- Check logs: `sudo journalctl -u fastapi-techkids -f`
- Verify file permissions: `sudo chown -R www-data:www-data /var/www/vhosts/ungozu.com/techkids.ungozu.com`
- Test manual start: `sudo -u www-data bash -c "cd /var/www/vhosts/ungozu.com/techkids.ungozu.com && source venv/bin/activate && python main.py"`

### 2. Database Connection Issues
- Verify MySQL is running: `sudo systemctl status mysql`
- Test connection: `mysql -u techkids -p -h localhost techkids`
- Check database URL format in environment variables

### 3. Import Errors
- Activate venv and test imports: `sudo -u www-data bash -c "source venv/bin/activate && python -c 'import backend.models'"`
- Reinstall requirements: `sudo -u www-data bash -c "source venv/bin/activate && pip install -r requirements.txt"`

### 4. Port Already in Use
- Check what's using port 8002: `sudo lsof -i :8002`
- Kill conflicting process if needed
- Change port in systemd service file if required