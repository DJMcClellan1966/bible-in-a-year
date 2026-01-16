"""
Bible reader module for managing daily readings
Implements classic Bible in a Year reading plans
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests

class BibleReader:
    """Manages Bible reading plans and daily passages"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.reading_plans_file = self.data_dir / "reading_plans.json"
        self.bible_text_file = self.data_dir / "bible_text.json"

        # Initialize reading plans
        self.reading_plans = self._load_reading_plans()

        # Try to load Bible text (will be minimal offline version)
        self.bible_text = self._load_bible_text()

    def _load_reading_plans(self) -> Dict[str, Any]:
        """Load or create reading plans"""
        if self.reading_plans_file.exists():
            try:
                with open(self.reading_plans_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading reading plans: {e}")

        # Create default reading plan
        return self._create_default_reading_plan()

    def _create_default_reading_plan(self) -> Dict[str, Any]:
        """Create a classic Bible in a Year reading plan"""
        # This is a simplified version - a full plan would have 365 days
        plan = {
            "name": "Classic Bible in a Year",
            "description": "Traditional chronological reading plan covering the entire Bible",
            "total_days": 365,
            "start_date": "2024-01-01",
            "readings": {}
        }

        # Generate sample readings for first few days
        # In a full implementation, this would be comprehensive
        sample_readings = {
            "2024-01-01": {
                "passages": ["Genesis 1-3", "Psalm 1", "Matthew 1"],
                "theme": "Creation and Beginning",
                "total_verses": 89
            },
            "2024-01-02": {
                "passages": ["Genesis 4-6", "Psalm 2", "Matthew 2"],
                "theme": "Early Humanity and Promise",
                "total_verses": 76
            },
            "2024-01-03": {
                "passages": ["Genesis 7-9", "Psalm 3", "Matthew 3"],
                "theme": "The Flood and Covenant",
                "total_verses": 82
            },
            "2024-01-04": {
                "passages": ["Genesis 10-12", "Psalm 4", "Matthew 4"],
                "theme": "Nations and Abraham's Call",
                "total_verses": 78
            },
            "2024-01-05": {
                "passages": ["Genesis 13-15", "Psalm 5", "Matthew 5:1-20"],
                "theme": "God's Promises and Beatitudes",
                "total_verses": 85
            }
        }

        plan["readings"] = sample_readings

        # Save the plan
        self.reading_plans_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.reading_plans_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)

        return plan

    def _load_bible_text(self) -> Dict[str, Any]:
        """Load Bible text data (simplified offline version)"""
        if self.bible_text_file.exists():
            try:
                with open(self.bible_text_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading Bible text: {e}")

        # Create minimal offline Bible text
        return self._create_minimal_bible_text()

    def _create_minimal_bible_text(self) -> Dict[str, Any]:
        """Create minimal Bible text for offline use"""
        # This would contain key passages, but for now just structure
        minimal_text = {
            "version": "KJV",
            "books": {
                "Genesis": {
                    "chapters": {
                        "1": {
                            "verses": {
                                "1": "In the beginning God created the heaven and the earth.",
                                "2": "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters."
                            }
                        }
                    }
                },
                "Psalms": {
                    "chapters": {
                        "1": {
                            "verses": {
                                "1": "Blessed is the man that walketh not in the counsel of the ungodly, nor standeth in the way of sinners, nor sitteth in the seat of the scornful."
                            }
                        }
                    }
                }
            }
        }

        # Save minimal text
        with open(self.bible_text_file, 'w', encoding='utf-8') as f:
            json.dump(minimal_text, f, indent=2, ensure_ascii=False)

        return minimal_text

    def get_reading_for_date(self, target_date: date) -> Optional[Dict[str, Any]]:
        """Get the reading assignment for a specific date"""
        date_str = target_date.strftime("%Y-%m-%d")

        # Check if we have a reading for this date
        if date_str in self.reading_plans["readings"]:
            reading = self.reading_plans["readings"][date_str].copy()

            # Try to get actual text if available
            reading["text"] = self._get_passage_text(reading["passages"])

            return reading

        # Calculate day of year for dynamic reading plans
        start_date = datetime.strptime(self.reading_plans["start_date"], "%Y-%m-%d").date()
        day_of_year = (target_date - start_date).days + 1

        if 1 <= day_of_year <= self.reading_plans["total_days"]:
            return self._generate_dynamic_reading(target_date, day_of_year)

        return None

    def _generate_dynamic_reading(self, target_date: date, day_of_year: int) -> Dict[str, Any]:
        """Generate a reading for dates not in the static plan"""
        # This is a simplified approach - real implementation would have comprehensive plans

        # Very basic structure: cycle through different parts of the Bible
        bible_sections = [
            ("Old Testament History", ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]),
            ("Old Testament Poetry", ["Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon"]),
            ("Old Testament Prophets", ["Isaiah", "Jeremiah", "Ezekiel", "Daniel"]),
            ("New Testament Gospels", ["Matthew", "Mark", "Luke", "John"]),
            ("New Testament Letters", ["Romans", "Corinthians", "Galatians", "Ephesians"]),
            ("New Testament History", ["Acts"]),
            ("General Epistles", ["Hebrews", "James", "Peter", "Jude"]),
            ("Apocalyptic", ["Revelation"])
        ]

        section_idx = (day_of_year - 1) // 45  # Roughly 8 sections over 365 days
        if section_idx >= len(bible_sections):
            section_idx = len(bible_sections) - 1

        section_name, books = bible_sections[section_idx]

        # Generate basic reading (simplified)
        reading = {
            "passages": [f"{books[0]} {day_of_year % 10 + 1}", f"Psalm {day_of_year % 150 + 1}"],
            "theme": f"{section_name} - Day {day_of_year}",
            "total_verses": 50,  # Approximate
            "text": self._get_passage_text([f"{books[0]} {day_of_year % 10 + 1}"])
        }

        return reading

    def _get_passage_text(self, passages: List[str]) -> Dict[str, Any]:
        """Get text for Bible passages (simplified offline version)"""
        text_data = {}

        for passage in passages:
            # Very basic parsing - in real app would have proper Bible API
            if "Genesis 1" in passage:
                text_data[passage] = {
                    "text": self.bible_text["books"]["Genesis"]["chapters"]["1"]["verses"],
                    "citation": "Genesis 1:1-2 (KJV)"
                }
            elif "Psalm 1" in passage:
                text_data[passage] = {
                    "text": self.bible_text["books"]["Psalms"]["chapters"]["1"]["verses"],
                    "citation": "Psalm 1:1 (KJV)"
                }
            else:
                text_data[passage] = {
                    "text": {"1": f"[Text for {passage} would be loaded from Bible API or local database]"},
                    "citation": f"{passage} (KJV)",
                    "note": "Full text available when online or with complete Bible database"
                }

        return text_data

    def get_reading_plan_info(self) -> Dict[str, Any]:
        """Get information about the current reading plan"""
        return {
            "name": self.reading_plans["name"],
            "description": self.reading_plans["description"],
            "total_days": self.reading_plans["total_days"],
            "start_date": self.reading_plans["start_date"],
            "days_loaded": len(self.reading_plans["readings"])
        }

    def get_upcoming_readings(self, start_date: date, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming reading assignments"""
        readings = []
        current_date = start_date

        for i in range(days):
            reading = self.get_reading_for_date(current_date)
            if reading:
                reading["date"] = current_date.strftime("%Y-%m-%d")
                readings.append(reading)
            current_date += timedelta(days=1)

        return readings

    def search_passages(self, query: str) -> List[Dict[str, Any]]:
        """Search for passages containing specific text (basic implementation)"""
        # This would integrate with a proper Bible search API
        # For now, return basic structure
        return [
            {
                "reference": "Genesis 1:1",
                "text": "In the beginning God created the heaven and the earth.",
                "relevance_score": 0.9
            }
        ]

    def download_bible_text(self, version: str = "KJV"):
        """Download Bible text from online API (would need API key/service)"""
        # This would implement downloading from a Bible API service
        # For now, just update the version info
        self.bible_text["version"] = version
        with open(self.bible_text_file, 'w', encoding='utf-8') as f:
            json.dump(self.bible_text, f, indent=2, ensure_ascii=False)

        print(f"Bible text version updated to {version}")