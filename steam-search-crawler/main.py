"""
Steam Game Search Engine - Data Crawler
Main script for collecting, processing, and storing Steam game data.

This service handles:
1. Steam API data collection
2. Data cleaning and validation
3. Database storage
4. Search index generation
5. Scheduled data updates
"""

import asyncio
import logging
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class CrawlerConfig:
    """Configuration for the Steam data crawler."""
    steam_api_key: str
    steam_api_base_url: str = "https://api.steampowered.com"
    database_path: str = "data/games_data.db"
    raw_data_path: str = "data/raw/"
    processed_data_path: str = "data/processed/"
    batch_size: int = 100
    rate_limit_delay: float = 1.0
    max_retries: int = 3

def get_config() -> CrawlerConfig:
    """Load configuration from environment variables."""
    return CrawlerConfig(
        steam_api_key=os.getenv("STEAM_API_KEY", ""),
        steam_api_base_url=os.getenv("STEAM_API_BASE_URL", "https://api.steampowered.com"),
        database_path=os.getenv("DATABASE_PATH", "data/games_data.db"),
        raw_data_path=os.getenv("RAW_DATA_PATH", "data/raw/"),
        processed_data_path=os.getenv("PROCESSED_DATA_PATH", "data/processed/"),
        batch_size=int(os.getenv("BATCH_SIZE", "100")),
        rate_limit_delay=float(os.getenv("RATE_LIMIT_DELAY", "1.0")),
        max_retries=int(os.getenv("MAX_RETRIES", "3"))
    )

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class GameData:
    """Data model for a Steam game."""
    app_id: int
    title: str
    description: str
    price: float
    genres: List[str]
    developers: List[str]
    publishers: List[str]
    release_date: str
    review_score: float
    review_count: int
    player_count: int
    deck_compatible: bool
    coop_type: Optional[str]
    platforms: List[str]
    screenshots: List[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

# ============================================================================
# Steam API Client
# ============================================================================

class SteamAPIClient:
    """Client for interacting with Steam API."""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.session = requests.Session()
        
    async def get_app_list(self) -> List[Dict[str, Any]]:
        """
        Fetch the complete list of Steam applications.
        
        Returns:
            List of app dictionaries with app_id and name
        """
        logger.info("Fetching Steam app list...")
        
        url = f"{self.config.steam_api_base_url}/ISteamApps/GetAppList/v2/"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            apps = data.get("applist", {}).get("apps", [])
            
            logger.info(f"Retrieved {len(apps)} applications from Steam API")
            return apps
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch app list: {e}")
            return []
    
    async def get_app_details(self, app_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information for a specific Steam application.
        
        Args:
            app_id: Steam application ID
            
        Returns:
            App details dictionary or None if failed
        """
        url = f"{self.config.steam_api_base_url}/appdetails"
        params = {
            "appids": app_id,
            "key": self.config.steam_api_key
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            app_data = data.get(str(app_id), {})
            
            if app_data.get("success"):
                return app_data.get("data")
            else:
                logger.warning(f"No data available for app {app_id}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Failed to fetch details for app {app_id}: {e}")
            return None
    
    async def get_app_reviews(self, app_id: int) -> Dict[str, Any]:
        """
        Fetch review data for a specific Steam application.
        
        Args:
            app_id: Steam application ID
            
        Returns:
            Review data dictionary
        """
        url = f"{self.config.steam_api_base_url}/appreviews/{app_id}"
        params = {
            "json": 1,
            "language": "english",
            "review_type": "all",
            "purchase_type": "all"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch reviews for app {app_id}: {e}")
            return {}

# ============================================================================
# Data Processing
# ============================================================================

class DataProcessor:
    """Processes and cleans raw Steam data."""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        
    def clean_game_data(self, raw_data: Dict[str, Any]) -> Optional[GameData]:
        """
        Clean and validate raw game data from Steam API.
        
        Args:
            raw_data: Raw data from Steam API
            
        Returns:
            Cleaned GameData object or None if invalid
        """
        try:
            # Extract basic information
            app_id = raw_data.get("steam_appid")
            title = raw_data.get("name", "").strip()
            description = raw_data.get("short_description", "").strip()
            
            # Skip if missing essential data
            if not app_id or not title:
                return None
            
            # Extract price information
            price_data = raw_data.get("price_overview", {})
            price = price_data.get("final", 0) / 100.0 if price_data else 0.0
            
            # Extract genres
            genres = [g.get("description", "") for g in raw_data.get("genres", [])]
            
            # Extract developers and publishers
            developers = raw_data.get("developers", [])
            publishers = raw_data.get("publishers", [])
            
            # Extract release date
            release_date = raw_data.get("release_date", {}).get("date", "")
            
            # Extract platform information
            platforms = []
            platform_data = raw_data.get("platforms", {})
            if platform_data.get("windows"): platforms.append("Windows")
            if platform_data.get("mac"): platforms.append("Mac")
            if platform_data.get("linux"): platforms.append("Linux")
            
            # Extract screenshots
            screenshots = [s.get("path_full", "") for s in raw_data.get("screenshots", [])]
            
            # Extract tags (categories)
            tags = [c.get("description", "") for c in raw_data.get("categories", [])]
            
            # Determine Steam Deck compatibility (placeholder logic)
            deck_compatible = "Steam Deck" in tags or "Controller Support" in tags
            
            # Determine co-op type (placeholder logic)
            coop_type = None
            if "Local Co-op" in tags:
                coop_type = "Local"
            elif "Online Co-op" in tags:
                coop_type = "Online"
            
            now = datetime.now()
            
            return GameData(
                app_id=app_id,
                title=title,
                description=description,
                price=price,
                genres=genres,
                developers=developers,
                publishers=publishers,
                release_date=release_date,
                review_score=0.0,  # To be filled from review data
                review_count=0,    # To be filled from review data
                player_count=0,    # To be filled from player data
                deck_compatible=deck_compatible,
                coop_type=coop_type,
                platforms=platforms,
                screenshots=screenshots,
                tags=tags,
                created_at=now,
                updated_at=now
            )
            
        except Exception as e:
            logger.error(f"Failed to clean game data: {e}")
            return None

# ============================================================================
# Database Manager
# ============================================================================

class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.db_path = config.database_path
        
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
    def initialize_database(self):
        """Create database tables if they don't exist."""
        logger.info("Initializing database...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create games table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    app_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    price REAL,
                    genres TEXT,
                    developers TEXT,
                    publishers TEXT,
                    release_date TEXT,
                    review_score REAL,
                    review_count INTEGER,
                    player_count INTEGER,
                    deck_compatible BOOLEAN,
                    coop_type TEXT,
                    platforms TEXT,
                    screenshots TEXT,
                    tags TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON games(title)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_genres ON games(genres)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price ON games(price)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deck_compatible ON games(deck_compatible)")
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def save_game(self, game: GameData):
        """Save a single game to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO games (
                    app_id, title, description, price, genres, developers, publishers,
                    release_date, review_score, review_count, player_count,
                    deck_compatible, coop_type, platforms, screenshots, tags,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game.app_id, game.title, game.description, game.price,
                json.dumps(game.genres), json.dumps(game.developers), json.dumps(game.publishers),
                game.release_date, game.review_score, game.review_count, game.player_count,
                game.deck_compatible, game.coop_type, json.dumps(game.platforms),
                json.dumps(game.screenshots), json.dumps(game.tags),
                game.created_at, game.updated_at
            ))
            
            conn.commit()

# ============================================================================
# Main Crawler
# ============================================================================

class SteamCrawler:
    """Main crawler orchestrating the data collection process."""
    
    def __init__(self):
        self.config = get_config()
        self.api_client = SteamAPIClient(self.config)
        self.processor = DataProcessor(self.config)
        self.db_manager = DatabaseManager(self.config)
        
    async def run_full_crawl(self):
        """Run a complete crawl of Steam data."""
        logger.info("Starting full Steam data crawl...")
        
        # Initialize database
        self.db_manager.initialize_database()
        
        # Get app list
        apps = await self.api_client.get_app_list()
        
        if not apps:
            logger.error("Failed to retrieve app list. Exiting.")
            return
        
        # Process apps in batches
        total_apps = len(apps)
        processed = 0
        
        for i in range(0, total_apps, self.config.batch_size):
            batch = apps[i:i + self.config.batch_size]
            
            for app in batch:
                app_id = app.get("appid")
                if not app_id:
                    continue
                
                try:
                    # Fetch detailed app data
                    app_details = await self.api_client.get_app_details(app_id)
                    
                    if app_details:
                        # Process and clean data
                        game_data = self.processor.clean_game_data(app_details)
                        
                        if game_data:
                            # Save to database
                            self.db_manager.save_game(game_data)
                            processed += 1
                            
                            if processed % 100 == 0:
                                logger.info(f"Processed {processed}/{total_apps} games")
                    
                    # Rate limiting
                    await asyncio.sleep(self.config.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Failed to process app {app_id}: {e}")
                    continue
        
        logger.info(f"Crawl completed. Processed {processed} games total.")

# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Main entry point for the crawler."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Steam Game Data Crawler")
    parser.add_argument("--full-crawl", action="store_true", help="Run full data crawl")
    parser.add_argument("--init-db", action="store_true", help="Initialize database only")
    
    args = parser.parse_args()
    
    crawler = SteamCrawler()
    
    if args.init_db:
        crawler.db_manager.initialize_database()
        logger.info("Database initialization completed.")
    elif args.full_crawl:
        await crawler.run_full_crawl()
    else:
        logger.info("No action specified. Use --help for options.")

if __name__ == "__main__":
    asyncio.run(main())
