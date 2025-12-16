"""
Populate Embeddings Script

This script generates and stores vector embeddings for all games in the database.
Embeddings are used for semantic search with pgvector extension.

Usage:
    # Process all games
    python -m scripts.populate_embeddings
    
    # Process only 100 games (for testing)
    python -m scripts.populate_embeddings --limit 100
    
    # Use smaller batch size (for memory-constrained systems)
    python -m scripts.populate_embeddings --batch-size 50
    
    # Start from specific game (for resuming interrupted runs)
    python -m scripts.populate_embeddings --start-from 1000

Prerequisites:
    - pgvector extension enabled in Supabase
    - embedding column added to games_prod table
    - sentence-transformers installed

Output:
    Updates the embedding column for all games in steam.games_prod table
"""

import asyncio
import argparse
import sys
import logging
from typing import List, Dict, Any
from supabase import create_client, Client
from app.config import settings
from app.services.embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def populate_embeddings(
    batch_size: int = 100,
    limit: int = None,
    start_from: int = 0
):
    """
    Generate and store embeddings for all games
    
    Args:
        batch_size: Number of games to process per batch (default: 100)
        limit: Max number of games to process (None = all)
        start_from: Start from specific game index (default: 0)
    
    Process:
        1. Fetch games from database
        2. Generate embeddings in batches
        3. Update database with embeddings
        4. Report progress
    """
    print("=" * 70)
    print("Steam Game Embedding Population")
    print("=" * 70)
    
    # Initialize Supabase client
    logger.info("Connecting to Supabase...")
    db: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SECRET_KEY
    )
    logger.info("✓ Connected to Supabase")
    
    # Fetch count of games
    logger.info("Fetching game count...")
    count_query = db.schema(settings.DATABASE_SCHEMA)\
        .table(settings.DATABASE_TABLE)\
        .select('appid', count='exact')\
        .limit(1)
    
    count_response = count_query.execute()
    total_games_in_db = count_response.count
    
    logger.info(f"Found {total_games_in_db} games in database")
    
    # Build query
    logger.info("Fetching games from database...")
    query = db.schema(settings.DATABASE_SCHEMA)\
        .table(settings.DATABASE_TABLE)\
        .select('appid, name, short_description, genres')\
        .order('appid', desc=False)
    
    # Apply limit if specified
    if limit:
        query = query.limit(limit)
        logger.info(f"Limiting to {limit} games")
    
    # Apply offset if starting from specific game
    if start_from > 0:
        query = query.range(start_from, start_from + (limit or total_games_in_db) - 1)
        logger.info(f"Starting from game index {start_from}")
    
    # Fetch games
    response = query.execute()
    games = response.data
    
    if not games:
        logger.error("No games found in database")
        print("\n❌ No games to process")
        return
    
    total_games = len(games)
    logger.info(f"✓ Fetched {total_games} games to process")
    
    print("\n" + "=" * 70)
    print(f"Processing {total_games} games in batches of {batch_size}")
    print("=" * 70)
    
    # Process in batches
    processed = 0
    failed = 0
    total_batches = (total_games + batch_size - 1) // batch_size
    
    for i in range(0, total_games, batch_size):
        batch = games[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"\nBatch {batch_num}/{total_batches}")
        print("-" * 70)
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} games)...")
        
        try:
            # Generate embeddings for batch
            logger.info(f"Generating embeddings for {len(batch)} games...")
            embeddings = EmbeddingService.encode_batch(batch, show_progress=False)
            logger.info(f"✓ Generated {len(embeddings)} embeddings")
            
            # Update each game with its embedding
            logger.info("Updating database...")
            for game, embedding in zip(batch, embeddings):
                try:
                    db.schema(settings.DATABASE_SCHEMA)\
                        .table(settings.DATABASE_TABLE)\
                        .update({'embedding': embedding})\
                        .eq('appid', game['appid'])\
                        .execute()
                    
                    processed += 1
                    
                except Exception as e:
                    logger.error(f"Failed to update game {game['appid']} ({game.get('name', 'Unknown')}): {e}")
                    failed += 1
            
            # Progress report
            progress_pct = (processed / total_games) * 100
            print(f"✓ Batch {batch_num} complete")
            print(f"  Progress: {processed}/{total_games} ({progress_pct:.1f}%)")
            if failed > 0:
                print(f"  Failed: {failed}")
            
        except Exception as e:
            logger.error(f"Failed to process batch {batch_num}: {e}")
            print(f"❌ Batch {batch_num} failed: {e}")
            failed += len(batch)
    
    # Final summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total games processed: {processed}/{total_games}")
    print(f"Success rate: {(processed / total_games) * 100:.1f}%")
    if failed > 0:
        print(f"Failed: {failed}")
    print("=" * 70)
    
    if processed > 0:
        logger.info(f"✅ Successfully processed {processed}/{total_games} games!")
    else:
        logger.error("❌ No games were processed successfully")


def verify_setup():
    """
    Verify that pgvector is set up correctly
    
    Checks:
    - Can connect to Supabase
    - Table exists
    - Embedding column exists
    """
    print("Verifying setup...")
    print("-" * 70)
    
    try:
        # Connect to Supabase
        db: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SECRET_KEY
        )
        print("✓ Connected to Supabase")
        
        # Try to query a single game with embedding column
        result = db.schema(settings.DATABASE_SCHEMA)\
            .table(settings.DATABASE_TABLE)\
            .select('appid, name, embedding')\
            .limit(1)\
            .execute()
        
        if result.data:
            game = result.data[0]
            has_embedding = game.get('embedding') is not None
            print(f"✓ Table exists: {settings.DATABASE_SCHEMA}.{settings.DATABASE_TABLE}")
            print(f"✓ Embedding column exists")
            if has_embedding:
                print(f"✓ Sample game already has embedding: {game['name']}")
            else:
                print(f"  Sample game needs embedding: {game['name']}")
        
        print("\n✅ Setup verification complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Setup verification failed: {e}")
        print("\nPlease ensure:")
        print("1. pgvector extension is enabled: CREATE EXTENSION vector;")
        print("2. Embedding column exists:")
        print("   ALTER TABLE steam.games_prod ADD COLUMN embedding vector(384);")
        print("3. Index is created:")
        print("   CREATE INDEX ON steam.games_prod USING ivfflat (embedding vector_cosine_ops);")
        return False


def main():
    """Main entry point for script"""
    parser = argparse.ArgumentParser(
        description='Populate game embeddings for semantic search',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all games
  python -m scripts.populate_embeddings

  # Process only 100 games (testing)
  python -m scripts.populate_embeddings --limit 100

  # Use smaller batch size
  python -m scripts.populate_embeddings --batch-size 50

  # Verify setup only
  python -m scripts.populate_embeddings --verify-only
"""
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of games per batch (default: 100)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of games to process (default: all)'
    )
    
    parser.add_argument(
        '--start-from',
        type=int,
        default=0,
        help='Start from specific game index (default: 0)'
    )
    
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify setup, do not process games'
    )
    
    args = parser.parse_args()
    
    # Verify setup
    if not verify_setup():
        sys.exit(1)
    
    if args.verify_only:
        print("\nSetup verification complete. Use without --verify-only to process games.")
        sys.exit(0)
    
    # Run embedding population
    print("\nStarting embedding population...")
    print()
    
    try:
        asyncio.run(populate_embeddings(
            batch_size=args.batch_size,
            limit=args.limit,
            start_from=args.start_from
        ))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Progress has been saved. You can resume with --start-from")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

