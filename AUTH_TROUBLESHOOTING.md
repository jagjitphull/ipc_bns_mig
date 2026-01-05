# Authentication Troubleshooting Guide

This guide helps fix login and registration issues.

## Quick Fix (Try This First!)

```bash
# Run the automated fix script
./fix-auth.sh
```

This will:
1. ✅ Check if database has all auth tables
2. ✅ Create missing tables if needed
3. ✅ Test authentication system
4. ✅ Report any issues found

---

## Common Issues and Solutions

### Issue 1: "Registration failed" or "Email already registered"

**Symptoms:**
- Cannot register new users
- Get error message during registration
- Form submission fails

**Solutions:**

#### A. Run database repair
```bash
./fix-auth.sh
```

#### B. Check backend logs
```bash
docker logs ipc-bns-backend --tail 50
```

Look for errors like:
- `Table 'users' doesn't exist`
- `no such table: users`
- `UNIQUE constraint failed`

#### C. Manual database check
```bash
# Enter backend container
docker exec -it ipc-bns-backend bash

# Run Python
python

# Check database
>>> from database import init_db
>>> engine, SessionLocal = init_db()
>>> db = SessionLocal()
>>> from auth_models import User
>>> db.query(User).count()
# If this works, database is OK
# If error, database needs repair
```

---

### Issue 2: "Old user cannot login"

**Symptoms:**
- User previously registered
- Now cannot log in
- Gets "Incorrect email or password" error

**Possible Causes:**

#### A. Database was reset/cleared
**Solution:** Users need to re-register

#### B. Password hash algorithm changed
**Solution:** User must reset password (or re-register)

#### C. User table structure changed
**Solution:** Run database repair
```bash
./fix-auth.sh
```

#### D. Check if user exists
```bash
docker exec -it ipc-bns-backend python << 'PYTHON'
from database import init_db
from auth_models import User

engine, SessionLocal = init_db()
db = SessionLocal()

# List all users
users = db.query(User).all()
print(f"\nTotal users: {len(users)}")
for user in users:
    print(f"  - {user.email} (ID: {user.id}, Active: {user.is_active})")
PYTHON
```

---

### Issue 3: 401 Unauthorized after login

**Symptoms:**
- Login succeeds
- Gets token
- But API calls return 401

**Solution:**
This is the axios interceptor issue we already fixed. Make sure you:

```bash
# Rebuild frontend with latest code
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Clear browser cache
# Or use incognito mode
```

---

### Issue 4: Database tables don't exist

**Symptoms:**
- Backend logs show "no such table: users"
- Registration and login both fail
- Database error messages

**Solution:**

```bash
# Option 1: Automated repair
./fix-auth.sh

# Option 2: Manual repair
docker exec -it ipc-bns-backend python /app/app/repair_database.py

# Option 3: Full database reset (CAUTION: Deletes all data!)
docker exec -it ipc-bns-backend rm /app/data/legal_reasoning.db
docker exec -it ipc-bns-backend python /app/app/init_db.py --force
docker restart ipc-bns-backend
```

---

## Manual Database Inspection

### Check what tables exist

```bash
docker exec -it ipc-bns-backend python << 'PYTHON'
from sqlalchemy import inspect, create_engine

engine = create_engine("sqlite:///./data/legal_reasoning.db")
inspector = inspect(engine)

print("\nExisting tables:")
for table in inspector.get_table_names():
    print(f"  ✓ {table}")
PYTHON
```

### Expected auth tables:
- ✅ `users`
- ✅ `subscriptions`
- ✅ `usage_logs`
- ✅ `saved_analyses`
- ✅ `api_keys`
- ✅ `payment_history`

### Check user count

```bash
docker exec -it ipc-bns-backend python << 'PYTHON'
from database import init_db
from auth_models import User

engine, SessionLocal = init_db()
db = SessionLocal()

count = db.query(User).count()
print(f"Users in database: {count}")

if count > 0:
    users = db.query(User).all()
    for user in users:
        print(f"  - {user.email}")
PYTHON
```

---

## Frontend Issues

### Check browser console

1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Look for errors related to:
   - `Failed to fetch`
   - `401 Unauthorized`
   - `Network request failed`
   - `CORS error`

### Check local storage

1. Open Developer Tools (F12)
2. Go to Application tab (Chrome) or Storage tab (Firefox)
3. Check Local Storage
4. Look for:
   - `access_token`
   - `refresh_token`
   - `user`

If tokens exist but requests fail → Axios interceptor issue
If tokens don't exist after login → Login response issue

### Test API directly

```bash
# Test registration
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'

# If successful, you'll get access_token and refresh_token
# If error, check the error message

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

---

## Complete Reset (Last Resort)

⚠️ **WARNING:** This deletes ALL data including users, cases, and sections!

```bash
# Stop all containers
docker-compose down

# Remove database file
rm -rf backend/data/legal_reasoning.db
rm -rf backend/chroma_db/

# Remove volumes
docker volume rm ipc_bns_mig_backend-data
docker volume rm ipc_bns_mig_chroma-db

# Rebuild and start
docker-compose build --no-cache
docker-compose up -d

# Initialize database
docker exec -it ipc-bns-backend python /app/app/init_db.py --force

# Test registration
# Try registering a new user at: http://localhost:3000/register
```

---

## Verification Checklist

After fixing, verify:

### Backend
- [ ] Backend container running: `docker ps | grep ipc-bns-backend`
- [ ] Database file exists: `docker exec ipc-bns-backend ls -la /app/data/`
- [ ] Auth tables exist: `./fix-auth.sh`
- [ ] Backend logs clean: `docker logs ipc-bns-backend`

### Frontend
- [ ] Frontend container running: `docker ps | grep ipc-bns-frontend`
- [ ] Frontend rebuilt with latest code
- [ ] Browser cache cleared
- [ ] No console errors

### API Endpoints
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] Registration endpoint accessible: `curl http://localhost:8000/docs`
- [ ] Can see API docs: Open http://localhost:8000/docs in browser

### Registration Flow
- [ ] Can access /register page
- [ ] Form loads correctly
- [ ] Can submit form
- [ ] Gets success message or token
- [ ] Redirected to dashboard or logged in

### Login Flow
- [ ] Can access /login page
- [ ] Form loads correctly
- [ ] Can enter credentials
- [ ] Gets token on success
- [ ] Can access protected pages
- [ ] Token persists in localStorage

---

## Getting More Help

If issues persist, gather this information:

### 1. Backend logs
```bash
docker logs ipc-bns-backend > backend-logs.txt
```

### 2. Database info
```bash
./fix-auth.sh > database-check.txt
```

### 3. Browser console
- Take screenshot of browser console (F12 → Console tab)

### 4. Network tab
- Open F12 → Network tab
- Try to login/register
- Screenshot any failed requests (in red)
- Click failed request → Response tab → Screenshot

### 5. System info
```bash
docker --version
docker-compose --version
docker ps
docker images | grep ipc
```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Table 'users' doesn't exist` | Auth tables not created | Run `./fix-auth.sh` |
| `UNIQUE constraint failed: users.email` | Email already registered | Use different email or check existing users |
| `Incorrect email or password` | Wrong credentials OR user doesn't exist | Verify user exists with manual DB check |
| `401 Unauthorized` | Token not sent OR invalid | Check axios interceptors are working |
| `Failed to fetch` | Backend not running OR wrong URL | Check backend is running on port 8000 |
| `CORS error` | Frontend/backend domain mismatch | Check REACT_APP_API_URL setting |

---

## Prevention

To avoid auth issues in the future:

1. **Don't delete database file manually** - Use scripts instead
2. **Run fix-auth.sh after major updates** - Ensures tables exist
3. **Keep database backups** - Copy `backend/data/legal_reasoning.db` regularly
4. **Check logs regularly** - `docker logs ipc-bns-backend`
5. **Use the repair script** - Don't manually edit database

---

## Quick Reference

```bash
# Fix auth database
./fix-auth.sh

# Check backend logs
docker logs ipc-bns-backend --tail 100 -f

# Restart backend
docker-compose restart backend

# Rebuild frontend (if axios issue)
docker-compose build --no-cache frontend && docker-compose up -d frontend

# Full reset (CAUTION!)
docker-compose down && rm backend/data/legal_reasoning.db && docker-compose up -d

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

---

**Most issues are fixed by running:** `./fix-auth.sh`

**If that doesn't work:** Check backend logs and browser console for specific errors.
