# Frontend-Backend Integration - MVP Phase

## Overview

This document describes the frontend-backend integration for the MVP phase, which implements simple paginated game listing without search or filtering.

---

## API Integration

### Backend Endpoint

**GET** `/api/v1/games`

**Query Parameters:**
- `offset` (int, optional): Starting position (default: 0)
- `limit` (int, optional): Number of games per page (default: 20, max: 100)

**Response Format:**
```json
{
  "games": [
    {
      "game_id": 1610,
      "title": "Space Empires IV Deluxe",
      "price": 19.99,
      "genres": ["Strategy"],
      "categories": ["Single-player", "Multi-player"],
      "short_description": "...",
      "total_reviews": 248,
      "type": "game"
    }
  ],
  "total": 50000,
  "offset": 0,
  "limit": 20
}
```

### Frontend Implementation

**File:** `frontend-INST326-steam-search/src/pages/search.tsx`

**Features:**
- Displays all games with pagination
- URL-based page navigation (`/search?page=2`)
- Loading and error states
- Responsive pagination controls

**API Client:**
- Added `getAllGames(offset, limit)` method to `src/services/api.ts`
- Transforms backend response to match frontend `GameResult` type

---

## Data Transformation

### Backend → Frontend Mapping

| Backend Field | Frontend Field | Transformation |
|---------------|----------------|----------------|
| `game_id` | `id` | Direct mapping |
| `title` | `title` | Direct mapping |
| `price` | `price` | Direct mapping (already in USD) |
| `genres` | `genres` | Direct mapping |
| `categories` | - | Not used in MVP |
| `short_description` | `description` | Direct mapping |
| `total_reviews` | - | Not displayed in MVP |
| `type` | - | Not used in MVP |
| - | `score` | Set to 0 (no scoring in MVP) |
| - | `deck_compatible` | Set to false (not in backend yet) |
| - | `review_status` | Set to 'Mixed' (not in backend yet) |

---

## Testing

### 1. Backend Test

```bash
# Start backend
cd backend
source venv/bin/activate
python -m app.main
```

**Test endpoint:**
```bash
curl "http://localhost:8000/api/v1/games?offset=0&limit=5"
```

**Expected:** JSON response with 5 games

### 2. Frontend Test

```bash
# Start frontend (new terminal)
cd frontend-INST326-steam-search
npm run dev
```

**Test pages:**
- http://localhost:3000/search - First page
- http://localhost:3000/search?page=2 - Second page
- http://localhost:3000/search?page=3 - Third page

**Expected:**
- Games displayed in grid/list format
- Pagination controls at bottom
- Page numbers showing current page
- Previous/Next buttons working

### 3. Integration Test

**Steps:**
1. Open http://localhost:3000/search
2. Verify games are displayed
3. Click "Next" button
4. Verify URL changes to `?page=2`
5. Verify different games are displayed
6. Click page number "1"
7. Verify returns to first page

**Expected Behavior:**
- ✅ Games load on page load
- ✅ Pagination controls appear
- ✅ Clicking page numbers changes page
- ✅ URL updates with page parameter
- ✅ Browser back/forward buttons work
- ✅ Loading state shows during fetch
- ✅ Error state shows if backend is down

---

## Known Limitations (MVP Phase)

### Not Implemented
- ❌ Search functionality
- ❌ Filtering by genre, price, etc.
- ❌ Sorting options
- ❌ Game detail pages
- ❌ Review status display
- ❌ Steam Deck compatibility indicator

### Placeholder Values
- `score`: Always 0 (no ranking algorithm yet)
- `review_status`: Always 'Mixed' (not in backend)
- `deck_compatible`: Always false (not in backend)

---

## Future Enhancements (Phase 2)

### Backend
1. Implement POST `/api/v1/search/games` endpoint
2. Add search query processing
3. Add filtering support
4. Add sorting options
5. Implement BM25/Faiss search algorithms

### Frontend
1. Add search input box
2. Add filter sidebar
3. Add sorting dropdown
4. Implement search functionality
5. Add game detail pages

---

## Troubleshooting

### Issue: Games not loading

**Check:**
1. Backend is running on port 8000
2. Frontend environment variable `NEXT_PUBLIC_API_BASE_URL` is set
3. Browser console for errors
4. Network tab for API requests

**Solution:**
```bash
# Verify backend
curl http://localhost:8000/api/v1/health

# Check frontend env
cat frontend-INST326-steam-search/.env.local
# Should have: NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Issue: CORS errors

**Error:** `Access to fetch blocked by CORS policy`

**Solution:**
Verify backend `.env` has:
```env
CORS_ORIGINS=http://localhost:3000
```

Restart backend after changing.

### Issue: Pagination not working

**Check:**
1. URL updates when clicking page numbers
2. Browser console for errors
3. Network tab shows API calls with correct offset

**Debug:**
```javascript
// Add to search.tsx to debug
console.log('Current page:', currentPage);
console.log('Offset:', (currentPage - 1) * SEARCH_LIMITS.DEFAULT_LIMIT);
```

---

## Files Modified

### Backend
1. `backend/app/api/v1/health.py` - Fixed schema in health check
2. `backend/app/services/game_service.py` - Already has `.schema()` method

### Frontend
1. `frontend-INST326-steam-search/src/services/api.ts`
   - Added `getAllGames()` method
   - Added convenience export

2. `frontend-INST326-steam-search/src/pages/search.tsx`
   - Simplified to MVP version
   - Removed search/filter UI
   - Implemented simple pagination

---

## API Contract Verification

### Request
```
GET /api/v1/games?offset=0&limit=20
```

### Response Structure
```typescript
{
  games: Array<{
    game_id: number,
    title: string,
    price: number,
    genres: string[],
    categories: string[],
    short_description: string,
    total_reviews: number,
    type: string
  }>,
  total: number,
  offset: number,
  limit: number
}
```

### Frontend Expectation
```typescript
{
  results: Array<{
    id: number,
    title: string,
    price: number,
    genres: string[],
    description: string,
    score: number,
    review_status: string,
    deck_compatible: boolean
  }>,
  total: number,
  offset: number,
  limit: number
}
```

**Transformation:** Handled in `search.tsx` `loadGames()` function

---

## Success Criteria

✅ **Backend:**
- Endpoint returns game data
- Pagination works correctly
- Health check passes

✅ **Frontend:**
- Games display on /search page
- Pagination controls work
- URL updates with page parameter
- Loading states work
- Error handling works

✅ **Integration:**
- Frontend successfully calls backend API
- Data transforms correctly
- No CORS errors
- Page navigation works smoothly

---

**Status:** ✅ Complete
**Date:** December 15, 2025
**Phase:** MVP - Simple Pagination

