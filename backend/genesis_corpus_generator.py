"""
Batch generator to pre-generate complete corpus for Genesis chronological plan.
Builds everything upfront so daily readings are just pulled from files.
"""

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bible_data_modeler import BibleDataModeler, DailyReadingCorpus
from .bible_reader import BibleReader
from .web_scraper import BibleWebScraper


class GenesisCorpusGenerator:
    """Generate complete corpus for Genesis chronological plan."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.corpus_dir = self.data_dir / "genesis_corpus"
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        
        self.modeler = BibleDataModeler()
        self.bible_reader = BibleReader()
        self.web_scraper = BibleWebScraper()
        
        self.index_file = self.corpus_dir / "corpus_index.json"
    
    def generate_all_corpus(
        self,
        start_date: Optional[date] = None,
        year: int = 2024,
        include_web_data: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Generate corpus for all Genesis chronological readings."""
        if start_date is None:
            start_date = date(year, 1, 1)
        
        # Get all Genesis readings from chronological plan
        readings = self._get_genesis_chronological_readings()
        
        total = len(readings)
        generated = 0
        errors = []
        
        print(f"Generating corpus for {total} Genesis readings...")
        
        for i, (reading_date, passage) in enumerate(readings, 1):
            try:
                print(f"[{i}/{total}] Starting {passage}...")
                
                # Get web data if requested
                web_data = []
                if include_web_data:
                    try:
                        print(f"  → Fetching web data...")
                        web_data = self.web_scraper.get_relevant_data_for_passage(
                            passage, max_web_results=3
                        )
                        print(f"  → Found {len(web_data)} web sources")
                    except Exception as e:
                        print(f"Warning: Could not fetch web data for {passage}: {e}")
                
                # Build complete corpus
                print(f"  → Building corpus (this may take 5-15 minutes)...")
                corpus = self.modeler.build_complete_corpus(
                    passage=passage,
                    reading_date=reading_date,
                    web_data=web_data
                )
                
                # Extract chapter for organization
                chapter = self._extract_chapter(passage)
                
                # Save corpus
                self.modeler.save_corpus(corpus, chapter=chapter)
                
                generated += 1
                
                if progress_callback:
                    # Convert corpus to dict for progress callback
                    corpus_dict = self.modeler._corpus_to_dict(corpus)
                    progress_callback(i, total, passage, corpus_dict)
                else:
                    print(f"[{i}/{total}] Generated corpus for {passage} ({reading_date})")
                
            except Exception as e:
                error_msg = f"Error generating corpus for {passage} ({reading_date}): {e}"
                print(f"ERROR: {error_msg}")
                errors.append({
                    "passage": passage,
                    "date": reading_date.isoformat(),
                    "error": str(e)
                })
                continue
        
        # Create index
        index = self._create_index()
        self._save_index(index)
        
        return {
            "total": total,
            "generated": generated,
            "errors": errors,
            "index": index
        }
    
    def _get_genesis_chronological_readings(self) -> List[tuple]:
        """Get all Genesis readings from chronological plan."""
        readings = []
        start_date = date(2024, 1, 1)
        current_date = start_date
        
        # Genesis has 50 chapters - generate one per day for first 50 days
        # This ensures we cover all Genesis chapters systematically
        genesis_chapters = list(range(1, 51))
        
        for i, chapter in enumerate(genesis_chapters):
            reading_date = start_date + timedelta(days=i)
            passage = f"Genesis {chapter}"
            readings.append((reading_date, passage))
        
        return readings
    
    def _extract_chapter(self, passage: str) -> Optional[int]:
        """Extract chapter number from passage."""
        import re
        match = re.search(r"Genesis\s+(\d+)", passage)
        if match:
            return int(match.group(1))
        return None
    
    def _create_index(self) -> Dict[str, Any]:
        """Create index of all generated corpus files."""
        index = {
            "by_date": {},
            "by_chapter": {},
            "by_passage": {},
            "metadata": {
                "total_files": 0,
                "chapters_covered": set(),
                "date_range": {"start": None, "end": None}
            }
        }
        
        # Scan corpus directory
        for chapter_dir in self.corpus_dir.glob("chapter_*"):
            chapter_num = int(chapter_dir.name.split("_")[1])
            
            for corpus_file in chapter_dir.glob("*.json"):
                try:
                    data = json.loads(corpus_file.read_text(encoding="utf-8"))
                    
                    date_str = data.get("date", "")
                    passage = data.get("passage_data", {}).get("reference", "")
                    
                    if date_str and passage:
                        # Index by date
                        if date_str not in index["by_date"]:
                            index["by_date"][date_str] = []
                        index["by_date"][date_str].append({
                            "passage": passage,
                            "chapter": chapter_num,
                            "file": str(corpus_file.relative_to(self.corpus_dir))
                        })
                        
                        # Index by chapter
                        if chapter_num not in index["by_chapter"]:
                            index["by_chapter"][chapter_num] = []
                        index["by_chapter"][chapter_num].append({
                            "date": date_str,
                            "passage": passage,
                            "file": str(corpus_file.relative_to(self.corpus_dir))
                        })
                        
                        # Index by passage
                        index["by_passage"][passage] = {
                            "date": date_str,
                            "chapter": chapter_num,
                            "file": str(corpus_file.relative_to(self.corpus_dir))
                        }
                        
                        index["metadata"]["total_files"] += 1
                        index["metadata"]["chapters_covered"].add(chapter_num)
                        
                        # Update date range
                        if not index["metadata"]["date_range"]["start"]:
                            index["metadata"]["date_range"]["start"] = date_str
                        index["metadata"]["date_range"]["end"] = date_str
                
                except Exception as e:
                    print(f"Error indexing {corpus_file}: {e}")
                    continue
        
        # Convert set to list for JSON
        index["metadata"]["chapters_covered"] = sorted(list(index["metadata"]["chapters_covered"]))
        
        return index
    
    def _save_index(self, index: Dict[str, Any]) -> None:
        """Save corpus index to file."""
        self.index_file.write_text(
            json.dumps(index, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def load_index(self) -> Optional[Dict[str, Any]]:
        """Load corpus index."""
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return None
    
    def get_corpus_for_date(self, reading_date: date) -> Optional[DailyReadingCorpus]:
        """Get corpus for a specific date."""
        date_str = reading_date.isoformat()
        index = self.load_index()
        
        if not index:
            return None
        
        # Find passages for this date
        date_readings = index.get("by_date", {}).get(date_str, [])
        if not date_readings:
            return None
        
        # Get first Genesis passage (or all if multiple)
        for reading in date_readings:
            if reading["passage"].startswith("Genesis"):
                filepath = self.corpus_dir / reading["file"]
                if filepath.exists():
                    try:
                        data = json.loads(filepath.read_text(encoding="utf-8"))
                        return data  # Return as dict for now
                    except Exception:
                        continue
        
        return None
    
    def get_corpus_for_chapter(self, chapter: int) -> List[Dict[str, Any]]:
        """Get all corpus entries for a chapter."""
        index = self.load_index()
        
        if not index:
            return []
        
        chapter_readings = index.get("by_chapter", {}).get(chapter, [])
        corpus_list = []
        
        for reading in chapter_readings:
            filepath = self.corpus_dir / reading["file"]
            if filepath.exists():
                try:
                    data = json.loads(filepath.read_text(encoding="utf-8"))
                    corpus_list.append(data)
                except Exception:
                    continue
        
        # Sort by date
        corpus_list.sort(key=lambda x: x.get("date", ""))
        
        return corpus_list
