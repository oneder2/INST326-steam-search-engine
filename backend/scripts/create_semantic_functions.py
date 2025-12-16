#!/usr/bin/env python3
"""
Create Semantic Search Functions in PostgreSQL

This script creates the PostgreSQL functions needed for semantic search.
Since Supabase Python client doesn't support direct SQL execution,
this script provides instructions and validation.

Usage:
    python -m scripts.create_semantic_functions
"""

import sys
from pathlib import Path

def main():
    """Main function to display SQL setup instructions"""
    
    sql_file = Path(__file__).parent.parent / 'sql' / 'create_semantic_search_function.sql'
    
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return 1
    
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    print("=" * 80)
    print("🔧 Semantic Search Functions Setup")
    print("=" * 80)
    print()
    print("⚠️  Supabase Python client doesn't support direct SQL execution.")
    print("   You need to manually create the functions via Supabase SQL Editor.")
    print()
    print("📋 Steps:")
    print()
    print("1. Go to Supabase Dashboard:")
    print("   https://supabase.com/dashboard/project/[your-project-id]/sql")
    print()
    print("2. Click 'New Query'")
    print()
    print("3. Copy and paste the following SQL:")
    print()
    print("-" * 80)
    print(sql_content)
    print("-" * 80)
    print()
    print("4. Click 'Run' to execute")
    print()
    print("5. Verify functions are created:")
    print("   - steam.search_games_semantic")
    print("   - steam.search_games_semantic_simple")
    print()
    print("=" * 80)
    print()
    print("💡 Alternative: If you have psql access:")
    print()
    print(f"   psql -h [host] -U [user] -d [database] -f {sql_file}")
    print()
    print("=" * 80)
    
    # Also save to a temp file for easy copying
    output_file = Path(__file__).parent.parent / 'semantic_search_functions.sql'
    with open(output_file, 'w') as f:
        f.write(sql_content)
    
    print()
    print(f"✓ SQL saved to: {output_file}")
    print("  You can copy this file content to Supabase SQL Editor")
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

