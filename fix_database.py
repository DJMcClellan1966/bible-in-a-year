#!/usr/bin/env python3
"""
Fix database schema - recreate table if schema doesn't match.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "bible_app.db"

def check_and_fix_schema():
    """Check database schema and fix if needed."""
    if not DB_PATH.exists():
        print("Database doesn't exist. It will be created on first run.")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if table exists and get its schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='diary_entries'")
        result = cursor.fetchone()
        
        if result and result[0]:
            table_sql = result[0]
            # Check if entry_date column exists
            if 'entry_date' not in table_sql:
                print("WARNING: Database schema is outdated. Migrating...")
                
                # Backup existing data
                cursor.execute("SELECT * FROM diary_entries")
                old_data = cursor.fetchall()
                
                # Get column names from old table
                cursor.execute("PRAGMA table_info(diary_entries)")
                old_columns = [row[1] for row in cursor.fetchall()]
                
                print(f"Found {len(old_data)} entries to migrate")
                
                # Drop old table
                cursor.execute("DROP TABLE diary_entries")
                
                # Create new table with correct schema
                cursor.execute("""
                    CREATE TABLE diary_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entry_date DATE NOT NULL UNIQUE,
                        reading_passage TEXT NOT NULL,
                        personal_notes TEXT,
                        margin_notes TEXT,
                        ai_insights TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Migrate data if possible
                if old_data and 'date' in old_columns:
                    date_idx = old_columns.index('date')
                    reading_idx = old_columns.index('reading_passage') if 'reading_passage' in old_columns else None
                    
                    migrated = 0
                    for row in old_data:
                        try:
                            # Try to map old columns to new
                            date_val = row[date_idx] if date_idx < len(row) else None
                            passage = row[reading_idx] if reading_idx and reading_idx < len(row) else ""
                            notes = row[old_columns.index('personal_notes')] if 'personal_notes' in old_columns and old_columns.index('personal_notes') < len(row) else None
                            margin = row[old_columns.index('margin_notes')] if 'margin_notes' in old_columns and old_columns.index('margin_notes') < len(row) else None
                            insights = row[old_columns.index('ai_insights')] if 'ai_insights' in old_columns and old_columns.index('ai_insights') < len(row) else None
                            
                            if date_val:
                                cursor.execute("""
                                    INSERT INTO diary_entries (entry_date, reading_passage, personal_notes, margin_notes, ai_insights)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (date_val, passage, notes, margin, insights))
                                migrated += 1
                        except Exception as e:
                            print(f"  Skipped entry due to error: {e}")
                            continue
                    
                    print(f"SUCCESS: Migrated {migrated} entries")
                else:
                    print("WARNING: Could not migrate data (schema too different)")
                
                conn.commit()
                print("SUCCESS: Database schema updated successfully!")
            else:
                print("SUCCESS: Database schema is up to date")
        else:
            print("SUCCESS: Table doesn't exist yet - will be created on first run")
    
    except Exception as e:
        print(f"ERROR: Error checking schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Database Schema Fixer")
    print("=" * 60)
    check_and_fix_schema()
    print("=" * 60)
