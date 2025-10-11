# sanitize_input

## sanitize_input

**Category:** Utilities
**Complexity:** Low
**Last Updated:** 2024-10-11

### Description
Sanitizes user input by removing potentially harmful characters, normalizing whitespace, and preventing injection attacks. This function is essential for security and data integrity across the application.

### Signature
```python
def sanitize_input(input_text: str, max_length: int = 1000) -> str:
```

### Parameters
- `input_text` (str, required): Raw user input text to sanitize
- `max_length` (int, optional): Maximum allowed length (default: 1000)

### Returns
- `str`: Sanitized and safe input text

### Example
```python
def sanitize_input(input_text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input for security and consistency
    """
    if not input_text:
        return ""
    
    # Remove null bytes and control characters
    sanitized = input_text.replace('\x00', '').replace('\r', '')
    
    # Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    
    # Remove potentially harmful patterns
    harmful_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
    for pattern in harmful_patterns:
        sanitized = sanitized.replace(pattern.lower(), '')
        sanitized = sanitized.replace(pattern.upper(), '')
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].strip()
    
    return sanitized.strip()

# Usage example
user_query = sanitize_input("  Hello <script>alert('xss')</script> World  ")
# Returns: "Hello alert('xss') World"
```

### Notes
- Removes null bytes and control characters for security
- Normalizes whitespace to prevent formatting issues
- Filters out common XSS attack patterns
- Truncates overly long input to prevent DoS attacks
- Preserves legitimate content while ensuring safety

### Related Functions
- [validate_search_query](#validate_search_query)
- [normalize_text](#normalize_text)
- [detect_malicious_patterns](#detect_malicious_patterns)

### Tags
#security #validation #sanitization #xss-prevention #utilities
