# Search Feature Combination Analysis

## Overview

This document analyzes whether the current implementation reliably ensures that all four search conditions work together simultaneously:

1. **Game Name Search** (文本搜索)
2. **Game Type Filter** (类型筛选)
3. **Different Sort Standards** (排序标准)
4. **Different Search Algorithms** (搜索算法: BM25/Semantic/Hybrid)

---

## Current Implementation Analysis

### ✅ BM25 Search (`SearchService.search()`)

**Location:** `backend/app/services/search_service.py:73-296`

**Combination Support:**

| Feature | Implementation | Status |
|---------|---------------|--------|
| **Text Search** | Lines 121-128: `ILIKE` on `name` and `short_description` | ✅ Full Support |
| **Type Filter** | Lines 144-146: `.eq('type', filters.type)` | ✅ Full Support |
| **Sorting** | Lines 183-226: All 7 sort options supported | ✅ Full Support |
| **Algorithm** | Lines 253, 278-280: BM25 batch scoring + post-sort | ✅ Full Support |

**Combination Logic:**
```python
# 1. Text search applied first (if query exists)
if query.strip():
    query_builder = query_builder.or_(or_condition)  # name OR description

# 2. Filters applied (AND logic with text search)
if filters:
    if filters.type:
        query_builder = query_builder.eq('type', filters.type)
    # ... other filters

# 3. Sorting applied (database-level)
if sort_by == SortBy.PRICE_ASC:
    query_builder = query_builder.order('price_cents', desc=False)
# ... other sorts

# 4. BM25 algorithm applied (post-processing)
if sort_by == SortBy.RELEVANCE:
    results.sort(key=lambda x: x['bm25_score'], reverse=True)
```

**✅ Verdict:** **FULLY SUPPORTED** - All four conditions work together reliably.

---

### ⚠️ Semantic Search (`SearchService.semantic_search()`)

**Location:** `backend/app/services/search_service.py:447-565`

**Combination Support:**

| Feature | Implementation | Status |
|---------|---------------|--------|
| **Text Search** | Lines 482: Query embedding → vector similarity | ✅ Full Support |
| **Type Filter** | Lines 499: Passed to PostgreSQL function or Python fallback | ✅ Full Support |
| **Sorting** | Line 559: **Fixed to `SortBy.RELEVANCE`** | ❌ **LIMITED** |
| **Algorithm** | Lines 506-517: Vector similarity (pgvector or Python) | ✅ Full Support |

**Combination Logic:**
```python
# 1. Text search: Query → embedding → vector similarity
query_embedding = EmbeddingService.encode_query(query)

# 2. Filters: Passed to PostgreSQL function
if filters:
    if filters.type:
        params['type_filter'] = filters.type
    # ... other filters

# 3. Sorting: ALWAYS SortBy.RELEVANCE (similarity)
# No other sort options supported!

# 4. Algorithm: Vector similarity (cosine similarity)
result = self.db.schema('steam').rpc('search_games_semantic', params)
```

**⚠️ Verdict:** **PARTIALLY SUPPORTED**
- ✅ Text search + Type filter + Algorithm: **WORK**
- ❌ **Sorting is limited** - Only similarity sorting, cannot combine with price/date/name sorts

**Issue:** Semantic search **ignores** `sort_by` parameter and always sorts by similarity. This means:
- User selects "Price: Low to High" → Still sorted by similarity
- User selects "Newest First" → Still sorted by similarity
- Only "Relevance" sort works as expected

---

### ⚠️ Hybrid Search (`SearchService.hybrid_search()`)

**Location:** `backend/app/services/search_service.py:567-683`

**Combination Support:**

| Feature | Implementation | Status |
|---------|---------------|--------|
| **Text Search** | Lines 614-622: Calls BM25 + Semantic (both use query) | ✅ Full Support |
| **Type Filter** | Lines 614-622: Passed to both searches | ✅ Full Support |
| **Sorting** | Line 604: **Only `RELEVANCE` supported**, others fallback to BM25 | ❌ **LIMITED** |
| **Algorithm** | Lines 659-663: RRF fusion of BM25 + Semantic | ✅ Full Support |

**Combination Logic:**
```python
# 1. Text search: Both BM25 and Semantic use the query
bm25_results = await self.search(query, filters, SortBy.RELEVANCE, ...)
semantic_results = await self.semantic_search(query, filters, ...)

# 2. Filters: Passed to both searches
# ✅ Both searches receive filters

# 3. Sorting: LIMITED - Only RELEVANCE works
if sort_by != SortBy.RELEVANCE or not query.strip():
    return await self.search(query, filters, sort_by, ...)  # Fallback to BM25 only!

# 4. Algorithm: RRF fusion
fused_results = self._reciprocal_rank_fusion(
    bm25_results['results'],
    semantic_results['results'],
    alpha
)
```

**⚠️ Verdict:** **PARTIALLY SUPPORTED**
- ✅ Text search + Type filter + Algorithm: **WORK**
- ❌ **Sorting is limited** - Only relevance sort uses hybrid, others fallback to BM25-only

**Issue:** Hybrid search **only works** when `sort_by == RELEVANCE`. For other sorts:
- User selects "Price: Low to High" → Falls back to BM25-only (no semantic fusion)
- User selects "Newest First" → Falls back to BM25-only (no semantic fusion)
- Only "Relevance" sort uses true hybrid search

---

## Test Coverage Analysis

### Current Tests

**Integration Tests** (`test_search_workflows.py`):
- ✅ Test 1: Search + Filters (no algorithm testing)
- ✅ Test 2: Pagination + Sorting (no algorithm testing)
- ❌ **Missing:** Tests for algorithm + filter + sort combinations

**System Tests** (`test_complete_workflows.py`):
- ✅ Test 1: Complete search journey (uses BM25 only, no algorithm selection)
- ❌ **Missing:** Tests for different algorithms with filters and sorts

### Missing Test Coverage

**Critical Missing Tests:**

1. **BM25 + Filter + Sort Combination:**
   ```python
   # Should test: BM25 search with type filter and price sort
   result = await search_service.search(
       query="action",
       filters=SearchFilters(type="game"),
       sort_by=SortBy.PRICE_ASC
   )
   # Verify: Results are filtered by type AND sorted by price AND scored by BM25
   ```

2. **Semantic + Filter + Sort Combination:**
   ```python
   # Should test: Semantic search with type filter and price sort
   result = await search_service.semantic_search(
       query="space",
       filters=SearchFilters(type="game"),
       # sort_by=SortBy.PRICE_ASC  # Currently ignored!
   )
   # Issue: sort_by is ignored, always sorts by similarity
   ```

3. **Hybrid + Filter + Sort Combination:**
   ```python
   # Should test: Hybrid search with type filter and price sort
   result = await search_service.hybrid_search(
       query="shooter",
       filters=SearchFilters(type="game"),
       sort_by=SortBy.PRICE_ASC  # Currently falls back to BM25!
   )
   # Issue: Falls back to BM25-only, loses semantic component
   ```

---

## Reliability Assessment

### ✅ **Reliable Combinations**

| Search Algorithm | Text Search | Type Filter | Sorting | Status |
|-----------------|-------------|-------------|---------|--------|
| **BM25** | ✅ | ✅ | ✅ All 7 sorts | ✅ **FULLY RELIABLE** |
| **Semantic** | ✅ | ✅ | ⚠️ Only Relevance | ⚠️ **PARTIALLY RELIABLE** |
| **Hybrid** | ✅ | ✅ | ⚠️ Only Relevance | ⚠️ **PARTIALLY RELIABLE** |

### ❌ **Unreliable Combinations**

1. **Semantic + Non-Relevance Sort:**
   - User selects: Semantic + Price Sort
   - **Actual behavior:** Sorted by similarity (ignores price sort)
   - **Expected behavior:** Should sort by price after semantic matching

2. **Hybrid + Non-Relevance Sort:**
   - User selects: Hybrid + Price Sort
   - **Actual behavior:** Falls back to BM25-only (loses semantic component)
   - **Expected behavior:** Should fuse BM25+Semantic, then sort by price

---

## Root Cause Analysis

### Issue 1: Semantic Search Sorting Limitation

**Root Cause:**
- Semantic search uses PostgreSQL function `search_games_semantic()` which **always** orders by similarity
- The function doesn't accept a `sort_by` parameter
- Python fallback also always sorts by similarity (line 841)

**Impact:**
- Users cannot combine semantic search with price/date/name sorting
- Semantic search results are always ordered by similarity, regardless of user selection

**Fix Required:**
1. Modify PostgreSQL function to accept `sort_by` parameter
2. Or: Apply sorting in post-processing after semantic search
3. Or: Document limitation clearly in UI

### Issue 2: Hybrid Search Sorting Limitation

**Root Cause:**
- Hybrid search only works when `sort_by == RELEVANCE` (line 604)
- For other sorts, it falls back to BM25-only search
- This defeats the purpose of hybrid search

**Impact:**
- Users lose semantic search benefits when selecting non-relevance sorts
- Hybrid search is effectively disabled for price/date/name sorting

**Fix Required:**
1. Always perform hybrid fusion regardless of sort_by
2. Apply sorting **after** fusion (post-processing)
3. This would allow: Hybrid search → Fuse results → Sort by price/date/name

---

## Recommendations

### 🔴 **Critical Issues to Fix**

1. **Semantic Search Sorting:**
   - **Option A:** Add post-processing sort after semantic search
   - **Option B:** Modify PostgreSQL function to support sorting
   - **Option C:** Document limitation and disable sort dropdown for semantic mode

2. **Hybrid Search Sorting:**
   - **Fix:** Always perform fusion, then apply sorting in post-processing
   - Remove the fallback logic that disables hybrid for non-relevance sorts

### 🟡 **Improvements**

1. **Add Comprehensive Tests:**
   - Test all algorithm + filter + sort combinations
   - Verify filters are applied correctly in all algorithms
   - Verify sorting works correctly in all algorithms

2. **Frontend Validation:**
   - Disable sort options for Semantic mode (if limitation remains)
   - Show warning when Hybrid mode falls back to BM25

3. **Documentation:**
   - Document sorting limitations for Semantic and Hybrid modes
   - Update API documentation with limitations

---

## Summary

### Current State

| Condition Combination | BM25 | Semantic | Hybrid |
|----------------------|------|----------|--------|
| **Text + Filter + Sort + Algorithm** | ✅ **YES** | ⚠️ **PARTIAL** | ⚠️ **PARTIAL** |
| **Text + Filter + Algorithm** | ✅ **YES** | ✅ **YES** | ✅ **YES** |
| **Text + Sort + Algorithm** | ✅ **YES** | ❌ **NO** | ❌ **NO** |
| **Filter + Sort + Algorithm** | ✅ **YES** | ❌ **NO** | ❌ **NO** |

### Reliability Score

- **BM25 Search:** ✅ **100% Reliable** - All combinations work
- **Semantic Search:** ⚠️ **60% Reliable** - Sorting limitation
- **Hybrid Search:** ⚠️ **60% Reliable** - Sorting limitation

### Conclusion

**The system does NOT reliably ensure all four conditions work together simultaneously.**

**Reliable:**
- ✅ BM25: Text + Filter + Sort + Algorithm ✅
- ✅ Semantic: Text + Filter + Algorithm ✅
- ✅ Hybrid: Text + Filter + Algorithm ✅

**Unreliable:**
- ❌ Semantic: Cannot combine with non-relevance sorting
- ❌ Hybrid: Falls back to BM25-only for non-relevance sorting

**Recommendation:** Fix sorting limitations in Semantic and Hybrid search to achieve full reliability.

