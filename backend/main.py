"""
Bible in a Year backend API.
"""

from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .database import DiaryEntry, get_db, init_db
from .bible_reader import BibleReader
from .rag_system import RAGSystem
from .ollama_client import OllamaClient
from .genesis_commentary_generator import GenesisCommentaryGenerator
from .genesis_corpus_generator import GenesisCorpusGenerator
from .persona_engine import PersonaEngine
from .narrative_engine import NarrativeEngine
from .predictive_companion import PredictiveCompanion
from .living_commentary import LivingCommentarySystem
from .theological_profile import TheologicalProfileEngine
from .study_agent import AutonomousStudyAgent
from .bible_timeline import LivingBibleTimeline
from .character_study import CharacterStudySystem


class CommentaryRequest(BaseModel):
    passage: str
    helper: str = "augustine"
    personalized: bool = False


class QuestionRequest(BaseModel):
    question: str
    helper: str = "augustine"
    context: Optional[str] = None


class DiaryEntryCreate(BaseModel):
    entry_date: date
    reading_passage: str
    personal_notes: Optional[str] = None
    margin_notes: Optional[Dict[str, List[str]]] = None
    ai_insights: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="Bible in a Year",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Lazy initialization to speed up startup
_bible_reader: Optional[BibleReader] = None
_rag_system: Optional[RAGSystem] = None
_ollama_client: Optional[OllamaClient] = None
_genesis_generator: Optional[GenesisCommentaryGenerator] = None
_corpus_generator: Optional[GenesisCorpusGenerator] = None
_persona_engine: Optional[PersonaEngine] = None
_narrative_engine: Optional[NarrativeEngine] = None
_predictive_companion: Optional[PredictiveCompanion] = None
_living_commentary: Optional[LivingCommentarySystem] = None
_theological_profile: Optional[TheologicalProfileEngine] = None
_study_agent: Optional[AutonomousStudyAgent] = None
_bible_timeline: Optional[LivingBibleTimeline] = None
_character_study: Optional[CharacterStudySystem] = None


def get_bible_reader() -> BibleReader:
    global _bible_reader
    if _bible_reader is None:
        _bible_reader = BibleReader()
    return _bible_reader


def get_rag_system() -> RAGSystem:
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
        _rag_system.initialize_default_data()
    return _rag_system


def get_ollama_client() -> OllamaClient:
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


def get_genesis_generator() -> GenesisCommentaryGenerator:
    global _genesis_generator
    if _genesis_generator is None:
        _genesis_generator = GenesisCommentaryGenerator()
    return _genesis_generator


def get_corpus_generator() -> GenesisCorpusGenerator:
    global _corpus_generator
    if _corpus_generator is None:
        _corpus_generator = GenesisCorpusGenerator()
    return _corpus_generator


def get_persona_engine() -> PersonaEngine:
    global _persona_engine
    if _persona_engine is None:
        _persona_engine = PersonaEngine()
    return _persona_engine


def get_narrative_engine() -> NarrativeEngine:
    global _narrative_engine
    if _narrative_engine is None:
        _narrative_engine = NarrativeEngine()
    return _narrative_engine


def get_predictive_companion() -> PredictiveCompanion:
    global _predictive_companion
    if _predictive_companion is None:
        _predictive_companion = PredictiveCompanion()
    return _predictive_companion


def get_living_commentary() -> LivingCommentarySystem:
    global _living_commentary
    if _living_commentary is None:
        _living_commentary = LivingCommentarySystem()
    return _living_commentary


def get_theological_profile() -> TheologicalProfileEngine:
    global _theological_profile
    if _theological_profile is None:
        _theological_profile = TheologicalProfileEngine()
    return _theological_profile


def get_study_agent() -> AutonomousStudyAgent:
    global _study_agent
    if _study_agent is None:
        _study_agent = AutonomousStudyAgent()
    return _study_agent


def get_bible_timeline() -> LivingBibleTimeline:
    global _bible_timeline
    if _bible_timeline is None:
        _bible_timeline = LivingBibleTimeline()
    return _bible_timeline


def get_character_study() -> CharacterStudySystem:
    global _character_study
    if _character_study is None:
        _character_study = CharacterStudySystem()
    return _character_study


@app.get("/")
def root():
    return {
        "app": "Bible in a Year",
        "status": "ok",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow()}


@app.get("/api/readings/{reading_date}")
def get_daily_reading(reading_date: date, version: Optional[str] = None, plan_type: str = "classic", use_corpus: bool = False):
    # Check if corpus is available and requested
    if use_corpus and plan_type == "chronological":
        corpus_gen = get_corpus_generator()
        corpus = corpus_gen.get_corpus_for_date(reading_date)
        if corpus:
            # Return corpus data in reading format
            passage_data = corpus.get("passage_data", {})
            daily_summary = corpus.get("daily_summary", {})
            commentary_data = corpus.get("commentary_data", {})
            
            return {
                "date": reading_date,
                "passage_text": {passage_data.get("reference", ""): passage_data},
                "plan_type": plan_type,
                "passages": [passage_data.get("reference", "")],
                "theme": passage_data.get("theme", ""),
                "daily_summary": daily_summary,
                "commentary": commentary_data.get("synthesized_commentary", ""),
                "key_insights": commentary_data.get("key_insights", []),
                "theological_themes": commentary_data.get("theological_themes", []),
                "from_corpus": True
            }
    
    # Fallback to regular reading
    reader = get_bible_reader()
    reading = reader.get_reading_for_date(reading_date, plan_type=plan_type)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found.")
    passages_text = {}
    for passage in reading.get("passages", []):
        passages_text[passage] = reader.get_passage_text(passage, version=version)
    return {"date": reading_date, "passage_text": passages_text, "plan_type": plan_type, **reading}


@app.get("/api/reading-plans")
def get_reading_plans():
    """Get list of available reading plans."""
    return {
        "plans": [
            {
                "id": "classic",
                "name": "Classic Bible in a Year",
                "description": "Traditional plan: Old Testament, Psalms/Proverbs, and New Testament readings daily",
            },
            {
                "id": "chronological_cross_ref",
                "name": "Chronological Cross-Reference",
                "description": "Read Bible in chronological order with cross-referenced passages",
            },
            {
                "id": "fivexfive_new_testament",
                "name": "5x5x5 New Testament",
                "description": "Read through the New Testament 5 days a week (approx. 5 minutes per day)",
            },
            {
                "id": "mcheyne",
                "name": "Robert Murray M'Cheyne",
                "description": "Classic 4-reading plan: OT History, OT Prophets/Poetry, New Testament, and Psalms",
            },
            {
                "id": "52_week_genre",
                "name": "52 Week Bible Reading Plan (Daily Genre)",
                "description": "Organized by genre: Law, History, Poetry, Prophets, Gospels, Epistles",
            },
            {
                "id": "augustine_classic",
                "name": "Augustine's Commentary Plan",
                "description": "Chronological Bible reading with Augustine's interpretive commentary illuminating deeper meanings",
            },
            {
                "id": "aquinas_classic",
                "name": "Aquinas's Commentary Plan",
                "description": "Chronological Bible reading with Aquinas's systematic theological commentary on deeper meanings",
            },
        ],
        "default": "classic",
    }


@app.get("/api/passage")
def get_passage(reference: str, version: Optional[str] = None):
    text = get_bible_reader().get_passage_text(reference, version=version)
    if not text:
        raise HTTPException(status_code=404, detail="Passage not found.")
    return text


@app.get("/api/bible/versions")
def get_bible_versions():
    reader = get_bible_reader()
    return {
        "default_version": reader.bible_sources.get("default_version", "YLT"),
        "versions": reader.get_available_versions(),
    }


@app.post("/api/commentary")
def get_commentary(request: CommentaryRequest):
    context = get_rag_system().get_relevant_context(request.passage, helper=request.helper, top_k=5)
    commentary = get_ollama_client().generate_commentary(
        passage=request.passage,
        context=context,
        helper=request.helper,
        personalized=request.personalized,
    )
    return {
        "passage": request.passage,
        "helper": request.helper,
        "commentary": commentary,
        "timestamp": datetime.utcnow(),
    }


@app.post("/api/ask")
def ask_question(request: QuestionRequest):
    context = get_rag_system().get_relevant_context(request.question, helper=request.helper, top_k=5)
    answer = get_ollama_client().generate_answer(
        question=request.question,
        context=context,
        helper=request.helper,
        additional_context=request.context,
    )
    return {
        "question": request.question,
        "helper": request.helper,
        "answer": answer,
        "timestamp": datetime.utcnow(),
    }


@app.post("/api/diary")
def save_diary(entry: DiaryEntryCreate):
    with get_db() as db:
        existing = db.query(DiaryEntry).filter_by(entry_date=entry.entry_date).first()
        if existing:
            existing.reading_passage = entry.reading_passage
            existing.personal_notes = entry.personal_notes
            existing.margin_notes = json.dumps(entry.margin_notes or {})
            existing.ai_insights = entry.ai_insights
        else:
            db.add(
                DiaryEntry(
                    entry_date=entry.entry_date,
                    reading_passage=entry.reading_passage,
                    personal_notes=entry.personal_notes,
                    margin_notes=json.dumps(entry.margin_notes or {}),
                    ai_insights=entry.ai_insights,
                )
            )
        db.commit()
    return {"message": "Diary entry saved."}


@app.get("/api/diary/{entry_date}")
def get_diary(entry_date: date):
    with get_db() as db:
        entry = db.query(DiaryEntry).filter_by(entry_date=entry_date).first()
        if not entry:
            return {"exists": False}
        return {
            "exists": True,
            "entry_date": entry.entry_date,
            "reading_passage": entry.reading_passage,
            "personal_notes": entry.personal_notes,
            "margin_notes": json.loads(entry.margin_notes) if entry.margin_notes else {},
            "ai_insights": entry.ai_insights,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
        }


@app.get("/api/progress")
def get_progress():
    with get_db() as db:
        completed = db.query(DiaryEntry).count()
        # Get reading streak (consecutive days with diary entries)
        entries = db.query(DiaryEntry.entry_date).order_by(DiaryEntry.entry_date.desc()).all()
        streak = 0
        if entries:
            today = date.today()
            expected_date = today
            for entry_date, in entries:
                if entry_date == expected_date:
                    streak += 1
                    expected_date = entry_date - timedelta(days=1)
                elif entry_date < expected_date:
                    break
        
    return {
        "completed_readings": completed,
        "total_readings": 365,
        "completion_percentage": round((completed / 365) * 100, 2),
        "reading_streak": streak,
    }


@app.get("/api/diary/export")
def export_diary():
    """Export all diary entries as JSON."""
    from fastapi.responses import Response
    
    with get_db() as db:
        entries = db.query(DiaryEntry).order_by(DiaryEntry.entry_date).all()
        export_data = []
        for entry in entries:
            export_data.append({
                "entry_date": entry.entry_date.isoformat(),
                "reading_passage": entry.reading_passage,
                "personal_notes": entry.personal_notes,
                "margin_notes": json.loads(entry.margin_notes) if entry.margin_notes else {},
                "ai_insights": entry.ai_insights,
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
                "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
            })
    
    return Response(
        content=json.dumps({"entries": export_data}, indent=2, ensure_ascii=False),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=bible-diary.json"},
    )


@app.post("/api/commentary/regenerate")
def regenerate_commentary(request: CommentaryRequest):
    """Regenerate commentary for a passage and optionally save it."""
    context = get_rag_system().get_relevant_context(request.passage, helper=request.helper, top_k=5)
    
    # Get passage text for better context
    reader = get_bible_reader()
    passage_text_obj = reader.get_passage_text(request.passage)
    passage_text = request.passage
    if passage_text_obj and passage_text_obj.get("verses"):
        verses = passage_text_obj["verses"]
        verse_lines = [f"{verse}: {text}" for verse, text in list(verses.items())[:30]]
        passage_text = f"{request.passage}\n\n" + "\n".join(verse_lines)
    
    commentary = get_ollama_client().generate_commentary(
        passage=passage_text,
        context=context,
        helper=request.helper,
        personalized=request.personalized,
    )
    
    return {
        "passage": request.passage,
        "helper": request.helper,
        "commentary": commentary,
        "timestamp": datetime.utcnow(),
    }


@app.get("/api/helpers")
def get_helpers():
    return {
        "helpers": [
            {
                "id": "augustine",
                "name": "Saint Augustine",
                "description": "Bishop of Hippo, author of Confessions and City of God.",
                "specialties": ["Conversion", "Grace", "Scripture"],
            },
            {
                "id": "aquinas",
                "name": "Saint Thomas Aquinas",
                "description": "Doctor Angelicus, author of Summa Theologica.",
                "specialties": ["Theology", "Reason", "Systematic thought"],
            },
            {
                "id": "combined",
                "name": "Combined Wisdom",
                "description": "Synthesized insights from Augustine and Aquinas.",
                "specialties": ["Balanced guidance", "Context", "Doctrine"],
            },
        ]
    }


@app.get("/api/genesis/chapters")
def get_genesis_chapters():
    """Get list of all Genesis chapters."""
    generator = get_genesis_generator()
    chapters = generator.get_all_chapters()
    return {"chapters": chapters, "book": "Genesis"}


@app.get("/api/genesis/commentary/{chapter}")
def get_genesis_commentary(chapter: int, regenerate: bool = False):
    """Get condensed commentary for a Genesis chapter."""
    if chapter < 1 or chapter > 50:
        raise HTTPException(status_code=400, detail="Chapter must be between 1 and 50")
    
    generator = get_genesis_generator()
    
    # Try to get from cache first
    if not regenerate:
        cached = generator.get_condensed_commentary(chapter)
        if cached:
            return {
                "chapter": chapter,
                "book": "Genesis",
                "commentary": cached,
                "cached": True,
            }
    
    # Generate new commentary
    try:
        commentary = generator.generate_condensed_commentary(chapter, regenerate=regenerate)
        if not commentary:
            raise HTTPException(status_code=500, detail="Failed to generate commentary")
        
        return {
            "chapter": chapter,
            "book": "Genesis",
            "commentary": commentary,
            "cached": False,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating commentary: {str(e)}")


@app.get("/api/genesis/corpus/daily/{reading_date}")
def get_daily_corpus(reading_date: date):
    """Get complete corpus for a daily reading."""
    generator = get_corpus_generator()
    corpus = generator.get_corpus_for_date(reading_date)
    
    if not corpus:
        raise HTTPException(
            status_code=404,
            detail=f"Corpus not found for {reading_date}. Run batch generation first."
        )
    
    return corpus


@app.get("/api/genesis/corpus/chapter/{chapter}")
def get_chapter_corpus(chapter: int):
    """Get all corpus entries for a Genesis chapter."""
    if chapter < 1 or chapter > 50:
        raise HTTPException(status_code=400, detail="Chapter must be between 1 and 50")
    
    generator = get_corpus_generator()
    corpus_list = generator.get_corpus_for_chapter(chapter)
    
    return {
        "chapter": chapter,
        "book": "Genesis",
        "entries": corpus_list,
        "count": len(corpus_list)
    }


@app.get("/api/genesis/corpus/index")
def get_corpus_index():
    """Get corpus index."""
    generator = get_corpus_generator()
    index = generator.load_index()
    
    if not index:
        return {
            "exists": False,
            "message": "Corpus index not found. Run batch generation first."
        }
    
    return {
        "exists": True,
        "index": index
    }


@app.post("/api/genesis/corpus/generate")
def generate_corpus(include_web: bool = True, year: int = 2024):
    """Generate complete corpus for all Genesis readings (batch operation)."""
    generator = get_corpus_generator()
    
    try:
        result = generator.generate_all_corpus(
            year=year,
            include_web_data=include_web,
            progress_callback=lambda i, total, passage, corpus: print(
                f"[{i}/{total}] {passage}"
            )
        )
        
        return {
            "status": "completed",
            "total": result["total"],
            "generated": result["generated"],
            "errors": result["errors"],
            "message": f"Generated {result['generated']} corpus entries"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating corpus: {str(e)}")


# ===== AI Persona Conversations =====

class PersonaChatRequest(BaseModel):
    message: str
    persona: str = "augustine"
    conversation_id: Optional[str] = None
    context_passage: Optional[str] = None


@app.post("/api/persona/chat")
def persona_chat(request: PersonaChatRequest):
    """Chat with an AI persona (Augustine, Aquinas, etc.)."""
    engine = get_persona_engine()
    
    try:
        result = engine.chat_with_persona(
            persona=request.persona,
            message=request.message,
            conversation_id=request.conversation_id,
            context_passage=request.context_passage
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in persona chat: {str(e)}")


@app.get("/api/persona/conversation/{conversation_id}")
def get_conversation_summary(conversation_id: str):
    """Get summary of a conversation."""
    engine = get_persona_engine()
    return engine.get_conversation_summary(conversation_id)


# ===== Narrative Reconstruction Engine =====

@app.get("/api/narrative/stories")
def list_stories():
    """List all available biblical stories."""
    engine = get_narrative_engine()
    return {"stories": engine.list_available_stories()}


@app.get("/api/narrative/story/{story_id}")
def get_story(story_id: str):
    """Get a reconstructed biblical story."""
    engine = get_narrative_engine()
    story = engine.get_predefined_story(story_id)
    
    if not story:
        raise HTTPException(status_code=404, detail=f"Story '{story_id}' not found")
    
    # Convert to dict for JSON response
    return {
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


class ReconstructStoryRequest(BaseModel):
    name: str
    passages: List[str]


@app.post("/api/narrative/reconstruct")
def reconstruct_story(request: ReconstructStoryRequest):
    """Reconstruct a story from passages."""
    engine = get_narrative_engine()
    
    try:
        story = engine.reconstruct_story(request.name, request.passages)
        filepath = engine.save_story(story)
        
        return {
            "name": story.name,
            "description": story.description,
            "segments_count": len(story.segments),
            "saved_to": str(filepath)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reconstructing story: {str(e)}")


# ===== Predictive Spiritual Companion =====

@app.get("/api/predictive/insights/{passage}")
def get_proactive_insights(passage: str, reading_date: Optional[date] = None):
    """Get proactive insights for a passage."""
    companion = get_predictive_companion()
    
    if not reading_date:
        reading_date = date.today()
    
    # Get user reading history
    with get_db() as db:
        entries = db.query(DiaryEntry).order_by(DiaryEntry.entry_date.desc()).limit(20).all()
        user_history = [e.reading_passage for e in entries if e.reading_passage]
    
    try:
        insights = companion.get_proactive_insights(
            passage=passage,
            reading_date=reading_date,
            user_history=user_history
        )
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting insights: {str(e)}")


class ReadingPathRequest(BaseModel):
    goal: str
    current_progress: Optional[List[str]] = None


@app.post("/api/predictive/reading-path")
def suggest_reading_path(request: ReadingPathRequest):
    """Suggest a personalized reading path."""
    companion = get_predictive_companion()
    
    # Get current progress from diary
    current_progress = request.current_progress or []
    if not current_progress:
        with get_db() as db:
            entries = db.query(DiaryEntry).order_by(DiaryEntry.entry_date.desc()).limit(10).all()
            current_progress = [e.reading_passage for e in entries if e.reading_passage]
    
    # Get reading streak
    with get_db() as db:
        entries = db.query(DiaryEntry.entry_date).order_by(DiaryEntry.entry_date.desc()).all()
        streak = 0
        today = date.today()
        expected_date = today
        for entry_date, in entries:
            if entry_date == expected_date:
                streak += 1
                expected_date = entry_date - timedelta(days=1)
            elif entry_date < expected_date:
                break
    
    try:
        paths = companion.suggest_reading_path(
            goal=request.goal,
            current_progress=current_progress,
            reading_streak=streak
        )
        return {
            "paths": [
                {
                    "name": path.name,
                    "description": path.description,
                    "passages": path.passages,
                    "reason": path.reason,
                    "estimated_time": path.estimated_time
                }
                for path in paths
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error suggesting path: {str(e)}")


@app.get("/api/predictive/patterns")
def get_reading_patterns():
    """Get user's reading patterns and analysis."""
    companion = get_predictive_companion()
    return companion.get_user_reading_patterns()


# ===== Living Commentary System =====

@app.get("/api/commentary/latest/{passage}")
def get_latest_commentary(passage: str, helper: str = "augustine"):
    """Get latest version of a commentary."""
    system = get_living_commentary()
    version = system.get_latest_version(passage, helper)
    
    if not version:
        raise HTTPException(status_code=404, detail="Commentary not found. Generate one first.")
    
    return {
        "version": version.version,
        "passage": version.passage,
        "content": version.content,
        "helper": version.helper,
        "generated_at": version.generated_at,
        "quality_score": version.quality_score,
        "user_feedback_count": len(version.user_feedback),
        "improvements": version.improvements
    }


@app.get("/api/commentary/versions/{passage}")
def get_commentary_versions(passage: str, helper: str = "augustine"):
    """Get all versions of a commentary."""
    system = get_living_commentary()
    versions = system.get_all_versions(passage, helper)
    
    return {
        "passage": passage,
        "helper": helper,
        "versions": [
            {
                "version": v.version,
                "generated_at": v.generated_at,
                "quality_score": v.quality_score,
                "feedback_count": len(v.user_feedback),
                "improvements": v.improvements
            }
            for v in versions
        ]
    }


class CommentaryFeedbackRequest(BaseModel):
    passage: str
    helper: str
    feedback: str
    rating: Optional[int] = None
    version: Optional[int] = None


@app.post("/api/commentary/feedback")
def add_commentary_feedback(request: CommentaryFeedbackRequest):
    """Add feedback to a commentary version."""
    system = get_living_commentary()
    
    try:
        updated_version = system.add_feedback(
            passage=request.passage,
            helper=request.helper,
            feedback=request.feedback,
            rating=request.rating,
            version=request.version
        )
        
        return {
            "version": updated_version.version,
            "passage": updated_version.passage,
            "feedback_added": True,
            "new_version_generated": updated_version.version > (request.version or 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding feedback: {str(e)}")


@app.get("/api/commentary/conflicts/{passage}")
def detect_commentary_conflicts(passage: str):
    """Detect conflicts between different commentary perspectives."""
    system = get_living_commentary()
    
    try:
        conflicts = system.detect_conflicts(passage)
        return {
            "passage": passage,
            "conflicts": [
                {
                    "issue": conflict.issue,
                    "augustine_view": conflict.augustine_view[:300],
                    "aquinas_view": conflict.aquinas_view[:300],
                    "resolution": conflict.resolution
                }
                for conflict in conflicts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting conflicts: {str(e)}")


# ===== Theological DNA Profile =====

@app.get("/api/theological-profile")
def get_theological_profile_endpoint(user_id: str = "default", rebuild: bool = False):
    """Get user's theological profile."""
    engine = get_theological_profile()
    
    if rebuild:
        profile = engine.build_profile(user_id)
    else:
        profile = engine.get_profile(user_id)
    
    return {
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


# ===== Autonomous Study Agent =====

class CreateStudyPlanRequest(BaseModel):
    goal_description: str
    user_level: str = "intermediate"
    user_id: str = "default"


@app.post("/api/study-agent/create-plan")
def create_study_plan(request: CreateStudyPlanRequest):
    """Create a personalized study plan."""
    agent = get_study_agent()
    
    try:
        plan = agent.create_study_plan(
            goal_description=request.goal_description,
            user_level=request.user_level,
            user_id=request.user_id
        )
        
        return {
            "plan_id": plan.plan_id,
            "goal": {
                "goal_id": plan.goal.goal_id,
                "description": plan.goal.description,
                "target_passages": plan.goal.target_passages,
                "estimated_days": plan.goal.estimated_days
            },
            "sessions_count": len(plan.sessions),
            "overall_progress": plan.overall_progress
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating study plan: {str(e)}")


@app.get("/api/study-agent/active-plan")
def get_active_study_plan(user_id: str = "default"):
    """Get active study plan."""
    agent = get_study_agent()
    plan = agent.get_active_plan(user_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="No active study plan found")
    
    return {
        "plan_id": plan.plan_id,
        "goal": {
            "description": plan.goal.description,
            "status": plan.goal.status
        },
        "current_session": plan.sessions[plan.current_session_index] if plan.sessions else None,
        "overall_progress": plan.overall_progress,
        "sessions": [
            {
                "session_id": s.session_id,
                "passage": s.passage,
                "date": s.date,
                "understanding_score": s.understanding_score
            }
            for s in plan.sessions
        ]
    }


@app.get("/api/study-agent/quiz/{passage}")
def generate_quiz(passage: str, difficulty: str = "intermediate"):
    """Generate quiz questions for a passage."""
    agent = get_study_agent()
    
    try:
        questions = agent.generate_quiz(passage, difficulty)
        return {"passage": passage, "questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


class SubmitQuizAnswersRequest(BaseModel):
    passage: str
    answers: Dict[str, str]
    questions: List[Dict[str, Any]]


@app.post("/api/study-agent/assess")
def assess_understanding(request: SubmitQuizAnswersRequest):
    """Assess understanding from quiz answers."""
    agent = get_study_agent()
    
    try:
        score = agent.assess_understanding(
            request.passage,
            request.answers,
            request.questions
        )
        return {
            "passage": request.passage,
            "understanding_score": score,
            "feedback": "Good understanding" if score > 0.7 else "Needs more study" if score > 0.4 else "Review recommended"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing understanding: {str(e)}")


# ===== Living Bible Timeline =====

@app.get("/api/timeline/events")
def get_timeline_events(
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    category: Optional[str] = None
):
    """Get timeline events."""
    timeline = get_bible_timeline()
    
    events = timeline.get_timeline(start_date, end_date, category)
    
    return {
        "events": [
            {
                "event_id": e.event_id,
                "title": e.title,
                "description": e.description,
                "date_estimate": e.date_estimate,
                "date_numeric": e.date_numeric,
                "passages": e.passages,
                "characters": e.characters,
                "location": e.location,
                "category": e.category,
                "significance": e.significance
            }
            for e in events
        ]
    }


@app.get("/api/timeline/event/{event_id}")
def get_timeline_event(event_id: str):
    """Get a specific timeline event."""
    timeline = get_bible_timeline()
    event = timeline.get_event(event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    connected = timeline.get_connected_events(event_id)
    
    return {
        "event": {
            "event_id": event.event_id,
            "title": event.title,
            "description": event.description,
            "date_estimate": event.date_estimate,
            "passages": event.passages,
            "characters": event.characters,
            "location": event.location,
            "category": event.category,
            "significance": event.significance
        },
        "connected_events": [
            {
                "event_id": e.event_id,
                "title": e.title,
                "date_estimate": e.date_estimate
            }
            for e in connected
        ]
    }


@app.get("/api/timeline/periods")
def get_timeline_periods():
    """Get timeline periods."""
    timeline = get_bible_timeline()
    periods = timeline.get_periods()
    
    return {
        "periods": [
            {
                "period_id": p.period_id,
                "name": p.name,
                "start_date": p.start_date,
                "end_date": p.end_date,
                "description": p.description,
                "key_events": p.key_events,
                "themes": p.themes
            }
            for p in periods
        ]
    }


@app.get("/api/timeline/passage/{passage}")
def get_events_for_passage(passage: str):
    """Get timeline events for a passage."""
    timeline = get_bible_timeline()
    events = timeline.get_events_for_passage(passage)
    
    return {
        "passage": passage,
        "events": [
            {
                "event_id": e.event_id,
                "title": e.title,
                "date_estimate": e.date_estimate,
                "description": e.description
            }
            for e in events
        ]
    }


# ===== Cross-Temporal Dialogue =====

class DebateRequest(BaseModel):
    question: str
    persona1: str = "augustine"
    persona2: str = "aquinas"
    context_passage: Optional[str] = None


@app.post("/api/persona/debate")
def persona_debate(request: DebateRequest):
    """Get debate-style responses from two personas."""
    engine = get_persona_engine()
    
    try:
        result = engine.debate_mode(
            question=request.question,
            persona1=request.persona1,
            persona2=request.persona2,
            context_passage=request.context_passage
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in debate: {str(e)}")


class PanelRequest(BaseModel):
    question: str
    personas: List[str]
    context_passage: Optional[str] = None


@app.post("/api/persona/panel")
def persona_panel(request: PanelRequest):
    """Get panel-style responses from multiple personas."""
    engine = get_persona_engine()
    
    try:
        result = engine.panel_discussion(
            question=request.question,
            personas=request.personas,
            context_passage=request.context_passage
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in panel discussion: {str(e)}")


class HistoricalQARequest(BaseModel):
    question: str
    historical_figure: str
    time_period: Optional[str] = None


@app.post("/api/persona/historical-qa")
def historical_qa(request: HistoricalQARequest):
    """Get response from historical figure with period context."""
    engine = get_persona_engine()
    
    try:
        result = engine.historical_qa(
            question=request.question,
            historical_figure=request.historical_figure,
            time_period=request.time_period
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in historical Q&A: {str(e)}")


# ===== Character Study System =====

@app.get("/api/characters")
def list_characters(category: Optional[str] = None):
    """List all characters, optionally filtered by category."""
    system = get_character_study()
    characters = system.list_characters(category)
    
    return {
        "characters": [
            {
                "character_id": c.character_id,
                "name": c.name,
                "category": c.category,
                "description": c.description,
                "significance": c.significance,
                "key_passages": c.key_passages[:3]
            }
            for c in characters
        ]
    }


@app.get("/api/characters/{character_id}")
def get_character_profile(character_id: str):
    """Get detailed profile for a character."""
    system = get_character_study()
    profile = system.get_character_profile(character_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Character not found")
    
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


@app.get("/api/characters/{character_id}/arc")
def get_character_arc(character_id: str):
    """Get character development arc."""
    system = get_character_study()
    arc = system.get_character_arc(character_id)
    
    if not arc:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "character_id": arc.character_id,
        "stages": arc.stages,
        "turning_points": arc.turning_points,
        "growth_pattern": arc.growth_pattern,
        "transformation": arc.transformation
    }


@app.get("/api/characters/{character_id}/relationships")
def get_character_relationships(character_id: str):
    """Get relationships for a character."""
    system = get_character_study()
    relationships = system.get_character_relationships(character_id)
    
    return {
        "character_id": character_id,
        "relationships": [
            {
                "character1": r.character1,
                "character2": r.character2,
                "relationship_type": r.relationship_type,
                "passages": r.passages,
                "description": r.description,
                "significance": r.significance
            }
            for r in relationships
        ]
    }


@app.get("/api/characters/compare")
def compare_characters(character_ids: str):
    """Compare two or more characters (comma-separated IDs)."""
    system = get_character_study()
    ids = [id.strip() for id in character_ids.split(",")]
    
    comparison = system.compare_characters(ids)
    
    if not comparison:
        raise HTTPException(status_code=400, detail="Need at least 2 characters to compare")
    
    return {
        "characters": comparison.characters,
        "similarities": comparison.similarities,
        "differences": comparison.differences,
        "passages": comparison.passages,
        "insights": comparison.insights
    }


@app.get("/api/characters/{character_id}/study-questions")
def get_study_questions(character_id: str, difficulty: str = "intermediate"):
    """Generate study questions for a character."""
    system = get_character_study()
    questions = system.generate_study_questions(character_id, difficulty)
    
    return {
        "character_id": character_id,
        "difficulty": difficulty,
        "questions": questions
    }


@app.get("/api/characters/passage/{passage}")
def get_characters_for_passage(passage: str):
    """Find characters mentioned in a passage."""
    system = get_character_study()
    characters = system.get_characters_for_passage(passage)
    
    return {
        "passage": passage,
        "characters": [
            {
                "character_id": c.character_id,
                "name": c.name,
                "category": c.category,
                "description": c.description
            }
            for c in characters
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
