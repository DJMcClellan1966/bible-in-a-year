"""
Theological DNA Profile System.
Builds personal theological profile from reading patterns, questions, and insights.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .database import DiaryEntry, get_db
from .ollama_client import OllamaClient


@dataclass
class TheologicalTrait:
    """A theological trait or theme."""
    name: str
    strength: float  # 0.0 to 1.0
    evidence: List[str]
    growth_trend: str  # "increasing", "stable", "decreasing"


@dataclass
class TheologicalProfile:
    """Complete theological profile of a user."""
    user_id: str
    generated_at: str
    traits: List[TheologicalTrait]
    tradition_alignment: Dict[str, float]  # Augustine, Aquinas, etc.
    reading_patterns: Dict[str, Any]
    growth_metrics: Dict[str, Any]
    recommendations: List[str]


class TheologicalProfileEngine:
    """Builds and tracks theological profiles from user behavior."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.profiles_dir = self.data_dir / "theological_profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        self.ollama_client: Optional[OllamaClient] = None
    
    def _get_ollama(self) -> OllamaClient:
        if self.ollama_client is None:
            self.ollama_client = OllamaClient()
        return self.ollama_client
    
    def build_profile(self, user_id: str = "default") -> TheologicalProfile:
        """Build comprehensive theological profile from user data."""
        # Get user data
        user_data = self._collect_user_data()
        
        # Analyze reading patterns
        reading_patterns = self._analyze_reading_patterns(user_data)
        
        # Extract theological traits
        traits = self._extract_theological_traits(user_data)
        
        # Compare with historical traditions
        tradition_alignment = self._compare_with_traditions(traits, user_data)
        
        # Calculate growth metrics
        growth_metrics = self._calculate_growth_metrics(user_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(traits, reading_patterns)
        
        profile = TheologicalProfile(
            user_id=user_id,
            generated_at=datetime.utcnow().isoformat(),
            traits=traits,
            tradition_alignment=tradition_alignment,
            reading_patterns=reading_patterns,
            growth_metrics=growth_metrics,
            recommendations=recommendations
        )
        
        # Save profile
        self._save_profile(user_id, profile)
        
        return profile
    
    def _collect_user_data(self) -> Dict[str, Any]:
        """Collect all user data for analysis."""
        with get_db() as db:
            entries = db.query(DiaryEntry).order_by(DiaryEntry.entry_date).all()
            
            return {
                "diary_entries": [
                    {
                        "date": e.entry_date.isoformat(),
                        "passage": e.reading_passage,
                        "personal_notes": e.personal_notes,
                        "ai_insights": e.ai_insights,
                        "margin_notes": e.margin_notes
                    }
                    for e in entries
                ],
                "total_entries": len(entries),
                "date_range": {
                    "start": entries[0].entry_date.isoformat() if entries else None,
                    "end": entries[-1].entry_date.isoformat() if entries else None
                }
            }
    
    def _analyze_reading_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze reading patterns and preferences."""
        entries = user_data.get("diary_entries", [])
        
        # Book preferences
        books_read = {}
        for entry in entries:
            passage = entry.get("passage", "")
            if passage:
                book = passage.split()[0]
                books_read[book] = books_read.get(book, 0) + 1
        
        # Theme extraction from notes
        all_notes = " ".join([
            (e.get("personal_notes") or "") + " " + (e.get("ai_insights") or "")
            for e in entries
        ])
        
        # Reading frequency
        reading_days = len(entries)
        total_days = 365  # Assuming year-long plan
        consistency = reading_days / total_days if total_days > 0 else 0
        
        return {
            "books_read": books_read,
            "favorite_books": sorted(books_read.items(), key=lambda x: x[1], reverse=True)[:5],
            "reading_consistency": consistency,
            "total_readings": len(entries),
            "notes_length": len(all_notes),
            "engagement_level": "high" if consistency > 0.8 else "medium" if consistency > 0.5 else "low"
        }
    
    def _extract_theological_traits(self, user_data: Dict[str, Any]) -> List[TheologicalTrait]:
        """Extract theological traits from user's reading and notes."""
        entries = user_data.get("diary_entries", [])
        all_text = " ".join([
            (e.get("personal_notes") or "") + " " + (e.get("ai_insights") or "")
            for e in entries
        ])
        
        ollama = self._get_ollama()
        
        prompt = f"""Analyze this user's Bible study notes and extract their theological profile:

Notes and insights:
{all_text[:2000]}

Identify 5-7 key theological traits or themes that emerge from their reading patterns, questions, and reflections. For each trait, provide:
1. Trait name
2. Strength (0.0 to 1.0)
3. Evidence (2-3 examples from their notes)
4. Growth trend (increasing/stable/decreasing)

Return as JSON array:
[
  {{
    "name": "Trait name",
    "strength": 0.75,
    "evidence": ["evidence 1", "evidence 2"],
    "growth_trend": "increasing"
  }}
]"""
        
        system = "You are a theological analyst identifying spiritual growth patterns and theological themes."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                traits_data = json.loads(json_match.group())
                return [
                    TheologicalTrait(
                        name=t.get("name", ""),
                        strength=float(t.get("strength", 0.5)),
                        evidence=t.get("evidence", []),
                        growth_trend=t.get("growth_trend", "stable")
                    )
                    for t in traits_data[:7]
                ]
        except Exception:
            pass
        
        # Fallback: simple extraction
        traits = []
        keywords = {
            "grace": "Grace and Mercy",
            "faith": "Faith and Trust",
            "love": "Love and Compassion",
            "prayer": "Prayer and Devotion",
            "salvation": "Salvation and Redemption",
            "wisdom": "Wisdom and Understanding",
            "service": "Service and Ministry"
        }
        
        all_text_lower = all_text.lower()
        for keyword, trait_name in keywords.items():
            if keyword in all_text_lower:
                count = all_text_lower.count(keyword)
                strength = min(1.0, count / 10.0)  # Normalize
                traits.append(TheologicalTrait(
                    name=trait_name,
                    strength=strength,
                    evidence=[f"Frequently mentioned in notes ({count} times)"],
                    growth_trend="stable"
                ))
        
        return traits[:7]
    
    def _compare_with_traditions(
        self,
        traits: List[TheologicalTrait],
        user_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Compare user's profile with historical theological traditions."""
        ollama = self._get_ollama()
        
        trait_names = [t.name for t in traits]
        trait_summary = ", ".join(trait_names)
        
        prompt = f"""Compare this theological profile with historical traditions:

User's theological traits: {trait_summary}

Rate alignment (0.0 to 1.0) with:
1. Augustinian tradition (grace, sin, predestination, church authority)
2. Thomistic/Aquinas tradition (reason, natural law, systematic theology)
3. Reformed tradition (sovereignty, scripture, covenant)
4. Wesleyan tradition (sanctification, free will, holiness)
5. Mystical tradition (contemplation, union with God, experience)

Return as JSON object with alignment scores."""
        
        system = "You are comparing theological profiles with historical traditions."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # Fallback: simple scoring
        return {
            "Augustinian": 0.5,
            "Thomistic": 0.5,
            "Reformed": 0.5,
            "Wesleyan": 0.5,
            "Mystical": 0.5
        }
    
    def _calculate_growth_metrics(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate spiritual growth metrics over time."""
        entries = user_data.get("diary_entries", [])
        
        if len(entries) < 2:
            return {
                "growth_rate": 0.0,
                "consistency": 0.0,
                "engagement_trend": "insufficient_data"
            }
        
        # Analyze notes length over time (proxy for engagement)
        early_entries = entries[:len(entries)//3] if len(entries) > 3 else entries[:1]
        late_entries = entries[-len(entries)//3:] if len(entries) > 3 else entries[-1:]
        
        early_avg_length = sum(len(e.get("personal_notes", "") or "") for e in early_entries) / len(early_entries) if early_entries else 0
        late_avg_length = sum(len(e.get("personal_notes", "") or "") for e in late_entries) / len(late_entries) if late_entries else 0
        
        growth_rate = (late_avg_length - early_avg_length) / max(early_avg_length, 1)
        
        # Reading consistency
        total_days = (date.today() - date.fromisoformat(entries[0]["date"])).days if entries else 1
        consistency = len(entries) / max(total_days, 1)
        
        return {
            "growth_rate": growth_rate,
            "consistency": min(1.0, consistency),
            "engagement_trend": "increasing" if growth_rate > 0.1 else "stable" if growth_rate > -0.1 else "decreasing",
            "notes_growth": growth_rate
        }
    
    def _generate_recommendations(
        self,
        traits: List[TheologicalTrait],
        reading_patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized reading recommendations."""
        ollama = self._get_ollama()
        
        trait_summary = ", ".join([t.name for t in traits[:5]])
        favorite_books = ", ".join([b[0] for b in reading_patterns.get("favorite_books", [])[:3]])
        
        prompt = f"""Generate 5 personalized Bible reading recommendations based on:

Theological traits: {trait_summary}
Favorite books: {favorite_books}
Reading consistency: {reading_patterns.get('reading_consistency', 0):.0%}

Suggest specific passages, books, or themes that would:
1. Deepen existing interests
2. Address areas for growth
3. Provide balance to current reading
4. Challenge and expand understanding

Return as JSON array of recommendation strings."""
        
        system = "You are providing personalized Bible reading recommendations."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # Fallback recommendations
        return [
            "Continue exploring your favorite books in depth",
            "Try reading complementary passages on similar themes",
            "Explore books you haven't read yet",
            "Study passages that challenge your current understanding",
            "Read commentaries on passages you've found meaningful"
        ]
    
    def get_profile(self, user_id: str = "default") -> Optional[TheologicalProfile]:
        """Get existing profile or build new one."""
        profile_file = self.profiles_dir / f"{user_id}.json"
        
        if profile_file.exists():
            try:
                data = json.loads(profile_file.read_text(encoding="utf-8"))
                return self._profile_from_dict(data)
            except Exception:
                pass
        
        # Build new profile
        return self.build_profile(user_id)
    
    def _save_profile(self, user_id: str, profile: TheologicalProfile) -> None:
        """Save profile to file."""
        profile_file = self.profiles_dir / f"{user_id}.json"
        
        profile_dict = {
            "user_id": profile.user_id,
            "generated_at": profile.generated_at,
            "traits": [
                {
                    "name": t.name,
                    "strength": t.strength,
                    "evidence": t.evidence,
                    "growth_trend": t.growth_trend
                }
                for t in profile.traits
            ],
            "tradition_alignment": profile.tradition_alignment,
            "reading_patterns": profile.reading_patterns,
            "growth_metrics": profile.growth_metrics,
            "recommendations": profile.recommendations
        }
        
        profile_file.write_text(
            json.dumps(profile_dict, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def _profile_from_dict(self, data: Dict[str, Any]) -> TheologicalProfile:
        """Reconstruct profile from dictionary."""
        return TheologicalProfile(
            user_id=data.get("user_id", "default"),
            generated_at=data.get("generated_at", datetime.utcnow().isoformat()),
            traits=[
                TheologicalTrait(
                    name=t.get("name", ""),
                    strength=float(t.get("strength", 0.5)),
                    evidence=t.get("evidence", []),
                    growth_trend=t.get("growth_trend", "stable")
                )
                for t in data.get("traits", [])
            ],
            tradition_alignment=data.get("tradition_alignment", {}),
            reading_patterns=data.get("reading_patterns", {}),
            growth_metrics=data.get("growth_metrics", {}),
            recommendations=data.get("recommendations", [])
        )
