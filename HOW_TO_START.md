# How to Start the Project

Quick guide for starting the Steam Game Search Engine backend and frontend.

## ✅ Prerequisites Check

Before starting, verify you have:

```bash
# Check Python version (need 3.8+)
python3 --version

# Check Node.js version (need 18+)
node --version

# Check npm
npm --version
```

## 🚀 Quick Start Steps

### Step 1: Environment Variables (⚠️ IMPORTANT)

The `.env` file should already exist in the project root:

```
/home/gellar/Desktop/maryland/INST326/INST326-project/INST326-steam-searcher-engine/.env
```

**⚠️ CRITICAL: Replace the Secret Key Placeholder**

The `.env` file has a **placeholder** for the secret key. You MUST replace it with your real Supabase secret key:

1. Go to [supabase.com](https://supabase.com)
2. Open project: `bcaoujpzhoyrinhaydyu`
3. Go to **Project Settings** → **API**
4. Copy the **service_role** key (long JWT token starting with `eyJ...`)
5. Edit `.env` and replace `[your_secret_key]` with the real key

**Verify `.env` contains:**
```env
SUPABASE_URL=https://bcaoujpzhoyrinhaydyu.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_SRQy_SujM87ooPXX_uNqUA_RywMFt_J
SUPABASE_SECRET_KEY=eyJhbGc...  # ← Your REAL key here (NOT [your_secret_key])
DATABASE_SCHEMA=steam
DATABASE_TABLE=games_prod
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

**If you don't replace the placeholder, you'll see:**
```
❌ Database connection failed: Invalid API key
```

See `docs/tech-doc/DATABASE_CONNECTION_FIX.md` for detailed instructions.

### Step 2: Start Backend (Terminal 1)

```bash
# Navigate to backend directory
cd /home/gellar/Desktop/maryland/INST326/INST326-project/INST326-steam-searcher-engine/backend

# Activate virtual environment
source venv/bin/activate

# Start backend server
python -m app.main
```

**Expected output:**
```
🚀 Steam Game Search Engine API - Starting Up
✅ Supabase database connected successfully
✅ Database health check passed
✅ Application startup complete
📚 API Documentation: http://localhost:8000/docs
```

**Backend URLs:**
- API Root: http://localhost:8000/
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

### Step 3: Start Frontend (Terminal 2 - New Terminal)

```bash
# Navigate to frontend directory
cd /home/gellar/Desktop/maryland/INST326/INST326-project/INST326-steam-searcher-engine/frontend-INST326-steam-search

# Start frontend (dependencies should already be installed)
npm run dev
```

**Frontend URL:**
- http://localhost:3000

### Step 4: Verify Everything Works

**Test Backend:**
```bash
# In a new terminal
curl http://localhost:8000/api/v1/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-15T...",
  "database": "connected",
  "version": "0.1.0"
}
```

**Test Frontend:**
- Open browser: http://localhost:3000
- Frontend should load and be able to fetch games from backend

---

## 🛑 How to Stop

**Stop Backend:** Press `Ctrl+C` in Terminal 1

**Stop Frontend:** Press `Ctrl+C` in Terminal 2

---

## 🐛 Troubleshooting

### Backend won't start

**Problem:** "Module not found" error
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** "Database connection failed"
- Check `.env` file exists in project root (not in backend/)
- Verify `SUPABASE_URL` and `SUPABASE_SECRET_KEY` are correct

**Problem:** "Port 8000 already in use"
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>
```

### Frontend won't start

**Problem:** "Port 3000 already in use"
```bash
# Find and kill the process
lsof -i :3000
kill -9 <PID>
```

**Problem:** Dependencies not installed
```bash
cd frontend-INST326-steam-search
npm install
```

### Frontend can't connect to backend

**Problem:** CORS errors in browser console
- Verify backend is running on port 8000
- Check `CORS_ORIGINS` in `.env` includes `http://localhost:3000`
- Restart backend after changing `.env`

---

## 📝 Daily Workflow

**Every time you want to work on the project:**

1. Open two terminals
2. Terminal 1: Start backend
   ```bash
   cd backend
   source venv/bin/activate
   python -m app.main
   ```
3. Terminal 2: Start frontend
   ```bash
   cd frontend-INST326-steam-search
   npm run dev
   ```
4. Open browser to http://localhost:3000
5. When done, press `Ctrl+C` in both terminals

---

## 📚 More Information

- **Backend README**: `backend/README.md`
- **Detailed Startup Guide**: `docs/tech-doc/BACKEND_STARTUP_GUIDE.md`
- **Main README**: `README.md`
- **API Documentation**: http://localhost:8000/docs (when backend is running)

---

**Last Updated:** December 2025

