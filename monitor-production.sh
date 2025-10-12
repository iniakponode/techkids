#!/bin/bash

# TechKids Production Health Monitor
# Usage: ./monitor-production.sh [--watch]

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_NAME="fastapi-techkids"
APP_URL="http://localhost:8002"
PRODUCTION_PATH="/var/www/vhosts/ungozu.com/techkids.ungozu.com"

check_status() {
    local service="$1"
    local name="$2"
    
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✅ $name: Running${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: Not running${NC}"
        return 1
    fi
}

check_url() {
    local url="$1"
    local name="$2"
    
    if curl -f -s "$url" > /dev/null; then
        echo -e "${GREEN}✅ $name: Responding${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: Not responding${NC}"
        return 1
    fi
}

check_disk_space() {
    local threshold=90
    local usage=$(df "$PRODUCTION_PATH" | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt "$threshold" ]; then
        echo -e "${GREEN}✅ Disk Usage: ${usage}%${NC}"
    else
        echo -e "${RED}⚠️ Disk Usage: ${usage}% (High!)${NC}"
    fi
}

check_memory() {
    local mem_info=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ "$mem_info" -lt 80 ]; then
        echo -e "${GREEN}✅ Memory Usage: ${mem_info}%${NC}"
    else
        echo -e "${YELLOW}⚠️ Memory Usage: ${mem_info}%${NC}"
    fi
}

check_logs() {
    local error_count=$(journalctl -u "$SERVICE_NAME" --since "1 hour ago" | grep -i error | wc -l)
    
    if [ "$error_count" -eq 0 ]; then
        echo -e "${GREEN}✅ Recent Errors: None${NC}"
    else
        echo -e "${YELLOW}⚠️ Recent Errors: $error_count in last hour${NC}"
    fi
}

show_health_report() {
    echo -e "${BLUE}🏥 TechKids Production Health Report${NC}"
    echo "================================================"
    echo "⏰ $(date)"
    echo ""
    
    echo -e "${BLUE}📊 System Status:${NC}"
    check_status "$SERVICE_NAME" "FastAPI Service"
    check_status "mysql" "MySQL Database"
    check_status "nginx" "Nginx Web Server"
    echo ""
    
    echo -e "${BLUE}🌐 Application Status:${NC}"
    check_url "$APP_URL" "Local Application"
    check_url "https://techkids.ungozu.com" "Public Website"
    echo ""
    
    echo -e "${BLUE}💾 Resource Usage:${NC}"
    check_disk_space
    check_memory
    echo ""
    
    echo -e "${BLUE}📝 Log Status:${NC}"
    check_logs
    echo ""
    
    # Show recent git commit
    if [ -d "$PRODUCTION_PATH" ]; then
        cd "$PRODUCTION_PATH"
        echo -e "${BLUE}📦 Current Version:${NC}"
        echo "$(git log --oneline -1)"
        echo ""
    fi
    
    # Show process info
    echo -e "${BLUE}🔧 Process Information:${NC}"
    ps aux | grep -E "(uvicorn|gunicorn)" | grep -v grep || echo "No FastAPI processes found"
    echo ""
    
    echo "================================================"
}

# Watch mode
if [ "$1" = "--watch" ]; then
    echo -e "${BLUE}👀 Starting continuous monitoring (Ctrl+C to stop)${NC}"
    while true; do
        clear
        show_health_report
        sleep 30
    done
else
    show_health_report
fi