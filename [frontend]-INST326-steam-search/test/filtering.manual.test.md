# Function Library Filtering - Manual Test Guide

## Purpose
This guide helps you manually test the filtering functionality of the function library to ensure all filters work correctly.

---

## Test Environment Setup

1. **Start development server**:
```bash
npm run dev
```

2. **Open browser**:
```
http://localhost:3000/function-library
```

---

## Test Cases

### Test 1: Category Filtering via Navigator

**Steps**:
1. Wait for the page to load (should show all 12 functions)
2. Click on "🌐 API Endpoints" in the left sidebar
3. Verify that only 4 functions are displayed
4. Check that all displayed functions have "API Endpoint" category

**Expected Result**:
- ✅ Only 4 functions displayed
- ✅ All are API endpoints: search_games, get_game_detail, get_search_suggestions, health_check
- ✅ "API Endpoints" is highlighted in the navigator
- ✅ Other category functions are hidden

**Pass/Fail**: _______

---

### Test 2: Navigate Between Categories

**Steps**:
1. Click "🌐 API Endpoints" → should show 4 functions
2. Click "🔍 Search Algorithms" → should show 3 functions  
3. Click "💾 Data Access" → should show 4 functions
4. Click "🔒 Validation & Security" → should show 1 function
5. Click "📂 All Functions" → should show all 12 functions

**Expected Result**:
- ✅ Each category shows the correct number of functions
- ✅ Highlighting changes correctly
- ✅ Function counts match navigator badges

**Pass/Fail**: _______

---

### Test 3: Search Filter

**Steps**:
1. Click "📂 All Functions" to show all
2. Type "search" in the search box
3. Verify filtered results

**Expected Result**:
- ✅ Shows functions with "search" in name: search_games, search_bm25_index, search_faiss_index, get_search_suggestions
- ✅ Real-time filtering as you type
- ✅ Clear button appears when text is entered

**Pass/Fail**: _______

---

### Test 4: Combined Category + Search Filter

**Steps**:
1. Click "🌐 API Endpoints" (should show 4 functions)
2. Type "search" in search box
3. Verify filtered results

**Expected Result**:
- ✅ Shows only API endpoint functions with "search": search_games, get_search_suggestions
- ✅ Other search functions (from other categories) are hidden
- ✅ Both filters work together correctly

**Pass/Fail**: _______

---

### Test 5: Clear Filters

**Steps**:
1. Apply a category filter (click any category)
2. Type something in search box
3. Click "Clear Filters" button
4. Verify all filters are cleared

**Expected Result**:
- ✅ Category resets to "All Functions"
- ✅ Search box is cleared
- ✅ All 12 functions are displayed
- ✅ "Clear Filters" button disappears

**Pass/Fail**: _______

---

### Test 6: No Results State

**Steps**:
1. Type "nonexistentfunction" in search box
2. Verify "No Functions Found" message appears

**Expected Result**:
- ✅ No function cards displayed
- ✅ Shows "No Functions Found" message
- ✅ Suggestion to adjust filters is shown

**Pass/Fail**: _______

---

### Test 7: Navigator Function Counts

**Steps**:
1. Check the function count badges on each category
2. Click each category and count displayed functions manually

**Expected Result**:
- ✅ API Endpoints badge shows "4" and displays 4 functions
- ✅ Search Algorithms badge shows "3" and displays 3 functions
- ✅ Data Access badge shows "4" and displays 4 functions
- ✅ Validation & Security badge shows "1" and displays 1 function
- ✅ All Functions shows "12" total

**Pass/Fail**: _______

---

### Test 8: Mobile Responsiveness (if applicable)

**Steps**:
1. Resize browser to mobile width (< 1024px)
2. Verify floating button appears (bottom-right corner)
3. Click floating button to open navigator
4. Click a category
5. Verify navigator closes automatically

**Expected Result**:
- ✅ Navigator is hidden by default on mobile
- ✅ Floating button is visible
- ✅ Navigator slides in from left when opened
- ✅ Background overlay is visible
- ✅ Navigator closes when clicking overlay or selecting category

**Pass/Fail**: _______

---

### Test 9: Search by Tags

**Steps**:
1. Click "All Functions"
2. Type "fastapi" in search box
3. Verify results include functions tagged with #fastapi

**Expected Result**:
- ✅ Shows functions with #fastapi tag
- ✅ Tag-based search works correctly

**Pass/Fail**: _______

---

### Test 10: Category Dropdown (in Search Component)

**Steps**:
1. Locate the category dropdown in the search filters area
2. Select different categories from dropdown
3. Verify filtering works

**Expected Result**:
- ✅ Dropdown shows all categories
- ✅ Selecting a category filters functions
- ✅ Syncs with navigator selection

**Pass/Fail**: _______

---

## API Testing

### Test API Response Structure

**Command**:
```bash
curl -s http://localhost:3000/api/functions | jq '{
  success: .success,
  function_count: (.functions | length),
  category_count: (.categories | length),
  categories: .categories | map(.displayName),
  api_endpoint_functions: [.functions[] | select(.sourceFile | contains("api-endpoints")) | .name]
}'
```

**Expected Output**:
```json
{
  "success": true,
  "function_count": 12,
  "category_count": 4,
  "categories": [
    "API Endpoints",
    "Search Algorithms",
    "Data Access",
    "Validation & Security"
  ],
  "api_endpoint_functions": [
    "search_games",
    "get_game_detail",
    "get_search_suggestions",
    "health_check"
  ]
}
```

**Pass/Fail**: _______

---

## Integration Testing Script

Run this to verify filtering logic programmatically:

```bash
# Test category filtering
node -e "
const functions = [
  {name: 'search_games', category: 'API Endpoint', sourceFile: 'docs/functions/backend/api-endpoints/search_games.md'},
  {name: 'search_bm25_index', category: 'Search Algorithm', sourceFile: 'docs/functions/backend/search-algorithms/search_bm25_index.md'}
];

const filtered = functions.filter(f => f.sourceFile.includes('/api-endpoints/'));
console.log('Filtered count:', filtered.length);
console.log('Expected: 1, Actual:', filtered.length);
console.log('Pass:', filtered.length === 1 ? 'YES' : 'NO');
"
```

---

## Checklist

Before marking as complete, verify:

- [ ] All 12 functions load correctly
- [ ] All 4 categories display in navigator
- [ ] Category filtering works (tested all 4 categories)
- [ ] Search filtering works
- [ ] Combined filters work
- [ ] Clear filters works
- [ ] Function counts are accurate
- [ ] No console errors
- [ ] Mobile responsive works
- [ ] API returns correct data structure

---

## Known Issues

Document any issues found during testing:

1. _______________________________
2. _______________________________
3. _______________________________

---

## Test Summary

**Date**: __________
**Tester**: __________
**Pass Rate**: ____ / 10
**Status**: ☐ Pass ☐ Fail ☐ Partial

**Notes**:
________________________________
________________________________
________________________________

