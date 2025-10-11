# normalize_text

## normalize_text

**Category:** Utilities
**Complexity:** Low
**Last Updated:** 2024-10-11

### Description
Normalizes text for consistent processing across the application. Handles Unicode normalization, case conversion, whitespace cleanup, and character encoding issues to ensure reliable text matching and comparison.

### Signature
```python
def normalize_text(text: str, lowercase: bool = True, remove_accents: bool = False) -> str:
```

### Parameters
- `text` (str, required): Text to normalize
- `lowercase` (bool, optional): Convert to lowercase (default: True)
- `remove_accents` (bool, optional): Remove accent marks (default: False)

### Returns
- `str`: Normalized text string

### Example
```python
import unicodedata
import re

def normalize_text(text: str, lowercase: bool = True, remove_accents: bool = False) -> str:
    """
    Normalize text for consistent processing and comparison
    """
    if not text:
        return ""
    
    # Unicode normalization (NFC form)
    normalized = unicodedata.normalize('NFC', text)
    
    # Convert to lowercase if requested
    if lowercase:
        normalized = normalized.lower()
    
    # Remove accent marks if requested
    if remove_accents:
        normalized = remove_accent_marks(normalized)
    
    # Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove leading/trailing whitespace
    normalized = normalized.strip()
    
    return normalized

def remove_accent_marks(text: str) -> str:
    """Remove accent marks from text while preserving base characters"""
    # Decompose characters and remove combining marks
    decomposed = unicodedata.normalize('NFD', text)
    without_accents = ''.join(
        char for char in decomposed 
        if unicodedata.category(char) != 'Mn'
    )
    return without_accents

# Usage examples
text1 = normalize_text("  Café MÜNCHEN  ")
# Returns: "café münchen"

text2 = normalize_text("Café MÜNCHEN", remove_accents=True)
# Returns: "cafe munchen"

text3 = normalize_text("Multiple    spaces\t\nand\r\nnewlines")
# Returns: "multiple spaces and newlines"
```

### Notes
- Uses Unicode NFC normalization for consistent character representation
- Handles various whitespace characters (spaces, tabs, newlines)
- Optional accent removal for broader text matching
- Preserves original text structure while ensuring consistency
- Essential for reliable text comparison and search functionality

### Related Functions
- [sanitize_input](#sanitize_input)
- [tokenize_text](#tokenize_text)
- [validate_search_query](#validate_search_query)

### Tags
#normalization #unicode #text-processing #utilities #consistency
