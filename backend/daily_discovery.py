"""
Daily Discovery System - Something fascinating to draw you back every day.
Generates daily discoveries: connections, mysteries, insights that make you want to explore more.
"""

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bible_reader import BibleReader
from .rag_system import RAGSystem
from .ollama_client import OllamaClient


@dataclass
class DailyDiscovery:
    """A daily discovery designed to engage and inspire exploration."""
    date: str
    title: str
    type: str  # "connection", "mystery", "insight", "pattern", "character"
    passage: str
    discovery_text: str
    related_passages: List[str]
    why_interesting: str
    explore_further: List[str]


class DailyDiscoveryEngine:
    """Generates daily discoveries that make you want to explore more."""
    
    DISCOVERY_TYPES = [
        "hidden_connection",
        "literary_pattern",
        "theological_mystery",
        "character_insight",
        "historical_context",
        "cross_book_theme",
        "word_study",
        "fulfillment_pattern"
    ]
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.discoveries_file = self.data_dir / "daily_discoveries.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.bible_reader = BibleReader()
        self.rag_system: Optional[RAGSystem] = None
        self.ollama_client: Optional[OllamaClient] = None
    
    def _get_rag_system(self) -> RAGSystem:
        if self.rag_system is None:
            self.rag_system = RAGSystem()
            if not self.rag_system._has_cached_data():
                self.rag_system.initialize_default_data()
        return self.rag_system
    
    def _get_ollama(self) -> OllamaClient:
        if self.ollama_client is None:
            self.ollama_client = OllamaClient()
        return self.ollama_client
    
    def get_discovery_for_date(self, discovery_date: date = None, generate_if_missing: bool = False) -> Optional[DailyDiscovery]:
        """Get today's discovery - something fascinating to explore."""
        if not discovery_date:
            discovery_date = date.today()
        
        date_key = discovery_date.isoformat()
        
        # Try to load existing discovery
        existing = self._load_discovery(date_key)
        if existing:
            return self._dict_to_discovery(existing)
        
        # Generate if missing and requested
        if generate_if_missing:
            discovery = self._generate_discovery(discovery_date)
            if discovery:
                self._save_discovery(discovery)
                return discovery
        
        return None
    
    def _generate_discovery(self, discovery_date: date) -> Optional[DailyDiscovery]:
        """Generate a fascinating daily discovery."""
        try:
            # Pick a discovery type based on day of year
            day_of_year = discovery_date.timetuple().tm_yday
            discovery_type = self.DISCOVERY_TYPES[day_of_year % len(self.DISCOVERY_TYPES)]
            
            # Get a relevant passage (cycle through Bible based on day)
            # Build sequence manually (same as bible_reader)
            books = [
                ("Genesis", 50), ("Job", 42), ("Exodus", 40), ("Leviticus", 27),
                ("Numbers", 36), ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21),
                ("Ruth", 4), ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22),
                ("2 Kings", 25), ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10),
                ("Nehemiah", 13), ("Esther", 10), ("Psalms", 150), ("Proverbs", 31),
                ("Ecclesiastes", 12), ("Song of Solomon", 8), ("Isaiah", 66), ("Jeremiah", 52),
                ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12), ("Hosea", 14),
                ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4), ("Micah", 7),
                ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3), ("Haggai", 2),
                ("Zechariah", 14), ("Malachi", 4), ("Matthew", 28), ("Mark", 16),
                ("Luke", 24), ("John", 21), ("Acts", 28), ("James", 5), ("Galatians", 6),
                ("1 Thessalonians", 5), ("2 Thessalonians", 3), ("1 Corinthians", 16),
                ("2 Corinthians", 13), ("Romans", 16), ("Ephesians", 6), ("Philippians", 4),
                ("Colossians", 4), ("Philemon", 1), ("1 Timothy", 6), ("Titus", 3),
                ("2 Timothy", 4), ("1 Peter", 5), ("2 Peter", 3), ("Jude", 1),
                ("Hebrews", 13), ("Revelation", 22), ("1 John", 5), ("2 John", 1), ("3 John", 1),
            ]
            sequence = []
            for book, chapter_count in books:
                for ch in range(1, chapter_count + 1):
                    sequence.append((book, ch))
            
            passage_index = (day_of_year - 1) % len(sequence)
            book, chapter = sequence[passage_index]
            passage = f"{book} {chapter}"
            
            # Generate discovery based on type
            if discovery_type == "hidden_connection":
                return self._generate_connection_discovery(passage, discovery_date)
            elif discovery_type == "literary_pattern":
                return self._generate_pattern_discovery(passage, discovery_date)
            elif discovery_type == "theological_mystery":
                return self._generate_mystery_discovery(passage, discovery_date)
            elif discovery_type == "character_insight":
                return self._generate_character_discovery(passage, discovery_date)
            else:
                return self._generate_general_discovery(passage, discovery_date, discovery_type)
        except Exception as e:
            print(f"Error generating discovery: {e}")
            return None
    
    def _generate_connection_discovery(self, passage: str, discovery_date: date) -> Optional[DailyDiscovery]:
        """Generate a discovery about hidden connections."""
        ollama = self._get_ollama()
        
        prompt = f"""Generate a fascinating discovery about this Bible passage that will make someone want to explore more:

Passage: {passage}

Create a "hidden connection" discovery - something surprising like:
- This passage echoes another passage in a surprising way
- A word or theme appears in unexpected places
- This connects to a story told much later
- A pattern that spans multiple books

Make it:
1. Surprising ("Did you know...?")
2. Specific (mention actual connections)
3. Engaging (makes you want to explore)
4. Brief (100-150 words)

Title: A catchy 10-word title
Discovery: The fascinating insight
Why Interesting: Why this matters (50 words)
Related Passages: List 2-3 passages to explore"""
        
        system = "You are a biblical scholar who reveals fascinating connections and patterns that inspire deeper exploration."
        
        response = ollama._generate(prompt, system, ollama.default_model)
        
        # Parse response (simplified)
        lines = response.split("\n")
        title = lines[0].replace("Title:", "").strip() if len(lines) > 0 else "Hidden Connection"
        discovery_text = "\n".join([l for l in lines[1:] if "Why" not in l and "Related" not in l])[:500]
        
        return DailyDiscovery(
            date=discovery_date.isoformat(),
            title=title or "Hidden Connection Discovered",
            type="connection",
            passage=passage,
            discovery_text=discovery_text or "An intriguing connection awaits exploration.",
            related_passages=[passage],
            why_interesting="This connection reveals deeper patterns in Scripture.",
            explore_further=[passage]
        )
    
    def _generate_pattern_discovery(self, passage: str, discovery_date: date) -> Optional[DailyDiscovery]:
        """Generate a discovery about literary patterns."""
        return DailyDiscovery(
            date=discovery_date.isoformat(),
            title="Literary Pattern Discovered",
            type="pattern",
            passage=passage,
            discovery_text=f"The passage {passage} reveals an intriguing literary pattern that appears throughout Scripture.",
            related_passages=[passage],
            why_interesting="Patterns reveal intentional structure and meaning.",
            explore_further=[passage]
        )
    
    def _generate_mystery_discovery(self, passage: str, discovery_date: date) -> Optional[DailyDiscovery]:
        """Generate a discovery about theological mysteries."""
        return DailyDiscovery(
            date=discovery_date.isoformat(),
            title="Theological Mystery Unveiled",
            type="mystery",
            passage=passage,
            discovery_text=f"{passage} contains a theological mystery that has fascinated scholars for centuries.",
            related_passages=[passage],
            why_interesting="Mysteries invite deeper contemplation and understanding.",
            explore_further=[passage]
        )
    
    def _generate_character_discovery(self, passage: str, discovery_date: date) -> Optional[DailyDiscovery]:
        """Generate a discovery about character insights."""
        return DailyDiscovery(
            date=discovery_date.isoformat(),
            title="Character Insight Revealed",
            type="character",
            passage=passage,
            discovery_text=f"A fascinating insight about the characters in {passage}.",
            related_passages=[passage],
            why_interesting="Character insights reveal human nature and divine interaction.",
            explore_further=[passage]
        )
    
    def _generate_general_discovery(self, passage: str, discovery_date: date, discovery_type: str) -> Optional[DailyDiscovery]:
        """Generate a general discovery."""
        return DailyDiscovery(
            date=discovery_date.isoformat(),
            title="Fascinating Discovery",
            type=discovery_type,
            passage=passage,
            discovery_text=f"An intriguing discovery about {passage}.",
            related_passages=[passage],
            why_interesting="This discovery invites deeper exploration.",
            explore_further=[passage]
        )
    
    def _load_discovery(self, date_key: str) -> Optional[Dict[str, Any]]:
        """Load a pre-generated discovery."""
        if self.discoveries_file.exists():
            try:
                data = json.loads(self.discoveries_file.read_text(encoding="utf-8"))
                return data.get(date_key)
            except Exception:
                pass
        return None
    
    def _save_discovery(self, discovery: DailyDiscovery) -> None:
        """Save a discovery for future use."""
        data = {}
        if self.discoveries_file.exists():
            try:
                data = json.loads(self.discoveries_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        data[discovery.date] = {
            "date": discovery.date,
            "title": discovery.title,
            "type": discovery.type,
            "passage": discovery.passage,
            "discovery_text": discovery.discovery_text,
            "related_passages": discovery.related_passages,
            "why_interesting": discovery.why_interesting,
            "explore_further": discovery.explore_further
        }
        
        try:
            self.discoveries_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass
    
    def _dict_to_discovery(self, data: Dict[str, Any]) -> DailyDiscovery:
        """Convert dict to DailyDiscovery dataclass."""
        return DailyDiscovery(
            date=data.get("date", ""),
            title=data.get("title", ""),
            type=data.get("type", "insight"),
            passage=data.get("passage", ""),
            discovery_text=data.get("discovery_text", ""),
            related_passages=data.get("related_passages", []),
            why_interesting=data.get("why_interesting", ""),
            explore_further=data.get("explore_further", [])
        )
