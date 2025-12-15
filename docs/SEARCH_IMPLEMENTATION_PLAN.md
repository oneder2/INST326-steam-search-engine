# Search Implementation Plan - Executive Summary

**Date:** December 15, 2025  
**Status:** Ready to implement

---

## 🔍 Database Analysis Results

### Available Data
✅ **name** (text) - Game titles  
✅ **short_description** (text) - Game descriptions (100+ chars)  
✅ **genres** (jsonb) - Game genres for filtering  
✅ **categories** (jsonb) - Game categories  
✅ **price_cents** (integer) - Indexed for fast filtering  
✅ **type** (text) - Indexed for fast filtering  
✅ **total_reviews** (integer) - For popularity sorting  
✅ **release_date** (date) - For date sorting  

⚠️ **search_tsv** (text) - Currently NULL (not populated)

### Conclusion
We have excellent data for search! The `search_tsv` field exists but is empty, so we'll search directly on `name` and `short_description`.

---

## 🎯 Recommended Implementation Path

### Phase 1: Basic Search + Filters (Week 1-2) ⭐ START HERE

**Why this first:**
- Quick to implement (2-3 days)
- Immediate value to users
- Uses existing indexes
- No complex algorithms needed

**What to implement:**
1. Text search on `name` and `short_description` (ILIKE)
2. Genre filter (JSONB containment)
3. Price range filter (indexed!)
4. Type filter (game/dlc - indexed!)
5. Sort by: price, reviews, date

**API Endpoint:**
```
POST /api/v1/search/games

Request:
{
  "query": "strategy war",           // Search in name + description
  "filters": {
    "price_max": 2000,               // $20 max (in cents)
    "genres": ["Strategy"],          // Must contain Strategy
    "type": "game"                   // Only games (not DLC)
  },
  "sort_by": "reviews",              // Sort by total_reviews DESC
  "offset": 0,
  "limit": 20
}

Response:
{
  "results": [...],
  "total": 156,
  "offset": 0,
  "limit": 20
}
```

**Estimated Performance:**
- Latency: < 100ms
- Works for 1000+ games easily
- Scales with PostgreSQL

---

### Phase 2: Multi-Field Search (Week 3)

**Why this second:**
- Better search relevance
- Still simple (just more fields)
- No new dependencies

**What to add:**
1. Search in multiple fields with weighting:
   - `name`: weight 10 (most important)
   - `short_description`: weight 5
   - `detailed_desc`: weight 1
2. Better text matching (split query into tokens)

**Implementation:**
```python
# Pseudo-code
tokens = query.lower().split()  # ["strategy", "war"]

for token in tokens:
    results = results.filter(
        OR(
            name.ilike(f'%{token}%'),           # Weight: 10 points if in name
            short_description.ilike(f'%{token}%'),  # Weight: 5 points if in desc
        )
    )

# Sort by: (matches_in_name * 10) + (matches_in_desc * 5)
```

---

### Phase 3: BM25 Ranking (Week 4) 🚀 PROFESSIONAL QUALITY

**Why this third:**
- Industry-standard relevance ranking
- Much better than simple matching
- Not too complex

**What to add:**
1. Install BM25 library: `pip install rank-bm25`
2. Build in-memory index (for 1009 games, ~100MB RAM)
3. Combine BM25 score with filters

**Performance:**
- Latency: ~200ms (acceptable)
- Memory: ~100-500MB
- Quality: Professional-grade search

---

### Phase 4 (Optional): Semantic Search (Future)

**Why last:**
- Most complex
- Requires ML model
- High memory usage
- Good for "games like X" queries

**When to implement:**
- After Phase 3 is working well
- If users ask for semantic features
- If you have GPU available

---

## 📋 Implementation Checklist

### Week 1-2: Phase 1 (MVP++)

#### Backend Tasks
- [ ] Create `SearchQuerySchema` Pydantic model
- [ ] Create `SearchFilters` Pydantic model  
- [ ] Create `POST /api/v1/search/games` endpoint
- [ ] Implement basic ILIKE search on `name`
- [ ] Add price filter (use index: `price_cents BETWEEN min AND max`)
- [ ] Add genre filter (use JSONB: `genres @> '["Action"]'`)
- [ ] Add type filter (use index: `type = 'game'`)
- [ ] Add sorting (price, reviews, date)
- [ ] Add pagination
- [ ] Test with Postman/curl

#### Frontend Tasks
- [ ] Update `src/services/api.ts` with `searchGames(query, filters)`
- [ ] Update `src/pages/search.tsx` to add search input box
- [ ] Add filter sidebar (restore from original design)
- [ ] Add sort dropdown
- [ ] Connect search to API
- [ ] Test in browser

#### Testing
- [ ] Test empty query (should return all games with filters)
- [ ] Test with query + no filters
- [ ] Test with query + filters
- [ ] Test pagination with search results
- [ ] Test all sort options

---

## 🎨 Frontend UI Changes

### Search Box (restore)
```tsx
<SearchBox
  value={searchQuery}
  onChange={setSearchQuery}
  onSearch={handleSearch}
  placeholder="Search for strategy, RPG, action games..."
/>
```

### Filters Sidebar (restore)
```tsx
<SearchFilters
  filters={filters}
  onFiltersChange={handleFiltersChange}
>
  <PriceRangeFilter max={filters.price_max} />
  <GenreFilter selected={filters.genres} />
  <TypeFilter selected={filters.type} />
</SearchFilters>
```

### Sort Dropdown
```tsx
<SortDropdown
  value={sortBy}
  onChange={setSortBy}
  options={[
    { value: 'relevance', label: 'Relevance' },
    { value: 'price_asc', label: 'Price: Low to High' },
    { value: 'price_desc', label: 'Price: High to Low' },
    { value: 'reviews', label: 'Most Reviewed' },
    { value: 'newest', label: 'Newest First' },
  ]}
/>
```

---

## 🔧 Backend Code Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── search.py          # NEW: Search endpoint
│   │       ├── games.py            # Existing
│   │       └── health.py           # Existing
│   ├── models/
│   │   ├── search.py               # NEW: Search models
│   │   └── game.py                 # Existing
│   ├── services/
│   │   ├── search_service.py       # NEW: Search logic
│   │   └── game_service.py         # Existing
│   └── utils/
│       └── text_utils.py           # NEW: Text processing helpers
```

---

## 📝 Sample Code

### Backend: Search Endpoint (Phase 1)

```python
# app/api/v1/search.py
from fastapi import APIRouter, Depends
from supabase import Client
from app.database import get_db
from app.models.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter()

@router.post(
    "/search/games",
    response_model=SearchResponse,
    summary="Search Games",
    description="Search games with filters and sorting"
)
async def search_games(
    request: SearchRequest,
    db: Client = Depends(get_db)
):
    """
    Search for games using text query and filters
    
    Features:
    - Text search in name and short_description
    - Filter by price, genre, type
    - Sort by price, reviews, date
    - Pagination support
    """
    service = SearchService(db)
    results = await service.search(
        query=request.query,
        filters=request.filters,
        sort_by=request.sort_by,
        offset=request.offset,
        limit=request.limit
    )
    return results
```

### Backend: Search Service (Phase 1)

```python
# app/services/search_service.py
from typing import List, Dict, Any, Optional
from supabase import Client
from app.models.search import SearchFilters, SortBy
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db_client: Client):
        self.db = db_client
    
    async def search(
        self,
        query: str = "",
        filters: Optional[SearchFilters] = None,
        sort_by: SortBy = SortBy.RELEVANCE,
        offset: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search games with filters
        
        Phase 1: Simple ILIKE search
        Phase 2: Multi-field search
        Phase 3: BM25 ranking
        """
        try:
            # Start building query
            db_query = self.db.table(settings.DATABASE_TABLE).select(
                'appid, name, price_cents, genres, categories, '
                'short_description, total_reviews, type, release_date'
            )
            
            # Apply text search if query provided
            if query.strip():
                # Phase 1: Simple ILIKE on name
                # TODO Phase 2: Add short_description
                # TODO Phase 3: Use BM25
                db_query = db_query.ilike('name', f'%{query}%')
            
            # Apply filters
            if filters:
                # Price filter (use index!)
                if filters.price_min is not None:
                    db_query = db_query.gte('price_cents', filters.price_min)
                if filters.price_max is not None:
                    db_query = db_query.lte('price_cents', filters.price_max)
                
                # Type filter (use index!)
                if filters.type:
                    db_query = db_query.eq('type', filters.type)
                
                # Genre filter (JSONB containment)
                if filters.genres:
                    for genre in filters.genres:
                        db_query = db_query.contains('genres', [genre])
            
            # Apply sorting
            if sort_by == SortBy.PRICE_ASC:
                db_query = db_query.order('price_cents', desc=False)
            elif sort_by == SortBy.PRICE_DESC:
                db_query = db_query.order('price_cents', desc=True)
            elif sort_by == SortBy.REVIEWS:
                db_query = db_query.order('total_reviews', desc=True)
            elif sort_by == SortBy.NEWEST:
                db_query = db_query.order('release_date', desc=True)
            elif sort_by == SortBy.OLDEST:
                db_query = db_query.order('release_date', desc=False)
            else:  # RELEVANCE (default to name for now)
                db_query = db_query.order('name')
            
            # Get count (for pagination)
            count_query = self.db.table(settings.DATABASE_TABLE).select('appid', count='exact')
            # Apply same filters to count
            # ... (repeat filter logic for count)
            count_result = count_query.execute()
            total = count_result.count if hasattr(count_result, 'count') else 0
            
            # Apply pagination
            result = db_query.range(offset, offset + limit - 1).execute()
            
            # Transform results
            games = []
            for game in result.data:
                games.append({
                    'game_id': game['appid'],
                    'title': game['name'],
                    'price': round(game['price_cents'] / 100, 2) if game['price_cents'] else 0.0,
                    'genres': game['genres'] if game['genres'] else [],
                    'categories': game['categories'] if game['categories'] else [],
                    'description': game['short_description'],
                    'total_reviews': game['total_reviews'],
                    'type': game['type'],
                    'release_date': game['release_date'],
                    'relevance_score': 1.0,  # TODO: Implement actual scoring
                })
            
            logger.info(f"✅ Search completed: query='{query}', found {len(games)} games")
            
            return {
                'results': games,
                'total': total,
                'offset': offset,
                'limit': limit,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise
```

---

## 🚀 Quick Start Commands

### 1. Test Current API
```bash
curl "http://localhost:8000/api/v1/games?offset=0&limit=5"
```

### 2. After implementing search
```bash
# Test basic search
curl -X POST http://localhost:8000/api/v1/search/games \
  -H "Content-Type: application/json" \
  -d '{
    "query": "strategy",
    "offset": 0,
    "limit": 10
  }'

# Test with filters
curl -X POST http://localhost:8000/api/v1/search/games \
  -H "Content-Type: application/json" \
  -d '{
    "query": "RPG",
    "filters": {
      "price_max": 2000,
      "genres": ["RPG"],
      "type": "game"
    },
    "sort_by": "reviews",
    "offset": 0,
    "limit": 20
  }'
```

---

## 📊 Success Metrics

### Phase 1 Success Criteria
- [ ] Search returns relevant results
- [ ] Filters work correctly
- [ ] Sorting works correctly
- [ ] Response time < 200ms
- [ ] Frontend displays results
- [ ] Pagination works

### User Experience Goals
- [ ] Users can find games by name
- [ ] Users can filter by price/genre
- [ ] Results update in real-time
- [ ] Loading states show during search
- [ ] Empty results show helpful message

---

## 🎯 Next Actions

**Immediate (Today/Tomorrow):**
1. Review this plan
2. Decide on Phase 1 scope
3. Start backend implementation

**This Week:**
1. Implement Phase 1 backend
2. Update frontend UI
3. Test integration
4. Deploy to test environment

**Next Week:**
1. Gather user feedback
2. Plan Phase 2 improvements
3. Consider BM25 implementation

---

**Ready to start?** Let me know which phase you'd like to implement first!


