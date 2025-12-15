"""
Persistence Service for Steam Game Search Engine

This module provides data persistence capabilities including:
- Save/load search history
- Import game data from CSV/JSON
- Export search results to CSV/JSON
- File I/O with proper error handling

Uses Python best practices:
- pathlib for file path management
- Context managers (with statements) for file operations
- Exception handling for I/O errors
- Data validation before use
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import csv
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PersistenceService:
    """
    Handles all data persistence operations for the application.
    
    Features:
    - Save/load search history between sessions
    - Import game data from standard formats (CSV, JSON)
    - Export search results to CSV/JSON
    - Proper error handling and data validation
    """
    
    def __init__(self, data_directory: str = "backend/data"):
        """
        Initialize persistence service with data directory.
        
        Args:
            data_directory: Path to directory for storing data files
        """
        self.data_dir = Path(data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Persistence service initialized with directory: {self.data_dir}")
    
    # ========================================================================
    # SAVE/LOAD SYSTEM STATE (Required for Project 4)
    # ========================================================================
    
    def save_search_history(self, searches: List[Dict[str, Any]]) -> bool:
        """
        Save search history to JSON file.
        
        Args:
            searches: List of search queries with metadata
        
        Returns:
            True if save successful, False otherwise
        
        Example:
            searches = [
                {"query": "adventure", "timestamp": "2025-12-14T22:30:00", "results_count": 86},
                {"query": "action", "timestamp": "2025-12-14T22:31:00", "results_count": 152}
            ]
        """
        file_path = self.data_dir / "search_history.json"
        
        try:
            # Use context manager for safe file handling
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(searches, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved {len(searches)} search records to {file_path}")
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"❌ Failed to save search history: {e}")
            return False
    
    def load_search_history(self) -> List[Dict[str, Any]]:
        """
        Load search history from JSON file.
        
        Returns:
            List of previous searches, empty list if file not found
        
        Error Handling:
            - FileNotFoundError: Returns empty list (first run)
            - JSONDecodeError: Returns empty list (corrupted file)
            - Other errors: Logs error and returns empty list
        """
        file_path = self.data_dir / "search_history.json"
        
        try:
            # Check if file exists
            if not file_path.exists():
                logger.info("ℹ️ No search history file found (first run)")
                return []
            
            # Use context manager for safe file reading
            with open(file_path, 'r', encoding='utf-8') as f:
                searches = json.load(f)
            
            # Validate data structure
            if not isinstance(searches, list):
                logger.warning("⚠️ Invalid search history format, returning empty list")
                return []
            
            logger.info(f"✅ Loaded {len(searches)} search records from {file_path}")
            return searches
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Corrupted search history file: {e}")
            return []
        except (IOError, OSError) as e:
            logger.error(f"❌ Failed to load search history: {e}")
            return []
    
    def save_user_preferences(self, preferences: Dict[str, Any]) -> bool:
        """
        Save user preferences (filters, sort settings, etc.).
        
        Args:
            preferences: Dictionary of user settings
        
        Returns:
            True if save successful
        
        Example:
            preferences = {
                "default_sort": "relevance",
                "default_limit": 20,
                "favorite_genres": ["Action", "RPG"],
                "price_filter_max": 30
            }
        """
        file_path = self.data_dir / "user_preferences.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2)
            
            logger.info(f"✅ Saved user preferences to {file_path}")
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"❌ Failed to save preferences: {e}")
            return False
    
    def load_user_preferences(self) -> Dict[str, Any]:
        """
        Load user preferences.
        
        Returns:
            Dictionary of user settings, default values if file not found
        """
        file_path = self.data_dir / "user_preferences.json"
        
        # Default preferences
        defaults = {
            "default_sort": "relevance",
            "default_limit": 20,
            "favorite_genres": [],
            "price_filter_max": None
        }
        
        try:
            if not file_path.exists():
                return defaults
            
            with open(file_path, 'r', encoding='utf-8') as f:
                preferences = json.load(f)
            
            # Merge with defaults (in case new settings added)
            return {**defaults, **preferences}
            
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.error(f"❌ Failed to load preferences: {e}")
            return defaults
    
    # ========================================================================
    # IMPORT CAPABILITIES (Required for Project 4)
    # ========================================================================
    
    def import_games_from_csv(self, csv_file_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        Import game data from CSV file.
        
        Args:
            csv_file_path: Path to CSV file
        
        Returns:
            List of game dictionaries if successful, None if error
        
        CSV Format Expected:
            appid,name,price_cents,genres,categories,type
            
        Error Handling:
            - File not found
            - Invalid CSV format
            - Missing required columns
            - Data validation
        """
        file_path = Path(csv_file_path)
        
        try:
            if not file_path.exists():
                logger.error(f"❌ CSV file not found: {file_path}")
                return None
            
            games = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate required columns
                required_columns = {'appid', 'name', 'price_cents'}
                if not required_columns.issubset(set(reader.fieldnames or [])):
                    logger.error(f"❌ CSV missing required columns: {required_columns}")
                    return None
                
                for row in reader:
                    # Validate and transform data
                    try:
                        game = {
                            'appid': int(row['appid']),
                            'name': row['name'],
                            'price_cents': int(row.get('price_cents', 0)),
                            'genres': json.loads(row.get('genres', '[]')),
                            'categories': json.loads(row.get('categories', '[]')),
                            'type': row.get('type', 'game')
                        }
                        games.append(game)
                    except (ValueError, json.JSONDecodeError) as e:
                        logger.warning(f"⚠️ Skipping invalid row: {e}")
                        continue
            
            logger.info(f"✅ Imported {len(games)} games from CSV")
            return games
            
        except (IOError, OSError) as e:
            logger.error(f"❌ Failed to import CSV: {e}")
            return None
    
    def import_games_from_json(self, json_file_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        Import game data from JSON file.
        
        Args:
            json_file_path: Path to JSON file
        
        Returns:
            List of game dictionaries if successful, None if error
        
        JSON Format Expected:
            [
                {"appid": 123, "name": "Game Name", "price_cents": 1999, ...},
                ...
            ]
        """
        file_path = Path(json_file_path)
        
        try:
            if not file_path.exists():
                logger.error(f"❌ JSON file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                games = json.load(f)
            
            # Validate data structure
            if not isinstance(games, list):
                logger.error("❌ JSON must contain a list of games")
                return None
            
            # Validate each game has required fields
            valid_games = []
            for game in games:
                if 'appid' in game and 'name' in game:
                    valid_games.append(game)
                else:
                    logger.warning(f"⚠️ Skipping invalid game entry: {game.get('name', 'unknown')}")
            
            logger.info(f"✅ Imported {len(valid_games)} games from JSON")
            return valid_games
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON format: {e}")
            return None
        except (IOError, OSError) as e:
            logger.error(f"❌ Failed to import JSON: {e}")
            return None
    
    # ========================================================================
    # EXPORT FEATURES (Required for Project 4)
    # ========================================================================
    
    def export_to_csv(
        self, 
        data: List[Dict[str, Any]], 
        filename: Optional[str] = None,
        columns: Optional[List[str]] = None
    ) -> Optional[Path]:
        """
        Export search results to CSV file.
        
        Args:
            data: List of game dictionaries to export
            filename: Optional custom filename
            columns: Optional list of columns to include
        
        Returns:
            Path to created file if successful, None if error
        
        Usage:
            service.export_to_csv(search_results, "my_search_results.csv")
        """
        if not data:
            logger.warning("⚠️ No data to export")
            return None
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_results_{timestamp}.csv"
        
        file_path = self.data_dir / filename
        
        try:
            # Determine columns
            if columns is None:
                # Use all keys from first item
                columns = list(data[0].keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                
                for item in data:
                    # Only write columns that exist in this item
                    row = {col: item.get(col, '') for col in columns}
                    writer.writerow(row)
            
            logger.info(f"✅ Exported {len(data)} records to {file_path}")
            return file_path
            
        except (IOError, OSError) as e:
            logger.error(f"❌ Failed to export CSV: {e}")
            return None
    
    def export_to_json(
        self, 
        data: List[Dict[str, Any]], 
        filename: Optional[str] = None
    ) -> Optional[Path]:
        """
        Export search results to JSON file.
        
        Args:
            data: List of game dictionaries to export
            filename: Optional custom filename
        
        Returns:
            Path to created file if successful, None if error
        """
        if not data:
            logger.warning("⚠️ No data to export")
            return None
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_results_{timestamp}.json"
        
        file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exported {len(data)} records to {file_path}")
            return file_path
            
        except (IOError, OSError) as e:
            logger.error(f"❌ Failed to export JSON: {e}")
            return None
    
    def generate_summary_report(
        self, 
        search_results: Dict[str, Any],
        filename: Optional[str] = None
    ) -> Optional[Path]:
        """
        Generate a summary report of search results.
        
        Args:
            search_results: Search results dictionary with metadata
            filename: Optional custom filename
        
        Returns:
            Path to created report file
        
        Report includes:
            - Search query
            - Total results found
            - Filter criteria applied
            - Top results summary
            - Genre distribution
            - Price statistics
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_report_{timestamp}.txt"
        
        file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("STEAM GAME SEARCH ENGINE - SEARCH REPORT\n")
                f.write("=" * 70 + "\n\n")
                
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Query information
                f.write(f"Search Query: {search_results.get('query', 'N/A')}\n")
                f.write(f"Total Results: {search_results.get('total', 0)}\n")
                f.write(f"Results Shown: {len(search_results.get('results', []))}\n\n")
                
                # Filters applied
                filters = search_results.get('filters_applied')
                if filters:
                    f.write("Filters Applied:\n")
                    for key, value in filters.items():
                        if value is not None:
                            f.write(f"  - {key}: {value}\n")
                    f.write("\n")
                
                # Top results
                results = search_results.get('results', [])
                if results:
                    f.write("Top Results:\n")
                    for i, game in enumerate(results[:10], 1):
                        f.write(f"  {i}. {game.get('title', 'Unknown')} - ${game.get('price', 0):.2f}\n")
                        f.write(f"     Relevance: {game.get('relevance_score', 0)*100:.0f}%\n")
                    f.write("\n")
                
                # Genre distribution
                all_genres = []
                for game in results:
                    all_genres.extend(game.get('genres', []))
                
                if all_genres:
                    from collections import Counter
                    genre_counts = Counter(all_genres)
                    f.write("Genre Distribution:\n")
                    for genre, count in genre_counts.most_common(10):
                        f.write(f"  - {genre}: {count}\n")
                    f.write("\n")
                
                # Price statistics
                prices = [g.get('price', 0) for g in results if g.get('price', 0) > 0]
                if prices:
                    f.write("Price Statistics:\n")
                    f.write(f"  - Average: ${sum(prices)/len(prices):.2f}\n")
                    f.write(f"  - Minimum: ${min(prices):.2f}\n")
                    f.write(f"  - Maximum: ${max(prices):.2f}\n")
                
                f.write("\n" + "=" * 70 + "\n")
                f.write("End of Report\n")
                f.write("=" * 70 + "\n")
            
            logger.info(f"✅ Generated summary report: {file_path}")
            return file_path
            
        except (IOError, OSError) as e:
            logger.error(f"❌ Failed to generate report: {e}")
            return None

