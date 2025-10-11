# Steam Game Search Engine - Backend API

This is the Python FastAPI backend service for the Steam Game Search Engine. It provides RESTful API endpoints for game search, recommendations, and data retrieval.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Install Dependencies**:
   ```bash
   # For production deployment (minimal dependencies)
   pip install -r requirements-core.txt
   
   # For full development (includes ML libraries)
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   # Development server
   python main.py
   
   # Or using uvicorn directly
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API**:
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/v1/health
   - **Root Endpoint**: http://localhost:8000/

## 📋 API Endpoints

### Core Endpoints

#### Search Games
```bash
POST /api/v1/search/games
Content-Type: application/json

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

#### Get Game Details
```bash
GET /api/v1/games/{game_id}
```

#### Search Suggestions
```bash
GET /api/v1/search/suggest?prefix=rogue
```

#### Health Check
```bash
GET /api/v1/health
```

## 🏗️ Architecture

### Current Implementation
- **Framework**: FastAPI with Pydantic models
- **Data**: Mock data for deployment testing
- **CORS**: Configured for frontend communication
- **Health Monitoring**: Built-in health checks

### Planned Features
- **Database**: SQLite for game metadata storage
- **Search**: BM25 keyword search implementation
- **ML**: Faiss vector search for semantic similarity
- **Ranking**: Fusion algorithm combining multiple signals

## 🔧 Configuration

### Environment Variables
```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://steam-search-frontend.onrender.com

# Database Configuration (when implemented)
DATABASE_URL=sqlite:///data/games_data.db
FAISS_INDEX_PATH=data/game_embeddings.faiss
BM25_INDEX_PATH=data/bm25_index.pkl

# API Configuration
API_RATE_LIMIT=100
CACHE_TTL=3600
LOG_LEVEL=INFO
```

## 🧪 Testing

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test search endpoint
curl -X POST http://localhost:8000/api/v1/search/games \
  -H "Content-Type: application/json" \
  -d '{"query": "roguelike games", "limit": 5}'

# Test game details
curl http://localhost:8000/api/v1/games/1
```

### Automated Testing (when implemented)
```bash
pytest tests/
pytest --cov=. tests/
```

## 📦 Dependencies

### Core Dependencies (requirements-core.txt)
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **httpx**: HTTP client
- **requests**: HTTP library
- **python-multipart**: Form data support
- **python-dotenv**: Environment variables
- **python-dateutil**: Date utilities

### Full Dependencies (requirements.txt)
Includes additional libraries for:
- Machine learning (faiss-cpu, sentence-transformers)
- Data processing (pandas, numpy, scikit-learn)
- Security (python-jose)
- Monitoring (structlog, sentry-sdk)
- Development tools (pytest, black, flake8)

## 🚀 Deployment

### Render.com Deployment
This backend is configured for deployment on Render.com:

```yaml
# render.yaml (in project root)
services:
  - type: web
    name: steam-search-backend
    env: python
    buildCommand: pip install -r steam-search-backend/requirements-core.txt
    startCommand: cd steam-search-backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements-core.txt .
RUN pip install -r requirements-core.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 Documentation

- **API Documentation**: Available at `/docs` when server is running
- **Function Library**: See `../docs/functions/backend/` for detailed function documentation
- **API Contract**: See `../docs/技术文档/API 契约与后端实现文档.md`

## 🔗 Related Services

- **Frontend**: Next.js application in project root
- **Data Crawler**: Steam data collection service in `../steam-search-crawler/`
- **Documentation**: Comprehensive docs in `../docs/`

## 🤝 Development

### Code Style
- **Formatter**: Black
- **Linter**: Flake8
- **Import Sorting**: isort
- **Type Checking**: Pydantic models

### Adding New Features
1. Update Pydantic models in `main.py`
2. Implement new endpoints
3. Add tests in `tests/` directory
4. Update API documentation
5. Update function library documentation

## 📄 License

This project is part of the INST326 group assignment.
