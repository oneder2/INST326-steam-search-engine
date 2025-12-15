# Steam Game Search Engine

A modern game discovery platform built with Next.js and FastAPI, powered by Supabase PostgreSQL database.

## 🎮 Project Overview

Steam Game Search Engine provides an intelligent interface for discovering Steam games through:

- **Modern Interface**: Responsive, Steam-themed UI built with React and TypeScript
- **RESTful API**: FastAPI backend with paginated game data retrieval
- **Type-Safe Development**: Full TypeScript and Pydantic type definitions
- **Database**: Supabase PostgreSQL with 50,000+ game records

**Course**: INST326 - Object-Oriented Programming | University of Maryland | Fall 2024

## 👥 Team Members

**Team:** INST326 Project Team  
**Project:** Steam Game Search Engine (Project 4)

### Individual Contributions

**Development:**
- Backend architecture and API implementation
- Search service with multi-field search and weighted relevance scoring
- Data persistence service (save/load, import/export)
- Frontend-backend integration
- Comprehensive testing suite (20 automated tests)

**Documentation:**
- Technical documentation and architecture guides
- API documentation (Swagger/OpenAPI)
- Testing strategy and test documentation
- User guides and setup instructions

**Quality Assurance:**
- Unit testing (7 tests)
- Integration testing (8 tests)
- System testing (5 tests)
- Manual testing and bug fixes

## 📊 Project Status

✅ **Phase 2 Complete** | 🚧 **Phase 3 Planned**

**Completed:**
- ✅ Backend API with Supabase integration
- ✅ Frontend-Backend integration
- ✅ Paginated game listing (1,009 games)
- ✅ Text search (multi-field: name + description)
- ✅ Advanced filtering (price, genre, type)
- ✅ Sorting options (7 types)
- ✅ Weighted relevance scoring
- ✅ Responsive UI with Steam theme

**Next Phase:**
- 📋 BM25 ranking algorithm (Phase 3)
- 📋 Search suggestions (Phase 3)
- 📋 Semantic search with embeddings (Phase 4 - optional)

---

## 🏗️ Architecture

```
INST326-steam-searcher-engine/
├── frontend-INST326-steam-search/    # Next.js (Port 3000)
├── backend/                           # FastAPI (Port 8000)
├── docs/                              # Documentation
├── .env                               # Environment variables
└── README.md                          # This file
```

### Tech Stack

**Frontend:**
- Next.js 14, TypeScript, Tailwind CSS, React Hooks

**Backend:**
- FastAPI, Python 3.8+, Pydantic v2, Uvicorn

**Database:**
- Supabase PostgreSQL (Schema: `steam`, Table: `games_prod`)

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+ and pip
- Supabase account with credentials

### 1. Clone Repository

```bash
git clone https://github.com/oneder2/INST326-steam-searcher-engine.git
cd INST326-steam-searcher-engine
```

### 2. Configure Environment

Create `.env` in project root:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_your_key
SUPABASE_SECRET_KEY=your_secret_key

# Database
DATABASE_SCHEMA=steam
DATABASE_TABLE=games_prod

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

**Get Supabase credentials:** [supabase.com](https://supabase.com) → Project Settings → API

### 3. Start Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac: or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m app.main
```

**Backend running at:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

### 4. Start Frontend (New Terminal)

```bash
cd frontend-INST326-steam-search
npm install
npm run dev
```

**Frontend running at:** http://localhost:3000

---

## 📡 API Endpoints

### Health Check
```bash
GET /api/v1/health
```

### Get Games (Paginated)
```bash
GET /api/v1/games?offset=0&limit=20
```

**Response:**
```json
{
  "games": [
    {
      "game_id": 570,
      "title": "Dota 2",
      "price": 0.00,
      "genres": ["Action", "Free to Play"],
      "categories": ["Multi-player"],
      "short_description": "...",
      "total_reviews": 1500000,
      "type": "game"
    }
  ],
  "total": 50000,
  "offset": 0,
  "limit": 20
}
```

### Get Game Details
```bash
GET /api/v1/games/{game_id}
```

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration management
│   ├── database.py              # Supabase connection
│   ├── models/                  # Pydantic models
│   │   ├── game.py             # Game data models
│   │   └── common.py           # Common models
│   ├── api/v1/                 # API routes
│   │   ├── games.py            # Game endpoints
│   │   └── health.py           # Health check
│   └── services/               # Business logic
│       └── game_service.py     # Game service
└── requirements.txt            # Dependencies

frontend-INST326-steam-search/
├── src/
│   ├── components/             # React components
│   ├── pages/                  # Next.js pages
│   ├── services/               # API clients
│   ├── types/                  # TypeScript types
│   └── styles/                 # CSS styles
└── package.json               # Dependencies
```

---

## 🗄️ Database Schema

**Table:** `steam.games_prod`

| Column | Type | Description |
|--------|------|-------------|
| `appid` | bigint | Game ID (Primary Key) |
| `name` | text | Game title |
| `price_cents` | integer | Price in cents |
| `genres` | jsonb | Game genres (JSON array) |
| `categories` | jsonb | Game categories (JSON array) |
| `short_description` | text | Brief description |
| `detailed_desc` | text | Full description |
| `release_date` | date | Release date |
| `total_reviews` | integer | Review count |
| `dlc_count` | integer | DLC count |
| `type` | text | Item type (game/dlc/demo) |

**Field Mappings (Database → API):**
- `appid` → `game_id`
- `name` → `title`
- `price_cents` → `price` (÷100 for USD)

---

## 🛠️ Development Commands

### Backend
```bash
cd backend
source venv/bin/activate
python -m app.main                    # Start server
uvicorn app.main:app --reload         # With auto-reload
```

### Frontend
```bash
cd frontend-INST326-steam-search
npm run dev                           # Development server
npm run build                         # Production build
npm run lint                          # Lint code
npm test                              # Run tests
```

---

## 🧪 Running Tests

### Comprehensive Test Suite

Our project includes **20 automated tests** covering unit, integration, and system testing:

```bash
cd backend

# Run all tests
python -m unittest discover tests

# Run with verbose output
python -m unittest discover tests -v

# Run specific test suite
python -m unittest discover tests/unit          # Unit tests (7 tests)
python -m unittest discover tests/integration   # Integration tests (8 tests)
python -m unittest discover tests/system        # System tests (5 tests)

# Run single test file
python -m unittest tests.unit.test_persistence
python -m unittest tests.integration.test_search_workflows
python -m unittest tests.system.test_complete_workflows
```

### Test Coverage

- **Unit Tests (7)**: Test individual methods (PersistenceService, file I/O)
- **Integration Tests (8)**: Test component interactions (search workflows, filters, pagination)
- **System Tests (5)**: Test complete user workflows (search journey, session persistence, import/export)

**Test Documentation:** See `docs/TESTING_STRATEGY.md` for detailed testing strategy and rationale.

---

## 📚 Documentation

### Core Documentation
- **Backend README**: `backend/README.md`
- **Backend Startup Guide**: `docs/tech-doc/BACKEND_STARTUP_GUIDE.md`
- **Frontend Development**: `frontend-INST326-steam-search/DEVELOPMENT.md`
- **API Contract**: `docs/tech-doc/API-contract-backend.md`

### Testing Documentation (Project 4)
- **Testing Strategy**: `docs/TESTING_STRATEGY.md` - Complete testing approach and coverage
- **Integration Tests**: `backend/tests/integration/` - 8 tests verifying component coordination
- **System Tests**: `backend/tests/system/` - 5 tests verifying complete workflows

### Project 4 Requirements
- **Requirements Gap Analysis**: `docs/PROJECT_REQUIREMENTS_GAP_ANALYSIS.md`
- **Data Persistence**: Implemented in `backend/app/services/persistence_service.py`
  - Save/load search history
  - Import from CSV/JSON
  - Export to CSV/JSON
  - File I/O with pathlib and context managers
  
### Technical Documentation
- **Search Implementation**: `docs/SEARCH_IMPLEMENTATION_PLAN.md`
- **Phase 1 & 2 Complete**: `docs/PHASE1_SEARCH_COMPLETE.md`, `docs/PHASE2_IMPLEMENTATION_COMPLETE.md`
- **All Technical Docs**: `docs/tech-doc/`

---

## 🔧 Troubleshooting

**Port already in use:**
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

**Database connection failed:**
- Verify `.env` file exists in project root
- Check `SUPABASE_URL` and `SUPABASE_SECRET_KEY`
- Ensure no extra spaces in environment variables

**Module not found:**
```bash
# Backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
npm install
```

**CORS errors:**
- Verify `CORS_ORIGINS` in `.env` includes `http://localhost:3000`

---

## 🌐 Deployment

**Backend:** Deploy to Render.com or any Python hosting service
**Frontend:** Deploy to Vercel or Render.com
**Environment:** Configure production environment variables

See individual service documentation for detailed deployment instructions.

---

## 📞 Support

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Technical Docs**: `docs/` directory
- **Course**: INST326 - University of Maryland

---

## 📄 License

MIT License - Academic project for INST326 course

---

**Current Phase:** MVP - Basic game data retrieval with pagination  
**Future Phases:** Search functionality, filtering, ranking algorithms  
**Version:** 0.1.0
