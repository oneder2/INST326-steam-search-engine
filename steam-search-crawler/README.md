# Steam Game Search Engine - Data Crawler

This is the data collection and processing service for the Steam Game Search Engine. It handles Steam API data collection, data cleaning, database storage, and search index generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Steam API Key (get from https://steamcommunity.com/dev/apikey)
- pip package manager

### Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Steam API key and configuration
   ```

3. **Initialize Database**:
   ```bash
   python main.py --init-db
   ```

4. **Run Data Collection**:
   ```bash
   # Full crawl (takes several hours)
   python main.py --full-crawl
   
   # Update existing data
   python main.py --update
   
   # Generate search indices
   python main.py --build-indices
   ```

## 📋 Features

### Data Collection
- **Steam API Integration**: Fetches game data from official Steam API
- **Rate Limiting**: Respects Steam API rate limits
- **Batch Processing**: Processes games in configurable batches
- **Error Handling**: Robust error handling with retry logic
- **Progress Tracking**: Real-time progress monitoring

### Data Processing
- **Data Cleaning**: Validates and cleans raw Steam data
- **Price Normalization**: Converts prices to standard format
- **Genre Standardization**: Normalizes game genres and categories
- **Platform Detection**: Identifies supported platforms
- **Steam Deck Compatibility**: Detects Steam Deck compatibility
- **Co-op Type Detection**: Identifies local vs online co-op games

### Database Management
- **SQLite Storage**: Efficient local database storage
- **Schema Management**: Automatic database schema creation
- **Data Validation**: Ensures data integrity
- **Indexing**: Optimized database indices for fast queries
- **Backup Support**: Database backup and restore functionality

### Search Index Generation
- **BM25 Index**: Generates keyword search indices
- **Vector Embeddings**: Creates semantic search embeddings using Sentence Transformers
- **Faiss Integration**: Builds efficient vector similarity search indices
- **Index Optimization**: Optimizes indices for fast search performance

## 🏗️ Architecture

### Data Flow
```
Steam API → Raw Data → Data Cleaning → Database Storage → Search Indices
    ↓           ↓            ↓              ↓               ↓
  JSON       Validation   GameData      SQLite         BM25/Faiss
```

### Components
- **SteamAPIClient**: Handles Steam API communication
- **DataProcessor**: Cleans and validates raw data
- **DatabaseManager**: Manages SQLite database operations
- **IndexBuilder**: Generates search indices
- **SteamCrawler**: Orchestrates the entire process

## 🔧 Configuration

### Environment Variables (.env)
```env
# Steam API Configuration
STEAM_API_KEY=your-steam-api-key-here
STEAM_API_BASE_URL=https://api.steampowered.com

# Database Configuration
DATABASE_PATH=data/games_data.db
BACKUP_PATH=data/backups/

# Processing Configuration
BATCH_SIZE=100
RATE_LIMIT_DELAY=1.0
MAX_RETRIES=3
WORKER_THREADS=4

# Search Index Configuration
FAISS_INDEX_PATH=data/game_embeddings.faiss
BM25_INDEX_PATH=data/bm25_index.pkl
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=crawler.log
```

### Command Line Options
```bash
# Database operations
python main.py --init-db              # Initialize database
python main.py --backup-db            # Backup database
python main.py --restore-db backup.db # Restore from backup

# Data collection
python main.py --full-crawl           # Complete data crawl
python main.py --update               # Update existing data
python main.py --crawl-new            # Crawl only new games

# Index generation
python main.py --build-indices        # Build all search indices
python main.py --build-bm25           # Build BM25 index only
python main.py --build-faiss          # Build Faiss index only

# Maintenance
python main.py --cleanup              # Clean up old data
python main.py --validate             # Validate data integrity
python main.py --stats                # Show database statistics
```

## 📊 Data Schema

### Games Table
```sql
CREATE TABLE games (
    app_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price REAL,
    genres TEXT,                -- JSON array
    developers TEXT,            -- JSON array
    publishers TEXT,            -- JSON array
    release_date TEXT,
    review_score REAL,
    review_count INTEGER,
    player_count INTEGER,
    deck_compatible BOOLEAN,
    coop_type TEXT,            -- 'Local', 'Online', or NULL
    platforms TEXT,            -- JSON array
    screenshots TEXT,          -- JSON array
    tags TEXT,                 -- JSON array
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Indices
- `idx_title`: Fast title searches
- `idx_genres`: Genre-based filtering
- `idx_price`: Price range queries
- `idx_deck_compatible`: Steam Deck filtering

## 🧪 Testing

### Manual Testing
```bash
# Test Steam API connection
python -c "from main import SteamAPIClient, get_config; import asyncio; asyncio.run(SteamAPIClient(get_config()).get_app_list())"

# Test database connection
python -c "from main import DatabaseManager, get_config; DatabaseManager(get_config()).initialize_database()"

# Test data processing
python main.py --validate
```

### Automated Testing
```bash
pytest tests/
pytest --cov=. tests/
```

## 📈 Performance

### Crawling Performance
- **Full Crawl**: ~50,000 games in 6-8 hours
- **Rate Limit**: 1 request per second (configurable)
- **Memory Usage**: ~500MB during processing
- **Database Size**: ~100MB for full dataset

### Index Generation
- **BM25 Index**: ~2 minutes for 50,000 games
- **Faiss Index**: ~10 minutes for 50,000 games
- **Index Size**: ~200MB total for all indices

## 🔄 Scheduling

### Cron Jobs
```bash
# Daily updates (new games only)
0 2 * * * cd /path/to/crawler && python main.py --crawl-new

# Weekly full update
0 1 * * 0 cd /path/to/crawler && python main.py --update

# Monthly index rebuild
0 0 1 * * cd /path/to/crawler && python main.py --build-indices

# Daily backup
0 3 * * * cd /path/to/crawler && python main.py --backup-db
```

## 📁 Output Files

### Database
- `data/games_data.db`: Main SQLite database
- `data/backups/`: Database backups

### Search Indices
- `data/game_embeddings.faiss`: Faiss vector index
- `data/bm25_index.pkl`: BM25 keyword index
- `data/index_metadata.json`: Index metadata

### Logs and Reports
- `crawler.log`: Crawler execution logs
- `data/reports/`: Data quality reports
- `data/stats/`: Collection statistics

## 🤝 Integration

### Backend API Integration
The crawler generates data files that are consumed by the FastAPI backend:
- Database file is read by the API service
- Search indices are loaded at API startup
- Data updates trigger index rebuilds

### Frontend Integration
- No direct integration with frontend
- Data flows through the backend API
- Crawler runs independently as a data pipeline

## 🔗 Related Services

- **Backend API**: `../steam-search-backend/` - Consumes crawler data
- **Frontend**: Project root - Displays processed data
- **Documentation**: `../docs/` - Comprehensive documentation

## 📄 License

This project is part of the INST326 group assignment.
