"""
Core AI system to model Bible data into coherent form using different data types.
Extracts and builds robust commentary with web data integration.
"""

import json
import re
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .bible_reader import BibleReader
from .rag_system import RAGSystem
from .ollama_client import OllamaClient
from .commentary_loader import CommentaryLoader


@dataclass
class VerseData:
    """Structured data for a single verse."""
    reference: str
    text: str
    chapter: int
    verse: int
    book: str


@dataclass
class PassageData:
    """Structured data for a Bible passage."""
    reference: str
    verses: List[VerseData]
    full_text: str
    theme: Optional[str] = None
    context: Optional[str] = None


@dataclass
class CommentaryData:
    """Structured commentary data from multiple sources."""
    passage: str
    external_commentaries: List[Dict[str, Any]]
    augustine_commentary: str
    aquinas_commentary: str
    web_data: List[Dict[str, Any]]
    synthesized_commentary: str
    key_insights: List[str]
    theological_themes: List[str]


@dataclass
class DailySummary:
    """Daily summary in verse-like format."""
    date: str
    passage: str
    summary_verse: str  # Condensed summary in verse-like format
    key_message: str
    reflection: str
    application: str


@dataclass
class DailyReadingCorpus:
    """Complete corpus for a daily reading."""
    date: str
    passage_data: PassageData
    commentary_data: CommentaryData
    daily_summary: DailySummary
    metadata: Dict[str, Any]


class BibleDataModeler:
    """Core AI system to model Bible data into coherent form."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.corpus_dir = self.data_dir / "genesis_corpus"
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        
        self.bible_reader: Optional[BibleReader] = None
        self.rag_system: Optional[RAGSystem] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.commentary_loader: Optional[CommentaryLoader] = None
    
    def _get_bible_reader(self) -> BibleReader:
        if self.bible_reader is None:
            self.bible_reader = BibleReader()
        return self.bible_reader
    
    def _get_rag_system(self) -> RAGSystem:
        if self.rag_system is None:
            self.rag_system = RAGSystem()
            self.rag_system.initialize_default_data()
        return self.rag_system
    
    def _get_ollama_client(self) -> OllamaClient:
        if self.ollama_client is None:
            self.ollama_client = OllamaClient()
        return self.ollama_client
    
    def _get_commentary_loader(self) -> CommentaryLoader:
        if self.commentary_loader is None:
            self.commentary_loader = CommentaryLoader()
        return self.commentary_loader
    
    def model_passage_data(self, passage: str) -> PassageData:
        """Model a Bible passage into structured data."""
        reader = self._get_bible_reader()
        
        # Ensure passage format is correct (e.g., "Genesis 1" not just "Genesis 1:")
        passage_clean = passage.strip()
        if not passage_clean:
            raise ValueError(f"Empty passage reference")
        
        # Try multiple formats and versions
        passage_text_obj = None
        
        # Try as-is first (from JSON)
        passage_text_obj = reader.get_passage_text(passage_clean)
        
        # If that fails, try loading from HTML source files (if available)
        if not passage_text_obj or not passage_text_obj.get("verses"):
            # Get available versions
            versions = reader.get_available_versions()
            for version in versions[:3]:  # Try first 3 versions
                try:
                    passage_text_obj = reader.get_passage_text(passage_clean, version=version)
                    if passage_text_obj and passage_text_obj.get("verses"):
                        break
                except Exception:
                    continue
        
        if not passage_text_obj or not passage_text_obj.get("verses"):
            # Last resort: create a minimal passage data structure
            book, chapter, _ = self._parse_reference(passage_clean)
            
            # Check what chapters are available for Genesis
            available_info = ""
            if reader.bible_text and reader.bible_text.get('books', {}).get(book):
                book_data = reader.bible_text['books'][book]
                available_chapters = list(book_data.get('chapters', {}).keys())[:10]
                available_info = f" Available chapters for {book}: {available_chapters}"
            
            raise ValueError(
                f"Could not load passage: {passage_clean}. "
                f"Book: {book}, Chapter: {chapter}.{available_info}"
            )
        
        # Parse reference
        book, chapter, verse_range = self._parse_reference(passage)
        
        # Extract verses
        verses_data = []
        verses_dict = passage_text_obj["verses"]
        full_text_parts = []
        
        for verse_num, text in verses_dict.items():
            verse_obj = VerseData(
                reference=f"{book} {chapter}:{verse_num}",
                text=text,
                chapter=chapter,
                verse=int(verse_num) if verse_num.isdigit() else 0,
                book=book
            )
            verses_data.append(verse_obj)
            full_text_parts.append(f"{verse_num} {text}")
        
        full_text = " ".join(full_text_parts)
        
        # Extract theme using AI
        theme = self._extract_theme(full_text, passage)
        
        return PassageData(
            reference=passage,
            verses=verses_data,
            full_text=full_text,
            theme=theme,
            context=self._extract_context(passage, book, chapter)
        )
    
    def model_commentary_data(
        self,
        passage: str,
        passage_data: PassageData,
        web_data: List[Dict[str, Any]]
    ) -> CommentaryData:
        """Model commentary data from multiple sources."""
        loader = self._get_commentary_loader()
        rag = self._get_rag_system()
        ollama = self._get_ollama_client()
        
        # Get external commentaries
        book, chapter, _ = self._parse_reference(passage)
        external_commentaries = loader.get_commentaries_for_chapter(book.lower(), chapter)
        
        # Get Augustine commentary
        print(f"    → Generating Augustine commentary...")
        augustine_context = rag.get_relevant_context(passage, helper="augustine", top_k=5)
        augustine_commentary = ollama.generate_commentary(
            passage=passage_data.full_text,
            context=augustine_context,
            helper="augustine",
            personalized=False,
        )
        
        # Get Aquinas commentary
        print(f"    → Generating Aquinas commentary...")
        aquinas_context = rag.get_relevant_context(passage, helper="aquinas", top_k=5)
        aquinas_commentary = ollama.generate_commentary(
            passage=passage_data.full_text,
            context=aquinas_context,
            helper="aquinas",
            personalized=False,
        )
        
        # Synthesize comprehensive commentary
        print(f"    → Synthesizing comprehensive commentary...")
        synthesized = self._synthesize_commentary(
            passage_data,
            external_commentaries,
            augustine_commentary,
            aquinas_commentary,
            web_data
        )
        
        # Extract key insights and themes
        print(f"    → Extracting insights and themes...")
        key_insights = self._extract_key_insights(synthesized)
        theological_themes = self._extract_theological_themes(synthesized, passage_data)
        
        return CommentaryData(
            passage=passage,
            external_commentaries=external_commentaries,
            augustine_commentary=augustine_commentary,
            aquinas_commentary=aquinas_commentary,
            web_data=web_data,
            synthesized_commentary=synthesized,
            key_insights=key_insights,
            theological_themes=theological_themes
        )
    
    def generate_daily_summary(
        self,
        passage_data: PassageData,
        commentary_data: CommentaryData,
        reading_date: date
    ) -> DailySummary:
        """Generate a daily summary in verse-like format."""
        print(f"    → Generating daily summary...")
        ollama = self._get_ollama_client()
        
        prompt = f"""Create a daily summary for {passage_data.reference} in the style of a Bible verse.

PASSAGE TEXT:
{passage_data.full_text[:1000]}

KEY INSIGHTS:
{chr(10).join(commentary_data.key_insights[:5])}

THEOLOGICAL THEMES:
{chr(10).join(commentary_data.theological_themes[:3])}

Create:
1. A summary verse (1-2 sentences, poetic and profound, like a Bible verse)
2. A key message (one clear sentence)
3. A reflection (2-3 sentences for meditation)
4. An application (one practical sentence for daily life)

Format as JSON:
{{
    "summary_verse": "...",
    "key_message": "...",
    "reflection": "...",
    "application": "..."
}}"""

        system_prompt = (
            "You are creating daily Bible reading summaries. Write in a style that is "
            "profound, poetic, and spiritually enriching. The summary verse should read "
            "like it could be in the Bible itself—concise, meaningful, and beautiful."
        )
        
        response = ollama._generate(
            prompt=prompt,
            system=system_prompt,
            model=ollama.default_model
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response (might have extra text)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                summary_dict = json.loads(json_match.group())
            else:
                # Fallback: try to parse whole response
                summary_dict = json.loads(response)
        except Exception:
            # Fallback: create basic summary
            summary_dict = {
                "summary_verse": f"In {passage_data.reference}, we see God's wisdom revealed.",
                "key_message": passage_data.theme or "God's word speaks to us today.",
                "reflection": "Take time to meditate on this passage and its meaning for your life.",
                "application": "Apply the wisdom of this passage to your daily walk with God."
            }
        
        return DailySummary(
            date=reading_date.isoformat(),
            passage=passage_data.reference,
            summary_verse=summary_dict.get("summary_verse", ""),
            key_message=summary_dict.get("key_message", ""),
            reflection=summary_dict.get("reflection", ""),
            application=summary_dict.get("application", "")
        )
    
    def build_complete_corpus(
        self,
        passage: str,
        reading_date: date,
        web_data: Optional[List[Dict[str, Any]]] = None
    ) -> DailyReadingCorpus:
        """Build complete corpus for a daily reading."""
        if web_data is None:
            web_data = []
        
        # Model passage data
        passage_data = self.model_passage_data(passage)
        
        # Model commentary data
        commentary_data = self.model_commentary_data(passage, passage_data, web_data)
        
        # Generate daily summary
        daily_summary = self.generate_daily_summary(passage_data, commentary_data, reading_date)
        
        # Create metadata
        metadata = {
            "generated_date": date.today().isoformat(),
            "reading_date": reading_date.isoformat(),
            "passage": passage,
            "sources_count": len(commentary_data.external_commentaries) + len(web_data),
            "version": "1.0"
        }
        
        return DailyReadingCorpus(
            date=reading_date.isoformat(),
            passage_data=passage_data,
            commentary_data=commentary_data,
            daily_summary=daily_summary,
            metadata=metadata
        )
    
    def save_corpus(self, corpus: DailyReadingCorpus, chapter: Optional[int] = None) -> Path:
        """Save corpus to file."""
        # Organize by chapter if provided
        if chapter:
            chapter_dir = self.corpus_dir / f"chapter_{chapter}"
            chapter_dir.mkdir(exist_ok=True)
            filename = f"{corpus.date}_{corpus.passage_data.reference.replace(' ', '_')}.json"
            filepath = chapter_dir / filename
        else:
            filename = f"{corpus.date}_{corpus.passage_data.reference.replace(' ', '_')}.json"
            filepath = self.corpus_dir / filename
        
        # Convert to dict (handling dataclasses)
        corpus_dict = self._corpus_to_dict(corpus)
        
        filepath.write_text(
            json.dumps(corpus_dict, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        return filepath
    
    def load_corpus(self, date_str: str, passage: str) -> Optional[DailyReadingCorpus]:
        """Load corpus from file."""
        filename = f"{date_str}_{passage.replace(' ', '_')}.json"
        
        # Try to find in any chapter directory
        for chapter_dir in self.corpus_dir.glob("chapter_*"):
            filepath = chapter_dir / filename
            if filepath.exists():
                return self._load_corpus_from_file(filepath)
        
        # Try root corpus directory
        filepath = self.corpus_dir / filename
        if filepath.exists():
            return self._load_corpus_from_file(filepath)
        
        return None
    
    def _parse_reference(self, reference: str) -> Tuple[str, int, str]:
        """Parse Bible reference into book, chapter, verse range."""
        # Pattern: "Book Chapter:Verse-Verse" or "Book Chapter"
        match = re.match(r"(\w+)\s+(\d+)(?::(\d+(?:-\d+)?))?", reference)
        if not match:
            raise ValueError(f"Invalid reference format: {reference}")
        
        book = match.group(1)
        chapter = int(match.group(2))
        verse_range = match.group(3) if match.group(3) else ""
        
        return book, chapter, verse_range
    
    def _extract_theme(self, text: str, passage: str) -> str:
        """Extract theme from passage text."""
        ollama = self._get_ollama_client()
        prompt = f"Extract the main theme of this Bible passage in one sentence:\n\n{text[:500]}"
        system = "You are a Bible scholar. Extract the core theme concisely."
        theme = ollama._generate(prompt, system, ollama.default_model)
        return theme.strip()[:200]  # Limit length
    
    def _extract_context(self, passage: str, book: str, chapter: int) -> str:
        """Extract context about the passage."""
        return f"This passage is from {book} chapter {chapter}, part of the broader narrative of the book."
    
    def _synthesize_commentary(
        self,
        passage_data: PassageData,
        external_commentaries: List[Dict[str, Any]],
        augustine: str,
        aquinas: str,
        web_data: List[Dict[str, Any]]
    ) -> str:
        """Synthesize comprehensive commentary from all sources."""
        ollama = self._get_ollama_client()
        
        # Safely extract text from external commentaries
        external_text_parts = []
        for c in external_commentaries[:5]:
            if isinstance(c, dict):
                source = c.get('source', 'Unknown')
                content = c.get('content', '')
                if isinstance(content, str):
                    external_text_parts.append(f"From {source}:\n{content[:1500]}")
                elif isinstance(content, dict):
                    # Try to extract text from nested structure
                    content_str = str(content)
                    external_text_parts.append(f"From {source}:\n{content_str[:1500]}")
        external_text = "\n\n---\n\n".join(external_text_parts)
        
        # Safely extract text from web data
        web_text_parts = []
        for w in web_data[:3]:
            if isinstance(w, dict):
                source = w.get('source', 'Web')
                content = w.get('content', '')
                if isinstance(content, str):
                    web_text_parts.append(f"From {source}:\n{content[:1000]}")
        web_text = "\n\n---\n\n".join(web_text_parts)
        
        prompt = f"""Synthesize a comprehensive, robust commentary on {passage_data.reference}:

BIBLE TEXT:
{passage_data.full_text[:1500]}

EXTERNAL COMMENTARIES:
{external_text[:2000]}

AUGUSTINE'S COMMENTARY:
{augustine[:1500]}

AQUINAS'S COMMENTARY:
{aquinas[:1500]}

WEB DATA:
{web_text[:1500]}

Create a unified, comprehensive commentary that:
1. Integrates insights from all sources seamlessly
2. Identifies new connections and deeper meanings
3. Maintains theological depth and accuracy
4. Is well-organized and accessible
5. Highlights key themes, interpretations, and applications

Write a complete, robust commentary (1500-2000 words) that synthesizes all perspectives."""
        
        system = (
            "You are a master theological scholar synthesizing insights from multiple "
            "authoritative sources. Create comprehensive, robust commentaries that integrate "
            "all perspectives into a coherent, insightful whole."
        )
        
        payload = {
            "model": ollama.default_model,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 3000,  # Higher limit for comprehensive commentary
            },
        }
        
        response = ollama._post("/api/generate", payload)
        return response.get("response", "Unable to generate commentary.")
    
    def _extract_key_insights(self, commentary: str) -> List[str]:
        """Extract key insights from commentary."""
        ollama = self._get_ollama_client()
        prompt = f"Extract 5 key insights from this commentary as a JSON array:\n\n{commentary[:2000]}"
        system = "Extract key insights as a JSON array of strings."
        response = ollama._generate(prompt, system, ollama.default_model)
        
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # Fallback: simple extraction
        sentences = re.split(r'[.!?]+', commentary)
        return [s.strip() for s in sentences[:5] if len(s.strip()) > 20]
    
    def _extract_theological_themes(self, commentary: str, passage_data: PassageData) -> List[str]:
        """Extract theological themes."""
        ollama = self._get_ollama_client()
        prompt = f"Extract 3-5 theological themes from this passage and commentary:\n\n{passage_data.full_text[:500]}\n\n{commentary[:1000]}"
        system = "Extract theological themes as a JSON array of strings."
        response = ollama._generate(prompt, system, ollama.default_model)
        
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        return ["Divine revelation", "Human nature", "Covenant relationship"]
    
    def _corpus_to_dict(self, corpus: DailyReadingCorpus) -> Dict[str, Any]:
        """Convert corpus dataclass to dictionary."""
        def convert_value(v):
            if hasattr(v, '__dict__'):
                return asdict(v) if hasattr(v, '__dataclass_fields__') else str(v)
            elif isinstance(v, list):
                return [convert_value(item) for item in v]
            elif isinstance(v, dict):
                return {k: convert_value(val) for k, val in v.items()}
            return v
        
        result = {}
        for field, value in corpus.__dict__.items():
            try:
                result[field] = convert_value(value)
            except Exception as e:
                # If conversion fails, try asdict directly for dataclasses
                try:
                    if hasattr(value, '__dataclass_fields__'):
                        result[field] = asdict(value)
                    else:
                        result[field] = str(value)
                except Exception:
                    result[field] = str(value)
        return result
    
    def _load_corpus_from_file(self, filepath: Path) -> DailyReadingCorpus:
        """Load corpus from JSON file."""
        data = json.loads(filepath.read_text(encoding="utf-8"))
        
        # Reconstruct dataclasses (simplified - would need full reconstruction)
        # For now, return as dict-like object
        return data
