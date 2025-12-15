# Database Connection Issue - Invalid API Key

## Problem

When starting the backend, you see this error:
```
❌ Database connection failed: Invalid API key
```

## Cause

The `.env` file contains a placeholder for `SUPABASE_SECRET_KEY`:
```env
SUPABASE_SECRET_KEY=[your_secret_key]  # ← This is a placeholder!
```

## Solution

You need to replace the placeholder with your actual Supabase secret key.

### Step 1: Get Your Real Secret Key

1. Go to [supabase.com](https://supabase.com)
2. Open your project: `bcaoujpzhoyrinhaydyu`
3. Go to **Project Settings** → **API**
4. Find the **service_role** key (this is your secret key)
5. Copy the full key value

### Step 2: Update .env File

Edit the `.env` file in the project root:

```env
# Replace this line:
SUPABASE_SECRET_KEY=[your_secret_key]

# With your actual key (example format):
SUPABASE_SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSI...
```

**Important:** 
- The secret key is a long JWT token (starts with `eyJ...`)
- Do NOT include brackets `[]`
- Do NOT add quotes around the key
- Make sure there are no spaces before or after the key

### Step 3: Restart Backend

```bash
# Stop backend (Ctrl+C if running)
# Start again
cd backend
source venv/bin/activate
python -m app.main
```

You should now see:
```
✅ Database connection established
✅ Database health check passed
```

## Security Note

⚠️ **Never commit the real secret key to Git!**

The `.env` file is already in `.gitignore`, so it won't be committed. Keep it safe and never share it publicly.

---

**Last Updated:** December 2025

