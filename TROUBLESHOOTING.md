# Troubleshooting Guide - IPC/BNS Legal Reasoning Agent

## Common Issues and Solutions

### 1. Database Initialization Error (EOFError)

**Error Message:**
```
EOFError: EOF when reading a line
Error: EOF when reading a line at init_db.py
```

**Cause:** The database initialization script was trying to prompt for user input in a non-interactive Docker environment.

**Solution:** ✅ **FIXED** in latest commit

The system now:
- Automatically detects non-interactive environments
- Skips initialization prompt if database already exists
- Reuses existing data on container restarts

**To apply the fix:**

```bash
# Stop existing containers
docker-compose down

# Remove old volumes (optional - only if you want fresh data)
docker-compose down -v

# Rebuild and restart with the fix
docker-compose up --build
```

**Force Database Reinitialization:**

If you need to clear and repopulate the database:

```bash
# Method 1: Environment variable
FORCE_DB_INIT=true docker-compose up --build

# Method 2: Manual (if running without Docker)
cd backend/app
python init_db.py --force
```

---

### 2. Network Error / Failed to Load Statistics

**Symptoms:**
- Frontend shows "Failed to load statistics: Network Error"
- API requests fail
- Backend not responding

**Possible Causes:**

#### A. Backend Container Not Running

```bash
# Check container status
docker-compose ps

# View backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

#### B. Backend Still Initializing

The backend takes 30-60 seconds to:
1. Initialize database
2. Load sentence transformer models
3. Create vector embeddings
4. Start FastAPI server

**Solution:** Wait 1-2 minutes after `docker-compose up`, then refresh the page.

#### C. Port Conflict

Another service might be using port 8000.

```bash
# Check what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Solution: Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

---

### 3. Out of Memory During Initialization

**Error:**
```
Killed
Container exited with code 137
```

**Cause:** Sentence transformer models require significant RAM for creating embeddings.

**Solutions:**

#### A. Increase Docker Memory

Docker Desktop:
- Settings → Resources → Memory
- Increase to at least 4GB (8GB recommended)

#### B. Use Lighter Model

Edit `backend/app/rag_system.py`:

```python
# Change from:
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# To lighter model:
self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
```

#### C. Reduce Batch Size

In `rag_system.py`, add batch processing:

```python
# In add_cases method
batch_size = 5
for i in range(0, len(cases), batch_size):
    batch = cases[i:i+batch_size]
    # Process batch...
```

---

### 4. ChromaDB Persistence Issues

**Symptoms:**
- Cases need to be re-indexed every restart
- "Collection not found" errors

**Solution:**

Ensure volumes are properly mounted:

```yaml
# In docker-compose.yml
volumes:
  - chroma-db:/app/chroma_db  # Persistent volume
```

**Clear and Rebuild:**

```bash
docker-compose down -v  # Remove volumes
docker-compose up --build
```

---

### 5. Frontend Build Failures

**Error:**
```
npm ERR! Failed at build script
```

**Solutions:**

#### A. Node Version Mismatch

```bash
# Ensure Node 18+ is used
node --version

# Update Dockerfile if needed:
FROM node:18-alpine
```

#### B. Clear npm Cache

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### C. Memory Issues

Increase Node memory:

```bash
# In frontend/package.json
"scripts": {
  "build": "NODE_OPTIONS='--max-old-space-size=4096' react-scripts build"
}
```

---

### 6. CORS Errors

**Error:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Cause:** Frontend trying to access backend from different origin.

**Solution:**

Backend `main.py` already has CORS configured. Verify:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For production**, update to specific origins:

```python
allow_origins=["https://yourdomain.com"]
```

---

### 7. Database Lock Errors

**Error:**
```
database is locked
```

**Cause:** Multiple processes trying to access SQLite simultaneously.

**Solutions:**

#### A. Use PostgreSQL (Production)

```python
# In database.py
DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
```

#### B. Increase Timeout

```python
# In database.py
engine = create_engine(
    db_path,
    connect_args={"timeout": 30}  # Increased timeout
)
```

---

### 8. Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'xyz'
```

**Solutions:**

```bash
# Rebuild backend container
docker-compose build backend

# Or manually install
cd backend
pip install -r requirements.txt
```

---

### 9. Vector Search Returns No Results

**Symptoms:**
- Case search always returns empty
- RAG system not finding matches

**Debug Steps:**

```bash
# Check if ChromaDB has data
docker-compose exec backend python -c "
from app.rag_system import CaseLawRAG
rag = CaseLawRAG()
print(rag.collection.count())
"

# Should print number > 0
```

**Solution:**

Force reinitialize:

```bash
FORCE_DB_INIT=true docker-compose up --build
```

---

### 10. Slow Performance

**Symptoms:**
- API requests take too long
- UI is laggy

**Optimizations:**

#### A. Use Production Build

Frontend is already optimized with nginx in production.

#### B. Add Caching

Install Redis and add caching layer:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_section_analysis(section):
    # Cached analysis
    pass
```

#### C. Database Indexing

Already indexed on `ipc_section`, `bns_section`, and foreign keys.

---

## Health Check Commands

```bash
# Check all containers
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# View logs
docker-compose logs -f

# Check database
docker-compose exec backend python -c "
from app.database import init_db, IPCBNSMapping
engine, SessionLocal = init_db()
db = SessionLocal()
print(f'Sections: {db.query(IPCBNSMapping).count()}')
"
```

---

## Reset Everything

If all else fails, complete reset:

```bash
# Stop and remove everything
docker-compose down -v

# Remove Docker images
docker-compose rm -f

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up
```

---

## Getting Help

1. **Check Logs First:**
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. **Enable Debug Mode:**
   ```python
   # In main.py
   uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
   ```

3. **Test API Directly:**
   ```bash
   # Test health
   curl http://localhost:8000/health

   # Test sections endpoint
   curl http://localhost:8000/sections
   ```

4. **Check Browser Console:**
   - Open DevTools (F12)
   - Check Console for JavaScript errors
   - Check Network tab for failed requests

---

## Known Limitations

1. **SQLite in Production:**
   - Not ideal for concurrent writes
   - Consider PostgreSQL for production

2. **Vector Search Scale:**
   - ChromaDB works well for <10,000 documents
   - For larger datasets, consider Pinecone or Weaviate

3. **No Authentication:**
   - Current version has no auth
   - Add JWT tokens for production

4. **Memory Usage:**
   - Sentence transformers require ~2GB RAM
   - Plan accordingly for hosting

---

## Performance Benchmarks

**Expected Performance (on 4GB RAM):**

| Operation | Time |
|-----------|------|
| Container Startup | 30-60s |
| Database Init (first time) | 45-90s |
| Section Analysis | <500ms |
| Case Search | <1s |
| Memo Generation | 1-2s |
| Frontend Load | <2s |

---

## Support

- **Documentation:** See README.md and USAGE_GUIDE.md
- **API Docs:** http://localhost:8000/docs
- **Issues:** Report on GitHub

---

**Last Updated:** 2026-01-03
