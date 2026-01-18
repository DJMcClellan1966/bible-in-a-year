"""
Narrative Reconstruction Engine.
Reconstructs complete Bible stories across multiple books with timelines and commentary.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .bible_reader import BibleReader
from .ollama_client import OllamaClient


@dataclass
class StorySegment:
    """A segment of a biblical story."""
    passage: str
    book: str
    chapter: int
    verses: Optional[str]
    narrative_order: int
    text: str


@dataclass
class BiblicalStory:
    """A complete biblical story reconstructed from multiple passages."""
    name: str
    description: str
    segments: List[StorySegment]
    timeline: List[Dict[str, Any]]
    connecting_commentary: str
    key_characters: List[str]
    themes: List[str]


class NarrativeEngine:
    """Reconstructs biblical stories across multiple books."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.stories_dir = self.data_dir / "stories"
        self.stories_dir.mkdir(parents=True, exist_ok=True)
        
        self.stories_file = self.data_dir / "biblical_stories.json"
        self.bible_reader: Optional[BibleReader] = None
        self.ollama_client: Optional[OllamaClient] = None
    
    def _get_bible_reader(self) -> BibleReader:
        if self.bible_reader is None:
            self.bible_reader = BibleReader()
        return self.bible_reader
    
    def _get_ollama(self) -> OllamaClient:
        if self.ollama_client is None:
            self.ollama_client = OllamaClient()
        return self.ollama_client
    
    def reconstruct_story(self, story_name: str, passages: List[str]) -> BiblicalStory:
        """Reconstruct a complete story from multiple passages."""
        segments = []
        
        for i, passage in enumerate(passages):
            # Load passage text
            text_obj = self._get_bible_reader().get_passage_text(passage)
            book, chapter, verses = self._parse_reference(passage)
            
            text = ""
            if text_obj and text_obj.get("verses"):
                verse_texts = [f"{v}: {t}" for v, t in text_obj["verses"].items()]
                text = " ".join(verse_texts)
            
            segments.append(StorySegment(
                passage=passage,
                book=book,
                chapter=chapter,
                verses=verses,
                narrative_order=i,
                text=text
            ))
        
        # Generate connecting commentary
        connecting_commentary = self._generate_connecting_commentary(segments)
        
        # Extract key characters
        key_characters = self._extract_characters(segments)
        
        # Extract themes
        themes = self._extract_themes(segments)
        
        # Build timeline
        timeline = self._build_timeline(segments)
        
        return BiblicalStory(
            name=story_name,
            description=f"Complete narrative of {story_name} reconstructed from {len(segments)} passages",
            segments=segments,
            timeline=timeline,
            connecting_commentary=connecting_commentary,
            key_characters=key_characters,
            themes=themes
        )
    
    def get_predefined_story(self, story_id: str) -> Optional[BiblicalStory]:
        """Get a predefined biblical story."""
        stories = self._load_story_definitions()
        story_def = stories.get(story_id)
        
        if not story_def:
            return None
        
        return self.reconstruct_story(
            story_def["name"],
            story_def["passages"]
        )
    
    def list_available_stories(self) -> List[Dict[str, Any]]:
        """List all available predefined stories."""
        stories = self._load_story_definitions()
        return [
            {
                "id": story_id,
                "name": story_def["name"],
                "description": story_def.get("description", ""),
                "passage_count": len(story_def.get("passages", []))
            }
            for story_id, story_def in stories.items()
        ]
    
    def _load_story_definitions(self) -> Dict[str, Any]:
        """Load predefined story definitions."""
        if self.stories_file.exists():
            try:
                return json.loads(self.stories_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        # Default stories
        default_stories = {
            "abraham_journey": {
                "name": "Abraham's Journey",
                "description": "The complete journey of Abraham from Ur to Canaan",
                "passages": [
                    "Genesis 12", "Genesis 13", "Genesis 14", "Genesis 15", "Genesis 16",
                    "Genesis 17", "Genesis 18", "Genesis 19", "Genesis 20", "Genesis 21",
                    "Genesis 22", "Genesis 23", "Genesis 24", "Genesis 25:1-18"
                ]
            },
            "joseph_story": {
                "name": "Joseph's Story",
                "description": "The story of Joseph from favored son to Egyptian ruler",
                "passages": [
                    "Genesis 37", "Genesis 39", "Genesis 40", "Genesis 41",
                    "Genesis 42", "Genesis 43", "Genesis 44", "Genesis 45",
                    "Genesis 46", "Genesis 47", "Genesis 48", "Genesis 49", "Genesis 50"
                ]
            },
            "jesus_last_week": {
                "name": "Jesus' Last Week",
                "description": "The final week of Jesus' earthly ministry (all 4 Gospels)",
                "passages": [
                    "Matthew 21", "Matthew 22", "Matthew 23", "Matthew 24",
                    "Matthew 25", "Matthew 26", "Matthew 27", "Matthew 28",
                    "Mark 11", "Mark 12", "Mark 13", "Mark 14", "Mark 15", "Mark 16",
                    "Luke 19", "Luke 20", "Luke 21", "Luke 22", "Luke 23", "Luke 24",
                    "John 12", "John 13", "John 14", "John 15", "John 16",
                    "John 17", "John 18", "John 19", "John 20", "John 21"
                ]
            }
        }
        
        self.stories_file.write_text(
            json.dumps(default_stories, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return default_stories
    
    def _generate_connecting_commentary(self, segments: List[StorySegment]) -> str:
        """Generate commentary connecting the story segments."""
        ollama = self._get_ollama()
        
        segment_texts = "\n\n---\n\n".join([
            f"{seg.passage}:\n{seg.text[:500]}"
            for seg in segments[:10]  # Limit for performance
        ])
        
        prompt = f"""These are passages from a biblical story. Write a connecting commentary that:
1. Shows how these passages form a cohesive narrative
2. Highlights key transitions and turning points
3. Identifies recurring themes
4. Explains the overall arc and meaning

Passages:
{segment_texts}

Write 300-500 words of connecting commentary."""
        
        system = "You are a biblical scholar providing narrative commentary that connects passages into a coherent story."
        
        response = ollama._generate(prompt, system, ollama.default_model)
        return response[:2000]  # Limit length
    
    def _extract_characters(self, segments: List[StorySegment]) -> List[str]:
        """Extract key characters from story segments."""
        # Simple extraction - could be enhanced with AI
        characters = set()
        common_names = ["Abraham", "Sarah", "Isaac", "Jacob", "Joseph", "Jesus", "Peter", "Paul"]
        
        all_text = " ".join([seg.text for seg in segments])
        for name in common_names:
            if name in all_text:
                characters.add(name)
        
        return sorted(list(characters))[:10]
    
    def _extract_themes(self, segments: List[StorySegment]) -> List[str]:
        """Extract themes from story segments."""
        ollama = self._get_ollama()
        
        combined_text = "\n".join([seg.text[:300] for seg in segments[:5]])
        prompt = f"Extract 3-5 main themes from this biblical narrative as a JSON array:\n\n{combined_text}"
        system = "Extract themes as a JSON array of strings."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        return ["Faith", "Promise", "Providence"]
    
    def _build_timeline(self, segments: List[StorySegment]) -> List[Dict[str, Any]]:
        """Build timeline of story events."""
        timeline = []
        for seg in segments:
            timeline.append({
                "order": seg.narrative_order,
                "passage": seg.passage,
                "book": seg.book,
                "chapter": seg.chapter,
                "summary": seg.text[:100] + "..."
            })
        return timeline
    
    def _parse_reference(self, reference: str) -> Tuple[str, int, str]:
        """Parse Bible reference."""
        import re
        match = re.match(r"(\w+(?:\s+\w+)?)\s+(\d+)(?::(\d+(?:-\d+)?))?", reference)
        if match:
            return match.group(1), int(match.group(2)), match.group(3) or ""
        return "", 0, ""
    
    def save_story(self, story: BiblicalStory) -> Path:
        """Save a reconstructed story."""
        filepath = self.stories_dir / f"{story.name.lower().replace(' ', '_')}.json"
        
        story_dict = {
            "name": story.name,
            "description": story.description,
            "segments": [
                {
                    "passage": seg.passage,
                    "book": seg.book,
                    "chapter": seg.chapter,
                    "verses": seg.verses,
                    "narrative_order": seg.narrative_order,
                    "text": seg.text
                }
                for seg in story.segments
            ],
            "timeline": story.timeline,
            "connecting_commentary": story.connecting_commentary,
            "key_characters": story.key_characters,
            "themes": story.themes
        }
        
        filepath.write_text(
            json.dumps(story_dict, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        return filepath
