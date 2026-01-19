"""
Prebuild content for faster loading.
Generates and caches frequently accessed content.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import time

from backend.character_bible import CharacterBible
from backend.bible_reader import BibleReader
from backend.character_study import CharacterStudySystem


def prebuild_character_perspectives():
    """Prebuild character perspectives for popular passages."""
    print("📖 Prebuilding Character Perspectives...")
    
    character_bible = CharacterBible()
    character_study = CharacterStudySystem()
    bible_reader = BibleReader()
    
    # Get all characters
    all_characters = character_study.list_characters()
    
    # Popular passages to prebuild
    popular_passages = [
        "Genesis 1", "Genesis 2", "Genesis 3",
        "Genesis 12", "Genesis 22", "Genesis 37",
        "Exodus 3", "Exodus 14", "Exodus 20",
        "1 Samuel 17", "2 Samuel 11", "1 Kings 19",
        "Isaiah 53", "Jeremiah 1", "Ezekiel 37",
        "Matthew 1", "Matthew 5", "Matthew 26",
        "Mark 1", "Luke 2", "John 1", "John 3",
        "Acts 2", "Acts 9", "Romans 8",
        "1 Corinthians 13", "Revelation 21"
    ]
    
    # Key characters to prioritize
    key_characters = ["Adam", "Eve", "Noah", "Abraham", "Sarah", "Isaac", 
                     "Jacob", "Joseph", "Moses", "David", "Solomon",
                     "Isaiah", "Jeremiah", "Daniel", "Mary", "Joseph (NT)",
                     "Peter", "Paul", "John", "Jesus"]
    
    total = len(popular_passages) * len(key_characters)
    current = 0
    
    for passage in popular_passages:
        # Find characters in this passage
        passage_characters = character_study.get_characters_for_passage(passage)
        passage_char_names = [c.name for c in passage_characters]
        
        # Also try key characters
        for char_name in key_characters:
            if char_name in passage_char_names or char_name.lower() in [c.name.lower() for c in passage_characters]:
                try:
                    current += 1
                    print(f"[{current}/{total}] {char_name} on {passage}...", end=" ")
                    
                    # This will cache automatically
                    character_bible.get_character_perspective(char_name, passage, use_cache=True)
                    print("✓")
                except Exception as e:
                    print(f"✗ Error: {e}")
                    continue
    
    print(f"\n✅ Prebuilt {current} character perspectives")


def prebuild_character_chapters():
    """Prebuild full chapters for key characters."""
    print("\n📚 Prebuilding Character Chapters...")
    
    character_bible = CharacterBible()
    character_study = CharacterStudySystem()
    
    # Get all characters first
    all_characters = character_study.list_characters()
    character_dict = {c.name.lower(): c.character_id for c in all_characters}
    
    # Key characters and their books
    character_books = {
        "Abraham": ["Genesis"],
        "Moses": ["Exodus", "Numbers", "Deuteronomy"],
        "David": ["1 Samuel", "2 Samuel", "1 Chronicles"],
        "Solomon": ["1 Kings", "2 Chronicles"],
        "Isaiah": ["Isaiah"],
        "Jeremiah": ["Jeremiah"],
        "Ezekiel": ["Ezekiel"],
        "Daniel": ["Daniel"],
        "Peter": ["Matthew", "Mark", "Luke", "John", "Acts"],
        "Paul": ["Acts", "Romans", "1 Corinthians", "2 Corinthians", 
                "Galatians", "Ephesians", "Philippians", "Colossians"],
        "John": ["John", "1 John", "2 John", "3 John", "Revelation"]
    }
    
    # Calculate total (10 chapters per book)
    total = sum(len(books) * 10 for books in character_books.values())
    current = 0
    
    for char_name, books in character_books.items():
        # Try to find character ID
        char_id = character_dict.get(char_name.lower())
        if not char_id:
            # Try alternate names or partial match
            for c in all_characters:
                if char_name.lower() in c.name.lower() or c.name.lower() in char_name.lower():
                    char_id = c.character_id
                    char_name = c.name  # Use actual name
                    break
        
        if not char_id:
            print(f"⚠️ Character '{char_name}' not found, skipping...")
            continue
            
        for book in books:
            # Get chapter count (simplified - you might want to get actual count)
            max_chapters = 50  # Most books have < 50 chapters
            
            for chapter in range(1, min(max_chapters + 1, 11)):  # First 10 chapters
                try:
                    current += 1
                    print(f"[{current}/{total}] {char_name} - {book} {chapter}...", end=" ")
                    
                    character_bible.get_character_bible_chapter(
                        char_name, book, chapter, use_cache=True
                    )
                    print("✓")
                except Exception as e:
                    # Chapter might not exist
                    error_str = str(e).lower()
                    if "not found" not in error_str and "error" not in error_str[:50]:
                        print(f"✗ Error: {e}")
                    else:
                        print("✗ (skipped)")
                    continue
    
    print(f"\n✅ Prebuilt character chapters")


def prebuild_daily_discoveries():
    """Prebuild daily discoveries for next year."""
    print("\n✨ Prebuilding Daily Discoveries...")
    
    from backend.daily_discovery import DailyDiscoveryEngine
    from datetime import date, timedelta
    
    discovery_engine = DailyDiscoveryEngine()
    today = date.today()
    
    # Prebuild next 365 days
    total = 365
    current = 0
    
    for day in range(365):
        target_date = today + timedelta(days=day)
        try:
            current += 1
            if current % 10 == 0:
                print(f"[{current}/{total}] Generating discovery for {target_date}...")
            
            # This will cache automatically
            discovery_engine.get_daily_discovery(target_date, generate=True)
        except Exception as e:
            print(f"Error for {target_date}: {e}")
            continue
    
    print(f"\n✅ Prebuilt {current} daily discoveries")


def main():
    """Main prebuild function."""
    print("🚀 Starting Content Prebuild...\n")
    start_time = time.time()
    
    try:
        # Prebuild character perspectives
        prebuild_character_perspectives()
        
        # Prebuild character chapters (optional - takes longer)
        # prebuild_character_chapters()
        
        # Prebuild daily discoveries (optional - takes longer)
        # prebuild_daily_discoveries()
        
        elapsed = time.time() - start_time
        print(f"\n🎉 Prebuild complete in {elapsed:.1f} seconds!")
        print("\n💡 Tip: Run this script periodically to keep content fresh.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Prebuild interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during prebuild: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
