# tokenize_text

## tokenize_text

**Category:** Utilities
**Complexity:** Medium
**Last Updated:** 2024-10-11

### Description
Tokenizes text for search indexing and processing. Handles multiple languages, removes stop words, applies stemming, and normalizes tokens for consistent search behavior across the application.

### Signature
```python
def tokenize_text(text: str, language: str = "english", remove_stopwords: bool = True) -> List[str]:
```

### Parameters
- `text` (str, required): Text to tokenize
- `language` (str, optional): Language for stop words and stemming (default: "english")
- `remove_stopwords` (bool, optional): Whether to remove stop words (default: True)

### Returns
- `List[str]`: List of normalized tokens

### Example
```python
import re
import string
from typing import List

def tokenize_text(text: str, language: str = "english", remove_stopwords: bool = True) -> List[str]:
    """
    Tokenize text for search indexing with language-aware processing
    """
    if not text:
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into tokens
    tokens = text.split()
    
    # Remove stop words if requested
    if remove_stopwords:
        stop_words = get_stop_words(language)
        tokens = [token for token in tokens if token not in stop_words]
    
    # Filter out very short tokens
    tokens = [token for token in tokens if len(token) > 2]
    
    # Apply stemming for better matching
    stemmed_tokens = [stem_word(token, language) for token in tokens]
    
    return stemmed_tokens

def get_stop_words(language: str) -> set:
    """Get stop words for the specified language"""
    english_stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
    }
    
    if language == "english":
        return english_stop_words
    else:
        return set()  # Add other languages as needed

def stem_word(word: str, language: str) -> str:
    """Simple stemming for common suffixes"""
    if language == "english":
        # Remove common suffixes
        suffixes = ['ing', 'ed', 'er', 'est', 'ly', 's']
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
    return word

# Usage example
tokens = tokenize_text("The best action games are amazing!")
# Returns: ['best', 'action', 'game', 'amaz']
```

### Notes
- Handles multiple languages with extensible stop word lists
- Applies simple but effective stemming for better matching
- Removes punctuation and normalizes case for consistency
- Filters out very short tokens to reduce noise
- Optimized for search indexing performance

### Related Functions
- [sanitize_input](#sanitize_input)
- [normalize_text](#normalize_text)
- [load_bm25_index](#load_bm25_index)

### Tags
#tokenization #nlp #search #stemming #stopwords #preprocessing
