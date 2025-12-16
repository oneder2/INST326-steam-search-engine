"""
Unit Tests for Persistence Service

Tests individual methods of PersistenceService in isolation.
Verifies save/load, import/export functionality.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.persistence_service import PersistenceService


class TestPersistenceService(unittest.TestCase):
    """Unit tests for PersistenceService class"""
    
    def setUp(self):
        """Create temporary directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.service = PersistenceService(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary directory after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_search_history(self):
        """Test saving and loading search history"""
        # Test data
        searches = [
            {"query": "adventure", "timestamp": "2025-12-14T22:00:00", "results_count": 86},
            {"query": "action", "timestamp": "2025-12-14T22:01:00", "results_count": 152}
        ]
        
        # Save
        result = self.service.save_search_history(searches)
        self.assertTrue(result, "Save should return True")
        
        # Load
        loaded = self.service.load_search_history()
        self.assertEqual(len(loaded), 2, "Should load 2 searches")
        self.assertEqual(loaded[0]["query"], "adventure")
        self.assertEqual(loaded[1]["results_count"], 152)
    
    def test_load_missing_file(self):
        """Test loading when file doesn't exist (first run)"""
        loaded = self.service.load_search_history()
        self.assertEqual(loaded, [], "Should return empty list for missing file")
    
    def test_save_and_load_preferences(self):
        """Test saving and loading user preferences"""
        prefs = {
            "default_sort": "price_asc",
            "default_limit": 50,
            "favorite_genres": ["Action", "RPG"]
        }
        
        # Save
        result = self.service.save_user_preferences(prefs)
        self.assertTrue(result)
        
        # Load
        loaded = self.service.load_user_preferences()
        self.assertEqual(loaded["default_sort"], "price_asc")
        self.assertEqual(len(loaded["favorite_genres"]), 2)
    
    def test_export_to_csv(self):
        """Test exporting data to CSV"""
        data = [
            {"game_id": 1, "title": "Game 1", "price": 19.99},
            {"game_id": 2, "title": "Game 2", "price": 29.99}
        ]
        
        file_path = self.service.export_to_csv(data, "test_export.csv")
        
        self.assertIsNotNone(file_path, "Export should return file path")
        self.assertTrue(file_path.exists(), "CSV file should exist")
        
        # Verify content
        with open(file_path, 'r') as f:
            content = f.read()
            self.assertIn("game_id", content)
            self.assertIn("Game 1", content)
    
    def test_export_to_json(self):
        """Test exporting data to JSON"""
        data = [
            {"game_id": 1, "title": "Game 1"},
            {"game_id": 2, "title": "Game 2"}
        ]
        
        file_path = self.service.export_to_json(data, "test_export.json")
        
        self.assertIsNotNone(file_path)
        self.assertTrue(file_path.exists())
        
        # Verify content
        with open(file_path, 'r') as f:
            loaded = json.load(f)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0]["title"], "Game 1")
    
    def test_export_empty_data(self):
        """Test exporting empty data returns None"""
        result = self.service.export_to_csv([], "empty.csv")
        self.assertIsNone(result, "Exporting empty data should return None")


if __name__ == '__main__':
    unittest.main()


