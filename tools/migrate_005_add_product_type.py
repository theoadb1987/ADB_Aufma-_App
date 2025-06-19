#!/usr/bin/env python3
"""
Migration 005: Add product_type column to positions table.

This migration adds the product_type column to existing positions tables
to support product type integration.
"""
import sys
import os
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def migrate_database(db_path: str) -> bool:
    """
    Apply migration to add product_type column to positions table.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        True if migration was successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if positions table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='positions'
        """)
        
        if not cursor.fetchone():
            print(f"⚠️  Positions table not found in {db_path}")
            return False
        
        # Check if product_type column already exists
        cursor.execute("PRAGMA table_info(positions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'product_type' in columns:
            print(f"✅ Column 'product_type' already exists in {db_path}")
            return True
        
        # Add the product_type column
        print(f"🔧 Adding product_type column to positions table in {db_path}")
        cursor.execute("ALTER TABLE positions ADD COLUMN product_type TEXT DEFAULT ''")
        
        # Commit the changes
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully added product_type column to {db_path}")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add product_type column to positions table')
    parser.add_argument('database', help='Path to database file to migrate')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    db_path = args.database
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        sys.exit(1)
    
    if args.dry_run:
        print(f"🔍 DRY RUN: Would add product_type column to {db_path}")
        print("   This would execute: ALTER TABLE positions ADD COLUMN product_type TEXT DEFAULT ''")
        return
    
    print(f"🚀 Starting migration for {db_path}")
    success = migrate_database(db_path)
    
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()