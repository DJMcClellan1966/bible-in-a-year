"""
Bible in a Year backend API.
"""

from datetime import date, datetime
import json
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .database import DiaryEntry, get_db, init_db
from .bible_reader import BibleReader
from .rag_system import RAGSystem
from .ollama_client import OllamaClient


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


app = FastAPI(
    title="Bible in a Year",
    version="0.1.0",
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


@app.on_event("startup")
async def startup_event():
    init_db()


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
def get_daily_reading(reading_date: date, version: Optional[str] = None):
    reader = get_bible_reader()
    reading = reader.get_reading_for_date(reading_date)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found.")
    passages_text = {}
    for passage in reading.get("passages", []):
        passages_text[passage] = reader.get_passage_text(passage, version=version)
    return {"date": reading_date, "passage_text": passages_text, **reading}


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
    return {
        "completed_readings": completed,
        "total_readings": 365,
        "completion_percentage": round((completed / 365) * 100, 2),
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
