"""
Generate condensed Genesis commentaries by synthesizing multiple sources.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .commentary_loader import CommentaryLoader
from .bible_reader import BibleReader
from .rag_system import RAGSystem
from .ollama_client import OllamaClient


class GenesisCommentaryGenerator:
    """Generate condensed Genesis commentaries from multiple sources."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.commentary_dir = self.data_dir / "commentary"
        self.condensed_file = self.data_dir / "genesis_condensed_commentaries.json"
        
        self.loader = CommentaryLoader(self.commentary_dir)
        self.bible_reader: Optional[BibleReader] = None
        self.rag_system: Optional[RAGSystem] = None
        self.ollama_client: Optional[OllamaClient] = None
    
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
    
    def generate_condensed_commentary(
        self,
        chapter: int,
        regenerate: bool = False
    ) -> Optional[str]:
        """Generate or retrieve condensed commentary for a Genesis chapter."""
        # Load existing if available and not regenerating
        if not regenerate:
            existing = self._load_condensed_commentaries()
            if existing and str(chapter) in existing:
                return existing[str(chapter)]
        
        # Generate new commentary
        passage = f"Genesis {chapter}"
        
        # 1. Get passage text
        reader = self._get_bible_reader()
        passage_text_obj = reader.get_passage_text(passage)
        passage_text = passage
        if passage_text_obj and passage_text_obj.get("verses"):
            verses = passage_text_obj["verses"]
            verse_lines = [f"{verse}: {text}" for verse, text in verses.items()]
            passage_text = f"{passage}\n\n" + "\n".join(verse_lines)
        
        # 2. Get external commentaries
        external_commentaries = self.loader.get_commentaries_for_chapter("genesis", chapter)
        external_text = "\n\n---\n\n".join([
            f"From {comm['source']}:\n{comm['content'][:2000]}"
            for comm in external_commentaries[:5]  # Limit to 5 sources
        ])
        
        # 3. Get Augustine commentary
        rag = self._get_rag_system()
        augustine_context = rag.get_relevant_context(passage, helper="augustine", top_k=5)
        augustine_commentary = self._get_ollama_client().generate_commentary(
            passage=passage_text,
            context=augustine_context,
            helper="augustine",
            personalized=False,
        )
        
        # 4. Get Aquinas commentary
        aquinas_context = rag.get_relevant_context(passage, helper="aquinas", top_k=5)
        aquinas_commentary = self._get_ollama_client().generate_commentary(
            passage=passage_text,
            context=aquinas_context,
            helper="aquinas",
            personalized=False,
        )
        
        # 5. Synthesize into condensed commentary
        synthesis_prompt = f"""Synthesize a condensed, comprehensive commentary on {passage} by integrating insights from multiple sources:

BIBLE TEXT:
{passage_text[:2000]}

EXTERNAL COMMENTARIES:
{external_text[:3000]}

AUGUSTINE'S COMMENTARY:
{augustine_commentary[:1500]}

AQUINAS'S COMMENTARY:
{aquinas_commentary[:1500]}

Create a unified, condensed commentary that:
1. Preserves the most important insights from each source
2. Identifies any new connections or insights that emerge from combining these perspectives
3. Maintains theological depth while being accessible
4. Organizes thoughts clearly with clear structure
5. Highlights key themes, interpretations, and applications

Write as a comprehensive but condensed commentary (aim for 800-1200 words) that synthesizes all these perspectives into a coherent whole."""

        system_prompt = (
            "You are a theological scholar synthesizing insights from multiple authoritative "
            "commentaries on Genesis. Your task is to create a unified, condensed commentary "
            "that preserves the best insights from each source while identifying new connections "
            "and deeper meanings that emerge from their combination. Write with clarity, depth, "
            "and theological precision."
        )
        
        # Use higher token limit for synthesis
        ollama = self._get_ollama_client()
        # Temporarily increase num_predict for synthesis
        original_num_predict = 1500
        # Create a custom payload with higher token limit
        payload = {
            "model": ollama.default_model,
            "system": system_prompt,
            "prompt": synthesis_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2500,  # Higher limit for synthesis
            },
        }
        response = ollama._post("/api/generate", payload)
        condensed = response.get("response", "Unable to generate a response at this time.")
        
        # Save to cache
        self._save_condensed_commentary(chapter, condensed)
        
        return condensed
    
    def _load_condensed_commentaries(self) -> Dict[str, str]:
        """Load cached condensed commentaries."""
        if self.condensed_file.exists():
            try:
                return json.loads(self.condensed_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}
    
    def _save_condensed_commentary(self, chapter: int, commentary: str) -> None:
        """Save condensed commentary to cache."""
        existing = self._load_condensed_commentaries()
        existing[str(chapter)] = commentary
        self.condensed_file.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def get_all_chapters(self) -> List[int]:
        """Get list of all Genesis chapters (1-50)."""
        return list(range(1, 51))
    
    def get_condensed_commentary(self, chapter: int) -> Optional[str]:
        """Get condensed commentary for a chapter (from cache or generate)."""
        existing = self._load_condensed_commentaries()
        if str(chapter) in existing:
            return existing[str(chapter)]
        return None
