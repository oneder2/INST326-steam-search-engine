# Backend Startup Guide

Comprehensive guide for starting and running the Steam Game Search Engine backend API.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [First-Time Setup](#first-time-setup)
- [Daily Development Workflow](#daily-development-workflow)
- [Environment Configuration](#environment-configuration)
- [Starting the Backend](#starting-the-backend)
- [Verification Steps](#verification-steps)
- [Common Issues](#common-issues)
- [Integration with Frontend](#integration-with-frontend)

---

## ✅ Prerequisites

Before starting, ensure you have:

1. **Python 3.8+** installed
   ```bash
   python3 --version
   ```

2. **pip** (Python package manager)
   ```bash
   pip --version
   ```

3. **Supabase account** with database configured
   - Project URL
   - Publishable Key
   - Secret Key

4. **Git** (for version control)

5. **Terminal/Command line** access

---

## 🚀 First-Time Setup

Follow these steps for initial setup (only needed once):

### Step 1: Navigate to Backend Directory

```bash
# From project root
cd backend
```

### Step 2: Create Virtual Environment

**Why?** Isolates project dependencies from system Python

```bash
# Create virtual environment
python3 -m venv venv
```

This creates a `venv/` folder containing isolated Python environment.

### Step 3: Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

**Success indicator:** Your terminal prompt should show `(venv)` prefix

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Supabase client (database)
- Pydantic (data validation)
- Other utilities

**Expected output:** Installation progress for ~10 packages

### Step 5: Configure Environment Variables

The `.env` file should already exist in the **project root** (not in backend/).

**Verify it contains:**
```env
SUPABASE_URL=https://bcaoujpzhoyrinhaydyu.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_SRQy_SujM87ooPXX_uNqUA_RywMFt_J
SUPABASE_SECRET_KEY=[your_secret_key]

DATABASE_SCHEMA=steam
DATABASE_TABLE=games_prod

BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

**Location:** `/home/gellar/Desktop/maryland/INST326/INST326-project/INST326-steam-searcher-engine/.env`

---

## 🔄 Daily Development Workflow

For subsequent development sessions:

### 1. Navigate to Backend Directory

```bash
cd /home/gellar/Desktop/maryland/INST326/INST326-project/INST326-steam-searcher-engine/backend
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate  # Linux/Mac
```

### 3. Start the Backend Server

```bash
python -m app.main
```

**Alternative start methods:**

```bash
# Method 1: Direct Python execution (recommended for development)
python -m app.main

# Method 2: Using Uvicorn directly (for more control)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Method 3: Production mode (no auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Keep Server Running

The server will continue running until you stop it with `Ctrl+C`.

---

## 🔧 Environment Configuration

### Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://xyz.supabase.co` |
| `SUPABASE_SECRET_KEY` | Backend authentication | `your_secret_key` |
| `DATABASE_SCHEMA` | Database schema name | `steam` |
| `DATABASE_TABLE` | Main table name | `games_prod` |
| `BACKEND_HOST` | Server bind address | `0.0.0.0` (all interfaces) |
| `BACKEND_PORT` | Server port | `8000` |
| `CORS_ORIGINS` | Allowed frontend URLs | `http://localhost:3000` |
| `ENVIRONMENT` | Environment name | `development` |
| `DEBUG` | Debug mode | `True` (dev), `False` (prod) |
| `LOG_LEVEL` | Logging verbosity | `INFO`, `DEBUG`, `WARNING` |

### Configuration File Location

**Important:** The `.env` file is located in the **project root**, not in `backend/` folder.

```
INST326-steam-searcher-engine/
├── .env                    ← Environment file HERE
├── backend/
│   ├── app/
│   │   ├── config.py      ← Reads from ../.env
│   │   └── main.py
│   └── requirements.txt
└── frontend-INST326-steam-search/
```

The `config.py` loads from parent directory using `env_file="../.env"`.

---

## 🎯 Starting the Backend

### Quick Start Command

From backend directory with venv activated:

```bash
python -m app.main
```

### Expected Startup Output

```
2025-12-15 10:30:00 - root - INFO - ======================================================================
2025-12-15 10:30:00 - root - INFO - 🚀 Steam Game Search Engine API - Starting Up
2025-12-15 10:30:00 - root - INFO - ======================================================================
2025-12-15 10:30:00 - root - INFO - Environment: development
2025-12-15 10:30:00 - root - INFO - Debug Mode: True
2025-12-15 10:30:00 - root - INFO - Host: 0.0.0.0:8000
2025-12-15 10:30:00 - root - INFO - Database: https://bcaoujpzhoyrinhaydyu.supabase.co
2025-12-15 10:30:00 - root - INFO - Schema: steam
2025-12-15 10:30:00 - root - INFO - Table: games_prod
2025-12-15 10:30:00 - root - INFO - ✅ Supabase database connected successfully
2025-12-15 10:30:00 - root - INFO - ✅ Database health check passed
2025-12-15 10:30:00 - root - INFO - ======================================================================
2025-12-15 10:30:00 - root - INFO - ✅ Application startup complete
2025-12-15 10:30:00 - root - INFO - 📚 API Documentation: http://localhost:8000/docs
2025-12-15 10:30:00 - root - INFO - ======================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Success Indicators

✅ "Database connected successfully"
✅ "Database health check passed"
✅ "Application startup complete"
✅ "Uvicorn running on http://0.0.0.0:8000"

---

## ✅ Verification Steps

After starting the backend, verify it's working:

### 1. Check API Root

**Browser:** http://localhost:8000/

**cURL:**
```bash
curl http://localhost:8000/
```

**Expected response:**
```json
{
  "message": "Steam Game Search Engine API",
  "version": "0.1.0",
  "status": "operational",
  "documentation": {
    "swagger_ui": "/docs",
    "redoc": "/redoc"
  },
  "endpoints": {
    "health": "/api/v1/health",
    "games_list": "/api/v1/games",
    "game_detail": "/api/v1/games/{game_id}"
  }
}
```

### 2. Check Health Endpoint

**Browser:** http://localhost:8000/api/v1/health

**cURL:**
```bash
curl http://localhost:8000/api/v1/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-15T10:30:00.000Z",
  "database": "connected",
  "version": "0.1.0"
}
```

### 3. Check Games List

**Browser:** http://localhost:8000/api/v1/games?offset=0&limit=5

**cURL:**
```bash
curl "http://localhost:8000/api/v1/games?offset=0&limit=5"
```

**Expected response:** JSON array with games data

### 4. Check API Documentation

**Browser:** http://localhost:8000/docs

You should see interactive Swagger UI with all endpoints documented.

---

## 🐛 Common Issues

### Issue 1: "ModuleNotFoundError"

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Issue 2: "Database connection failed"

**Error:**
```
❌ Database connection failed: Invalid API key
```

**Cause:** Incorrect Supabase credentials

**Solution:**
1. Verify `.env` file exists in project root
2. Check `SUPABASE_URL` is correct
3. Verify `SUPABASE_SECRET_KEY` is valid
4. Ensure no extra spaces in environment variables

### Issue 3: "Port already in use"

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Cause:** Another process is using port 8000

**Solution:**

**Option 1: Kill existing process**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

**Option 2: Change port**
```env
# In .env file
BACKEND_PORT=8001
```

### Issue 4: "CORS errors from frontend"

**Error in frontend console:**
```
Access to fetch at 'http://localhost:8000/api/v1/games' blocked by CORS policy
```

**Solution:**
Verify `CORS_ORIGINS` in `.env` includes frontend URL:
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Issue 5: Virtual environment not found

**Error:**
```
source: venv/bin/activate: No such file or directory
```

**Solution:**
Create virtual environment first:
```bash
python3 -m venv venv
```

---

## 🔗 Integration with Frontend

### Frontend Configuration

The frontend should have these environment variables:

```env
# frontend-INST326-steam-search/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Testing Integration

1. **Start Backend** (port 8000)
   ```bash
   cd backend
   source venv/bin/activate
   python -m app.main
   ```

2. **Start Frontend** (port 3000) - in new terminal
   ```bash
   cd frontend-INST326-steam-search
   npm run dev
   ```

3. **Verify** both services:
   - Backend: http://localhost:8000/api/v1/health
   - Frontend: http://localhost:3000

4. **Test API calls** from frontend:
   - Frontend should fetch games from backend
   - Check browser console for any errors
   - Verify network tab shows successful API requests

---

## 📝 Development Tips

### Auto-Reload

When `DEBUG=True`, the server automatically reloads when you save code changes.

### Viewing Logs

All logs are printed to console. Adjust verbosity with `LOG_LEVEL`:
- `DEBUG`: Very verbose (shows all operations)
- `INFO`: Standard (recommended for development)
- `WARNING`: Only warnings and errors
- `ERROR`: Only errors

### API Testing

**Interactive Documentation:** http://localhost:8000/docs
- Test all endpoints directly in browser
- See request/response schemas
- No need for separate API client

### Database Queries

Monitor database queries in logs when `LOG_LEVEL=DEBUG`:
```
DEBUG - Fetching games: offset=0, limit=20
DEBUG - ✅ Successfully fetched 20 games
```

---

## 🎓 Quick Reference

### Common Commands

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate

# Start backend
python -m app.main

# Install new dependency
pip install package-name
pip freeze > requirements.txt

# Deactivate virtual environment
deactivate

# Stop server
Ctrl+C
```

### Important URLs

- API Root: http://localhost:8000/
- Health Check: http://localhost:8000/api/v1/health
- Games List: http://localhost:8000/api/v1/games
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### File Locations

- Backend code: `backend/app/`
- Environment file: `../env` (project root)
- Dependencies: `backend/requirements.txt`
- Virtual environment: `backend/venv/`

---

## ✅ Startup Checklist

Use this checklist each time you start development:

- [ ] Navigate to backend directory
- [ ] Activate virtual environment (`source venv/bin/activate`)
- [ ] Verify `.env` file exists in project root
- [ ] Start backend (`python -m app.main`)
- [ ] Check health endpoint (http://localhost:8000/api/v1/health)
- [ ] Start frontend in separate terminal
- [ ] Verify integration (frontend can fetch data)

---

## 📞 Getting Help

If you encounter issues not covered here:

1. Check server logs for error messages
2. Verify all environment variables are set
3. Test endpoints using http://localhost:8000/docs
4. Check database connection using health endpoint
5. Review backend README.md for additional troubleshooting

---

**Last Updated:** December 2025  
**Version:** 1.0.0  
**Author:** INST326 Project Team

