#!/usr/bin/env python3
"""
Batch generate Augustine or Aquinas commentaries for the entire Bible reading plan.
Usage:
    python generate_commentaries.py                    # Generate Augustine commentaries
    python generate_commentaries.py --helper aquinas   # Generate Aquinas commentaries
"""

import json
import time
from datetime import date, timedelta
from pathlib import Path

from backend.bible_reader import BibleReader
from backend.ollama_client import OllamaClient
from backend.rag_system import RAGSystem


def generate_all_commentaries(start_day: int = 1, end_day: int = 365, resume: bool = True, helper: str = "augustine"):
    """Generate commentaries for all passages in the reading plan.
    
    Args:
        start_day: Starting day (1-365)
        end_day: Ending day (1-365)
        resume: If True, skip already generated commentaries
        helper: Either "augustine" or "aquinas"
    """
    helper_name = "Augustine" if helper == "augustine" else "Aquinas"
    print(f"Generating {helper_name} commentaries for days {start_day} to {end_day}...")
    print("This will take several hours. Press Ctrl+C to pause and resume later.\n")
    
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    commentaries_file = data_dir / f"{helper}_commentaries.json"
    
    # Load existing commentaries if resuming
    commentaries = {"by_passage": {}, "by_day": {}}
    if resume and commentaries_file.exists():
        try:
            commentaries = json.loads(commentaries_file.read_text(encoding="utf-8"))
            print(f"Loaded {len(commentaries['by_passage'])} existing commentaries.\n")
        except Exception as e:
            print(f"Warning: Could not load existing commentaries: {e}\n")
    
    # Initialize components
    bible_reader = BibleReader()
    rag_system = RAGSystem()
    rag_system.initialize_default_data()
    ollama = OllamaClient()
    
    # Start from January 1, 2024
    start_date = date(2024, 1, 1)
    
    total_generated = 0
    total_skipped = 0
    total_errors = 0
    start_time = time.time()
    total_days = end_day - start_day + 1
    
    try:
        for day_index in range(start_day, end_day + 1):
            # Calculate progress
            progress = ((day_index - start_day) / total_days) * 100
            elapsed = time.time() - start_time
            if total_generated > 0 and elapsed > 0:
                avg_time_per_commentary = elapsed / total_generated
                estimated_remaining = (total_days - (day_index - start_day)) * avg_time_per_commentary
                eta_hours = estimated_remaining / 3600
                print(f"\n[Progress: {progress:.1f}%] Generated: {total_generated} | Skipped: {total_skipped} | Errors: {total_errors}")
                print(f"Estimated time remaining: {eta_hours:.1f} hours")
            print("-" * 60)
            reading_date = start_date + timedelta(days=day_index - 1)
            day_key = str(day_index)
            
            # Skip if already generated
            if day_key in commentaries.get("by_day", {}):
                total_skipped += 1
                continue
            
            # Get reading for this day (using chronological plan)
            reading = bible_reader.get_reading_for_date(reading_date, plan_type="chronological")
            if not reading or not reading.get("passages"):
                print(f"Day {day_index}: No passages found")
                continue
            
            passages = reading.get("passages", [])
            day_commentaries = {}
            
            print(f"Day {day_index} ({reading_date}): Generating commentaries for {len(passages)} passages...")
            
            for passage in passages:
                # Skip if already generated
                if passage in commentaries.get("by_passage", {}):
                    day_commentaries[passage] = commentaries["by_passage"][passage]
                    continue
                
                try:
                    # Get the actual passage text for better commentary
                    passage_text_obj = bible_reader.get_passage_text(passage)
                    passage_text = passage
                    if passage_text_obj and passage_text_obj.get("verses"):
                        # Format passage text from verses
                        verses = passage_text_obj["verses"]
                        verse_lines = [f"{verse}: {text}" for verse, text in verses.items()]
                        passage_text = f"{passage}\n\n" + "\n".join(verse_lines[:50])  # Limit to 50 verses for context
                    
                    # Get relevant context from RAG based on helper's writings
                    context = rag_system.get_relevant_context(passage, helper=helper, top_k=3)
                    
                    # Generate commentary with full passage context
                    print(f"  - {passage}...", end="", flush=True)
                    commentary = ollama.generate_commentary(
                        passage=passage_text,
                        context=context,
                        helper=helper,
                        personalized=False,
                    )
                    
                    if commentary and len(commentary.strip()) > 50:  # Basic validation
                        day_commentaries[passage] = commentary
                        commentaries["by_passage"][passage] = commentary
                        print(f" ✓ ({len(commentary)} chars)")
                        total_generated += 1
                        
                        # Save after each commentary (in case of interruption)
                        commentaries["by_day"][day_key] = {
                            "date": reading_date.isoformat(),
                            "passages": passages,
                            "commentaries": day_commentaries,
                        }
                        commentaries_file.write_text(
                            json.dumps(commentaries, indent=2, ensure_ascii=False),
                            encoding="utf-8"
                        )
                    else:
                        print(f" ✗ (too short)")
                        total_errors += 1
                    
                    # Small delay to avoid overwhelming Ollama
                    time.sleep(2)
                    
                except KeyboardInterrupt:
                    print("\n\nInterrupted. Saving progress...")
                    commentaries["by_day"][day_key] = {
                        "date": reading_date.isoformat(),
                        "passages": passages,
                        "commentaries": day_commentaries,
                    }
                    commentaries_file.write_text(
                        json.dumps(commentaries, indent=2, ensure_ascii=False),
                        encoding="utf-8"
                    )
                    print(f"Progress saved. Generated: {total_generated}, Skipped: {total_skipped}, Errors: {total_errors}")
                    print(f"Resume with: python generate_commentaries.py --start {day_index}")
                    return
                except Exception as e:
                    print(f" ✗ Error: {e}")
                    total_errors += 1
            
            print(f"Day {day_index} complete.\n")
            
    except KeyboardInterrupt:
        print("\n\nInterrupted. Saving progress...")
        commentaries_file.write_text(
            json.dumps(commentaries, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    print(f"\n{'='*60}")
    print(f"Generation complete!")
    print(f"Generated: {total_generated} new commentaries")
    print(f"Skipped: {total_skipped} (already exist)")
    print(f"Errors: {total_errors}")
    print(f"Total: {len(commentaries['by_passage'])} commentaries saved")
    print(f"{'='*60}")


if __name__ == "__main__":
    import sys
    
    start_day = 1
    end_day = 365
    
    # Parse command line arguments
    helper = "augustine"
    if "--start" in sys.argv:
        idx = sys.argv.index("--start")
        if idx + 1 < len(sys.argv):
            start_day = int(sys.argv[idx + 1])
    
    if "--end" in sys.argv:
        idx = sys.argv.index("--end")
        if idx + 1 < len(sys.argv):
            end_day = int(sys.argv[idx + 1])
    
    if "--helper" in sys.argv:
        idx = sys.argv.index("--helper")
        if idx + 1 < len(sys.argv):
            helper_arg = sys.argv[idx + 1].lower()
            if helper_arg in ("augustine", "aquinas"):
                helper = helper_arg
    
    generate_all_commentaries(start_day=start_day, end_day=end_day, resume=True, helper=helper)
