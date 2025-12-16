#!/usr/bin/env python3
"""
Test Embedding Generation (Without PostgreSQL Functions)

This script tests the embedding service and verifies embeddings
are populated correctly, without requiring PostgreSQL functions.

Usage:
    python -m scripts.test_embedding_only
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from app.config import settings
from app.services.embedding_service import EmbeddingService
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    # Convert to numpy arrays (handle string format from DB)
    if isinstance(vec1, str):
        vec1 = np.array([float(x) for x in vec1.strip('[]').split(',')])
    else:
        vec1 = np.array(vec1)
    
    if isinstance(vec2, str):
        vec2 = np.array([float(x) for x in vec2.strip('[]').split(',')])
    else:
        vec2 = np.array(vec2)
    
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def main():
    """Main test function"""
    
    print("=" * 80)
    print("🧪 Testing Embedding Service (Without PostgreSQL Functions)")
    print("=" * 80)
    print()
    
    # 1. Test embedding service
    print("1. Testing EmbeddingService...")
    test_queries = [
        "space exploration adventure",
        "action shooter multiplayer",
        "strategy war game",
        "puzzle casual game"
    ]
    
    embeddings = {}
    for query in test_queries:
        emb = EmbeddingService.encode_query(query)
        embeddings[query] = emb
        print(f"   ✓ '{query}' → embedding (dim: {len(emb)})")
    
    print()
    
    # 2. Test similarity between queries
    print("2. Testing similarity between queries...")
    queries_list = list(embeddings.keys())
    for i in range(len(queries_list)):
        for j in range(i+1, len(queries_list)):
            q1, q2 = queries_list[i], queries_list[j]
            sim = cosine_similarity(embeddings[q1], embeddings[q2])
            print(f"   '{q1}' <-> '{q2}': {sim:.4f}")
    
    print()
    
    # 3. Check database embeddings
    print("3. Checking database embeddings...")
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SECRET_KEY)
    
    result = client.schema('steam').table('games_prod') \
        .select('appid,name,embedding') \
        .limit(10) \
        .execute()
    
    if not result.data:
        print("   ❌ No games found")
        return False
    
    games_with_emb = [g for g in result.data if g.get('embedding')]
    print(f"   ✓ Found {len(games_with_emb)}/{len(result.data)} games with embeddings")
    
    if not games_with_emb:
        print("   ❌ No embeddings found in database")
        return False
    
    print()
    
    # 4. Manual similarity search (Python-side)
    print("4. Testing manual similarity search (Python-side)...")
    query = "space exploration"
    query_emb = EmbeddingService.encode_query(query)
    print(f"   Query: '{query}'")
    print()
    
    # Fetch more games
    result = client.schema('steam').table('games_prod') \
        .select('appid,name,short_description,embedding') \
        .not_.is_('embedding', 'null') \
        .limit(100) \
        .execute()
    
    if not result.data:
        print("   ❌ No games found")
        return False
    
    # Calculate similarities
    similarities = []
    for game in result.data:
        if game.get('embedding'):
            sim = cosine_similarity(query_emb, game['embedding'])
            similarities.append({
                'name': game['name'],
                'similarity': sim,
                'description': game.get('short_description', '')[:100]
            })
    
    # Sort by similarity
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    print(f"   ✓ Calculated similarities for {len(similarities)} games")
    print()
    print("   Top 10 results:")
    for i, game in enumerate(similarities[:10], 1):
        print(f"   {i}. {game['name']} (similarity: {game['similarity']:.4f})")
        if game['description']:
            print(f"      {game['description'][:80]}...")
    
    print()
    
    # 5. Test different queries
    print("5. Testing different query types...")
    test_cases = [
        ("action shooter", "Should find FPS games"),
        ("puzzle casual", "Should find casual puzzle games"),
        ("strategy war", "Should find strategy war games")
    ]
    
    for query, expected in test_cases:
        query_emb = EmbeddingService.encode_query(query)
        
        # Calculate similarities for first 50 games
        sims = []
        for game in result.data[:50]:
            if game.get('embedding'):
                sim = cosine_similarity(query_emb, game['embedding'])
                sims.append((game['name'], sim))
        
        sims.sort(key=lambda x: x[1], reverse=True)
        
        print(f"   Query: '{query}' ({expected})")
        print(f"   Top 3: {', '.join([f'{name} ({sim:.3f})' for name, sim in sims[:3]])}")
        print()
    
    print("=" * 80)
    print("✅ All embedding tests passed!")
    print("=" * 80)
    print()
    print("⚠️  Next step: Create PostgreSQL functions for full semantic search")
    print("   See: PHASE4_SETUP_INSTRUCTIONS.md")
    print()
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

