#!/usr/bin/env python3
"""
Test Semantic Search Functionality

This script tests the semantic search implementation after:
1. Embeddings are populated
2. PostgreSQL functions are created

Usage:
    python -m scripts.test_semantic_search
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from app.config import settings
from app.services.search_service import SearchService
from app.services.embedding_service import EmbeddingService
from app.models.search import SearchFilters
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_semantic_search():
    """Test semantic search functionality"""
    
    print("=" * 80)
    print("🧪 Testing Semantic Search")
    print("=" * 80)
    print()
    
    # 1. Connect to database
    print("1. Connecting to Supabase...")
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SECRET_KEY)
    print("   ✓ Connected")
    print()
    
    # 2. Check embeddings exist
    print("2. Checking embeddings...")
    result = client.table('games_prod').select('appid,name,embedding').limit(5).execute()
    
    if not result.data:
        print("   ❌ No games found")
        return False
    
    games_with_embeddings = [g for g in result.data if g.get('embedding')]
    print(f"   ✓ Found {len(games_with_embeddings)}/{len(result.data)} games with embeddings")
    
    if not games_with_embeddings:
        print("   ⚠️  No embeddings found. Run populate_embeddings.py first!")
        return False
    
    print()
    
    # 3. Test embedding service
    print("3. Testing EmbeddingService...")
    test_query = "action shooter multiplayer"
    query_embedding = EmbeddingService.encode_query(test_query)
    print(f"   Query: '{test_query}'")
    print(f"   ✓ Generated embedding (dim: {len(query_embedding)})")
    print()
    
    # 4. Test PostgreSQL function (simple version)
    print("4. Testing PostgreSQL function (simple)...")
    try:
        result = client.rpc(
            'search_games_semantic_simple',
            {
                'query_embedding': query_embedding,
                'match_limit': 5
            }
        ).execute()
        
        if result.data:
            print(f"   ✓ Function works! Found {len(result.data)} results")
            print()
            print("   Top 5 results:")
            for i, game in enumerate(result.data, 1):
                print(f"   {i}. {game['name']} (similarity: {game['similarity']:.4f})")
            print()
        else:
            print("   ⚠️  Function returned no results")
            print()
    except Exception as e:
        print(f"   ❌ Function failed: {e}")
        print()
        print("   ⚠️  Make sure to create the PostgreSQL functions!")
        print("   Run: python -m scripts.create_semantic_functions")
        print()
        return False
    
    # 5. Test SearchService semantic_search
    print("5. Testing SearchService.semantic_search()...")
    search_service = SearchService(client)
    
    try:
        result = await search_service.semantic_search(
            query="space exploration adventure",
            limit=10
        )
        
        print(f"   ✓ Semantic search works! Found {len(result['results'])} results")
        print()
        print("   Top 5 results:")
        for i, game in enumerate(result['results'][:5], 1):
            print(f"   {i}. {game['title']} (similarity: {game['similarity_score']:.4f})")
        print()
        
    except Exception as e:
        print(f"   ❌ Semantic search failed: {e}")
        print()
        return False
    
    # 6. Test with filters
    print("6. Testing semantic search with filters...")
    try:
        result = await search_service.semantic_search(
            query="action shooter",
            filters=SearchFilters(
                price_max=5000,
                genres=["Action"]
            ),
            limit=5
        )
        
        print(f"   ✓ Filtered search works! Found {len(result['results'])} results")
        print()
        print("   Results:")
        for i, game in enumerate(result['results'], 1):
            print(f"   {i}. {game['title']} - ${game['price']:.2f} (similarity: {game['similarity_score']:.4f})")
        print()
        
    except Exception as e:
        print(f"   ❌ Filtered search failed: {e}")
        print()
        return False
    
    # 7. Test hybrid search
    print("7. Testing hybrid search (BM25 + Semantic)...")
    try:
        result = await search_service.hybrid_search(
            query="strategy war game",
            alpha=0.5,  # 50% BM25 + 50% semantic
            limit=10
        )
        
        print(f"   ✓ Hybrid search works! Found {len(result['results'])} results")
        print()
        print("   Top 5 results:")
        for i, game in enumerate(result['results'][:5], 1):
            print(f"   {i}. {game['title']} (fusion score: {game.get('fusion_score', 0):.6f})")
        print()
        
    except Exception as e:
        print(f"   ❌ Hybrid search failed: {e}")
        print()
        return False
    
    print("=" * 80)
    print("✅ All tests passed!")
    print("=" * 80)
    print()
    
    return True


def main():
    """Main function"""
    success = asyncio.run(test_semantic_search())
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

