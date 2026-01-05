#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Let's Encrypt SSL Certificate Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓${NC} Loaded .env file"
else
    echo -e "${RED}✗${NC} .env file not found!"
    echo "Please create .env from .env.example and configure your domain."
    echo "Command: cp .env.example .env"
    exit 1
fi

# Check required variables
if [ -z "$DOMAIN_NAME" ]; then
    echo -e "${RED}✗${NC} DOMAIN_NAME not set in .env"
    exit 1
fi

if [ -z "$LETSENCRYPT_EMAIL" ]; then
    echo -e "${RED}✗${NC} LETSENCRYPT_EMAIL not set in .env"
    exit 1
fi

echo -e "${YELLOW}Domain:${NC} $DOMAIN_NAME"
echo -e "${YELLOW}Email:${NC} $LETSENCRYPT_EMAIL"
echo -e "${YELLOW}Environment:${NC} ${CERTBOT_ENV:-staging}"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p nginx/conf.d
echo -e "${GREEN}✓${NC} Directories created"

# Check if nginx is running
if ! docker ps | grep -q ipc-bns-nginx; then
    echo ""
    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose up -d nginx
    sleep 5
fi

# Determine certbot arguments
if [ "$CERTBOT_ENV" = "staging" ]; then
    CERTBOT_ARGS="--staging"
    echo -e "${YELLOW}⚠${NC}  Using staging environment (test certificates)"
    echo "   To get real certificates, set CERTBOT_ENV=production in .env"
else
    CERTBOT_ARGS=""
    echo -e "${GREEN}✓${NC} Using production environment (real certificates)"
fi

echo ""
echo "Obtaining SSL certificate..."
echo "This may take a minute..."
echo ""

# Request certificate
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    $CERTBOT_ARGS \
    --email $LETSENCRYPT_EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN_NAME

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ SSL certificate obtained successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Update nginx configuration to use HTTPS"
    echo "   Run: ./enable-https.sh"
    echo ""

    if [ "$CERTBOT_ENV" = "staging" ]; then
        echo -e "${YELLOW}Note:${NC} You're using staging certificates (not trusted by browsers)"
        echo "To get real certificates:"
        echo "  1. Edit .env and set CERTBOT_ENV=production"
        echo "  2. Run this script again: ./setup-ssl.sh"
        echo "  3. Then run: ./enable-https.sh"
    fi
else
    echo ""
    echo -e "${RED}✗ Failed to obtain SSL certificate${NC}"
    echo ""
    echo "Common issues:"
    echo "1. Domain DNS not pointing to this server"
    echo "2. Port 80 not accessible from internet"
    echo "3. Firewall blocking connections"
    echo ""
    echo "Troubleshooting:"
    echo "  • Check DNS: dig $DOMAIN_NAME"
    echo "  • Check port 80: curl http://$DOMAIN_NAME"
    echo "  • Check logs: docker-compose logs nginx"
    exit 1
fi
