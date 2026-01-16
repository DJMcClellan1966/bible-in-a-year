"""
Bible in a Year App with AI Helpers
Backend API using FastAPI with RAG-powered AI assistants
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from datetime import datetime, date
import json

# Import our modules
from .database import init_db, get_db
from .models import User, Reading, DiaryEntry, AIHelper
from .rag_system import RAGSystem
from .ollama_client import OllamaClient
from .bible_reader import BibleReader

app = FastAPI(
    title="Bible in a Year with AI Helpers",
    description="A spiritual journey companion powered by AI interpretations from Saints Augustine and Aquinas",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="../static"), name="static")

# Initialize components
db = init_db()
rag_system = RAGSystem()
ollama_client = OllamaClient()
bible_reader = BibleReader()

# Pydantic models for API
class ReadingPlan(BaseModel):
    date: date
    passages: List[str]
    theme: Optional[str] = None

class DiaryEntryCreate(BaseModel):
    date: date
    reading_passage: str
    personal_notes: Optional[str] = None
    margin_notes: Optional[Dict[str, str]] = None
    ai_insights: Optional[str] = None

class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None
    helper: str = "augustine"  # Options: augustine, aquinas, combined

class CommentaryRequest(BaseModel):
    passage: str
    helper: str = "augustine"
    personalized: bool = False

@app.get("/")
async def root():
    """Root endpoint with app information"""
    return {
        "message": "Bible in a Year with AI Helpers",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Daily Bible readings",
            "AI-powered commentary from Saints Augustine and Aquinas",
            "Personal diary with margin notes",
            "Progress tracking",
            "Offline-friendly"
        ]
    }

@app.get("/api/readings/{reading_date}")
async def get_daily_reading(reading_date: date):
    """Get the daily Bible reading for a specific date"""
    try:
        reading = bible_reader.get_reading_for_date(reading_date)
        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found for this date")

        return {
            "date": reading_date,
            "passages": reading["passages"],
            "theme": reading.get("theme"),
            "text": reading.get("text")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/diary")
async def create_diary_entry(entry: DiaryEntryCreate):
    """Create or update a diary entry for a reading"""
    try:
        with get_db() as session:
            # Check if entry exists
            existing = session.query(DiaryEntry).filter_by(
                user_id=1,  # Default user for now
                date=entry.date
            ).first()

            if existing:
                # Update existing
                existing.personal_notes = entry.personal_notes
                existing.margin_notes = json.dumps(entry.margin_notes) if entry.margin_notes else None
                existing.ai_insights = entry.ai_insights
            else:
                # Create new
                new_entry = DiaryEntry(
                    user_id=1,
                    date=entry.date,
                    reading_passage=entry.reading_passage,
                    personal_notes=entry.personal_notes,
                    margin_notes=json.dumps(entry.margin_notes) if entry.margin_notes else None,
                    ai_insights=entry.ai_insights
                )
                session.add(new_entry)

            session.commit()
            return {"message": "Diary entry saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/diary/{entry_date}")
async def get_diary_entry(entry_date: date):
    """Get diary entry for a specific date"""
    try:
        with get_db() as session:
            entry = session.query(DiaryEntry).filter_by(
                user_id=1,
                date=entry_date
            ).first()

            if not entry:
                return {"date": entry_date, "exists": False}

            return {
                "date": entry.date,
                "reading_passage": entry.reading_passage,
                "personal_notes": entry.personal_notes,
                "margin_notes": json.loads(entry.margin_notes) if entry.margin_notes else None,
                "ai_insights": entry.ai_insights,
                "created_at": entry.created_at,
                "updated_at": entry.updated_at
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/commentary")
async def get_ai_commentary(request: CommentaryRequest):
    """Get AI-powered commentary on a Bible passage"""
    try:
        # Get relevant context from RAG system
        context = rag_system.get_relevant_context(
            request.passage,
            helper=request.helper,
            top_k=5
        )

        # Generate commentary using Ollama
        commentary = await ollama_client.generate_commentary(
            passage=request.passage,
            context=context,
            helper=request.helper,
            personalized=request.personalized
        )

        return {
            "passage": request.passage,
            "helper": request.helper,
            "commentary": commentary,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ask")
async def ask_ai_helper(request: QuestionRequest):
    """Ask a question to an AI helper"""
    try:
        # Get relevant context from RAG system
        context = rag_system.get_relevant_context(
            request.question,
            helper=request.helper,
            top_k=3
        )

        # Generate answer using Ollama
        answer = await ollama_client.generate_answer(
            question=request.question,
            context=context,
            helper=request.helper,
            additional_context=request.context
        )

        return {
            "question": request.question,
            "helper": request.helper,
            "answer": answer,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/progress")
async def get_reading_progress():
    """Get user's reading progress"""
    try:
        with get_db() as session:
            total_readings = session.query(Reading).count()
            completed_readings = session.query(DiaryEntry).filter(
                DiaryEntry.user_id == 1,
                DiaryEntry.personal_notes.isnot(None)
            ).count()

            return {
                "total_readings": total_readings,
                "completed_readings": completed_readings,
                "completion_percentage": (completed_readings / total_readings * 100) if total_readings > 0 else 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/helpers")
async def get_available_helpers():
    """Get list of available AI helpers"""
    return {
        "helpers": [
            {
                "id": "augustine",
                "name": "Saint Augustine",
                "description": "Bishop of Hippo, Doctor of the Church, known for Confessions and City of God",
                "specialties": ["Scripture interpretation", "Philosophy of God", "Personal conversion"]
            },
            {
                "id": "aquinas",
                "name": "Saint Thomas Aquinas",
                "description": "Doctor Angelicus, Summa Theologica, integration of faith and reason",
                "specialties": ["Theological reasoning", "Natural law", "Systematic theology"]
            },
            {
                "id": "combined",
                "name": "Combined Wisdom",
                "description": "Insights from both Augustine and Aquinas",
                "specialties": ["Comprehensive analysis", "Historical context", "Doctrinal clarity"]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )