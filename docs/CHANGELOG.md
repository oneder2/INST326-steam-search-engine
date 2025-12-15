# Changelog

All notable changes to the Steam Game Search Engine project.

---

## [Phase 2] - 2025-12-15

### Added
- ✅ Multi-field search (name + short_description)
- ✅ Weighted relevance scoring algorithm
- ✅ Instant filter updates (fixed lag issue)
- ✅ 7 sorting options
- ✅ Genre multi-select filter
- ✅ Price range filter
- ✅ Game type filter
- ✅ Complete search UI

### Changed
- 🔧 Search now searches in both name and description fields
- 🔧 Relevance scores now weighted (name: 10x, description: 5x)
- 🔧 Filter updates now instant (no 1-click delay)

### Performance
- Search results increased 5.7x (15 → 86 for "adventure")
- Response time: ~300ms (still excellent)
- Filter response: Instant

### Files Modified
- `backend/app/services/search_service.py` - Multi-field search + weighted scoring
- `frontend-INST326-steam-search/src/pages/search.tsx` - Fixed filter lag

---

## [Phase 1] - 2025-12-15

### Added
- ✅ Basic text search in game names
- ✅ Search API endpoint (POST /api/v1/search/games)
- ✅ Search models (SearchRequest, SearchFilters, SearchResponse)
- ✅ Search service with filter logic
- ✅ Frontend search UI
- ✅ Pagination
- ✅ URL state management

### Features
- Text search in game names (ILIKE)
- Price filtering
- Genre filtering (JSONB)
- Type filtering
- Sorting by relevance, price, reviews, date
- Pagination (20 per page)

### Files Created
- `backend/app/models/search.py`
- `backend/app/services/search_service.py`
- `backend/app/api/v1/search.py`

### Files Modified
- `backend/app/main.py` - Added search router
- `frontend-INST326-steam-search/src/services/api.ts` - Added simpleSearch()
- `frontend-INST326-steam-search/src/pages/search.tsx` - Full search UI

---

## [MVP] - 2025-12-14

### Added
- ✅ Backend FastAPI setup
- ✅ Supabase database integration
- ✅ Frontend Next.js setup
- ✅ Basic game listing (GET /api/v1/games)
- ✅ Pagination
- ✅ Health check endpoint

### Fixed
- 🐛 Database schema issue (public → steam)
- 🐛 Environment variable loading (.env path)
- 🐛 Supabase key compatibility (new format)
- 🐛 Deprecation warnings (FastAPI lifespan)

### Database
- Schema: steam
- Table: games_prod
- Records: 1,009 games
- Fields: appid, name, price_cents, genres, categories, etc.

---

## Upcoming (Phase 3)

### Planned Features
- BM25 ranking algorithm
- Search suggestions/autocomplete
- Highlighted search terms in results
- Advanced relevance tuning

### Planned Fixes
- Mobile responsive improvements
- Performance optimizations
- Cache frequent queries

---

**Last Updated:** December 15, 2025

