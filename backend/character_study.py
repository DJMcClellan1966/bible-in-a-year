"""
Character Study System.
Comprehensive study system for biblical characters with profiles, arcs, relationships, and insights.
"""

import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bible_reader import BibleReader
from .ollama_client import OllamaClient
from .rag_system import RAGSystem


@dataclass
class CharacterProfile:
    """Profile of a biblical character."""
    character_id: str
    name: str
    alternate_names: List[str]
    description: str
    category: str  # "patriarch", "prophet", "king", "disciple", "woman", "minor"
    key_passages: List[str]
    first_appearance: str
    last_appearance: str
    timeline_period: str
    significance: str
    traits: List[str]
    character_arc: str
    key_relationships: List[Dict[str, str]]
    themes: List[str]
    lessons: List[str]


@dataclass
class CharacterArc:
    """Character development arc across the Bible."""
    character_id: str
    stages: List[Dict[str, Any]]  # Development stages with passages
    turning_points: List[Dict[str, Any]]
    growth_pattern: str
    transformation: str


@dataclass
class CharacterRelationship:
    """Relationship between two characters."""
    character1: str
    character2: str
    relationship_type: str  # "father-son", "teacher-disciple", "allies", "enemies", etc.
    passages: List[str]
    description: str
    significance: str


@dataclass
class CharacterComparison:
    """Comparison between characters."""
    characters: List[str]
    similarities: List[str]
    differences: List[str]
    passages: List[str]
    insights: str


class CharacterStudySystem:
    """Manages character study system with profiles, arcs, and relationships."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.characters_dir = self.data_dir / "characters"
        self.characters_dir.mkdir(parents=True, exist_ok=True)
        
        self.profiles_file = self.characters_dir / "profiles.json"
        self.relationships_file = self.characters_dir / "relationships.json"
        
        self.bible_reader: Optional[BibleReader] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.rag_system: Optional[RAGSystem] = None
        
        # Initialize default characters if needed
        if not self.profiles_file.exists():
            self._initialize_default_characters()
    
    def _get_bible_reader(self) -> BibleReader:
        if self.bible_reader is None:
            self.bible_reader = BibleReader()
        return self.bible_reader
    
    def _get_ollama(self) -> OllamaClient:
        if self.ollama_client is None:
            self.ollama_client = OllamaClient()
        return self.ollama_client
    
    def _get_rag(self) -> RAGSystem:
        if self.rag_system is None:
            self.rag_system = RAGSystem()
            self.rag_system.initialize_default_data()
        return self.rag_system
    
    def _initialize_default_characters(self) -> None:
        """Initialize default character profiles."""
        characters = {
            "abraham": CharacterProfile(
                character_id="abraham",
                name="Abraham",
                alternate_names=["Abram"],
                description="The father of faith, called by God to leave his homeland and become the father of many nations.",
                category="patriarch",
                key_passages=["Genesis 12", "Genesis 15", "Genesis 17", "Genesis 22", "Romans 4", "Hebrews 11"],
                first_appearance="Genesis 11:26",
                last_appearance="Genesis 25:10",
                timeline_period="2000-1800 BC",
                significance="Foundational covenant figure, model of faith",
                traits=["Faithful", "Obedient", "Trusting", "Hospitable", "Intercessory"],
                character_arc="Journey from idolatry to faith, from doubt to trust, from fear to obedience",
                key_relationships=[
                    {"character": "Sarah", "relationship": "husband-wife", "description": "Partner in the covenant promise"},
                    {"character": "Isaac", "relationship": "father-son", "description": "Covenant heir, offered in sacrifice"},
                    {"character": "God", "relationship": "covenant", "description": "Covenant relationship based on faith"}
                ],
                themes=["Faith", "Covenant", "Promise", "Sacrifice", "Obedience"],
                lessons=["Trust God's promises even when they seem impossible", "Obedience requires faith", "God provides"]
            ),
            "moses": CharacterProfile(
                character_id="moses",
                name="Moses",
                alternate_names=[],
                description="The deliverer of Israel, prophet, lawgiver, and mediator between God and His people.",
                category="prophet",
                key_passages=["Exodus 2-4", "Exodus 14", "Exodus 20", "Exodus 32-34", "Numbers 12", "Deuteronomy 34"],
                first_appearance="Exodus 2:1",
                last_appearance="Deuteronomy 34:12",
                timeline_period="1526-1406 BC",
                significance="Deliverer, prophet, lawgiver, type of Christ",
                traits=["Humble", "Reluctant leader", "Intercessor", "Faithful", "Patient"],
                character_arc="From prince to shepherd to deliverer, from anger to patience, from doubt to confidence",
                key_relationships=[
                    {"character": "Aaron", "relationship": "brother-partner", "description": "Brother and spokesman"},
                    {"character": "Pharaoh", "relationship": "adversary", "description": "Opponent in deliverance"},
                    {"character": "Israelites", "relationship": "leader-people", "description": "Guided through wilderness"}
                ],
                themes=["Deliverance", "Law", "Covenant", "Mediation", "Faithfulness"],
                lessons=["God equips those He calls", "Leadership requires patience and intercession", "Obedience matters more than ability"]
            ),
            "david": CharacterProfile(
                character_id="david",
                name="David",
                alternate_names=[],
                description="The shepherd-king, man after God's own heart, warrior, poet, and ancestor of Christ.",
                category="king",
                key_passages=["1 Samuel 16", "1 Samuel 17", "2 Samuel 11-12", "2 Samuel 22", "Psalm 51", "Acts 13:22"],
                first_appearance="1 Samuel 16:1",
                last_appearance="1 Kings 2:11",
                timeline_period="1040-970 BC",
                significance="Anointed king, covenant recipient, ancestor of Christ, model of repentance",
                traits=["Courageous", "Passionate", "Repentant", "Worshiper", "Warrior"],
                character_arc="From shepherd to king, from innocence to sin to repentance, from warrior to worshiper",
                key_relationships=[
                    {"character": "Jonathan", "relationship": "friendship", "description": "Deep friendship"},
                    {"character": "Saul", "relationship": "adversary-king", "description": "Persecuted by jealous king"},
                    {"character": "Bathsheba", "relationship": "marriage", "description": "Restored relationship after sin"}
                ],
                themes=["Covenant", "Repentance", "Worship", "Kingship", "Redemption"],
                lessons=["Even great leaders sin, but true repentance restores", "God sees the heart", "Worship in all circumstances"]
            ),
            "jesus": CharacterProfile(
                character_id="jesus",
                name="Jesus Christ",
                alternate_names=["Yeshua", "Messiah", "Christ", "Son of God", "Son of Man"],
                description="The Son of God, Savior, Messiah, fully God and fully man, the central figure of Christianity.",
                category="messiah",
                key_passages=["Matthew 1-28", "Mark 1-16", "Luke 1-24", "John 1-21", "Philippians 2", "Colossians 1"],
                first_appearance="Matthew 1:1",
                last_appearance="Revelation 22:20",
                timeline_period="4 BC - 30 AD",
                significance="Savior, Redeemer, Son of God, fulfillment of prophecy",
                traits=["Compassionate", "Just", "Humble", "Obedient", "Sacrificial", "Loving"],
                character_arc="From incarnation to ministry to crucifixion to resurrection to ascension",
                key_relationships=[
                    {"character": "God the Father", "relationship": "father-son", "description": "Eternal relationship"},
                    {"character": "Disciples", "relationship": "teacher-students", "description": "Taught and commissioned"},
                    {"character": "Humanity", "relationship": "savior-saved", "description": "Came to save the lost"}
                ],
                themes=["Salvation", "Love", "Sacrifice", "Obedience", "Kingdom", "Redemption"],
                lessons=["Love God and neighbor", "Serve rather than be served", "Obedience to God's will", "Forgiveness"]
            ),
            "paul": CharacterProfile(
                character_id="paul",
                name="Paul",
                alternate_names=["Saul of Tarsus"],
                description="Apostle to the Gentiles, transformed persecutor, theologian, church planter, and writer of much of the New Testament.",
                category="apostle",
                key_passages=["Acts 9", "Acts 13-28", "Romans", "1 Corinthians 15", "Galatians 1-2", "Philippians 3"],
                first_appearance="Acts 7:58",
                last_appearance="2 Timothy 4:22",
                timeline_period="5-67 AD",
                significance="Apostle to Gentiles, theologian, church planter, example of transformation",
                traits=["Zealous", "Transformed", "Persevering", "Scholarly", "Passionate", "Humble"],
                character_arc="From persecutor to persecuted, from legalist to grace preacher, from self-righteous to Christ-dependent",
                key_relationships=[
                    {"character": "Barnabas", "relationship": "partnership", "description": "Early ministry partner"},
                    {"character": "Timothy", "relationship": "mentor-disciple", "description": "Spiritual son"},
                    {"character": "Peter", "relationship": "colleague", "description": "Apostolic partnership"}
                ],
                themes=["Grace", "Transformation", "Mission", "Suffering", "Gospel", "Unity"],
                lessons=["God can transform anyone", "Grace is greater than works", "Suffering for Christ is honor", "Unity in diversity"]
            )
        }
        
        self._save_profiles(list(characters.values()))
    
    def get_character_profile(self, character_id: str) -> Optional[CharacterProfile]:
        """Get profile for a character."""
        profiles = self._load_profiles()
        for profile in profiles:
            if profile.character_id == character_id or profile.name.lower() == character_id.lower():
                return profile
            if character_id.lower() in [name.lower() for name in profile.alternate_names]:
                return profile
        return None
    
    def list_characters(self, category: Optional[str] = None) -> List[CharacterProfile]:
        """List all characters, optionally filtered by category."""
        profiles = self._load_profiles()
        if category:
            profiles = [p for p in profiles if p.category == category]
        return sorted(profiles, key=lambda p: p.name)
    
    def get_character_arc(self, character_id: str) -> Optional[CharacterArc]:
        """Get character development arc."""
        profile = self.get_character_profile(character_id)
        if not profile:
            return None
        
        ollama = self._get_ollama()
        
        # Analyze character arc from key passages
        passages_text = ", ".join(profile.key_passages[:5])
        
        prompt = f"""Analyze the character development arc for {profile.name}:

Character: {profile.name}
Key Passages: {passages_text}
Description: {profile.description}

Identify:
1. Development stages with key passages
2. Major turning points
3. Growth pattern
4. Overall transformation

Return as JSON with stages, turning_points, growth_pattern, and transformation."""
        
        system = "You are analyzing biblical character development."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return CharacterArc(
                    character_id=character_id,
                    stages=data.get("stages", []),
                    turning_points=data.get("turning_points", []),
                    growth_pattern=data.get("growth_pattern", ""),
                    transformation=data.get("transformation", "")
                )
        except Exception:
            pass
        
        # Fallback: simple arc
        return CharacterArc(
            character_id=character_id,
            stages=[{"stage": "Introduction", "passage": profile.first_appearance}],
            turning_points=[],
            growth_pattern="Steady development",
            transformation=profile.character_arc
        )
    
    def get_character_relationships(self, character_id: str) -> List[CharacterRelationship]:
        """Get relationships for a character."""
        profile = self.get_character_profile(character_id)
        if not profile:
            return []
        
        relationships = []
        for rel_data in profile.key_relationships:
            relationships.append(CharacterRelationship(
                character1=profile.name,
                character2=rel_data["character"],
                relationship_type=rel_data["relationship"],
                passages=profile.key_passages[:3],  # Simplified
                description=rel_data["description"],
                significance=f"Key relationship in {profile.name}'s story"
            ))
        
        return relationships
    
    def compare_characters(self, character_ids: List[str]) -> Optional[CharacterComparison]:
        """Compare two or more characters."""
        profiles = [self.get_character_profile(cid) for cid in character_ids]
        profiles = [p for p in profiles if p]
        
        if len(profiles) < 2:
            return None
        
        ollama = self._get_ollama()
        
        profiles_text = "\n".join([f"{p.name}: {p.description}" for p in profiles])
        
        prompt = f"""Compare these biblical characters:

{profiles_text}

Identify:
1. Similarities (3-5)
2. Differences (3-5)
3. Key passages showing comparison
4. Insights from the comparison

Return as JSON."""
        
        system = "You are comparing biblical characters for study purposes."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return CharacterComparison(
                    characters=[p.name for p in profiles],
                    similarities=data.get("similarities", []),
                    differences=data.get("differences", []),
                    passages=data.get("passages", []),
                    insights=data.get("insights", "")
                )
        except Exception:
            pass
        
        # Fallback
        return CharacterComparison(
            characters=[p.name for p in profiles],
            similarities=["Both are significant biblical figures"],
            differences=["Different time periods and roles"],
            passages=[],
            insights="Both demonstrate important spiritual lessons"
        )
    
    def generate_study_questions(self, character_id: str, difficulty: str = "intermediate") -> List[Dict[str, Any]]:
        """Generate study questions for a character."""
        profile = self.get_character_profile(character_id)
        if not profile:
            return []
        
        ollama = self._get_ollama()
        
        prompt = f"""Create 5-7 study questions for studying {profile.name} ({difficulty} level):

Character: {profile.name}
Key Passages: {', '.join(profile.key_passages[:5])}
Themes: {', '.join(profile.themes[:3])}

Create questions that:
1. Explore character traits and development
2. Examine relationships
3. Identify key themes and lessons
4. Apply insights to modern life

Return as JSON array of questions with question text, type, and explanation."""
        
        system = "You are creating Bible study questions for character study."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # Fallback questions
        return [
            {
                "question": f"What are the key character traits of {profile.name}?",
                "type": "analysis",
                "explanation": f"Examine {profile.name}'s actions and words to identify traits"
            },
            {
                "question": f"What was {profile.name}'s relationship with God like?",
                "type": "reflection",
                "explanation": f"Consider how {profile.name} responded to God's call and guidance"
            }
        ]
    
    def get_characters_for_passage(self, passage: str) -> List[CharacterProfile]:
        """Find characters mentioned in a passage."""
        profiles = self._load_profiles()
        matching = []
        
        # Simple matching - could be enhanced with AI
        passage_lower = passage.lower()
        for profile in profiles:
            for key_passage in profile.key_passages:
                if passage_lower in key_passage.lower() or key_passage.lower() in passage_lower:
                    matching.append(profile)
                    break
        
        return matching
    
    def _load_profiles(self) -> List[CharacterProfile]:
        """Load character profiles."""
        if not self.profiles_file.exists():
            return []
        
        try:
            data = json.loads(self.profiles_file.read_text(encoding="utf-8"))
            return [self._profile_from_dict(d) for d in data]
        except Exception:
            return []
    
    def _save_profiles(self, profiles: List[CharacterProfile]) -> None:
        """Save character profiles."""
        data = [self._profile_to_dict(p) for p in profiles]
        self.profiles_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def _profile_to_dict(self, profile: CharacterProfile) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "character_id": profile.character_id,
            "name": profile.name,
            "alternate_names": profile.alternate_names,
            "description": profile.description,
            "category": profile.category,
            "key_passages": profile.key_passages,
            "first_appearance": profile.first_appearance,
            "last_appearance": profile.last_appearance,
            "timeline_period": profile.timeline_period,
            "significance": profile.significance,
            "traits": profile.traits,
            "character_arc": profile.character_arc,
            "key_relationships": profile.key_relationships,
            "themes": profile.themes,
            "lessons": profile.lessons
        }
    
    def _profile_from_dict(self, data: Dict[str, Any]) -> CharacterProfile:
        """Reconstruct profile from dictionary."""
        return CharacterProfile(
            character_id=data.get("character_id", ""),
            name=data.get("name", ""),
            alternate_names=data.get("alternate_names", []),
            description=data.get("description", ""),
            category=data.get("category", ""),
            key_passages=data.get("key_passages", []),
            first_appearance=data.get("first_appearance", ""),
            last_appearance=data.get("last_appearance", ""),
            timeline_period=data.get("timeline_period", ""),
            significance=data.get("significance", ""),
            traits=data.get("traits", []),
            character_arc=data.get("character_arc", ""),
            key_relationships=data.get("key_relationships", []),
            themes=data.get("themes", []),
            lessons=data.get("lessons", [])
        )
