#!/usr/bin/env python3
"""
Batch generate complete Genesis corpus for all chronological readings.
Run this script to pre-generate all corpus data upfront.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.genesis_corpus_generator import GenesisCorpusGenerator


def main():
    print("=" * 60)
    print("Genesis Corpus Generator")
    print("=" * 60)
    print()
    print("This will generate complete corpus for all Genesis readings.")
    print("This includes:")
    print("  - Structured Bible passage data")
    print("  - Comprehensive commentary (Augustine, Aquinas, external, web)")
    print("  - Daily summaries (verse-like format)")
    print("  - Key insights and theological themes")
    print()
    print("This may take a while depending on the number of readings...")
    print()
    
    include_web = input("Include web scraping? (y/n, default: y): ").strip().lower() != 'n'
    year = input("Year for readings (default: 2024): ").strip()
    year = int(year) if year.isdigit() else 2024
    
    print()
    print("Starting generation...")
    print()
    
    generator = GenesisCorpusGenerator()
    
    def progress_callback(i, total, passage, corpus):
        print(f"[{i}/{total}] ✓ {passage} - {corpus.get('date', 'N/A')}")
    
    try:
        result = generator.generate_all_corpus(
            year=year,
            include_web_data=include_web,
            progress_callback=progress_callback
        )
        
        print()
        print("=" * 60)
        print("Generation Complete!")
        print("=" * 60)
        print(f"Total readings: {result['total']}")
        print(f"Successfully generated: {result['generated']}")
        print(f"Errors: {len(result['errors'])}")
        
        if result['errors']:
            print()
            print("Errors encountered:")
            for error in result['errors']:
                print(f"  - {error['passage']} ({error['date']}): {error['error']}")
        
        print()
        print("Corpus files saved to: data/genesis_corpus/")
        print("Index saved to: data/genesis_corpus/corpus_index.json")
        print()
        print("You can now use the corpus in the app!")
        
    except KeyboardInterrupt:
        print()
        print("\nGeneration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
