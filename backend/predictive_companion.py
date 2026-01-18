"""
Predictive Spiritual Companion.
AI that anticipates questions, suggests connections, and provides proactive guidance.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .bible_reader import BibleReader
from .database import DiaryEntry, get_db
from .ollama_client import OllamaClient
from .rag_system import RAGSystem


@dataclass
class Prediction:
    """A prediction or suggestion from the companion."""
    type: str  # "question", "connection", "warning", "suggestion"
    content: str
    related_passage: Optional[str] = None
    confidence: float = 0.0
    priority: int = 0  # Higher = more important


@dataclass
class ReadingPath:
    """A suggested reading path."""
    name: str
    description: str
    passages: List[str]
    reason: str
    estimated_time: int  # minutes


class PredictiveCompanion:
    """Proactive AI companion that anticipates needs and guides reading."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.bible_reader: Optional[BibleReader] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.rag_system: Optional[RAGSystem] = None
    
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
    
    def predict_questions(self, passage: str, user_history: Optional[List[str]] = None) -> List[Prediction]:
        """Predict questions the user might have about a passage."""
        ollama = self._get_ollama()
        
        # Analyze passage difficulty and common questions
        passage_text_obj = self._get_bible_reader().get_passage_text(passage)
        passage_text = passage
        if passage_text_obj and passage_text_obj.get("verses"):
            verse_texts = [f"{v}: {t}" for v, t in list(passage_text_obj["verses"].items())[:10]]
            passage_text = "\n".join(verse_texts)
        
        history_context = ""
        if user_history:
            history_context = f"\n\nUser's reading history includes: {', '.join(user_history[-5:])}"
        
        prompt = f"""Analyze this Bible passage and predict 3-5 questions a reader might have:

Passage: {passage}
Text: {passage_text[:500]}
{history_context}

Predict questions that:
1. Address potential confusion or difficulty
2. Connect to broader theological themes
3. Relate to practical application
4. Show curiosity about context or meaning

Return as JSON array of strings."""
        
        system = "You are an experienced Bible teacher predicting common student questions."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                return [
                    Prediction(
                        type="question",
                        content=q,
                        related_passage=passage,
                        confidence=0.7,
                        priority=1
                    )
                    for q in questions[:5]
                ]
        except Exception:
            pass
        
        # Fallback: common questions
        return [
            Prediction(
                type="question",
                content=f"What is the main message of {passage}?",
                related_passage=passage,
                confidence=0.5,
                priority=1
            )
        ]
    
    def find_connections(
        self,
        current_passage: str,
        reading_history: List[str],
        days_back: int = 7
    ) -> List[Prediction]:
        """Find connections between current passage and past readings."""
        if not reading_history:
            return []
        
        ollama = self._get_ollama()
        
        # Get current passage context
        current_text_obj = self._get_bible_reader().get_passage_text(current_passage)
        current_text = current_passage
        if current_text_obj and current_text_obj.get("verses"):
            verse_texts = [f"{v}: {t}" for v, t in list(current_text_obj["verses"].items())[:5]]
            current_text = "\n".join(verse_texts)
        
        # Get recent readings context
        recent_readings = reading_history[-5:] if len(reading_history) > 5 else reading_history
        recent_context = "\n".join([f"- {r}" for r in recent_readings])
        
        prompt = f"""Find connections between this passage and recent readings:

Current Passage: {current_passage}
{current_text[:300]}

Recent Readings:
{recent_context}

Identify:
1. Thematic connections
2. Cross-references
3. Continuity of ideas
4. Contrasts or developments

Return as JSON array of connection descriptions."""
        
        system = "You are identifying connections between biblical passages."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                connections = json.loads(json_match.group())
                return [
                    Prediction(
                        type="connection",
                        content=conn,
                        related_passage=recent_readings[-1] if recent_readings else None,
                        confidence=0.6,
                        priority=2
                    )
                    for conn in connections[:3]
                ]
        except Exception:
            pass
        
        return []
    
    def warn_about_difficulty(self, passage: str) -> List[Prediction]:
        """Warn about potentially confusing or difficult passages."""
        ollama = self._get_ollama()
        
        prompt = f"""Analyze this passage for potential difficulty:

{passage}

Identify:
1. What might confuse readers
2. Common misinterpretations
3. Historical/cultural context needed
4. Theological complexity

Return a brief warning (1-2 sentences) or null if passage is straightforward.
Return as JSON with 'warning' field."""
        
        system = "You are identifying potentially difficult biblical passages."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                warning = data.get("warning")
                if warning:
                    return [
                        Prediction(
                            type="warning",
                            content=warning,
                            related_passage=passage,
                            confidence=0.7,
                            priority=3  # High priority
                        )
                    ]
        except Exception:
            pass
        
        return []
    
    def suggest_reading_path(
        self,
        goal: str,
        current_progress: List[str],
        reading_streak: int = 0
    ) -> List[ReadingPath]:
        """Suggest personalized reading paths based on goals."""
        ollama = self._get_ollama()
        
        current_books = set()
        for passage in current_progress[-10:]:
            parts = passage.split()
            if len(parts) >= 2:
                current_books.add(" ".join(parts[:-1]))
        
        prompt = f"""Create a personalized Bible reading path:

Goal: {goal}
Recent readings: {', '.join(current_progress[-5:]) if current_progress else 'None'}
Reading streak: {reading_streak} days

Suggest a reading path (3-5 passages) that:
1. Advances toward the goal
2. Builds on recent readings
3. Is appropriate for the reading level
4. Maintains engagement

Return as JSON with 'name', 'description', 'passages' (array), 'reason', 'estimated_time' fields."""
        
        system = "You are creating personalized Bible reading paths."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return [
                    ReadingPath(
                        name=data.get("name", "Suggested Path"),
                        description=data.get("description", ""),
                        passages=data.get("passages", [])[:5],
                        reason=data.get("reason", ""),
                        estimated_time=data.get("estimated_time", 15)
                    )
                ]
        except Exception:
            pass
        
        # Fallback
        return [
            ReadingPath(
                name="Continuation Path",
                description="Continue your current reading plan",
                passages=current_progress[-3:] if current_progress else [],
                reason="Maintains consistency with your current journey",
                estimated_time=15
            )
        ]
    
    def get_proactive_insights(
        self,
        passage: str,
        reading_date: date,
        user_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all proactive insights for a passage."""
        predictions = []
        
        # Predict questions
        predictions.extend(self.predict_questions(passage, user_history))
        
        # Find connections
        if user_history:
            predictions.extend(self.find_connections(passage, user_history))
        
        # Warn about difficulty
        predictions.extend(self.warn_about_difficulty(passage))
        
        # Sort by priority
        predictions.sort(key=lambda p: p.priority, reverse=True)
        
        return {
            "passage": passage,
            "date": reading_date.isoformat(),
            "predictions": [
                {
                    "type": p.type,
                    "content": p.content,
                    "related_passage": p.related_passage,
                    "confidence": p.confidence,
                    "priority": p.priority
                }
                for p in predictions
            ]
        }
    
    def get_user_reading_patterns(self) -> Dict[str, Any]:
        """Analyze user's reading patterns."""
        with get_db() as db:
            entries = db.query(DiaryEntry).order_by(DiaryEntry.entry_date.desc()).all()
            
            if not entries:
                return {
                    "total_readings": 0,
                    "streak": 0,
                    "common_themes": [],
                    "confusion_points": []
                }
            
            # Analyze themes from notes
            all_notes = " ".join([e.personal_notes or "" for e in entries[:50]])
            
            # Calculate streak
            streak = 0
            today = date.today()
            expected_date = today
            for entry in entries:
                if entry.entry_date == expected_date:
                    streak += 1
                    expected_date = entry.entry_date - timedelta(days=1)
                elif entry.entry_date < expected_date:
                    break
            
            return {
                "total_readings": len(entries),
                "streak": streak,
                "common_themes": self._extract_themes(all_notes),
                "confusion_points": self._extract_confusion_points(all_notes),
                "last_reading": entries[0].entry_date.isoformat() if entries else None
            }
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract common themes from user notes."""
        # Simple keyword extraction - could be enhanced
        themes = []
        keywords = {
            "grace": "Grace",
            "faith": "Faith",
            "love": "Love",
            "prayer": "Prayer",
            "forgiveness": "Forgiveness"
        }
        text_lower = text.lower()
        for keyword, theme in keywords.items():
            if keyword in text_lower:
                themes.append(theme)
        return list(set(themes))[:5]
    
    def _extract_confusion_points(self, text: str) -> List[str]:
        """Extract points where user might be confused."""
        # Look for confusion indicators in notes
        confusion_keywords = ["confused", "don't understand", "unclear", "difficult", "hard"]
        if any(keyword in text.lower() for keyword in confusion_keywords):
            return ["Consider reviewing passages on themes you've found challenging"]
        return []
