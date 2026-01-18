"""
Living Bible Timeline System.
Interactive 3D timeline of Bible events with connections and context.
"""

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .bible_reader import BibleReader


@dataclass
class TimelineEvent:
    """A single event on the Bible timeline."""
    event_id: str
    title: str
    description: str
    date_estimate: str  # e.g., "2000 BC", "30 AD"
    date_numeric: int  # For sorting (negative for BC)
    passages: List[str]
    characters: List[str]
    location: str
    category: str  # "creation", "patriarch", "exodus", "kingdom", "prophet", "gospel", "church"
    connections: List[str]  # IDs of connected events
    significance: str


@dataclass
class TimelinePeriod:
    """A period on the timeline."""
    period_id: str
    name: str
    start_date: int
    end_date: int
    description: str
    key_events: List[str]  # Event IDs
    themes: List[str]


class LivingBibleTimeline:
    """Manages interactive Bible timeline with events and connections."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.timeline_dir = self.data_dir / "bible_timeline"
        self.timeline_dir.mkdir(parents=True, exist_ok=True)
        
        self.events_file = self.timeline_dir / "events.json"
        self.periods_file = self.timeline_dir / "periods.json"
        
        self.bible_reader: Optional[BibleReader] = None
        
        # Initialize default timeline if needed
        if not self.events_file.exists():
            self._initialize_default_timeline()
    
    def _get_bible_reader(self) -> BibleReader:
        if self.bible_reader is None:
            self.bible_reader = BibleReader()
        return self.bible_reader
    
    def _initialize_default_timeline(self) -> None:
        """Initialize default Bible timeline with major events."""
        events = [
            TimelineEvent(
                event_id="creation",
                title="Creation",
                description="God creates the heavens and the earth, and all living things.",
                date_estimate="4000 BC",
                date_numeric=-4000,
                passages=["Genesis 1-2"],
                characters=["God", "Adam", "Eve"],
                location="Garden of Eden",
                category="creation",
                connections=[],
                significance="Foundation of all existence and relationship with God"
            ),
            TimelineEvent(
                event_id="fall",
                title="The Fall",
                description="Adam and Eve disobey God and sin enters the world.",
                date_estimate="3900 BC",
                date_numeric=-3900,
                passages=["Genesis 3"],
                characters=["Adam", "Eve", "Serpent"],
                location="Garden of Eden",
                category="creation",
                connections=["creation"],
                significance="Introduction of sin and need for redemption"
            ),
            TimelineEvent(
                event_id="flood",
                title="The Great Flood",
                description="God sends a flood to cleanse the earth, saving Noah and his family.",
                date_estimate="2500 BC",
                date_numeric=-2500,
                passages=["Genesis 6-9"],
                characters=["Noah", "God"],
                location="Earth",
                category="patriarch",
                connections=["fall"],
                significance="God's judgment and preservation of the righteous"
            ),
            TimelineEvent(
                event_id="abraham_call",
                title="Call of Abraham",
                description="God calls Abraham to leave his homeland and promises to make him a great nation.",
                date_estimate="2000 BC",
                date_numeric=-2000,
                passages=["Genesis 12"],
                characters=["Abraham", "God"],
                location="Ur / Canaan",
                category="patriarch",
                connections=[],
                significance="Beginning of God's covenant with His people"
            ),
            TimelineEvent(
                event_id="exodus",
                title="The Exodus",
                description="God delivers Israel from slavery in Egypt through Moses.",
                date_estimate="1446 BC",
                date_numeric=-1446,
                passages=["Exodus 1-15"],
                characters=["Moses", "Aaron", "Pharaoh"],
                location="Egypt / Red Sea",
                category="exodus",
                connections=["abraham_call"],
                significance="God's deliverance and establishment of the Law"
            ),
            TimelineEvent(
                event_id="david_king",
                title="David Becomes King",
                description="David is anointed king of Israel, establishing the Davidic dynasty.",
                date_estimate="1000 BC",
                date_numeric=-1000,
                passages=["1 Samuel 16", "2 Samuel 2"],
                characters=["David", "Samuel", "Saul"],
                location="Israel",
                category="kingdom",
                connections=["abraham_call"],
                significance="Establishment of the Davidic covenant"
            ),
            TimelineEvent(
                event_id="exile",
                title="Babylonian Exile",
                description="Jerusalem is destroyed and the people are taken into exile in Babylon.",
                date_estimate="586 BC",
                date_numeric=-586,
                passages=["2 Kings 25", "Jeremiah 52"],
                characters=["Nebuchadnezzar", "Zedekiah"],
                location="Jerusalem / Babylon",
                category="prophet",
                connections=["david_king"],
                significance="Judgment and preparation for restoration"
            ),
            TimelineEvent(
                event_id="jesus_birth",
                title="Birth of Jesus",
                description="Jesus Christ is born in Bethlehem, fulfilling Messianic prophecies.",
                date_estimate="4 BC",
                date_numeric=-4,
                passages=["Matthew 1-2", "Luke 1-2"],
                characters=["Jesus", "Mary", "Joseph"],
                location="Bethlehem",
                category="gospel",
                connections=["abraham_call", "david_king"],
                significance="Incarnation - God becomes man"
            ),
            TimelineEvent(
                event_id="jesus_crucifixion",
                title="Crucifixion and Resurrection",
                description="Jesus is crucified and rises from the dead, providing salvation for all.",
                date_estimate="30 AD",
                date_numeric=30,
                passages=["Matthew 27-28", "Mark 15-16", "Luke 23-24", "John 19-20"],
                characters=["Jesus", "Pilate", "Mary Magdalene"],
                location="Jerusalem",
                category="gospel",
                connections=["jesus_birth", "fall"],
                significance="Atonement for sin and victory over death"
            ),
            TimelineEvent(
                event_id="pentecost",
                title="Pentecost",
                description="The Holy Spirit descends on the apostles, beginning the Church age.",
                date_estimate="30 AD",
                date_numeric=30,
                passages=["Acts 2"],
                characters=["Peter", "Apostles"],
                location="Jerusalem",
                category="church",
                connections=["jesus_crucifixion"],
                significance="Birth of the Church and empowerment for mission"
            )
        ]
        
        periods = [
            TimelinePeriod(
                period_id="creation_period",
                name="Creation to Flood",
                start_date=-4000,
                end_date=-2500,
                description="From creation through the flood",
                key_events=["creation", "fall", "flood"],
                themes=["Creation", "Sin", "Judgment", "Preservation"]
            ),
            TimelinePeriod(
                period_id="patriarch_period",
                name="Patriarchs",
                start_date=-2000,
                end_date=-1500,
                description="Age of the patriarchs: Abraham, Isaac, Jacob, Joseph",
                key_events=["abraham_call"],
                themes=["Covenant", "Promise", "Faith"]
            ),
            TimelinePeriod(
                period_id="exodus_period",
                name="Exodus and Law",
                start_date=-1500,
                end_date=-1000,
                description="Exodus from Egypt and giving of the Law",
                key_events=["exodus"],
                themes=["Deliverance", "Law", "Covenant"]
            ),
            TimelinePeriod(
                period_id="kingdom_period",
                name="Kingdom of Israel",
                start_date=-1000,
                end_date=-586,
                description="United and divided kingdoms",
                key_events=["david_king", "exile"],
                themes=["Kingship", "Covenant", "Prophecy"]
            ),
            TimelinePeriod(
                period_id="gospel_period",
                name="Life of Christ",
                start_date=-4,
                end_date=30,
                description="Birth, ministry, death, and resurrection of Jesus",
                key_events=["jesus_birth", "jesus_crucifixion"],
                themes=["Incarnation", "Atonement", "Resurrection"]
            ),
            TimelinePeriod(
                period_id="church_period",
                name="Early Church",
                start_date=30,
                end_date=100,
                description="Birth and growth of the early Church",
                key_events=["pentecost"],
                themes=["Holy Spirit", "Mission", "Growth"]
            )
        ]
        
        self._save_events(events)
        self._save_periods(periods)
    
    def get_timeline(
        self,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[TimelineEvent]:
        """Get timeline events within date range and category."""
        events = self._load_events()
        
        filtered = events
        
        if start_date is not None:
            filtered = [e for e in filtered if e.date_numeric >= start_date]
        
        if end_date is not None:
            filtered = [e for e in filtered if e.date_numeric <= end_date]
        
        if category:
            filtered = [e for e in filtered if e.category == category]
        
        return sorted(filtered, key=lambda e: e.date_numeric)
    
    def get_event(self, event_id: str) -> Optional[TimelineEvent]:
        """Get a specific event by ID."""
        events = self._load_events()
        for event in events:
            if event.event_id == event_id:
                return event
        return None
    
    def get_connected_events(self, event_id: str) -> List[TimelineEvent]:
        """Get all events connected to a given event."""
        event = self.get_event(event_id)
        if not event:
            return []
        
        events = self._load_events()
        connected = [e for e in events if e.event_id in event.connections]
        connected.extend([e for e in events if event_id in e.connections])
        
        return connected
    
    def get_periods(self) -> List[TimelinePeriod]:
        """Get all timeline periods."""
        return self._load_periods()
    
    def get_events_for_passage(self, passage: str) -> List[TimelineEvent]:
        """Find timeline events related to a passage."""
        events = self._load_events()
        matching = []
        
        # Simple matching - could be enhanced
        passage_lower = passage.lower()
        for event in events:
            for event_passage in event.passages:
                if passage_lower in event_passage.lower() or event_passage.lower() in passage_lower:
                    matching.append(event)
                    break
        
        return matching
    
    def add_custom_event(
        self,
        title: str,
        description: str,
        date_estimate: str,
        passages: List[str],
        characters: List[str] = None,
        location: str = "",
        category: str = "custom",
        connections: List[str] = None
    ) -> TimelineEvent:
        """Add a custom event to the timeline."""
        # Parse date
        date_numeric = self._parse_date(date_estimate)
        
        event = TimelineEvent(
            event_id=f"custom_{len(self._load_events())}",
            title=title,
            description=description,
            date_estimate=date_estimate,
            date_numeric=date_numeric,
            passages=passages or [],
            characters=characters or [],
            location=location,
            category=category,
            connections=connections or [],
            significance=""
        )
        
        events = self._load_events()
        events.append(event)
        self._save_events(events)
        
        return event
    
    def _parse_date(self, date_str: str) -> int:
        """Parse date string to numeric value (negative for BC)."""
        date_str = date_str.strip().upper()
        if "BC" in date_str:
            year = int(date_str.replace("BC", "").strip())
            return -year
        elif "AD" in date_str:
            year = int(date_str.replace("AD", "").strip())
            return year
        else:
            # Try to parse as number
            try:
                year = int(date_str)
                return -year if year > 1000 else year
            except:
                return 0
    
    def _load_events(self) -> List[TimelineEvent]:
        """Load events from file."""
        if not self.events_file.exists():
            return []
        
        try:
            data = json.loads(self.events_file.read_text(encoding="utf-8"))
            return [self._event_from_dict(d) for d in data]
        except Exception:
            return []
    
    def _save_events(self, events: List[TimelineEvent]) -> None:
        """Save events to file."""
        data = [self._event_to_dict(e) for e in events]
        self.events_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def _load_periods(self) -> List[TimelinePeriod]:
        """Load periods from file."""
        if not self.periods_file.exists():
            return []
        
        try:
            data = json.loads(self.periods_file.read_text(encoding="utf-8"))
            return [self._period_from_dict(d) for d in data]
        except Exception:
            return []
    
    def _save_periods(self, periods: List[TimelinePeriod]) -> None:
        """Save periods to file."""
        data = [self._period_to_dict(p) for p in periods]
        self.periods_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def _event_to_dict(self, event: TimelineEvent) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": event.event_id,
            "title": event.title,
            "description": event.description,
            "date_estimate": event.date_estimate,
            "date_numeric": event.date_numeric,
            "passages": event.passages,
            "characters": event.characters,
            "location": event.location,
            "category": event.category,
            "connections": event.connections,
            "significance": event.significance
        }
    
    def _event_from_dict(self, data: Dict[str, Any]) -> TimelineEvent:
        """Reconstruct event from dictionary."""
        return TimelineEvent(
            event_id=data.get("event_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            date_estimate=data.get("date_estimate", ""),
            date_numeric=data.get("date_numeric", 0),
            passages=data.get("passages", []),
            characters=data.get("characters", []),
            location=data.get("location", ""),
            category=data.get("category", ""),
            connections=data.get("connections", []),
            significance=data.get("significance", "")
        )
    
    def _period_to_dict(self, period: TimelinePeriod) -> Dict[str, Any]:
        """Convert period to dictionary."""
        return {
            "period_id": period.period_id,
            "name": period.name,
            "start_date": period.start_date,
            "end_date": period.end_date,
            "description": period.description,
            "key_events": period.key_events,
            "themes": period.themes
        }
    
    def _period_from_dict(self, data: Dict[str, Any]) -> TimelinePeriod:
        """Reconstruct period from dictionary."""
        return TimelinePeriod(
            period_id=data.get("period_id", ""),
            name=data.get("name", ""),
            start_date=data.get("start_date", 0),
            end_date=data.get("end_date", 0),
            description=data.get("description", ""),
            key_events=data.get("key_events", []),
            themes=data.get("themes", [])
        )
