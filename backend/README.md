# Steam Game Search Engine - Backend API

FastAPI-based backend service for the Steam Game Search Engine project. Provides RESTful API endpoints for game data retrieval from Supabase PostgreSQL database.

## 📋 Project Information

- **Framework**: FastAPI 0.104.1
- **Python Version**: 3.8+
- **Database**: Supabase (PostgreSQL)
- **Schema**: `steam`
- **Table**: `games_prod`
- **API Version**: v0.1.0

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Supabase account with configured database
- Environment variables (see Configuration section)

### Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On Linux/Mac:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root directory (not in backend/) with the following variables:
   
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_PUBLISHABLE_KEY=sb_publishable_your_key_here
   SUPABASE_SECRET_KEY=your_secret_key_here
   
   # Database Configuration
   DATABASE_SCHEMA=steam
   DATABASE_TABLE=games_prod
   
   # Server Configuration
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8000
   
   # CORS Configuration
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   
   # Application Configuration
   ENVIRONMENT=development
   DEBUG=True
   LOG_LEVEL=INFO
   ```

5. **Start the server**
   ```bash
   # From backend directory
   python -m app.main
   
   # Or using uvicorn directly
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Verify installation**
   - API Root: http://localhost:8000/
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── database.py              # Database connection manager
│   │
│   ├── models/                  # Pydantic data models
│   │   ├── __init__.py
│   │   ├── game.py             # Game-related models
│   │   └── common.py           # Common models (errors, health)
│   │
│   ├── api/                     # API route handlers
│   │   ├── __init__.py
│   │   └── v1/                 # API version 1
│   │       ├── __init__.py
│   │       ├── health.py       # Health check endpoint
│   │       └── games.py        # Game data endpoints
│   │
│   └── services/               # Business logic layer
│       ├── __init__.py
│       └── game_service.py     # Game data service
│
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔌 API Endpoints

### Health Check

**GET** `/api/v1/health`

Check service and database health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-15T10:30:00.000Z",
  "database": "connected",
  "version": "0.1.0"
}
```

### Get Games List (Paginated)

**GET** `/api/v1/games?offset=0&limit=20`

Retrieve paginated list of games.

**Query Parameters:**
- `offset` (int, optional): Starting position (default: 0)
- `limit` (int, optional): Number of games per page (default: 20, max: 100)

**Response:**
```json
{
  "games": [
    {
      "game_id": 570,
      "title": "Dota 2",
      "price": 0.00,
      "genres": ["Action", "Free to Play"],
      "categories": ["Multi-player", "Co-op"],
      "short_description": "Every day, millions of players...",
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

**GET** `/api/v1/games/{game_id}`

Retrieve detailed information for a specific game.

**Path Parameters:**
- `game_id` (int): Steam game ID (appid)

**Response:**
```json
{
  "game_id": 570,
  "title": "Dota 2",
  "price": 0.00,
  "genres": ["Action", "Free to Play", "MOBA"],
  "categories": ["Multi-player", "Co-op", "Steam Achievements"],
  "short_description": "Every day, millions of players...",
  "detailed_description": "Dota 2 is a multiplayer online battle arena...",
  "release_date": "2013-07-09",
  "total_reviews": 1500000,
  "dlc_count": 0,
  "type": "game"
}
```

## 🗄️ Database Schema

### Table: `steam.games_prod`

| Column | Type | Description |
|--------|------|-------------|
| `appid` | bigint | Steam game ID (Primary Key) |
| `name` | text | Game title |
| `release_date` | date | Release date |
| `genres` | jsonb | Game genres (JSON array) |
| `categories` | jsonb | Game categories (JSON array) |
| `short_description` | text | Brief description |
| `detailed_desc` | text | Full description |
| `price_cents` | integer | Price in cents |
| `total_reviews` | integer | Total number of reviews |
| `dlc_count` | integer | Number of DLCs |
| `type` | text | Item type (game, dlc, demo) |
| `search_tsv` | text | Full-text search vector |

### Field Mappings (Database → API)

| Database Field | API Field | Transformation |
|----------------|-----------|----------------|
| `appid` | `game_id` | Direct mapping |
| `name` | `title` | Direct mapping |
| `price_cents` | `price` | Divide by 100 (cents to USD) |
| `detailed_desc` | `detailed_description` | Direct mapping |
| `genres` | `genres` | Parse JSONB to array |
| `categories` | `categories` | Parse JSONB to array |

## 🔧 Configuration

### Environment Variables

All configuration is managed through environment variables loaded from `.env` file in the project root.

**Required Variables:**
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SECRET_KEY`: Backend secret key (bypasses RLS)

**Optional Variables (with defaults):**
- `DATABASE_SCHEMA`: Database schema (default: "steam")
- `DATABASE_TABLE`: Table name (default: "games_prod")
- `BACKEND_HOST`: Server host (default: "0.0.0.0")
- `BACKEND_PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Allowed CORS origins (default: "http://localhost:3000")
- `ENVIRONMENT`: Environment name (default: "development")
- `DEBUG`: Debug mode (default: True)
- `LOG_LEVEL`: Logging level (default: "INFO")

### Supabase Authentication

This backend uses the **new-style Supabase authentication**:

- **SUPABASE_SECRET_KEY**: Used for backend service authentication
  - Provides full database access
  - Bypasses Row Level Security (RLS)
  - Must be kept confidential
  - Never expose to frontend

- **SUPABASE_PUBLISHABLE_KEY**: For frontend use only (not used in backend)

## 🧪 Testing

### Manual Testing

**Test Health Endpoint:**
```bash
curl http://localhost:8000/api/v1/health
```

**Test Games List:**
```bash
curl "http://localhost:8000/api/v1/games?offset=0&limit=5"
```

**Test Game Details:**
```bash
curl http://localhost:8000/api/v1/games/570
```

### Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these interfaces to:
- Browse all available endpoints
- Test API calls directly
- View request/response schemas
- Download OpenAPI specification

## 📝 Development

### Running in Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Start with auto-reload
python -m app.main
```

The server will automatically reload when code changes are detected (if DEBUG=True).

### Adding New Endpoints

1. Create route handler in `app/api/v1/`
2. Define Pydantic models in `app/models/`
3. Implement business logic in `app/services/`
4. Register router in `app/main.py`

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings for all modules, classes, and functions
- Keep functions focused and single-purpose
- Use meaningful variable and function names

## 🚀 Deployment

### Production Deployment

1. **Set production environment variables**
   ```env
   ENVIRONMENT=production
   DEBUG=False
   LOG_LEVEL=WARNING
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run with production server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t steam-api .
docker run -p 8000:8000 --env-file .env steam-api
```

## 🐛 Troubleshooting

### Common Issues

**Issue: Module not found error**
```
Solution: Ensure virtual environment is activated and dependencies are installed
```

**Issue: Database connection failed**
```
Solution: Verify SUPABASE_URL and SUPABASE_SECRET_KEY in .env file
```

**Issue: CORS errors from frontend**
```
Solution: Add frontend URL to CORS_ORIGINS in .env file
```

**Issue: Port already in use**
```
Solution: Change BACKEND_PORT in .env or kill process using the port
```

### Logging

Logs are output to console with timestamp and level:
```
2025-12-15 10:30:00 - app.main - INFO - Application startup complete
```

Adjust log level in `.env`:
- `DEBUG`: Verbose logging
- `INFO`: Standard logging (recommended)
- `WARNING`: Only warnings and errors
- `ERROR`: Only errors
- `CRITICAL`: Only critical errors

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check application logs
4. Contact the development team

## 📄 License

This project is part of the INST326 course at the University of Maryland.

---

**Version**: 0.1.0  
**Last Updated**: December 2025  
**Author**: INST326 Project Team


