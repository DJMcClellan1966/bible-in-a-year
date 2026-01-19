"""
AI Character Bible - Tells the Bible story from each character's unique perspective.
Each character narrates events they witnessed or were part of in their own voice.
"""

import json
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bible_reader import BibleReader
from .character_study import CharacterStudySystem
from .ollama_client import OllamaClient
from .rag_system import RAGSystem


@dataclass
class CharacterNarrative:
    """A narrative segment from a character's perspective."""
    character: str
    passage: str
    narrative_text: str
    perspective: str  # What makes this character's view unique
    emotional_tone: str
    key_insights: List[str]


@dataclass
class CharacterBibleChapter:
    """A chapter of the Bible told from a character's perspective."""
    character: str
    book: str
    chapter: int
    title: str
    narrative: str
    character_thoughts: str
    connections: List[str]  # Other passages this character appears in
    timeline_context: str


class CharacterBible:
    """Generates Bible narratives from character perspectives."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.character_bible_dir = self.data_dir / "character_bible"
        self.character_bible_dir.mkdir(parents=True, exist_ok=True)
        
        self.bible_reader: Optional[BibleReader] = None
        self.character_study: Optional[CharacterStudySystem] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.rag_system: Optional[RAGSystem] = None
    
    def _get_bible_reader(self) -> BibleReader:
        if self.bible_reader is None:
            self.bible_reader = BibleReader()
        return self.bible_reader
    
    def _get_character_study(self) -> CharacterStudySystem:
        if self.character_study is None:
            self.character_study = CharacterStudySystem()
        return self.character_study
    
    def _get_ollama(self) -> OllamaClient:
        if self.ollama_client is None:
            self.ollama_client = OllamaClient()
        return self.ollama_client
    
    def _get_rag(self) -> RAGSystem:
        if self.rag_system is None:
            self.rag_system = RAGSystem()
            if not self.rag_system._has_cached_data():
                self.rag_system.initialize_default_data()
        return self.rag_system
    
    def get_character_perspective(
        self,
        character: str,
        passage: str,
        use_cache: bool = True
    ) -> CharacterNarrative:
        """Get a character's unique perspective on a Bible passage."""
        # Check cache
        cache_file = self.character_bible_dir / f"{character}_{passage.replace(' ', '_').replace(':', '_')}.json"
        if use_cache and cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                return CharacterNarrative(**data)
            except Exception:
                pass
        
        # Get character profile
        character_profile = self._get_character_study().get_character_profile(character)
        if not character_profile:
            # Try to find character by partial name
            all_characters = self._get_character_study().get_all_characters()
            matching = [c for c in all_characters if character.lower() in c.get("name", "").lower()]
            if matching:
                character_profile = self._get_character_study().get_character_profile(matching[0]["id"])
        
        # Get passage text
        passage_text_obj = self._get_bible_reader().get_passage_text(passage)
        passage_text = ""
        if passage_text_obj and passage_text_obj.get("verses"):
            verse_texts = [f"{v}: {t}" for v, t in passage_text_obj["verses"].items()]
            passage_text = " ".join(verse_texts)
        
        # Get character's other appearances
        character_passages = self._get_character_study().get_characters_for_passage(passage)
        character_in_passage = any(
            c.get("id") == character or character.lower() in c.get("name", "").lower()
            for c in character_passages
        )
        
        # Build character context
        character_context = self._build_character_context(character, character_profile)
        
        # Generate narrative from character's perspective
        narrative = self._generate_character_narrative(
            character=character,
            passage=passage,
            passage_text=passage_text,
            character_context=character_context,
            character_in_passage=character_in_passage
        )
        
        result = CharacterNarrative(
            character=character,
            passage=passage,
            narrative_text=narrative["narrative"],
            perspective=narrative["perspective"],
            emotional_tone=narrative["emotional_tone"],
            key_insights=narrative["insights"]
        )
        
        # Cache result
        try:
            cache_file.write_text(
                json.dumps(asdict(result), indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass
        
        return result
    
    def get_character_bible_chapter(
        self,
        character: str,
        book: str,
        chapter: int,
        use_cache: bool = True
    ) -> CharacterBibleChapter:
        """Get a full chapter from a character's perspective."""
        passage = f"{book} {chapter}"
        
        # Check cache
        cache_file = self.character_bible_dir / f"{character}_{book}_{chapter}.json"
        if use_cache and cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                return CharacterBibleChapter(**data)
            except Exception:
                pass
        
        # Get passage text
        passage_text_obj = self._get_bible_reader().get_passage_text(passage)
        passage_text = ""
        if passage_text_obj and passage_text_obj.get("verses"):
            verse_texts = [f"{v}: {t}" for v, t in passage_text_obj["verses"].items()]
            passage_text = " ".join(verse_texts)
        
        # Get character profile
        character_profile = self._get_character_study().get_character_profile(character)
        character_context = self._build_character_context(character, character_profile)
        
        # Get all passages where this character appears
        all_characters = self._get_character_study().get_all_characters()
        character_id = None
        for c in all_characters:
            if character.lower() in c.get("name", "").lower() or c.get("id") == character:
                character_id = c.get("id")
                break
        
        connections = []
        if character_id:
            # Get character's arc to find related passages
            arc = self._get_character_study().get_character_arc(character_id)
            if arc and arc.get("key_passages"):
                connections = [p for p in arc["key_passages"] if p != passage][:5]
        
        # Generate chapter narrative
        narrative_data = self._generate_chapter_narrative(
            character=character,
            book=book,
            chapter=chapter,
            passage_text=passage_text,
            character_context=character_context,
            connections=connections
        )
        
        result = CharacterBibleChapter(
            character=character,
            book=book,
            chapter=chapter,
            title=narrative_data["title"],
            narrative=narrative_data["narrative"],
            character_thoughts=narrative_data["thoughts"],
            connections=connections,
            timeline_context=narrative_data["timeline"]
        )
        
        # Cache result
        try:
            cache_file.write_text(
                json.dumps(asdict(result), indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass
        
        return result
    
    def get_characters_for_book(self, book: str) -> List[Dict[str, Any]]:
        """Get all characters who appear in a book."""
        all_characters = self._get_character_study().get_all_characters()
        book_characters = []
        
        for char in all_characters:
            arc = self._get_character_study().get_character_arc(char.get("id"))
            if arc and arc.get("key_passages"):
                # Check if any passage is from this book
                for passage in arc["key_passages"]:
                    if passage.startswith(book):
                        book_characters.append({
                            "id": char.get("id"),
                            "name": char.get("name"),
                            "description": char.get("description", ""),
                            "passage_count": len([p for p in arc["key_passages"] if p.startswith(book)])
                        })
                        break
        
        return book_characters
    
    def _build_character_context(self, character: str, profile: Optional[Dict[str, Any]]) -> str:
        """Build context about a character for narrative generation."""
        if not profile:
            return f"{character} is a biblical character."
        
        context_parts = [f"{profile.get('name', character)}"]
        
        if profile.get("description"):
            context_parts.append(f"Description: {profile['description']}")
        
        if profile.get("role"):
            context_parts.append(f"Role: {profile['role']}")
        
        if profile.get("key_traits"):
            context_parts.append(f"Key traits: {', '.join(profile['key_traits'][:5])}")
        
        if profile.get("background"):
            context_parts.append(f"Background: {profile['background']}")
        
        return "\n".join(context_parts)
    
    def _generate_character_narrative(
        self,
        character: str,
        passage: str,
        passage_text: str,
        character_context: str,
        character_in_passage: bool
    ) -> Dict[str, Any]:
        """Generate narrative from character's perspective using AI."""
        ollama = self._get_ollama()
        
        if character_in_passage:
            prompt = f"""You are {character}, a biblical character. Tell this Bible passage from YOUR perspective, as if you were there experiencing it.

CHARACTER CONTEXT:
{character_context}

BIBLE PASSAGE ({passage}):
{passage_text}

Write a first-person narrative from {character}'s perspective. Include:
1. What you saw, heard, and felt
2. Your thoughts and reactions
3. What this event meant to you personally
4. How it affected your life or faith

Write in a natural, personal voice - as if {character} is telling their own story."""
        else:
            prompt = f"""You are {character}, a biblical character. Reflect on this Bible passage from YOUR unique perspective, even if you weren't directly present.

CHARACTER CONTEXT:
{character_context}

BIBLE PASSAGE ({passage}):
{passage_text}

Write a reflection from {character}'s perspective. Consider:
1. How would {character} understand this passage?
2. What connections would {character} see to their own life?
3. What wisdom or insight would {character} offer?
4. How does this relate to {character}'s experiences?

Write in {character}'s voice and style."""
        
        system_prompt = f"""You are {character}, a biblical character. Write in first person, using {character}'s unique voice, perspective, and experiences. Be authentic to their character, time period, and role in biblical history."""
        
        narrative_text = ollama._generate(
            prompt=prompt,
            system=system_prompt,
            model=ollama.default_model
        )
        
        # Extract perspective and insights
        analysis_prompt = f"""Analyze this narrative from {character}'s perspective:

NARRATIVE:
{narrative_text}

Provide:
1. What makes {character}'s perspective unique (one sentence)
2. The emotional tone (e.g., hopeful, fearful, joyful, reflective)
3. Three key insights {character} offers (bullet points)

Format as JSON:
{{
  "perspective": "...",
  "emotional_tone": "...",
  "insights": ["...", "...", "..."]
}}"""
        
        try:
            analysis = ollama._generate(
                prompt=analysis_prompt,
                system="You are a literary analyst. Provide structured analysis in JSON format.",
                model=ollama.default_model
            )
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', analysis, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                return {
                    "narrative": narrative_text,
                    "perspective": analysis_data.get("perspective", f"{character}'s unique viewpoint"),
                    "emotional_tone": analysis_data.get("emotional_tone", "reflective"),
                    "insights": analysis_data.get("insights", [])
                }
        except Exception:
            pass
        
        return {
            "narrative": narrative_text,
            "perspective": f"{character}'s unique viewpoint on this passage",
            "emotional_tone": "reflective",
            "insights": [
                f"{character}'s perspective on this event",
                "Personal connection to the passage",
                "Spiritual or practical insight"
            ]
        }
    
    def _generate_chapter_narrative(
        self,
        character: str,
        book: str,
        chapter: int,
        passage_text: str,
        character_context: str,
        connections: List[str]
    ) -> Dict[str, Any]:
        """Generate a full chapter narrative from character's perspective."""
        ollama = self._get_ollama()
        
        connections_text = "\n".join([f"- {p}" for p in connections[:3]]) if connections else "None"
        
        prompt = f"""You are {character}, a biblical character. Tell the story of {book} chapter {chapter} from YOUR perspective, as if you were narrating it.

CHARACTER CONTEXT:
{character_context}

CHAPTER TEXT ({book} {chapter}):
{passage_text}

RELATED PASSAGES WHERE YOU APPEAR:
{connections_text}

Write a complete narrative chapter from {character}'s first-person perspective. Include:
1. A compelling chapter title
2. The full story as {character} experienced or witnessed it
3. {character}'s inner thoughts and reflections
4. How this chapter fits into the broader timeline of {character}'s life
5. What this chapter meant to {character} personally

Write in {character}'s authentic voice - natural, personal, and true to their character."""
        
        system_prompt = f"""You are {character}, narrating your own story from the Bible. Write in first person, using {character}'s unique voice, perspective, and experiences. Make it engaging, personal, and true to biblical history."""
        
        narrative = ollama._generate(
            prompt=prompt,
            system=system_prompt,
            model=ollama.default_model
        )
        
        # Extract title, thoughts, and timeline
        extract_prompt = f"""From this narrative, extract:

NARRATIVE:
{narrative}

Provide:
1. A chapter title (one line)
2. {character}'s key thoughts/reflections (2-3 sentences)
3. Timeline context - where this fits in {character}'s life and biblical history (2-3 sentences)

Format as JSON:
{{
  "title": "...",
  "thoughts": "...",
  "timeline": "..."
}}"""
        
        try:
            extraction = ollama._generate(
                prompt=extract_prompt,
                system="Extract structured information in JSON format.",
                model=ollama.default_model
            )
            import re
            json_match = re.search(r'\{[^}]+\}', extraction, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                return {
                    "title": extracted.get("title", f"{book} {chapter} - {character}'s Story"),
                    "narrative": narrative,
                    "thoughts": extracted.get("thoughts", ""),
                    "timeline": extracted.get("timeline", "")
                }
        except Exception:
            pass
        
        return {
            "title": f"{book} {chapter} - {character}'s Perspective",
            "narrative": narrative,
            "thoughts": f"{character}'s reflections on this chapter.",
            "timeline": f"This chapter from {character}'s perspective in {book}."
        }
