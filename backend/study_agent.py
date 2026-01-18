"""
Autonomous Bible Study Agent.
AI tutor that creates personalized study plans, tracks understanding, and adapts.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bible_reader import BibleReader
from .database import DiaryEntry, get_db
from .ollama_client import OllamaClient


@dataclass
class StudyGoal:
    """A learning goal for Bible study."""
    goal_id: str
    description: str
    target_passages: List[str]
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    estimated_days: int
    created_at: str
    status: str  # "active", "completed", "paused"


@dataclass
class StudySession:
    """A study session with quiz and tracking."""
    session_id: str
    goal_id: str
    passage: str
    date: str
    quiz_questions: List[Dict[str, Any]]
    user_answers: Dict[str, str]
    understanding_score: float
    notes: str


@dataclass
class StudyPlan:
    """Complete personalized study plan."""
    plan_id: str
    goal: StudyGoal
    sessions: List[StudySession]
    current_session_index: int
    overall_progress: float
    next_review_date: Optional[str]
    adaptive_adjustments: List[str]


class AutonomousStudyAgent:
    """AI tutor that creates and manages personalized Bible study plans."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.study_plans_dir = self.data_dir / "study_plans"
        self.study_plans_dir.mkdir(parents=True, exist_ok=True)
        
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
    
    def create_study_plan(
        self,
        goal_description: str,
        user_level: str = "intermediate",
        user_id: str = "default"
    ) -> StudyPlan:
        """Create a personalized study plan for a learning goal."""
        ollama = self._get_ollama()
        
        # Get user's reading history for context
        with get_db() as db:
            entries = db.query(DiaryEntry).order_by(DiaryEntry.entry_date.desc()).limit(20).all()
            recent_readings = [e.reading_passage for e in entries if e.reading_passage]
        
        prompt = f"""Create a personalized Bible study plan:

Goal: {goal_description}
User Level: {user_level}
Recent Readings: {', '.join(recent_readings[:5]) if recent_readings else 'None'}

Create a structured study plan with:
1. 5-10 passages in optimal learning order
2. Estimated days to complete
3. Difficulty progression
4. Key learning objectives for each passage

Return as JSON:
{{
    "passages": ["passage1", "passage2", ...],
    "estimated_days": 14,
    "difficulty": "intermediate",
    "objectives": ["objective1", "objective2", ...]
}}"""
        
        system = "You are an expert Bible study tutor creating personalized learning plans."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
                passages = plan_data.get("passages", [])[:10]
            else:
                passages = recent_readings[:5] if recent_readings else ["Genesis 1", "John 1"]
        except Exception:
            passages = recent_readings[:5] if recent_readings else ["Genesis 1", "John 1"]
        
        # Create study goal
        goal = StudyGoal(
            goal_id=f"goal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            description=goal_description,
            target_passages=passages,
            difficulty_level=user_level,
            estimated_days=len(passages) * 2,  # 2 days per passage
            created_at=datetime.utcnow().isoformat(),
            status="active"
        )
        
        # Create initial sessions
        sessions = []
        for i, passage in enumerate(passages):
            session = StudySession(
                session_id=f"session_{i+1}",
                goal_id=goal.goal_id,
                passage=passage,
                date=(date.today() + timedelta(days=i*2)).isoformat(),
                quiz_questions=[],
                user_answers={},
                understanding_score=0.0,
                notes=""
            )
            sessions.append(session)
        
        plan = StudyPlan(
            plan_id=f"plan_{goal.goal_id}",
            goal=goal,
            sessions=sessions,
            current_session_index=0,
            overall_progress=0.0,
            next_review_date=None,
            adaptive_adjustments=[]
        )
        
        # Save plan
        self._save_plan(user_id, plan)
        
        return plan
    
    def generate_quiz(self, passage: str, difficulty: str = "intermediate") -> List[Dict[str, Any]]:
        """Generate quiz questions for a passage."""
        ollama = self._get_ollama()
        
        passage_text_obj = self._get_bible_reader().get_passage_text(passage)
        passage_text = passage
        if passage_text_obj and passage_text_obj.get("verses"):
            verse_texts = [f"{v}: {t}" for v, t in list(passage_text_obj["verses"].items())[:10]]
            passage_text = "\n".join(verse_texts)
        
        prompt = f"""Create 3-5 quiz questions for this Bible passage ({difficulty} level):

{passage_text[:800]}

Create questions that test:
1. Understanding of key concepts
2. Application to life
3. Connection to broader themes

Return as JSON array:
[
  {{
    "question": "...",
    "type": "multiple_choice",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "A",
    "explanation": "..."
  }}
]"""
        
        system = "You are creating educational quiz questions for Bible study."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # Fallback questions
        return [
            {
                "question": f"What is the main theme of {passage}?",
                "type": "short_answer",
                "explanation": "Consider the overall message and purpose."
            }
        ]
    
    def assess_understanding(
        self,
        passage: str,
        user_answers: Dict[str, str],
        quiz_questions: List[Dict[str, Any]]
    ) -> float:
        """Assess user's understanding from quiz answers."""
        ollama = self._get_ollama()
        
        answers_text = "\n".join([f"Q: {q.get('question', '')}\nA: {user_answers.get(str(i), 'No answer')}" 
                                  for i, q in enumerate(quiz_questions)])
        
        prompt = f"""Assess understanding of {passage} based on these quiz answers:

{answers_text}

Rate understanding from 0.0 to 1.0 and provide brief feedback.
Return as JSON:
{{
    "score": 0.75,
    "feedback": "Good understanding of main themes, but missed some details."
}}"""
        
        system = "You are assessing Bible study comprehension."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return float(data.get("score", 0.5))
        except Exception:
            pass
        
        # Fallback: simple scoring
        answered = len([a for a in user_answers.values() if a])
        total = len(quiz_questions)
        return answered / total if total > 0 else 0.0
    
    def adapt_plan(
        self,
        plan: StudyPlan,
        understanding_scores: List[float]
    ) -> StudyPlan:
        """Adapt study plan based on performance."""
        avg_score = sum(understanding_scores) / len(understanding_scores) if understanding_scores else 0.5
        
        adjustments = []
        
        # If understanding is low, slow down
        if avg_score < 0.6:
            adjustments.append("Reducing pace - adding review sessions")
            # Add review sessions
            for i in range(len(plan.sessions) // 3):
                review_session = StudySession(
                    session_id=f"review_{i}",
                    goal_id=plan.goal.goal_id,
                    passage=plan.sessions[i*3].passage,
                    date=(date.today() + timedelta(days=1)).isoformat(),
                    quiz_questions=[],
                    user_answers={},
                    understanding_score=0.0,
                    notes="Review session"
                )
                plan.sessions.insert((i+1)*3, review_session)
        
        # If understanding is high, accelerate
        elif avg_score > 0.85:
            adjustments.append("Accelerating pace - adding advanced passages")
            # Could add more challenging passages
        
        plan.adaptive_adjustments.extend(adjustments)
        plan.overall_progress = len([s for s in plan.sessions if s.understanding_score > 0]) / len(plan.sessions)
        
        return plan
    
    def get_active_plan(self, user_id: str = "default") -> Optional[StudyPlan]:
        """Get active study plan for user."""
        plans = self._load_plans(user_id)
        active = [p for p in plans if p.goal.status == "active"]
        return active[0] if active else None
    
    def _save_plan(self, user_id: str, plan: StudyPlan) -> None:
        """Save study plan."""
        plans_file = self.study_plans_dir / f"{user_id}_plans.json"
        plans = self._load_plans(user_id)
        
        # Update or add plan
        plans = [p for p in plans if p.plan_id != plan.plan_id]
        plans.append(plan)
        
        plans_dict = [self._plan_to_dict(p) for p in plans]
        plans_file.write_text(
            json.dumps(plans_dict, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def _load_plans(self, user_id: str) -> List[StudyPlan]:
        """Load study plans."""
        plans_file = self.study_plans_dir / f"{user_id}_plans.json"
        if plans_file.exists():
            try:
                data = json.loads(plans_file.read_text(encoding="utf-8"))
                return [self._plan_from_dict(d) for d in data]
            except Exception:
                pass
        return []
    
    def _plan_to_dict(self, plan: StudyPlan) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            "plan_id": plan.plan_id,
            "goal": {
                "goal_id": plan.goal.goal_id,
                "description": plan.goal.description,
                "target_passages": plan.goal.target_passages,
                "difficulty_level": plan.goal.difficulty_level,
                "estimated_days": plan.goal.estimated_days,
                "created_at": plan.goal.created_at,
                "status": plan.goal.status
            },
            "sessions": [
                {
                    "session_id": s.session_id,
                    "goal_id": s.goal_id,
                    "passage": s.passage,
                    "date": s.date,
                    "quiz_questions": s.quiz_questions,
                    "user_answers": s.user_answers,
                    "understanding_score": s.understanding_score,
                    "notes": s.notes
                }
                for s in plan.sessions
            ],
            "current_session_index": plan.current_session_index,
            "overall_progress": plan.overall_progress,
            "next_review_date": plan.next_review_date,
            "adaptive_adjustments": plan.adaptive_adjustments
        }
    
    def _plan_from_dict(self, data: Dict[str, Any]) -> StudyPlan:
        """Reconstruct plan from dictionary."""
        goal_data = data.get("goal", {})
        goal = StudyGoal(
            goal_id=goal_data.get("goal_id", ""),
            description=goal_data.get("description", ""),
            target_passages=goal_data.get("target_passages", []),
            difficulty_level=goal_data.get("difficulty_level", "intermediate"),
            estimated_days=goal_data.get("estimated_days", 0),
            created_at=goal_data.get("created_at", datetime.utcnow().isoformat()),
            status=goal_data.get("status", "active")
        )
        
        sessions = [
            StudySession(
                session_id=s.get("session_id", ""),
                goal_id=s.get("goal_id", ""),
                passage=s.get("passage", ""),
                date=s.get("date", ""),
                quiz_questions=s.get("quiz_questions", []),
                user_answers=s.get("user_answers", {}),
                understanding_score=float(s.get("understanding_score", 0.0)),
                notes=s.get("notes", "")
            )
            for s in data.get("sessions", [])
        ]
        
        return StudyPlan(
            plan_id=data.get("plan_id", ""),
            goal=goal,
            sessions=sessions,
            current_session_index=data.get("current_session_index", 0),
            overall_progress=float(data.get("overall_progress", 0.0)),
            next_review_date=data.get("next_review_date"),
            adaptive_adjustments=data.get("adaptive_adjustments", [])
        )
