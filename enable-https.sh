#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Enable HTTPS Configuration${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}✗${NC} .env file not found!"
    exit 1
fi

# Check if certificates exist
if [ ! -f "./certbot/conf/live/$DOMAIN_NAME/fullchain.pem" ]; then
    echo -e "${RED}✗${NC} SSL certificates not found for $DOMAIN_NAME"
    echo ""
    echo "Please run ./setup-ssl.sh first to obtain certificates"
    exit 1
fi

echo -e "${GREEN}✓${NC} SSL certificates found for $DOMAIN_NAME"

# Backup current nginx config
echo "Backing up current configuration..."
if [ -f "nginx/conf.d/default.conf" ]; then
    cp nginx/conf.d/default.conf nginx/conf.d/default.conf.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓${NC} Backup created"
fi

# Update docker-compose to use HTTPS configuration
echo "Updating nginx configuration to use HTTPS..."

# Update the nginx service command in docker-compose
sed -i.bak 's/app-http-only\.conf\.template/app.conf.template/g' docker-compose.yml

echo -e "${GREEN}✓${NC} Configuration updated"

# Reload nginx
echo "Reloading nginx..."
docker-compose restart nginx

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ HTTPS is now enabled!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Your site is now accessible at:"
    echo -e "  ${GREEN}https://$DOMAIN_NAME${NC}"
    echo ""
    echo "HTTP requests will automatically redirect to HTTPS."
    echo ""

    if [ "$CERTBOT_ENV" = "staging" ]; then
        echo -e "${YELLOW}⚠  Note: You're using staging certificates${NC}"
        echo "   Browsers will show a security warning."
        echo ""
        echo "To get trusted certificates:"
        echo "  1. Edit .env and set CERTBOT_ENV=production"
        echo "  2. Run: ./setup-ssl.sh"
        echo "  3. Run: ./enable-https.sh"
    else
        echo -e "${GREEN}Certificate auto-renewal is configured.${NC}"
        echo "Certificates will automatically renew before expiry."
    fi
    echo ""
else
    echo -e "${RED}✗${NC} Failed to reload nginx"
    echo "Check logs: docker-compose logs nginx"
    exit 1
fi
