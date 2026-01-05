# Local Development SSL/HTTPS Setup

This guide shows how to enable HTTPS on localhost for development and testing.

## Why Local SSL?

- Test HTTPS features before production deployment
- Test authentication flows that require secure contexts
- Test Service Workers and PWA features (require HTTPS)
- Match production environment more closely
- No mixed content warnings

## Quick Start

### One-Command Setup

```bash
# Run the automated setup script
./setup-local-ssl.sh
```

This will:
1. ✅ Install mkcert (if not already installed)
2. ✅ Create a local Certificate Authority
3. ✅ Generate SSL certificates for localhost
4. ✅ Configure nginx for HTTPS
5. ✅ Create docker-compose.local-ssl.yml

### Start with HTTPS

```bash
# Start all services with HTTPS enabled
docker-compose -f docker-compose.local-ssl.yml up -d

# View logs
docker-compose -f docker-compose.local-ssl.yml logs -f

# Stop services
docker-compose -f docker-compose.local-ssl.yml down
```

### Access Your App

Open in browser:
- 🔒 **https://localhost**
- 🔒 **https://127.0.0.1**
- 🔒 **https://192.168.1.23** (or your LAN IP)

**No browser warnings!** The certificates are trusted by your system.

---

## What is mkcert?

[mkcert](https://github.com/FiloSottile/mkcert) is a simple tool for making locally-trusted development certificates.

**Benefits:**
- Creates certificates trusted by your browser
- No security warnings
- Easy to use
- Automatically trusts the CA
- Works on all major browsers

**How it works:**
1. Creates a local Certificate Authority (CA)
2. Installs that CA in your system's trust store
3. Issues certificates signed by that CA
4. Your browser trusts the CA, so it trusts the certificates

---

## Manual Setup (Alternative)

If the script doesn't work, you can set up manually:

### Step 1: Install mkcert

**Linux (Ubuntu/Debian):**
```bash
sudo apt install wget libnss3-tools
wget https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
chmod +x mkcert-v1.4.4-linux-amd64
sudo mv mkcert-v1.4.4-linux-amd64 /usr/local/bin/mkcert
```

**macOS:**
```bash
brew install mkcert
brew install nss  # for Firefox
```

**Windows:**
```bash
choco install mkcert
```

### Step 2: Install Local CA

```bash
mkcert -install
```

This creates and installs a local Certificate Authority.

### Step 3: Generate Certificates

```bash
# Create directory
mkdir -p nginx/ssl-local

# Generate certificates
cd nginx/ssl-local
mkcert localhost 127.0.0.1 ::1 192.168.1.23

# Rename files for easier reference
mv localhost+*.pem cert.pem
mv localhost+*-key.pem key.pem

cd ../..
```

### Step 4: Use docker-compose.local-ssl.yml

The setup script creates this file. Just run:

```bash
docker-compose -f docker-compose.local-ssl.yml up -d
```

---

## Accessing from Mobile Devices

To test HTTPS on your phone/tablet on the same network:

### Step 1: Find Your Computer's IP

```bash
# Linux/Mac
ip addr show | grep inet

# or
ifconfig | grep inet

# Look for 192.168.x.x address
```

### Step 2: Install mkcert CA on Mobile

```bash
# Get the CA certificate
mkcert -CAROOT
# This shows where the CA cert is stored (e.g., ~/.local/share/mkcert)

# Copy the rootCA.pem file to your phone
# Then install it:
# - iOS: Settings → General → Profile
# - Android: Settings → Security → Install from storage
```

### Step 3: Access via IP

On your phone, visit: `https://192.168.1.23` (replace with your IP)

---

## Switching Between HTTP and HTTPS

### For HTTP (default):
```bash
docker-compose up -d
# Access: http://localhost:3000
```

### For HTTPS (local development):
```bash
docker-compose -f docker-compose.local-ssl.yml up -d
# Access: https://localhost
```

### For HTTPS (production with Let's Encrypt):
```bash
# See HTTPS_SETUP_GUIDE.md
./setup-ssl.sh
./enable-https.sh
```

---

## Configuration Files

### docker-compose.local-ssl.yml

Key differences from docker-compose.yml:

```yaml
# Frontend environment
environment:
  - REACT_APP_API_URL=https://localhost  # HTTPS instead of HTTP

# Nginx volumes
volumes:
  - ./nginx/ssl-local:/etc/nginx/ssl-local:ro  # Local SSL certs

# Nginx config
- ./nginx/conf.d/app-local-https.conf:/etc/nginx/conf.d/default.conf:ro
```

### nginx/conf.d/app-local-https.conf

```nginx
server {
    listen 443 ssl http2;

    ssl_certificate /etc/nginx/ssl-local/cert.pem;
    ssl_certificate_key /etc/nginx/ssl-local/key.pem;

    # ... rest of config
}
```

---

## Troubleshooting

### Issue: "mkcert: command not found"

**Solution:** Install mkcert manually (see Manual Setup above)

### Issue: Browser still shows warning

**Solutions:**
```bash
# 1. Reinstall CA
mkcert -uninstall
mkcert -install

# 2. Regenerate certificates
cd nginx/ssl-local
rm *.pem
mkcert localhost 127.0.0.1 192.168.1.23
mv localhost+*.pem cert.pem
mv localhost+*-key.pem key.pem

# 3. Restart browser completely
```

### Issue: "NET::ERR_CERT_AUTHORITY_INVALID"

**Cause:** CA not trusted by browser

**Solution:**
```bash
# Check where CA is installed
mkcert -CAROOT

# Reinstall
mkcert -install

# Restart browser
```

### Issue: Certificate for wrong domain

**Solution:** Regenerate with correct domains:
```bash
cd nginx/ssl-local
mkcert localhost 127.0.0.1 your-ip-here
mv localhost+*.pem cert.pem
mv localhost+*-key.pem key.pem
docker-compose -f docker-compose.local-ssl.yml restart nginx
```

### Issue: "SSL certificate problem"

**Solution:**
```bash
# Check certificate files exist
ls -la nginx/ssl-local/
# Should show: cert.pem and key.pem

# Check nginx config
docker exec ipc-bns-nginx nginx -t

# View nginx logs
docker-compose -f docker-compose.local-ssl.yml logs nginx
```

---

## Comparison: Local vs Production SSL

| Feature | Local (mkcert) | Production (Let's Encrypt) |
|---------|---------------|---------------------------|
| **Trust** | Only your machine | Globally trusted |
| **Setup** | Instant | Requires domain & DNS |
| **Cost** | Free | Free |
| **Renewal** | Manual (rarely needed) | Automatic |
| **Use case** | Development | Production |
| **Domain** | localhost, IPs | Real domains only |

---

## Best Practices

### Development Workflow

1. **Daily development:** Use HTTP (faster, simpler)
   ```bash
   docker-compose up -d
   ```

2. **Testing HTTPS features:** Use local SSL
   ```bash
   docker-compose -f docker-compose.local-ssl.yml up -d
   ```

3. **Production deployment:** Use Let's Encrypt
   ```bash
   ./setup-ssl.sh
   ./enable-https.sh
   ```

### Security Notes

⚠️ **Never commit** the following to git:
- `nginx/ssl-local/*.pem` (certificates)
- `~/.local/share/mkcert/rootCA*` (CA private key)

✅ **Safe to commit:**
- `docker-compose.local-ssl.yml`
- `nginx/conf.d/app-local-https.conf`
- `setup-local-ssl.sh`

---

## Uninstalling

To remove mkcert and certificates:

```bash
# Remove certificates
rm -rf nginx/ssl-local/

# Uninstall CA from system
mkcert -uninstall

# Remove mkcert (optional)
sudo rm /usr/local/bin/mkcert
```

---

## Additional Resources

- [mkcert GitHub](https://github.com/FiloSottile/mkcert)
- [Why HTTPS for local development?](https://web.dev/when-to-use-local-https/)
- [Chrome HTTPS requirements](https://developers.google.com/web/fundamentals/security/encrypt-in-transit/why-https)

---

## Quick Reference

```bash
# Setup (one time)
./setup-local-ssl.sh

# Start with HTTPS
docker-compose -f docker-compose.local-ssl.yml up -d

# Access
open https://localhost

# Stop
docker-compose -f docker-compose.local-ssl.yml down

# Logs
docker-compose -f docker-compose.local-ssl.yml logs -f nginx

# Regenerate certificates
cd nginx/ssl-local && mkcert localhost 127.0.0.1 192.168.1.23
```

---

**Happy secure local development! 🔒**
