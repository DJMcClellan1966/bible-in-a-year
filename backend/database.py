"""
Database setup and session management for Bible in a Year app
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'bible_app.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """User model for personalization and progress tracking"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    diary_entries = relationship("DiaryEntry", back_populates="user")
    readings = relationship("Reading", back_populates="user")

class Reading(Base):
    """Bible reading assignments for each day"""
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    passages = Column(Text, nullable=False)  # JSON string of passages
    theme = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For personalized plans

    # Relationships
    user = relationship("User", back_populates="readings")
    diary_entries = relationship("DiaryEntry", back_populates="reading")

class DiaryEntry(Base):
    """Personal diary entries for each reading"""
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reading_id = Column(Integer, ForeignKey("readings.id"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    reading_passage = Column(Text, nullable=False)
    personal_notes = Column(Text, nullable=True)
    margin_notes = Column(Text, nullable=True)  # JSON string of margin notes
    ai_insights = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="diary_entries")
    reading = relationship("Reading", back_populates="diary_entries")

class AIHelper(Base):
    """Available AI helpers and their configurations"""
    __tablename__ = "ai_helpers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    model_path = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReadingProgress(Base):
    """Track reading progress and completion"""
    __tablename__ = "reading_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reading_id = Column(Integer, ForeignKey("readings.id"), nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    time_spent_minutes = Column(Integer, default=0)

    # Relationships
    user = relationship("User")
    reading = relationship("Reading")

def init_db():
    """Initialize the database and create tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")

        # Create default user if not exists
        with get_db() as session:
            default_user = session.query(User).filter_by(username="default").first()
            if not default_user:
                default_user = User(username="default", email="user@localhost")
                session.add(default_user)
                session.commit()
                print("Default user created")

        return engine
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()