# Troubleshooting: Case Search Blank Page

This guide helps diagnose and fix the blank page issue on the Case Search page.

## Quick Fix - Try This First

```bash
# Run the automated rebuild script
./rebuild-frontend.sh
```

After rebuild, **clear your browser cache** or try in incognito mode.

---

## Manual Rebuild Steps

If the automated script doesn't work, try these manual steps:

```bash
# 1. Stop and remove containers
docker-compose down

# 2. Remove frontend image
docker rmi ipc_bns_mig_frontend

# 3. Rebuild with no cache
docker-compose build --no-cache frontend

# 4. Start everything
docker-compose up -d

# 5. Check logs
docker-compose logs -f frontend
```

---

## Diagnostic Checklist

### 1. Check Browser Console (MOST IMPORTANT)

1. Open the application in your browser
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Navigate to `/cases` page
5. **Look for RED error messages** - these tell us exactly what's wrong

**Common errors and fixes:**

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `useAuth must be used within an AuthProvider` | AuthProvider not wrapping component | Check App.js structure |
| `Cannot read property 'isAuthenticated' of null` | AuthContext not initialized | Verify AuthProvider is present |
| `Failed to compile` | Syntax error | Check browser console for line number |
| `Module not found` | Missing import | Verify all imports exist |

### 2. Check Network Tab

1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Refresh the page
4. Check if `main.chunk.js` and `bundle.js` files are loading
5. Look for any failed requests (red status codes)

### 3. Check Container Logs

```bash
# Frontend logs
docker-compose logs frontend | tail -50

# Backend logs (in case API is failing)
docker-compose logs backend | tail -50
```

Look for:
- ✅ `webpack compiled successfully`
- ❌ `ERROR in ...`
- ❌ `Module not found`
- ❌ `SyntaxError`

### 4. Verify File Changes

```bash
# Check if CaseSearch.js has the auth loading fix
grep -n "authLoading" frontend/src/pages/CaseSearch.js

# Should show line with: const { isAuthenticated, loading: authLoading } = useAuth();
```

### 5. Clear Browser Cache

The browser might be serving old cached files:

**Chrome/Edge:**
- Press `Ctrl + Shift + Delete`
- Select "Cached images and files"
- Click "Clear data"

**Firefox:**
- Press `Ctrl + Shift + Delete`
- Select "Cache"
- Click "Clear Now"

**Or use Incognito/Private Mode:**
- Chrome: `Ctrl + Shift + N`
- Firefox: `Ctrl + Shift + P`

---

## Common Issues and Solutions

### Issue 1: Page Shows Loading Forever
**Cause:** AuthContext stuck in loading state
**Fix:** Check if backend is running and `/auth/me` endpoint works

```bash
# Test backend
curl http://localhost:8000/health
curl http://localhost:8000/auth/me
```

### Issue 2: "Sign In" Prompt Shows Even When Logged In
**Cause:** AuthContext not detecting authentication
**Fix:** Check localStorage in browser DevTools

1. Open DevTools (F12)
2. Go to **Application** tab
3. Check **Local Storage**
4. Verify `access_token` exists

### Issue 3: Component Not Rendering At All
**Cause:** JavaScript error during render
**Fix:** Check browser console for errors (see Diagnostic #1 above)

### Issue 4: Old Code Still Running After Rebuild
**Cause:** Browser cache or Docker cache
**Fix:**
1. Hard refresh: `Ctrl + Shift + R`
2. Clear browser cache
3. Rebuild with `--no-cache` flag

---

## Debug Mode

Add console logs to identify where the component fails:

Edit `frontend/src/pages/CaseSearch.js` and add:

```javascript
function CaseSearch() {
  console.log('🔍 CaseSearch component mounting');
  const navigate = useNavigate();
  const { isAuthenticated, loading: authLoading } = useAuth();
  console.log('🔑 Auth state:', { isAuthenticated, authLoading });

  // ... rest of component
}
```

Then check browser console to see which logs appear.

---

## Still Not Working?

If none of the above helps, gather this information:

1. **Browser Console Screenshot** (F12 → Console tab)
2. **Network Tab Screenshot** (F12 → Network tab)
3. **Frontend Container Logs:**
   ```bash
   docker-compose logs frontend > frontend-logs.txt
   ```
4. **Browser Details:**
   - Browser name and version
   - Operating system
   - Any browser extensions enabled

---

## Files Modified in Latest Fix

The following files were updated to fix the blank page issue:

1. **frontend/src/pages/CaseSearch.js**
   - Added `authLoading` state handling
   - Added loading spinner while auth initializes
   - Fixed early return logic

2. **frontend/src/styles/App.css**
   - Added `.loading-container` styles
   - Added `.loading-spinner` animation

These changes ensure the component handles the authentication loading state properly instead of showing a blank page.

---

## Verification

After applying fixes, verify the page works:

1. **When not logged in:**
   - Should show "Authentication Required" message with login/signup buttons
   - Should show popular cases preview

2. **When logged in:**
   - Should show search form
   - Should show usage indicator
   - Should show popular cases
   - Search should work and return results

---

## Contact

If the issue persists after trying all steps above, please provide:
- Browser console errors
- Container logs
- Steps you've already tried

This will help identify the root cause more quickly.
