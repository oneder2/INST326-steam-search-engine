# Testing Strategy Documentation

**Project:** Steam Game Search Engine  
**Course:** INST326 Project 4  
**Date:** December 14, 2025

---

## 📋 Testing Overview

Our comprehensive testing suite includes:
- **7 Unit Tests**: Test individual methods in isolation
- **8 Integration Tests**: Test component interactions (exceeds 5-8 requirement)
- **5 System Tests**: Test complete end-to-end workflows (meets 3-5 requirement)

**Total Tests:** 20 automated tests  
**Framework:** Python unittest module  
**Status:** All critical tests passing ✅

---

## 🧪 Testing Strategy

### 1. Unit Tests (`tests/unit/`)

**Purpose:** Verify individual class methods work correctly in isolation

**Coverage:**
- PersistenceService methods
  - Save/load search history
  - Save/load user preferences
  - Export to CSV/JSON
  - Import from CSV/JSON
  - Error handling for missing files

**Test File:** `tests/unit/test_persistence.py`

**Key Tests:**
1. `test_save_and_load_search_history` - Verifies history persistence
2. `test_save_and_load_preferences` - Verifies preference management
3. `test_export_to_csv` - Verifies CSV export
4. `test_export_to_json` - Verifies JSON export
5. `test_load_missing_file` - Verifies graceful error handling
6. `test_export_empty_data` - Verifies edge case handling

---

### 2. Integration Tests (`tests/integration/`)

**Purpose:** Verify how components coordinate and interact

**Coverage:**
- Search + Filters coordination
- Pagination + Sorting integration
- Search → Export workflow
- Search history persistence workflow
- Filter validation across components
- SearchRequest model validation
- Import → Search workflow
- Error handling across layers

**Test File:** `tests/integration/test_search_workflows.py`

**Key Tests:**
1. `test_1_search_with_filters_integration` - Verify SearchRequest with Filters
2. `test_2_pagination_with_sorting_integration` - Verify offset/limit with sorting
3. `test_3_search_to_export_workflow` - Verify search results can be exported
4. `test_4_search_history_persistence_workflow` - Verify history save/load
5. `test_5_filter_validation_integration` - Verify filter validation
6. `test_6_search_request_model_integration` - Verify Pydantic model validation
7. `test_7_import_to_search_workflow` - Verify imported data can be searched
8. `test_8_error_handling_integration` - Verify graceful error handling

---

### 3. System Tests (`tests/system/`)

**Purpose:** Verify complete end-to-end user workflows

**Coverage:**
- Complete search journey (open app → search → filter → sort → export)
- Session persistence (save → close → reopen → restore)
- Data pipeline (import → search → export)
- User preferences management
- Error recovery scenarios

**Test File:** `tests/system/test_complete_workflows.py`

**Key Tests:**
1. `test_workflow_1_complete_search_journey` - Full search user journey
2. `test_workflow_2_save_load_session_persistence` - Session persistence
3. `test_workflow_3_import_search_export_pipeline` - Complete data pipeline
4. `test_workflow_4_user_preferences_management` - Preference persistence
5. `test_workflow_5_error_recovery` - Error handling and recovery

---

## 🎯 Coverage Rationale

### Why These Tests?

**Unit Tests Focus:**
- PersistenceService is critical for Project 4 I/O requirements
- Need to verify save/load functionality works independently
- Need to test file I/O error handling

**Integration Tests Focus:**
- Search is the core feature - must verify all parts work together
- Filters, sorting, pagination must coordinate correctly
- Export must work with search results
- History must persist across sessions

**System Tests Focus:**
- Verify real user workflows work end-to-end
- Ensure data persists between sessions (Project 4 requirement)
- Verify import/export pipelines work completely
- Test error recovery (robustness requirement)

---

## 🚀 How to Run Tests

### Run All Tests
```bash
cd backend
python -m unittest discover tests
```

### Run Specific Test Suite
```bash
# Unit tests only
python -m unittest discover tests/unit

# Integration tests only
python -m unittest discover tests/integration

# System tests only
python -m unittest discover tests/system
```

### Run Single Test File
```bash
python -m unittest tests.unit.test_persistence
python -m unittest tests.integration.test_search_workflows
python -m unittest tests.system.test_complete_workflows
```

### Run with Verbose Output
```bash
python -m unittest discover tests -v
```

---

## ✅ Test Results Summary

**Last Run:** December 14, 2025, 22:45

| Test Suite | Tests | Passed | Status |
|------------|-------|--------|--------|
| Unit Tests | 7 | 7 | ✅ All Pass |
| Integration Tests | 8 | 8 | ✅ All Pass |
| System Tests | 5 | 5 | ✅ All Pass |
| **Total** | **20** | **20** | ✅ **100%** |

---

## 📊 What We Test

### Data Persistence (Project 4 Requirement)
- ✅ Save search history to file
- ✅ Load search history from file
- ✅ Save user preferences
- ✅ Load user preferences
- ✅ Handle missing files gracefully
- ✅ Handle corrupted data gracefully

### Import Capabilities (Project 4 Requirement)
- ✅ Import from CSV format
- ✅ Import from JSON format
- ✅ Validate imported data
- ✅ Handle invalid files gracefully

### Export Features (Project 4 Requirement)
- ✅ Export search results to CSV
- ✅ Export search results to JSON
- ✅ Generate summary reports
- ✅ Handle empty data gracefully

### Core Search Functionality
- ✅ Multi-field text search
- ✅ Filter by price, genre, type
- ✅ Sort by multiple criteria
- ✅ Pagination with offset/limit
- ✅ Relevance scoring

### Error Handling
- ✅ Missing files
- ✅ Corrupted data
- ✅ Invalid input
- ✅ Empty data
- ✅ Graceful degradation

---

## 🔍 Testing Best Practices Used

### 1. Isolation
- Unit tests use temporary directories
- Tests clean up after themselves
- No dependency on external services (for time constraints)

### 2. Clarity
- Descriptive test names
- Clear docstrings explaining what is tested
- Print statements showing test progress

### 3. Coverage
- Test happy paths (normal operation)
- Test edge cases (empty data, missing files)
- Test error conditions (corrupted data, invalid input)

### 4. Organization
- Logical directory structure
- Tests grouped by type (unit/integration/system)
- Clear naming conventions

---

## 🎓 What This Demonstrates

**Project 4 Requirements Met:**
- ✅ Comprehensive testing suite
- ✅ Unit tests for individual methods
- ✅ 5-8 integration tests (we have 8)
- ✅ 3-5 system tests (we have 5)
- ✅ Testing strategy documented
- ✅ All tests passing
- ✅ Using Python unittest module
- ✅ Tests demonstrate I/O and persistence features

**Software Engineering Best Practices:**
- Automated testing
- Test-driven development mindset
- Clear documentation
- Reproducible results
- Professional quality assurance

---

## 📝 Notes

### Test Environment
- Tests run in isolated temporary directories
- Sample data files provided for import tests
- No external database required for basic tests
- All file I/O uses pathlib and context managers

### Future Enhancements
- Add tests with real database connection
- Add performance/load tests
- Add frontend integration tests
- Add API endpoint tests with test client

---

**Testing is critical for reliable software. Our comprehensive suite ensures the Steam Game Search Engine works correctly and handles errors gracefully.**



