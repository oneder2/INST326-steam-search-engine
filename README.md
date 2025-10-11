# Steam Game Search Engine

An intelligent game discovery platform that combines advanced search algorithms with modern web technologies to help users find their next favorite Steam game.

## 🎮 Project Overview

The Steam Game Search Engine addresses the limitations of Steam's current search functionality by implementing:

- **Intelligent Search**: Combines BM25 keyword matching with semantic search using vector embeddings
- **Fusion Ranking**: Advanced algorithm that balances relevance, review quality, and player activity
- **Advanced Filtering**: Comprehensive filters for price, platform, multiplayer type, and Steam Deck compatibility
- **Modern Interface**: Responsive, Steam-themed UI built with React and TypeScript

This project was developed as part of the **INST326 - Object-Oriented Programming** course at the University of Maryland.

## 🚀 Features

### Core Functionality
- **Natural Language Search**: Search using phrases like "games like Hades" or "cozy farming games"
- **Smart Recommendations**: Algorithm surfaces hidden gems alongside popular titles
- **Real-time Suggestions**: Autocomplete functionality for improved search experience
- **Detailed Game Information**: Comprehensive game details with quality metrics

### Technical Features
- **Type-Safe Development**: Full TypeScript implementation with comprehensive type definitions
- **Component Library**: Reusable UI components with consistent Steam-themed design
- **API Integration**: RESTful API client with error handling and caching
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Function Documentation**: Comprehensive function library for code documentation

## 🛠️ Technology Stack

### Frontend (Next.js)
- **Next.js 14** - React framework with SSR and routing
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework with Steam theme
- **React Hooks** - Modern state management
- **Axios** - HTTP client for FastAPI backend communication

### Backend (Python FastAPI)
- **FastAPI** - High-performance Python web framework
- **SQLite** - Lightweight database for game metadata
- **Faiss** - Vector similarity search library for semantic search
- **BM25** - Keyword search algorithm implementation
- **Pydantic** - Data validation and serialization
- **Sentence Transformers** - Text embedding generation
- **Uvicorn** - ASGI server for production deployment

### Development Tools
- **ESLint** - Code linting and quality checks
- **Prettier** - Code formatting
- **Jest** - Unit testing framework
- **TypeScript Compiler** - Type checking

## 📁 Project Structure

```
steam-searcher-engine/
├── src/                           # Frontend source code (Next.js)
│   ├── components/                # React components
│   │   ├── Layout/               # Layout components
│   │   ├── Search/               # Search-related components
│   │   └── FunctionLibrary/      # Function documentation components
│   ├── pages/                    # Next.js pages and API routes
│   │   ├── api/                  # Next.js API routes
│   │   │   └── functions.ts     # Function library API endpoint (NEW)
│   │   ├── function-library.tsx  # Function library page
│   │   └── ...                   # Other pages
│   ├── services/                 # API services and clients
│   ├── types/                    # TypeScript type definitions
│   ├── constants/                # Application constants
│   ├── hooks/                    # Custom React hooks
│   ├── utils/                    # Utility functions
│   │   └── markdownParser.ts    # Markdown parser utility (NEW)
│   └── styles/                   # Global styles and CSS
├── steam-search-backend/          # Backend API service (FastAPI)
│   ├── main.py                   # FastAPI application
│   ├── requirements.txt          # Full backend dependencies
│   ├── requirements-core.txt     # Core dependencies for deployment
│   ├── .env.example             # Environment configuration
│   └── README.md                 # Backend documentation
├── steam-search-crawler/          # Data collection service
│   ├── main.py                   # Crawler application
│   ├── requirements.txt          # Crawler dependencies
│   ├── .env.example             # Crawler configuration
│   └── README.md                 # Crawler documentation
├── docs/                          # Project documentation
│   ├── functions/                # Function library documentation (markdown)
│   │   └── backend/              # Python backend function docs (one file per function)
│   │       ├── old_format/       # Backup of old multi-function files
│   │       ├── search_games.md   # Individual function documentation
│   │       ├── apply_fusion_ranking.md
│   │       ├── validate_search_query.md
│   │       └── ... (12 total)    # Each function in its own file
│   ├── 技术文档/                  # Technical documentation
│   └── 软需求文档/                # Requirements documentation
├── test/                          # Test files (NEW)
│   ├── README.md                 # Testing guide
│   ├── markdownParser.test.ts   # Markdown parser tests
│   └── functionLibrary.integration.test.tsx # Integration tests
├── public/                       # Static assets
├── render.yaml                   # Render.com deployment config
├── Dockerfile.backend            # Backend Docker configuration
├── Dockerfile.frontend           # Frontend Docker configuration
├── package.json                  # Frontend dependencies and scripts
├── tsconfig.json                # TypeScript configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── next.config.js               # Next.js configuration
└── README.md                    # This file
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18.0.0 or higher
- **npm** 8.0.0 or higher
- **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/oneder2/INST326-steam-searcher-engine.git
   cd INST326-steam-searcher-engine
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode

## 📖 Usage

### Basic Search
1. Navigate to the home page
2. Enter your search query (e.g., "roguelike games", "games like Hades")
3. View intelligent search results with relevance scores

### Advanced Search
1. Go to the Search page (`/search`)
2. Use the search box for your query
3. Apply filters for price, platform, multiplayer type
4. Browse paginated results

### Function Library
1. Visit the Function Library page (`/function-library`)
2. Browse documented functions by category
3. Search for specific functions or features
4. View code examples and implementation details

## 🏗️ Architecture

### System Architecture
The Steam Game Search Engine follows a modern microservices architecture with separated concerns:

```
Frontend (Next.js)  ←→  Backend API (FastAPI)  ←→  Data Layer (SQLite + Indices)
     │                        │                        ↑
  React UI              Python Services           Data Crawler
  TypeScript           Search Algorithms          (Steam API)
  Tailwind CSS         API Endpoints                   │
     │                        │                        │
  Deployed on           Deployed on              Runs Independently
  Render.com           Render.com               (Data Collection)
```

### Service Separation
- **Frontend**: `/` - Next.js React application
- **Backend API**: `/steam-search-backend/` - FastAPI service
- **Data Crawler**: `/steam-search-crawler/` - Data collection service

### Frontend Architecture (Next.js)
- **Pages**: Next.js pages handling routing and server-side rendering
- **Components**: Reusable UI components with Steam-themed design
- **Services**: API clients for FastAPI backend communication
- **Types**: TypeScript definitions matching backend Pydantic models
- **Hooks**: Custom React hooks for state management
- **Utils**: Pure utility functions for data transformation

### Backend Architecture (Python FastAPI)
- **API Endpoints**: RESTful endpoints for search, game details, health checks
- **Search Algorithms**: BM25 keyword search and Faiss semantic search
- **Fusion Ranking**: Advanced algorithm combining multiple relevance signals
- **Data Access**: SQLite database operations and index management
- **Validation**: Input sanitization and security functions

### Data Layer
- **SQLite Database**: Game metadata (title, description, price, genres)
- **Faiss Index**: Vector embeddings for semantic search
- **BM25 Index**: Preprocessed keyword search index
- **Game ID Mapping**: Index position to game ID relationships

### API Design (FastAPI)
- **RESTful Endpoints**: Standard HTTP methods and status codes
- **Pydantic Models**: Type-safe request/response validation
- **Error Handling**: Comprehensive error responses with proper HTTP codes
- **Health Monitoring**: Built-in health checks and service status
- **CORS Support**: Configured for frontend-backend communication

## 📚 Python Backend Function Library

The project includes a comprehensive function library documenting all Python FastAPI backend functions with **dynamic markdown-based documentation**:

### 🆕 Dynamic Documentation System (Latest Feature)

**Latest Update**: The function library now features a **categorized folder structure with navigation sidebar**!

#### Key Features
1. **Categorized Organization**: Functions organized into 4 categories with dedicated folders
2. **Navigation Sidebar**: Left sidebar with icons, function counts, and quick navigation
3. **Category Metadata**: Each category has a `category.json` file with detailed information
4. **One File Per Function**: Each function in its own markdown file for maximum clarity
5. **Responsive Design**: Mobile-friendly with collapsible navigation

#### How It Works
1. **Folder Structure**: Functions organized in `docs/functions/backend/<category>/<function>.md`
2. **Auto-Parsing**: System reads nested directories and category metadata
3. **API Integration**: `/api/functions` returns functions grouped by category
4. **Frontend Display**: Interactive navigation sidebar with real-time filtering

#### Advantages
- ✅ **Easy Updates**: Modify function docs by editing markdown files (no code changes needed)
- ✅ **Categorized Structure**: Functions organized by purpose in dedicated folders
- ✅ **Visual Navigation**: Left sidebar with icons, counts, and quick filtering
- ✅ **Category Metadata**: Rich information about each category's purpose and best practices
- ✅ **Better Readability**: One file per function + folder organization
- ✅ **Version Control**: Documentation changes tracked through Git with minimal conflicts
- ✅ **Type-Safe**: Full TypeScript integration with type definitions

#### Updating Function Documentation
To add or modify function documentation:

1. **One File Per Function** - Each function has its own markdown file in `docs/functions/backend/`:
   - Examples: `search_games.md`, `apply_fusion_ranking.md`, `validate_search_query.md`
   - Total: 12 individual function documentation files
   - This structure improves readability and makes it easier to locate specific functions

2. **To modify an existing function**, edit its markdown file directly:
   - Locate the file: `docs/functions/backend/<function_name>.md`
   - Make your changes
   - Save the file
   - Refresh the function library page - changes appear automatically!

3. **To add a new function**, create a new markdown file following this format:
```markdown
# function_name

## function_name

**Category:** API Endpoint
**Complexity:** High
**Last Updated:** 2024-10-10

### Description
Function description here...

### Signature
\`\`\`python
def function_name(param: type) -> ReturnType:
\`\`\`

### Parameters
- `param` (type, required): Parameter description

### Returns
- `ReturnType`: Return value description

### Example
\`\`\`python
# Usage example
result = function_name(value)
\`\`\`

### Tags
#tag1 #tag2
```

**File naming**: Use the exact function name as the filename (e.g., `my_function.md` for `my_function()`)

### Categories
- **API Endpoints**: FastAPI endpoint functions (search_games, get_game_detail, health_check)
- **Search Algorithms**: BM25, Faiss semantic search, and fusion ranking algorithms
- **Data Access**: SQLite database operations and index loading functions
- **Validation & Security**: Input validation, sanitization, and security functions

### Documentation Format
Each Python function is documented with:
- Detailed description and purpose
- Python function signature with type hints
- Complete parameter documentation with types and default values
- Usage examples with working Python code
- Related functions and dependencies
- Complexity assessment and performance notes
- Tags for easy searching and categorization
- Integration with FastAPI framework

### Function Examples
- `search_games()` - Main FastAPI endpoint for game search
- `apply_fusion_ranking()` - Core ranking algorithm
- `search_bm25_index()` - BM25 keyword search implementation
- `search_faiss_index()` - Semantic search with vector embeddings
- `validate_search_query()` - Input validation and sanitization

Visit `/function-library` to explore the complete Python backend documentation.

### Technical Implementation
- **Parser**: Custom markdown parser with nested directory support (`src/utils/markdownParser.ts`)
- **API Endpoint**: `/api/functions` - Reads markdown files and category metadata
- **Navigator**: Left sidebar component with category navigation (`FunctionNavigator.tsx`)
- **Frontend**: Dynamic rendering with search, filter, and category navigation
- **Tests**: Comprehensive test suite in `test/` directory
- **Structure**: 4 categories, 12 functions, 17 total files

### Directory Structure
```
docs/functions/backend/
├── api-endpoints/        (🌐 4 functions) - REST API endpoints
├── search-algorithms/    (🔍 3 functions) - Search & ranking algorithms
├── data-access/          (💾 4 functions) - Database operations
└── validation/           (🔒 1 function)  - Security & validation
```

## 🧪 Testing

The project includes comprehensive tests for all major functionality, including the new markdown-based function library system.

### Test Suite Overview

#### 1. Markdown Parser Tests (`test/markdownParser.test.ts`)
Tests for the markdown parsing utility:
- ✅ Parse single and multiple function documents
- ✅ Extract function metadata (category, complexity, dates)
- ✅ Parse parameters with types and defaults
- ✅ Extract code examples and signatures
- ✅ Parse tags and related functions
- ✅ Handle edge cases and invalid input
- ✅ Validate documentation completeness

#### 2. Function Library Integration Tests (`test/functionLibrary.integration.test.ts`)
End-to-end tests for the function library feature:
- ✅ API endpoint responses
- ✅ Frontend component rendering
- ✅ Search and filter functionality
- ✅ Error handling and recovery
- ✅ User interactions (expand/collapse, copy code)
- ✅ Performance with large datasets

### Running Tests

#### Run All Tests
```bash
npm test                    # Run all tests
npm run test:watch         # Run tests in watch mode
npm run test:coverage      # Generate coverage report
```

#### Run Specific Test Suites
```bash
npm test markdownParser.test.ts              # Test markdown parser only
npm test functionLibrary.integration.test.tsx # Test function library integration
```

#### Test with Verbose Output
```bash
npm test -- --verbose       # Show detailed test output
```

### Test Coverage Goals

| Type      | Target | Description                |
|-----------|--------|----------------------------|
| Statements| ≥ 80%  | Code coverage for all files|
| Branches  | ≥ 75%  | Conditional logic coverage |
| Functions | ≥ 80%  | Function execution coverage|
| Lines     | ≥ 80%  | Line-by-line coverage      |

### Test Documentation

For detailed testing information, see [test/README.md](test/README.md) which includes:
- Complete test suite documentation
- Running and debugging tests
- Adding new tests
- Best practices and conventions
- CI/CD integration

### Type Checking
```bash
npm run type-check         # Check TypeScript types
```

### Linting
```bash
npm run lint               # Check code quality
npm run lint:fix           # Fix auto-fixable issues
```

### Continuous Integration

Tests run automatically on:
- Push to any branch
- Pull request creation
- Merge to main branch

The CI pipeline includes:
1. Install dependencies
2. TypeScript type checking
3. ESLint code quality checks
4. Complete test suite execution
5. Coverage report generation

## 🚀 Deployment

### Render.com Deployment

The project is configured for deployment on Render.com with separate services for frontend and backend:

#### Quick Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/oneder2/INST326-steam-searcher-engine)

#### Manual Deployment
1. **Backend Service** (Python FastAPI):
   ```bash
   # Build Command: pip install -r steam-search-backend/requirements-core.txt
   # Start Command: cd steam-search-backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Frontend Service** (Next.js):
   ```bash
   # Build Command: npm ci && npm run build
   # Start Command: npm start
   ```

3. **Data Crawler** (Independent Service):
   ```bash
   # Not deployed on Render - runs independently for data collection
   # Can be run on local machine or separate server
   ```

#### Environment Variables

**Frontend (Next.js)**:
```env
NEXT_PUBLIC_API_BASE_URL=https://steam-search-backend.onrender.com
NEXT_PUBLIC_APP_URL=https://steam-search-frontend.onrender.com
NEXT_PUBLIC_DEBUG=false
```

**Backend (FastAPI)**:
```env
PYTHON_VERSION=3.11.0
ENVIRONMENT=production
DATABASE_URL=sqlite:///data/games_data.db
FAISS_INDEX_PATH=data/game_embeddings.faiss
BM25_INDEX_PATH=data/bm25_index.pkl
CORS_ORIGINS=https://steam-search-frontend.onrender.com
```

### Local Development

#### Frontend Development
```bash
# Install dependencies
npm install

# Start Next.js development server
npm run dev                # Runs on http://localhost:3000
```

#### Backend API Development
```bash
# Navigate to backend directory
cd steam-search-backend

# Install dependencies
pip install -r requirements-core.txt  # Core dependencies (recommended)
# OR
pip install -r requirements.txt       # Full dependencies (includes ML libraries)

# Start FastAPI development server
python main.py             # Runs on http://localhost:8000
# OR
uvicorn main:app --reload  # Alternative start command
```

#### Data Crawler Development
```bash
# Navigate to crawler directory
cd steam-search-crawler

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Steam API key

# Initialize database
python main.py --init-db

# Run data collection
python main.py --full-crawl
```

**Note**: Each service has its own requirements.txt file optimized for its specific needs.

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📋 FastAPI Backend Documentation

### Core API Endpoints

#### Search Games (FastAPI)
```python
@app.post("/api/v1/search/games", response_model=GameResultSchema)
async def search_games(query: SearchQuerySchema) -> GameResultSchema:
```

**Request Body**:
```json
{
  "query": "roguelike games",
  "filters": {
    "price_max": 30,
    "coop_type": "Local",
    "platform": ["Windows", "SteamDeck"]
  },
  "limit": 20,
  "offset": 0
}
```

#### Get Game Details (FastAPI)
```python
@app.get("/api/v1/games/{game_id}", response_model=GameDetailResponse)
async def get_game_detail(game_id: int) -> GameDetailResponse:
```

#### Search Suggestions (FastAPI)
```python
@app.get("/api/v1/search/suggest", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(prefix: str) -> SearchSuggestionsResponse:
```

#### Health Check (FastAPI)
```python
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
```

### Backend Implementation
- **Framework**: Python FastAPI with Pydantic models
- **Database**: SQLite with async operations
- **Search**: BM25 + Faiss semantic search
- **Ranking**: Fusion algorithm combining multiple signals

For complete API documentation, see:
- [docs/技术文档/API 契约与后端实现文档.md](docs/技术文档/API%20契约与后端实现文档.md)
- [docs/functions/backend/](docs/functions/backend/) - Python function documentation

## 🤝 Contributing

This is an academic project for INST326. For course-related contributions:

1. Follow the established code style and conventions
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure TypeScript types are properly defined

### Code Style
- Use TypeScript for all new code
- Follow ESLint and Prettier configurations
- Write comprehensive JSDoc comments
- Use semantic commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Academic Information

- **Course**: INST326 - Object-Oriented Programming
- **Institution**: University of Maryland
- **Semester**: Fall 2024
- **Project Type**: Group Assignment

## 🔗 Links

- [Live Demo](https://steam-search-frontend.onrender.com) (Render Deployment)
- [Backend API](https://steam-search-backend.onrender.com) (FastAPI Backend)
- [Function Library](http://localhost:3000/function-library) (Python Backend Functions)
- [API Status](http://localhost:3000/api-status) (Backend Health Monitoring)
- [Technical Documentation](docs/技术文档/) (Architecture & API Contract)
- [Requirements Documentation](docs/软需求文档/) (PRD & SRS)
- [Deployment Guide](DEPLOYMENT.md) (Render.com Instructions)

## 📞 Support

For questions about this project:
- Check the [Function Library](http://localhost:3000/function-library) for code documentation
- Review the technical documentation in the `docs/` directory
- Contact the development team through course channels

---

**Note**: This project is developed for educational purposes as part of the INST326 course at the University of Maryland. It demonstrates modern web development practices, API design, and software engineering principles.
