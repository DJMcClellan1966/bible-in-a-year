"""
Enhanced Bible Reader with Integrated Commentary.
Combines modern exegesis and church fathers' wisdom throughout the Bible text.
"""

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bible_reader import BibleReader
from .rag_system import RAGSystem
from .ollama_client import OllamaClient


@dataclass
class EnhancedPassage:
    """A Bible passage with integrated commentary."""
    passage: str
    verses: Dict[str, str]
    modern_exegesis: Optional[str] = None
    church_fathers_wisdom: Optional[str] = None
    integrated_commentary: Optional[str] = None
    key_insights: Optional[List[str]] = None


class EnhancedBibleReader:
    """Reads Bible with integrated modern and traditional commentary."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.enhanced_plan_file = self.data_dir / "enhanced_reading_plan.json"
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
    
    def get_enhanced_passage(self, reference: str, generate_if_missing: bool = False) -> Optional[EnhancedPassage]:
        """Get a passage with integrated commentary (modern + church fathers)."""
        # Get base passage text
        passage_text = self.bible_reader.get_passage_text(reference)
        if not passage_text or not passage_text.get("verses"):
            return None
        
        verses = passage_text["verses"]
        
        # Try to load pre-generated enhanced commentary
        enhanced_data = self._load_enhanced_commentary(reference)
        
        # Generate if missing and requested
        if not enhanced_data and generate_if_missing:
            enhanced_data = self._generate_enhanced_commentary(reference, verses)
            if enhanced_data:
                self._save_enhanced_commentary(reference, enhanced_data)
        
        if not enhanced_data:
            return EnhancedPassage(
                passage=reference,
                verses=verses,
                key_insights=[]
            )
        
        return EnhancedPassage(
            passage=reference,
            verses=verses,
            modern_exegesis=enhanced_data.get("modern_exegesis"),
            church_fathers_wisdom=enhanced_data.get("church_fathers_wisdom"),
            integrated_commentary=enhanced_data.get("integrated_commentary"),
            key_insights=enhanced_data.get("key_insights", [])
        )
    
    def _generate_enhanced_commentary(self, reference: str, verses: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Generate integrated commentary combining modern exegesis and church fathers."""
        try:
            rag = self._get_rag_system()
            ollama = self._get_ollama()
            
            # Get passage text
            passage_text = "\n".join([f"{v}: {t}" for v, t in verses.items()])
            
            # Get church fathers' context
            augustine_context = rag.get_relevant_context(reference, helper="augustine", top_k=3)
            aquinas_context = rag.get_relevant_context(reference, helper="aquinas", top_k=3)
            
            # Generate integrated commentary that combines modern and traditional
            context_text = self._format_context(augustine_context, aquinas_context)
            
            prompt = f"""Provide comprehensive commentary on this Bible passage that integrates:

1. MODERN EXEGESIS: Current scholarly understanding, historical context, literary analysis
2. CHURCH FATHERS' WISDOM: Insights from Augustine, Aquinas, and early church tradition
3. INTEGRATED SYNTHESIS: How modern scholarship and traditional wisdom illuminate each other

Passage: {reference}

Text:
{passage_text}

{context_text}

Provide:
- Modern exegesis (200-300 words): Historical context, literary structure, current scholarship
- Church fathers' wisdom (200-300 words): Insights from Augustine, Aquinas, early tradition
- Integrated synthesis (300-400 words): How modern and traditional perspectives illuminate the passage together
- Key insights (3-5 bullet points): Main takeaways

Format as structured commentary."""
            
            system = """You are a biblical scholar who skillfully integrates modern exegetical scholarship with the wisdom of the church fathers (Augustine, Aquinas, and early Christian tradition). You present both perspectives respectfully and show how they complement each other to reveal deeper meaning."""
            
            commentary = ollama._generate(prompt, system, ollama.default_model)
            
            # Parse the structured response (simplified - in production, use structured output)
            # For now, return as-is and let frontend parse or improve parsing logic
            return {
                "modern_exegesis": self._extract_section(commentary, "MODERN EXEGESIS"),
                "church_fathers_wisdom": self._extract_section(commentary, "CHURCH FATHERS"),
                "integrated_commentary": commentary,  # Full commentary as fallback
                "key_insights": self._extract_key_insights(commentary)
            }
        except Exception as e:
            print(f"Error generating enhanced commentary: {e}")
            return None
    
    def _extract_section(self, text: str, section: str) -> Optional[str]:
        """Extract a section from structured commentary."""
        # Simple extraction - can be improved with better parsing
        lines = text.split("\n")
        in_section = False
        section_lines = []
        
        for line in lines:
            if section.upper() in line.upper():
                in_section = True
                continue
            if in_section:
                if line.strip() and not line.strip().startswith("-"):
                    if any(s.upper() in line.upper() for s in ["CHURCH FATHERS", "INTEGRATED", "KEY INSIGHTS"]):
                        break
                    section_lines.append(line)
        
        return "\n".join(section_lines).strip() if section_lines else None
    
    def _extract_key_insights(self, text: str) -> List[str]:
        """Extract key insights from commentary."""
        insights = []
        lines = text.split("\n")
        in_insights = False
        
        for line in lines:
            if "KEY INSIGHTS" in line.upper() or "KEY TAKEAWAYS" in line.upper():
                in_insights = True
                continue
            if in_insights and line.strip():
                if line.strip().startswith("-") or line.strip().startswith("•"):
                    insights.append(line.strip()[1:].strip())
                elif line.strip() and len(insights) < 5:
                    insights.append(line.strip())
        
        return insights[:5] if insights else []
    
    def _format_context(self, augustine_context: List[Dict], aquinas_context: List[Dict]) -> str:
        """Format context from church fathers."""
        context_parts = []
        
        if augustine_context:
            context_parts.append("From Augustine's writings:")
            for item in augustine_context[:2]:
                snippet = item.get("text", "")[:300]
                context_parts.append(f"- {snippet}")
        
        if aquinas_context:
            context_parts.append("\nFrom Aquinas's writings:")
            for item in aquinas_context[:2]:
                snippet = item.get("text", "")[:300]
                context_parts.append(f"- {snippet}")
        
        return "\n".join(context_parts)
    
    def _load_enhanced_commentary(self, reference: str) -> Optional[Dict[str, Any]]:
        """Load pre-generated enhanced commentary."""
        enhanced_file = self.data_dir / "enhanced_commentary.json"
        if enhanced_file.exists():
            try:
                data = json.loads(enhanced_file.read_text(encoding="utf-8"))
                return data.get(reference)
            except Exception:
                pass
        return None
    
    def _save_enhanced_commentary(self, reference: str, commentary_data: Dict[str, Any]) -> None:
        """Save enhanced commentary for future use."""
        enhanced_file = self.data_dir / "enhanced_commentary.json"
        data = {}
        if enhanced_file.exists():
            try:
                data = json.loads(enhanced_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        data[reference] = commentary_data
        
        try:
            enhanced_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass
    
    def create_enhanced_reading_plan(self, start_date: date = None, passages_per_day: int = 1) -> Dict[str, Any]:
        """Create a reading plan with integrated commentary throughout."""
        if not start_date:
            start_date = date.today()
        
        # Get chronological sequence - build it manually (same as bible_reader)
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
        
        total_chapters = len(sequence)
        
        # Calculate reading schedule
        plan = {
            "name": "Enhanced Bible Reading Plan",
            "description": "Integrated commentary: Modern exegesis + Church fathers' wisdom",
            "start_date": start_date.isoformat(),
            "passages_per_day": passages_per_day,
            "total_days": (total_chapters // passages_per_day) + 1,
            "readings": {}
        }
        
        # Generate plan entries
        current_date = start_date
        passage_index = 0
        
        while passage_index < total_chapters:
            day_key = current_date.isoformat()
            day_passages = []
            
            for _ in range(passages_per_day):
                if passage_index >= total_chapters:
                    break
                
                book, chapter = sequence[passage_index]
                passage_ref = f"{book} {chapter}"
                day_passages.append(passage_ref)
                passage_index += 1
            
            if day_passages:
                plan["readings"][day_key] = {
                    "passages": day_passages,
                    "date": day_key,
                    "enhanced": True  # Mark as enhanced plan
                }
            
            from datetime import timedelta
            current_date += timedelta(days=1)
        
        # Save plan
        try:
            self.enhanced_plan_file.write_text(
                json.dumps(plan, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass
        
        return plan
