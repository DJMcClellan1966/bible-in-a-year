"""
Database setup for Bible in a Year app.
"""

from contextlib import contextmanager
from datetime import datetime, date
from pathlib import Path

from sqlalchemy import Column, Date, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DB_PATH = Path(__file__).parent.parent / "bible_app.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_date = Column(Date, unique=True, index=True, nullable=False)
    reading_passage = Column(Text, nullable=False)
    personal_notes = Column(Text, nullable=True)
    margin_notes = Column(Text, nullable=True)  # JSON string
    ai_insights = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
