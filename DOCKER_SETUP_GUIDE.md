# Docker Setup Guide

This project has multiple Docker Compose configurations for different use cases.

## Available Configurations

### 1. **docker-compose.yml** - Development with Optional nginx
**Best for:** Local development and testing

```bash
docker-compose up -d
```

**Configuration:**
- Backend: `localhost:8000`
- Frontend: `localhost:3000`
- Includes nginx (optional) on ports 80/443
- Direct access to backend and frontend

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Via nginx: http://localhost (if nginx service running)

---

### 2. **docker-compose.local.yml** - Simple Local Development
**Best for:** Quick local testing without nginx

```bash
docker-compose -f docker-compose.local.yml up -d
```

**Configuration:**
- Backend: `localhost:8000` (direct)
- Frontend: `localhost:3000` (direct)
- No nginx, no SSL
- Simplest setup

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

### 3. **docker-compose.local-ssl.yml** - Local HTTPS
**Best for:** Testing HTTPS features locally

```bash
# First, run setup
./setup-local-ssl.sh

# Then start
docker-compose -f docker-compose.local-ssl.yml up -d
```

**Configuration:**
- Backend: Internal only (via nginx)
- Frontend: Internal only (via nginx)
- Nginx on ports 80/443 with mkcert SSL
- Trusted certificates (no warnings)

**Access:**
- Frontend: https://localhost
- Backend: https://localhost/api/* (via nginx)

**See:** `LOCAL_SSL_SETUP.md` for details

---

### 4. **Production with Let's Encrypt**
**Best for:** Production deployment with real domain

```bash
# Setup SSL certificates
./setup-ssl.sh

# Enable HTTPS
./enable-https.sh

# Start services
docker-compose up -d
```

**Configuration:**
- Backend: Internal only (via nginx)
- Frontend: Internal only (via nginx)
- Nginx with Let's Encrypt SSL
- Auto-renewing certificates

**See:** `HTTPS_SETUP_GUIDE.md` for details

---

## Quick Start Matrix

| Goal | Command | Access |
|------|---------|--------|
| **Quick local test** | `docker-compose up -d` | http://localhost:3000 |
| **Simple dev** | `docker-compose -f docker-compose.local.yml up -d` | http://localhost:3000 |
| **Test HTTPS locally** | `./setup-local-ssl.sh && docker-compose -f docker-compose.local-ssl.yml up -d` | https://localhost |
| **Production** | `./setup-ssl.sh && ./enable-https.sh` | https://your-domain.com |

---

## Current Issue Fix

If you're getting `ERR_CONNECTION_REFUSED` when registering:

```bash
# Stop current setup
docker-compose down

# Use simple local development setup
docker-compose -f docker-compose.local.yml up -d

# Or restart with main docker-compose (now fixed)
docker-compose up -d

# Fix database if needed
./fix-auth.sh
```

Then access: http://localhost:3000

---

## Port Reference

### Default Setup (docker-compose.yml)
```
8000  → Backend API
3000  → Frontend app
80    → nginx (HTTP)
443   → nginx (HTTPS)
```

### Local Simple (docker-compose.local.yml)
```
8000  → Backend API
3000  → Frontend app
```

### Local SSL (docker-compose.local-ssl.yml)
```
80    → nginx (redirects to 443)
443   → nginx (HTTPS)
        ├─ / → Frontend
        └─ /api/* → Backend
```

---

## Service Dependencies

```
Frontend → Backend
nginx → Frontend + Backend
certbot → nginx (for SSL renewal)
```

---

## Common Commands

### Start services
```bash
# Default
docker-compose up -d

# Local dev
docker-compose -f docker-compose.local.yml up -d

# Local SSL
docker-compose -f docker-compose.local-ssl.yml up -d
```

### Stop services
```bash
docker-compose down
# or
docker-compose -f docker-compose.local.yml down
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Rebuild
```bash
# Rebuild all
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache backend
docker-compose build --no-cache frontend

# Rebuild and restart
docker-compose up -d --build
```

### Check status
```bash
docker-compose ps
```

---

## Troubleshooting

### Backend not accessible

**Error:** `ERR_CONNECTION_REFUSED` on `localhost:8000`

**Solution:**
```bash
# Make sure using correct docker-compose file
docker-compose -f docker-compose.local.yml up -d

# Or check if backend is running
docker ps | grep backend

# Check backend logs
docker logs ipc-bns-backend
```

### Frontend shows blank page

**Solution:**
```bash
# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Clear browser cache
# Or use incognito mode
```

### nginx conflicts

**Error:** `Port 80 already in use`

**Solution:**
```bash
# Option 1: Stop nginx container
docker stop ipc-bns-nginx

# Option 2: Use simple local setup (no nginx)
docker-compose -f docker-compose.local.yml up -d

# Option 3: Stop system nginx
sudo systemctl stop nginx
```

### Database issues

**Solution:**
```bash
./fix-auth.sh
```

---

## Environment Variables

Create a `.env` file for custom configuration:

```bash
# Copy example
cp .env.example .env

# Edit as needed
nano .env
```

**Common variables:**
```bash
# For local development
REACT_APP_API_URL=http://localhost:8000

# For production with SSL
DOMAIN_NAME=your-domain.com
LETSENCRYPT_EMAIL=admin@example.com
CERTBOT_ENV=production
```

---

## Switching Between Setups

### From Default to Simple Local
```bash
docker-compose down
docker-compose -f docker-compose.local.yml up -d
```

### From Simple to SSL
```bash
docker-compose -f docker-compose.local.yml down
./setup-local-ssl.sh
docker-compose -f docker-compose.local-ssl.yml up -d
```

### From Local to Production
```bash
docker-compose down
./setup-ssl.sh
./enable-https.sh
docker-compose up -d
```

---

## Best Practices

1. **Development:** Use `docker-compose.local.yml` - fastest, simplest
2. **Testing HTTPS:** Use `docker-compose.local-ssl.yml` - test SSL features
3. **Production:** Use main `docker-compose.yml` with Let's Encrypt
4. **Debugging:** Use local setup with direct port access
5. **Keep separate:** Don't mix configurations - fully stop one before starting another

---

## Quick Reference

```bash
# Simple local dev (recommended for now)
docker-compose -f docker-compose.local.yml up -d
# Access: http://localhost:3000

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Stop
docker-compose -f docker-compose.local.yml down

# Fix auth
./fix-auth.sh

# Rebuild after code changes
docker-compose -f docker-compose.local.yml build frontend
docker-compose -f docker-compose.local.yml up -d
```

---

**For current connection issue, use:**

```bash
docker-compose down
docker-compose -f docker-compose.local.yml up -d
./fix-auth.sh
```

Then open: http://localhost:3000
