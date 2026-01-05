# HTTPS Setup Guide with Let's Encrypt

This guide will help you set up free SSL/TLS certificates using Let's Encrypt for your IPC/BNS Legal Reasoning Agent.

## Prerequisites

Before starting, ensure:

1. **Domain Name**: You have a registered domain (e.g., `legalai.example.com`)
2. **DNS Configuration**: Your domain's A record points to this server's public IP
3. **Port Access**: Ports 80 and 443 are open and accessible from the internet
4. **Docker**: Docker and docker-compose are installed

## Quick Start

### Step 1: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your domain and email
nano .env
```

Update these values in `.env`:
```bash
DOMAIN_NAME=your-domain.com
LETSENCRYPT_EMAIL=your-email@example.com
CERTBOT_ENV=staging  # Use 'staging' for testing first
```

### Step 2: Verify DNS

Make sure your domain points to this server:

```bash
# Check DNS resolution
dig your-domain.com

# or
nslookup your-domain.com

# Should show your server's public IP
```

### Step 3: Start Services with HTTP

```bash
# Start the application (HTTP only for now)
docker-compose up -d

# Verify services are running
docker-compose ps

# Check if nginx is accessible
curl http://your-domain.com
```

### Step 4: Obtain SSL Certificate (Test Mode)

```bash
# Make script executable
chmod +x setup-ssl.sh enable-https.sh

# Run SSL setup (uses staging certificates for testing)
./setup-ssl.sh
```

**Important**: The first run uses Let's Encrypt **staging environment** to avoid rate limits. Staging certificates are not trusted by browsers but let you test the setup.

### Step 5: Enable HTTPS

If Step 4 succeeded:

```bash
# Switch nginx to HTTPS configuration
./enable-https.sh
```

Your site should now be accessible at `https://your-domain.com` (with a security warning since it's a staging certificate).

### Step 6: Get Production Certificates

Once testing is successful:

```bash
# Edit .env and change to production
nano .env
# Set: CERTBOT_ENV=production

# Re-run SSL setup for real certificates
./setup-ssl.sh

# Re-enable HTTPS
./enable-https.sh
```

Now your site will have trusted SSL certificates! 🎉

## Detailed Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DOMAIN_NAME` | Your domain name | `legalai.example.com` |
| `LETSENCRYPT_EMAIL` | Email for certificate notifications | `admin@example.com` |
| `CERTBOT_ENV` | Certificate environment: `staging` or `production` | `staging` |

### Directory Structure

```
ipc_bns_mig/
├── nginx/
│   ├── nginx.conf                        # Main nginx configuration
│   └── conf.d/
│       ├── app.conf.template            # HTTPS configuration
│       └── app-http-only.conf.template  # HTTP-only configuration
├── certbot/
│   ├── conf/                            # SSL certificates stored here
│   └── www/                             # ACME challenge directory
├── docker-compose.yml                   # Updated with nginx & certbot
├── .env                                 # Your configuration (create this)
├── setup-ssl.sh                         # Certificate setup script
└── enable-https.sh                      # Enable HTTPS script
```

## Certificate Renewal

Certificates auto-renew every 12 hours via the certbot container. No manual intervention needed!

To manually renew:

```bash
docker-compose run --rm certbot renew
docker-compose restart nginx
```

## Troubleshooting

### Issue: "Failed to obtain SSL certificate"

**Causes:**
1. DNS not pointing to server
2. Port 80 not accessible
3. Firewall blocking traffic

**Solutions:**
```bash
# Check DNS
dig your-domain.com

# Check if port 80 is accessible from outside
curl -I http://your-domain.com

# Check nginx logs
docker-compose logs nginx

# Check certbot logs
docker-compose logs certbot
```

### Issue: "Connection refused" on HTTPS

**Cause:** SSL certificates not properly configured

**Solution:**
```bash
# Verify certificates exist
ls -la certbot/conf/live/your-domain.com/

# Check nginx configuration
docker exec ipc-bns-nginx nginx -t

# Restart nginx
docker-compose restart nginx
```

### Issue: Rate limit exceeded

**Cause:** Too many certificate requests (Let's Encrypt limit: 5/week)

**Solution:**
- Wait a week, or
- Use staging environment for testing:
  ```bash
  # In .env
  CERTBOT_ENV=staging
  ```

### Issue: Browser shows "Certificate not trusted"

**Cause:** Using staging certificates

**Solution:**
```bash
# Switch to production in .env
CERTBOT_ENV=production

# Re-run setup
./setup-ssl.sh
./enable-https.sh
```

## Security Features

The nginx configuration includes:

- ✅ **TLS 1.2 and 1.3** - Modern encryption protocols
- ✅ **Strong ciphers** - Mozilla Intermediate configuration
- ✅ **HSTS** - HTTP Strict Transport Security
- ✅ **OCSP Stapling** - Faster certificate verification
- ✅ **Security headers** - XSS, clickjacking protection
- ✅ **Auto-redirect** - HTTP → HTTPS
- ✅ **Auto-renewal** - Certificates renew automatically

## Manual Steps (Alternative Method)

If the scripts don't work, you can manually obtain certificates:

### 1. Start services
```bash
docker-compose up -d
```

### 2. Obtain certificate
```bash
docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d your-domain.com
```

### 3. Update nginx config
```bash
# Edit docker-compose.yml
# Change nginx command from:
#   app-http-only.conf.template
# to:
#   app.conf.template

# Restart nginx
docker-compose restart nginx
```

## Architecture

```
Internet
    ↓
Port 80/443 (nginx)
    ↓
├─→ Frontend (React) - Port 80 internal
│   └─→ Serves static files
│
└─→ Backend (FastAPI) - Port 8000 internal
    └─→ API endpoints (/auth, /cases, etc.)
```

**Benefits:**
- Single entry point (nginx)
- SSL termination at nginx
- Backend doesn't need SSL configuration
- Better performance with caching
- Enhanced security

## Testing

### Test HTTP → HTTPS redirect
```bash
curl -I http://your-domain.com
# Should show: Location: https://your-domain.com
```

### Test HTTPS
```bash
curl -I https://your-domain.com
# Should show: HTTP/2 200
```

### Test SSL grade
Visit: https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com

Should get **A** or **A+** rating!

## Maintenance

### View certificate info
```bash
docker-compose run --rm certbot certificates
```

### Force renewal
```bash
docker-compose run --rm certbot renew --force-renewal
docker-compose restart nginx
```

### Check renewal status
```bash
# Renewal happens automatically via certbot container
docker-compose logs certbot | grep -i renew
```

## Reverting to HTTP

If you need to disable HTTPS temporarily:

```bash
# Edit docker-compose.yml
# Change nginx command back to:
#   app-http-only.conf.template

# Restart nginx
docker-compose restart nginx
```

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)
- [Nginx SSL Configuration](https://ssl-config.mozilla.org/)
- [SSL Labs Test](https://www.ssllabs.com/ssltest/)

## Support

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Verify DNS: `dig your-domain.com`
3. Test connectivity: `curl http://your-domain.com`
4. Check firewall: `sudo ufw status` (if using ufw)

---

**Remember**: Always use **staging** environment for testing to avoid hitting Let's Encrypt rate limits!
