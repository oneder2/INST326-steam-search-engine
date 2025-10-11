# Python Backend Function Library Documentation

This directory contains comprehensive documentation for all Python FastAPI backend functions used in the Steam Game Search Engine project. Each function is documented in markdown format with detailed descriptions, parameters, examples, and usage guidelines showcasing the backend implementation.

## Directory Structure

```
docs/functions/
├── README.md                 # This file - overview and guidelines
└── backend/                 # Python FastAPI backend functions
    ├── api_endpoints.md     # FastAPI endpoint functions
    ├── search_algorithms.md # BM25, Faiss, and fusion ranking
    └── data_access.md       # Database and index loading functions
```

## Documentation Format

Each function should be documented using the following markdown format:

```markdown
## Function Name

**Category:** [Category Name]
**Complexity:** [Low/Medium/High]
**Last Updated:** [YYYY-MM-DD]

### Description
Brief description of what the function does and its purpose.

### Signature
```typescript
functionName(param1: Type1, param2: Type2): ReturnType
```

### Parameters
- `param1` (Type1, required): Description of parameter 1
- `param2` (Type2, optional): Description of parameter 2, default: defaultValue

### Returns
- `ReturnType`: Description of what the function returns

### Example
```typescript
// Example usage
const result = functionName(value1, value2);
console.log(result);
```

### Notes
Any additional notes, warnings, or important information.

### Related Functions
- [relatedFunction1](#related-function-1)
- [relatedFunction2](#related-function-2)

### Tags
#tag1 #tag2 #tag3
```

## Guidelines for Documentation

1. **Completeness**: Every public function should be documented
2. **Clarity**: Use clear, concise language that's easy to understand
3. **Examples**: Always provide practical, working examples
4. **Consistency**: Follow the standard format for all functions
5. **Updates**: Keep documentation current with code changes
6. **Testing**: Ensure all examples work as documented

## Function Categories

### API Endpoints
FastAPI endpoint functions that handle HTTP requests, implement business logic, and return structured responses. Includes search endpoints, game detail endpoints, and health checks.

### Search Algorithms
Core search functionality including BM25 keyword search, Faiss semantic search with embeddings, and fusion ranking algorithms that combine multiple relevance signals.

### Data Access
Functions for database operations, index loading, and data retrieval. Includes SQLite database access, Faiss index management, and BM25 index operations.

### Validation & Security
Input validation, sanitization, and security functions to ensure data integrity and prevent injection attacks. Includes query validation and malicious pattern detection.

## Usage in Function Library Page

The Function Library page (`/function-library`) automatically reads and parses these markdown files to generate an interactive documentation browser. The page provides:

- **Search functionality**: Find functions by name, description, or tags
- **Category filtering**: Browse functions by category
- **Interactive examples**: Copy code examples to clipboard
- **Export options**: Generate documentation in various formats

## Contributing

When adding new functions or updating existing ones:

1. Create or update the appropriate markdown file
2. Follow the standard documentation format
3. Include comprehensive examples
4. Add appropriate tags for searchability
5. Update the last modified date
6. Test all code examples

## Maintenance

This documentation is maintained by the INST326 development team. For questions or suggestions, please contact the project maintainers.

---

**Note**: This documentation system is designed for the INST326 group assignment and serves as both functional documentation and a demonstration of comprehensive code documentation practices.
