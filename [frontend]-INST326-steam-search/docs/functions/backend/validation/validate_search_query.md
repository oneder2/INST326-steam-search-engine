# validate_search_query

## validate_search_query

**Category:** Validation
**Complexity:** Medium
**Last Updated:** 2024-10-08

### Description
Validates and sanitizes user search input to prevent injection attacks and ensure query compatibility with search algorithms. Performs comprehensive input validation including length checks, character filtering, and malicious pattern detection.

### Signature
```python
def validate_search_query(query: str) -> str:
```

### Parameters
- `query` (str, required): Raw user search input

### Returns
- `str`: Cleaned and validated search query

### Example
```python
import re
from typing import List

# Security patterns to detect and remove
MALICIOUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # Script tags
    r'javascript:',                # JavaScript URLs
    r'on\w+\s*=',                 # Event handlers
    r'<iframe[^>]*>.*?</iframe>',  # Iframe tags
    r'eval\s*\(',                 # Eval functions
    r'document\.',                # DOM access
]

def validate_search_query(query: str) -> str:
    """
    Validate and sanitize search query input
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    # 1. Length validation
    if len(query) > 500:
        raise ValueError("Query exceeds maximum length of 500 characters")
    
    if len(query.strip()) < 1:
        raise ValueError("Query cannot be empty")
    
    # 2. Remove malicious patterns
    cleaned_query = query
    for pattern in MALICIOUS_PATTERNS:
        cleaned_query = re.sub(pattern, '', cleaned_query, flags=re.IGNORECASE)
    
    # 3. Remove HTML tags
    cleaned_query = re.sub(r'<[^>]+>', '', cleaned_query)
    
    # 4. Normalize whitespace
    cleaned_query = re.sub(r'\s+', ' ', cleaned_query.strip())
    
    # 5. Remove special characters (keep alphanumeric, spaces, basic punctuation)
    cleaned_query = re.sub(r'[^\w\s\-.,!?\'"]', '', cleaned_query)
    
    # 6. Final length check after cleaning
    if len(cleaned_query.strip()) < 1:
        raise ValueError("Query contains no valid search terms")
    
    return cleaned_query

def detect_sql_injection(query: str) -> bool:
    """Detect potential SQL injection patterns"""
    sql_patterns = [
        r'\b(union|select|insert|update|delete|drop|create|alter)\b',
        r'[\'";]',
        r'--',
        r'/\*.*?\*/',
        r'\bor\b.*?=.*?=',
        r'\band\b.*?=.*?='
    ]
    
    query_lower = query.lower()
    for pattern in sql_patterns:
        if re.search(pattern, query_lower):
            return True
    
    return False

# Usage in FastAPI endpoint
@app.post("/api/v1/search/games")
async def search_games(query: SearchQuerySchema):
    try:
        # Validate search query
        clean_query = validate_search_query(query.query)
        
        # Check for SQL injection
        if detect_sql_injection(clean_query):
            logger.warning(f"Potential SQL injection detected: {query.query}")
            raise HTTPException(status_code=400, detail="Invalid query format")
        
        # Proceed with search...
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Notes
- Maximum query length: 500 characters
- Removes HTML tags, script elements, and event handlers
- Preserves Unicode characters for international search terms
- Logs suspicious queries for security monitoring
- Raises HTTPException with appropriate status codes for FastAPI

### Related Functions
- [detect_sql_injection](#detect_sql_injection)
- [sanitize_input](#sanitize_input)
- [search_games](#search_games)

### Tags
#validation #security #sanitization #sql-injection #xss
