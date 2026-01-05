#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Local Development SSL Setup (mkcert)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    echo -e "${YELLOW}mkcert is not installed. Installing...${NC}"
    echo ""

    # Detect OS and install mkcert
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Detected Linux. Installing mkcert..."

        # Check for package manager
        if command -v apt-get &> /dev/null; then
            echo "Using apt..."
            sudo apt-get update
            sudo apt-get install -y wget libnss3-tools

            # Download and install mkcert
            wget https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
            chmod +x mkcert-v1.4.4-linux-amd64
            sudo mv mkcert-v1.4.4-linux-amd64 /usr/local/bin/mkcert

        elif command -v yum &> /dev/null; then
            echo "Using yum..."
            sudo yum install -y wget nss-tools

            wget https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
            chmod +x mkcert-v1.4.4-linux-amd64
            sudo mv mkcert-v1.4.4-linux-amd64 /usr/local/bin/mkcert
        else
            echo -e "${RED}Unsupported package manager. Please install mkcert manually:${NC}"
            echo "https://github.com/FiloSottile/mkcert#installation"
            exit 1
        fi

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS. Installing via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}Homebrew not found. Please install it first:${NC}"
            echo "https://brew.sh"
            exit 1
        fi
        brew install mkcert
        brew install nss  # for Firefox support

    else
        echo -e "${RED}Unsupported OS. Please install mkcert manually:${NC}"
        echo "https://github.com/FiloSottile/mkcert#installation"
        exit 1
    fi

    echo -e "${GREEN}✓ mkcert installed${NC}"
else
    echo -e "${GREEN}✓ mkcert is already installed${NC}"
fi

echo ""
echo "Setting up local Certificate Authority..."

# Install local CA
mkcert -install

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to install local CA${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Local CA installed${NC}"
echo ""

# Create directories
mkdir -p nginx/ssl-local
mkdir -p certbot/conf
mkdir -p certbot/www

echo "Generating SSL certificates for localhost..."
echo ""

# Generate certificates for localhost and common local domains
cd nginx/ssl-local

mkcert \
    localhost \
    127.0.0.1 \
    ::1 \
    "*.localhost" \
    local.ipc-bns.com \
    192.168.1.23

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to generate certificates${NC}"
    exit 1
fi

# Rename generated files to a standard name
mv localhost+*.pem cert.pem 2>/dev/null || true
mv localhost+*-key.pem key.pem 2>/dev/null || true

# If that didn't work, find and rename them
if [ ! -f cert.pem ]; then
    CERT_FILE=$(ls localhost*.pem 2>/dev/null | grep -v key | head -n 1)
    if [ -n "$CERT_FILE" ]; then
        mv "$CERT_FILE" cert.pem
    fi
fi

if [ ! -f key.pem ]; then
    KEY_FILE=$(ls localhost*-key.pem 2>/dev/null | head -n 1)
    if [ -n "$KEY_FILE" ]; then
        mv "$KEY_FILE" key.pem
    fi
fi

cd ../..

if [ -f nginx/ssl-local/cert.pem ] && [ -f nginx/ssl-local/key.pem ]; then
    echo -e "${GREEN}✓ SSL certificates generated${NC}"
    echo ""
    echo "Certificate location:"
    echo "  📄 Certificate: nginx/ssl-local/cert.pem"
    echo "  🔑 Private Key: nginx/ssl-local/key.pem"
    echo ""
else
    echo -e "${RED}✗ Certificate files not found${NC}"
    exit 1
fi

# Update nginx configuration for local development
echo "Updating nginx configuration for local SSL..."

# Create local SSL nginx config
cat > nginx/conf.d/app-local-https.conf <<'NGINX_CONFIG'
# Local Development HTTPS Configuration
server {
    listen 80;
    listen [::]:80;
    server_name localhost 127.0.0.1 192.168.1.23 local.ipc-bns.com;

    # Redirect to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name localhost 127.0.0.1 192.168.1.23 local.ipc-bns.com;

    # Local SSL certificates
    ssl_certificate /etc/nginx/ssl-local/cert.pem;
    ssl_certificate_key /etc/nginx/ssl-local/key.pem;

    # SSL configuration
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers (relaxed for local dev)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend - React app
    location / {
        proxy_pass http://frontend:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API - Direct access to all endpoints
    location ~ ^/(health|docs|openapi.json|auth|sections|section|analyze|memo|cases|stats|categories|subscription) {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers for local development
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
        add_header Access-Control-Allow-Credentials "true" always;

        # Handle OPTIONS requests
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # API prefix route (optional)
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_CONFIG

echo -e "${GREEN}✓ Nginx configuration created${NC}"
echo ""

# Update docker-compose for local SSL
echo "Creating docker-compose.local-ssl.yml..."

cat > docker-compose.local-ssl.yml <<'COMPOSE_CONFIG'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ipc-bns-backend
    expose:
      - "8000"
    volumes:
      - ./backend/app:/app/app
      - backend-data:/app/data
      - chroma-db:/app/chroma_db
    environment:
      - PYTHONUNBUFFERED=1
      - DATABASE_URL=sqlite:///./data/legal_reasoning.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ipc-bns-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: ipc-bns-frontend
    expose:
      - "80"
    environment:
      - REACT_APP_API_URL=https://localhost
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - ipc-bns-network

  nginx:
    image: nginx:alpine
    container_name: ipc-bns-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d/app-local-https.conf:/etc/nginx/conf.d/default.conf:ro
      - ./nginx/ssl-local:/etc/nginx/ssl-local:ro
      - nginx-cache:/var/cache/nginx
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    networks:
      - ipc-bns-network

volumes:
  backend-data:
    driver: local
  chroma-db:
    driver: local
  nginx-cache:
    driver: local

networks:
  ipc-bns-network:
    driver: bridge
COMPOSE_CONFIG

echo -e "${GREEN}✓ docker-compose.local-ssl.yml created${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Local SSL Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "To start with HTTPS:"
echo -e "  ${YELLOW}docker-compose -f docker-compose.local-ssl.yml up -d${NC}"
echo ""
echo "Your app will be available at:"
echo -e "  🔒 ${GREEN}https://localhost${NC}"
echo -e "  🔒 ${GREEN}https://127.0.0.1${NC}"
echo -e "  🔒 ${GREEN}https://192.168.1.23${NC}"
echo ""
echo "Features:"
echo "  ✓ Trusted SSL certificates (no browser warnings)"
echo "  ✓ Auto-redirect HTTP → HTTPS"
echo "  ✓ Works in all browsers"
echo ""
echo "To stop:"
echo -e "  ${YELLOW}docker-compose -f docker-compose.local-ssl.yml down${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} The certificates are only trusted on this machine."
echo "      Other devices will show security warnings unless they"
echo "      also install the mkcert CA certificate."
echo ""
