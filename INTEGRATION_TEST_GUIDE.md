# Frontend-Backend Integration Test Guide

Quick guide to test the complete frontend-backend integration.

## Prerequisites

- Backend running on port 8000
- Frontend running on port 3000
- Both services healthy

---

## Step 1: Start Backend

```bash
cd backend
source venv/bin/activate
python -m app.main
```

**Expected output:**
```
✅ Supabase database connected successfully
✅ Database health check passed
✅ Application startup complete
📚 API Documentation: http://localhost:8000/docs
```

**Verify:**
```bash
curl http://localhost:8000/api/v1/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "0.1.0"
}
```

---

## Step 2: Start Frontend

**New terminal:**
```bash
cd frontend-INST326-steam-search
npm run dev
```

**Expected output:**
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

## Step 3: Test Integration

### Test 1: Homepage
1. Open: http://localhost:3000
2. **Expected:** Homepage loads with navigation

### Test 2: Search Page (Game List)
1. Open: http://localhost:3000/search
2. **Expected:**
   - Page title: "Browse All Games"
   - Games displayed in grid/list
   - Pagination controls at bottom
   - "Showing X games" text

### Test 3: Pagination
1. On /search page, click "Next" button
2. **Expected:**
   - URL changes to `/search?page=2`
   - Different games displayed
   - Page 2 button highlighted
   - Previous button enabled

3. Click page number "1"
4. **Expected:**
   - Returns to first page
   - URL changes to `/search?page=1` or `/search`
   - Original games displayed

### Test 4: Direct Page Access
1. Navigate to: http://localhost:3000/search?page=3
2. **Expected:**
   - Page 3 games displayed
   - Page 3 button highlighted
   - Correct page info shown

### Test 5: Browser Navigation
1. Go to page 2
2. Click browser back button
3. **Expected:** Returns to page 1
4. Click browser forward button
5. **Expected:** Returns to page 2

---

## Step 4: Verify Data

### Check Game Data
1. On /search page, inspect a game card
2. **Should display:**
   - Game title
   - Price (in USD)
   - Genres (if available)
   - Short description (if available)

### Check Pagination Info
1. At bottom of page, check pagination text
2. **Should show:**
   - "Showing X - Y of Z games"
   - Current page number highlighted
   - Total pages calculated correctly

---

## Step 5: Test Error Handling

### Test Backend Down
1. Stop backend (Ctrl+C)
2. Refresh /search page
3. **Expected:**
   - Error message displayed
   - "Retry" button available
4. Restart backend
5. Click "Retry"
6. **Expected:** Games load successfully

---

## Verification Checklist

### Backend
- [ ] Starts without errors
- [ ] Health check returns "healthy"
- [ ] GET /api/v1/games returns data
- [ ] Pagination parameters work (offset, limit)
- [ ] No CORS errors in browser console

### Frontend
- [ ] Homepage loads
- [ ] /search page loads
- [ ] Games display correctly
- [ ] Pagination controls appear
- [ ] Page numbers clickable
- [ ] Previous/Next buttons work
- [ ] URL updates with page parameter
- [ ] Loading state shows during fetch
- [ ] Error state shows when backend down

### Integration
- [ ] Frontend successfully calls backend API
- [ ] Data displays correctly
- [ ] No console errors
- [ ] No network errors
- [ ] Page navigation smooth
- [ ] Browser back/forward work

---

## Expected API Calls

When you navigate to `/search?page=2`, you should see in Network tab:

**Request:**
```
GET http://localhost:8000/api/v1/games?offset=20&limit=20
```

**Response:**
```json
{
  "games": [...],
  "total": 50000,
  "offset": 20,
  "limit": 20
}
```

---

## Common Issues

### Issue: "Failed to load games"

**Check:**
```bash
# Is backend running?
curl http://localhost:8000/api/v1/health

# Check frontend env
cat frontend-INST326-steam-search/.env.local
```

**Should have:**
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Issue: CORS Error

**Browser console shows:**
```
Access to fetch blocked by CORS policy
```

**Fix:**
Check backend `.env`:
```env
CORS_ORIGINS=http://localhost:3000
```

Restart backend.

### Issue: No games displayed

**Check:**
1. Browser console for errors
2. Network tab for API response
3. Backend logs for errors

**Debug:**
```bash
# Test backend directly
curl "http://localhost:8000/api/v1/games?offset=0&limit=5"
```

---

## Success Criteria

✅ All checklist items completed
✅ No console errors
✅ No network errors
✅ Smooth page navigation
✅ Data displays correctly
✅ Pagination works as expected

---

## Next Steps

After successful integration test:

1. Document any issues found
2. Test on different browsers (Chrome, Firefox, Safari)
3. Test on mobile devices (responsive design)
4. Prepare for Phase 2 (search functionality)

---

**Last Updated:** December 15, 2025
**Status:** Ready for testing

