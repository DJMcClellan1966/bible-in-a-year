"""
Bible reading plan management.
"""

import json
import re
from dataclasses import dataclass
from datetime import date, timedelta
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class BibleReader:
    def __init__(self) -> None:
        self.data_dir = Path(__file__).parent.parent / "data"
        self.plan_file = self.data_dir / "reading_plans.json"
        self.bible_text_file = self.data_dir / "bible_text.json"
        self.sources_file = self.data_dir / "bible_sources.json"
        self.augustine_commentaries_file = self.data_dir / "augustine_commentaries.json"
        self.aquinas_commentaries_file = self.data_dir / "aquinas_commentaries.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._chapter_sequence = self._build_chapter_sequence()
        self.reading_plan = self._load_plan()
        self.bible_text = self._load_bible_text()
        self.bible_sources = self._load_bible_sources()
        self.augustine_commentaries = self._load_commentaries("augustine")
        self.aquinas_commentaries = self._load_commentaries("aquinas")

    def get_reading_for_date(self, reading_date: date, plan_type: str = "classic") -> Optional[Dict[str, Any]]:
        """Get reading for a date using the specified plan type."""
        if plan_type == "augustine_classic":
            # Get chronological plan reading and add Augustine commentaries
            chronological_reading = self._generate_plan_reading(reading_date, "chronological")
            if chronological_reading:
                day_of_year = reading_date.timetuple().tm_yday
                day_index = min(day_of_year, 365)
                commentaries = {}
                for passage in chronological_reading.get("passages", []):
                    commentary = self._get_commentary_for_passage(
                        passage, day_index, helper="augustine", fallback_to_generate=True
                    )
                    if commentary:
                        commentaries[passage] = commentary
                chronological_reading["commentaries"] = commentaries
                chronological_reading["theme"] = "Augustine's Commentary on Chronological Reading"
            return chronological_reading
        
        if plan_type == "aquinas_classic":
            # Get chronological plan reading and add Aquinas commentaries
            chronological_reading = self._generate_plan_reading(reading_date, "chronological")
            if chronological_reading:
                day_of_year = reading_date.timetuple().tm_yday
                day_index = min(day_of_year, 365)
                commentaries = {}
                for passage in chronological_reading.get("passages", []):
                    commentary = self._get_commentary_for_passage(
                        passage, day_index, helper="aquinas", fallback_to_generate=True
                    )
                    if commentary:
                        commentaries[passage] = commentary
                chronological_reading["commentaries"] = commentaries
                chronological_reading["theme"] = "Aquinas's Commentary on Chronological Reading"
            return chronological_reading
        
        if plan_type != "classic":
            return self._generate_plan_reading(reading_date, plan_type)
        
        # For classic plan, use day-of-year approach (works for any year)
        start_date_str = self.reading_plan.get("start_date", "2024-01-01")
        try:
            plan_start = date.fromisoformat(start_date_str)
        except Exception:
            plan_start = date(2024, 1, 1)
        
        # Normalize to same year as plan start for lookup
        normalized_date = date(plan_start.year, reading_date.month, reading_date.day)
        date_key = normalized_date.strftime("%Y-%m-%d")
        reading = self.reading_plan["readings"].get(date_key)
        
        # Only use JSON reading if it has the classic format (3 passages: OT + Psalm + NT)
        if reading and len(reading.get("passages", [])) >= 3:
            return reading

        # Fallback: generate classic plan format (OT + Psalm + NT) for missing or incomplete entries
        return self._generate_old_psalms_new_plan_for_date(reading_date)

    def _load_plan(self) -> Dict[str, Any]:
        if self.plan_file.exists():
            try:
                plan = json.loads(self.plan_file.read_text(encoding="utf-8"))
                plan = self._ensure_plan_complete(plan)
                return plan
            except Exception:
                pass
        plan = self._create_default_plan()
        self.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
        return plan

    def _create_default_plan(self) -> Dict[str, Any]:
        start = date(2024, 1, 1)
        plan = {
            "name": "Chronological Bible in a Year (Simplified)",
            "description": "A chronological-style plan generated from a simplified book order.",
            "start_date": start.strftime("%Y-%m-%d"),
            "total_days": 365,
            "readings": {},
        }
        return self._ensure_plan_complete(plan)

    def _generate_dynamic_reading(self, reading_date: date) -> Dict[str, Any]:
        start_date_str = self.reading_plan.get("start_date", "2024-01-01")
        try:
            start = date.fromisoformat(start_date_str)
        except Exception:
            start = date(2024, 1, 1)
        day_index = (reading_date - start).days + 1
        day_index = ((day_index - 1) % 365) + 1
        return {
            "passages": self._passages_for_day_index(day_index),
            "theme": "Chronological Journey",
        }

    def _generate_old_psalms_new_plan_for_date(self, reading_date: date) -> Dict[str, Any]:
        """Generate classic plan format (OT + Psalm + NT) for a given date using day-of-year."""
        day_of_year = reading_date.timetuple().tm_yday
        day_index = min(day_of_year, 365)
        return self._generate_old_psalms_new_plan(day_index)

    def _generate_plan_reading(self, reading_date: date, plan_type: str) -> Dict[str, Any]:
        """Generate reading based on plan type using day-of-year (1-365)."""
        # Use day of year so it works for any year
        day_of_year = reading_date.timetuple().tm_yday
        # Map day 366 (leap year Dec 31) to day 365
        day_index = min(day_of_year, 365)

        if plan_type == "augustine_classic" or plan_type == "aquinas_classic":
            # These are handled in get_reading_for_date, but keep for consistency
            return self._generate_old_psalms_new_plan(day_index)
        elif plan_type == "chronological_cross_ref":
            return self._generate_chronological_cross_ref_plan(day_index)
        elif plan_type == "fivexfive_new_testament":
            return self._generate_fivexfive_new_testament_plan(day_index)
        elif plan_type == "mcheyne":
            return self._generate_mcheyne_plan(day_index)
        elif plan_type == "52_week_genre":
            return self._generate_52_week_genre_plan(day_index)
        elif plan_type == "chronological":
            return self._generate_chronological_plan(day_index)
        elif plan_type == "old_psalms_new":
            return self._generate_old_psalms_new_plan(day_index)
        elif plan_type == "old_new_split":
            return self._generate_old_new_split_plan(day_index)
        else:
            return {
                "passages": self._passages_for_day_index(day_index),
                "theme": "Daily Bread",
            }

    def _generate_chronological_plan(self, day_index: int) -> Dict[str, Any]:
        """Pure chronological: straight through Bible from Genesis to Revelation."""
        sequence = self._chapter_sequence
        total_chapters = len(sequence)
        chapters_per_day = total_chapters / 365.0
        
        start_idx = int((day_index - 1) * chapters_per_day)
        end_idx = int(day_index * chapters_per_day)
        if day_index == 365:
            end_idx = total_chapters
        
        day_chapters = sequence[start_idx:end_idx]
        passages = self._compress_chapter_refs(day_chapters)
        
        return {
            "passages": passages,
            "theme": "Chronological Journey",
        }

    def _generate_old_psalms_new_plan(self, day_index: int) -> Dict[str, Any]:
        """Classic plan: Old Testament + Psalms/Proverbs + New Testament daily."""
        # OT books (excluding Psalms, Proverbs, Song of Solomon)
        ot_books = [
            ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
            ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
            ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
            ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
            ("Esther", 10), ("Job", 42), ("Ecclesiastes", 12), ("Song of Solomon", 8),
            ("Isaiah", 66), ("Jeremiah", 52), ("Lamentations", 5), ("Ezekiel", 48),
            ("Daniel", 12), ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1),
            ("Jonah", 4), ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3),
            ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4),
        ]
        
        # NT books
        nt_books = [
            ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21), ("Acts", 28),
            ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13), ("Galatians", 6),
            ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4), ("1 Thessalonians", 5),
            ("2 Thessalonians", 3), ("1 Timothy", 6), ("2 Timothy", 4), ("Titus", 3),
            ("Philemon", 1), ("Hebrews", 13), ("James", 5), ("1 Peter", 5), ("2 Peter", 3),
            ("1 John", 5), ("2 John", 1), ("3 John", 1), ("Jude", 1), ("Revelation", 22),
        ]
        
        # Build sequences
        ot_seq = []
        for book, count in ot_books:
            ot_seq.extend([(book, ch) for ch in range(1, count + 1)])
        
        ps_prov_seq = []
        ps_prov_seq.extend([("Psalms", ch) for ch in range(1, 151)])
        ps_prov_seq.extend([("Proverbs", ch) for ch in range(1, 32)])
        
        nt_seq = []
        for book, count in nt_books:
            nt_seq.extend([(book, ch) for ch in range(1, count + 1)])
        
        # Calculate daily readings
        ot_chapters_per_day = len(ot_seq) / 365.0
        ps_prov_cycle = len(ps_prov_seq)
        nt_chapters_per_day = len(nt_seq) / 365.0
        
        ot_start = int((day_index - 1) * ot_chapters_per_day)
        ot_end = int(day_index * ot_chapters_per_day)
        if day_index == 365:
            ot_end = len(ot_seq)
        ot_passages = self._compress_chapter_refs(ot_seq[ot_start:ot_end])
        
        ps_prov_idx = ((day_index - 1) * 2) % ps_prov_cycle
        ps_prov_passages = self._compress_chapter_refs(ps_prov_seq[ps_prov_idx:ps_prov_idx+2])
        
        nt_start = int((day_index - 1) * nt_chapters_per_day)
        nt_end = int(day_index * nt_chapters_per_day)
        if day_index == 365:
            nt_end = len(nt_seq)
        nt_passages = self._compress_chapter_refs(nt_seq[nt_start:nt_end])
        
        passages = ot_passages + ps_prov_passages + nt_passages
        return {
            "passages": passages,
            "theme": "Old Testament, Psalms/Proverbs, New Testament",
        }

    def _generate_old_new_split_plan(self, day_index: int) -> Dict[str, Any]:
        """Split plan: First half year OT, second half NT."""
        ot_books = [
            ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
            ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
            ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
            ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
            ("Esther", 10), ("Job", 42), ("Psalms", 150), ("Proverbs", 31),
            ("Ecclesiastes", 12), ("Song of Solomon", 8), ("Isaiah", 66), ("Jeremiah", 52),
            ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12), ("Hosea", 14),
            ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4), ("Micah", 7),
            ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3), ("Haggai", 2),
            ("Zechariah", 14), ("Malachi", 4),
        ]
        
        nt_books = [
            ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21), ("Acts", 28),
            ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13), ("Galatians", 6),
            ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4), ("1 Thessalonians", 5),
            ("2 Thessalonians", 3), ("1 Timothy", 6), ("2 Timothy", 4), ("Titus", 3),
            ("Philemon", 1), ("Hebrews", 13), ("James", 5), ("1 Peter", 5), ("2 Peter", 3),
            ("1 John", 5), ("2 John", 1), ("3 John", 1), ("Jude", 1), ("Revelation", 22),
        ]
        
        ot_seq = []
        for book, count in ot_books:
            ot_seq.extend([(book, ch) for ch in range(1, count + 1)])
        
        nt_seq = []
        for book, count in nt_books:
            nt_seq.extend([(book, ch) for ch in range(1, count + 1)])
        
        if day_index <= 183:  # First half year: OT
            chapters_per_day = len(ot_seq) / 183.0
            start_idx = int((day_index - 1) * chapters_per_day)
            end_idx = int(day_index * chapters_per_day)
            if day_index == 183:
                end_idx = len(ot_seq)
            passages = self._compress_chapter_refs(ot_seq[start_idx:end_idx])
            theme = "Old Testament"
        else:  # Second half year: NT
            nt_day = day_index - 183
            chapters_per_day = len(nt_seq) / 182.0
            start_idx = int((nt_day - 1) * chapters_per_day)
            end_idx = int(nt_day * chapters_per_day)
            if day_index == 365:
                end_idx = len(nt_seq)
            passages = self._compress_chapter_refs(nt_seq[start_idx:end_idx])
            theme = "New Testament"
        
        return {
            "passages": passages,
            "theme": theme,
        }

    def _generate_chronological_cross_ref_plan(self, day_index: int) -> Dict[str, Any]:
        """Chronological plan with cross-references - includes parallel passages."""
        sequence = self._chapter_sequence
        total_chapters = len(sequence)
        chapters_per_day = total_chapters / 365.0
        
        start_idx = int((day_index - 1) * chapters_per_day)
        end_idx = int(day_index * chapters_per_day)
        if day_index == 365:
            end_idx = total_chapters
        
        day_chapters = sequence[start_idx:end_idx]
        passages = self._compress_chapter_refs(day_chapters)
        
        # Add cross-reference: include related Psalms or NT if in OT section
        if day_index <= 150:  # First ~150 days cover OT
            # Add a Psalm reading that relates (cycle through Psalms)
            ps_idx = ((day_index - 1) % 150) + 1
            if "Psalms" not in " ".join(passages):
                passages.append(f"Psalm {ps_idx}")
        
        return {
            "passages": passages,
            "theme": "Chronological Cross-Reference",
        }

    def _generate_fivexfive_new_testament_plan(self, day_index: int) -> Dict[str, Any]:
        """5x5x5 New Testament: Read NT 5 days a week, ~5 minutes per day."""
        nt_books = [
            ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21), ("Acts", 28),
            ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13), ("Galatians", 6),
            ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4), ("1 Thessalonians", 5),
            ("2 Thessalonians", 3), ("1 Timothy", 6), ("2 Timothy", 4), ("Titus", 3),
            ("Philemon", 1), ("Hebrews", 13), ("James", 5), ("1 Peter", 5), ("2 Peter", 3),
            ("1 John", 5), ("2 John", 1), ("3 John", 1), ("Jude", 1), ("Revelation", 22),
        ]
        
        # Build NT sequence
        nt_seq = []
        for book, count in nt_books:
            nt_seq.extend([(book, ch) for ch in range(1, count + 1)])
        
        # 5 days per week = ~260 reading days (52 weeks * 5 days)
        # Spread NT over 260 days
        total_reading_days = 260
        day_in_plan = ((day_index - 1) % total_reading_days) + 1
        
        chapters_per_day = len(nt_seq) / total_reading_days
        start_idx = int((day_in_plan - 1) * chapters_per_day)
        end_idx = int(day_in_plan * chapters_per_day)
        if day_in_plan == total_reading_days:
            end_idx = len(nt_seq)
        
        passages = self._compress_chapter_refs(nt_seq[start_idx:end_idx])
        return {
            "passages": passages,
            "theme": "5x5x5 New Testament",
        }

    def _generate_mcheyne_plan(self, day_index: int) -> Dict[str, Any]:
        """Robert Murray M'Cheyne: 4 readings per day (OT History, OT Prophets/Poetry, NT, Psalms)."""
        # OT History books
        ot_history = [
            ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
            ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
            ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
            ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
            ("Esther", 10),
        ]
        
        # OT Prophets and Poetry
        ot_prophets_poetry = [
            ("Job", 42), ("Psalms", 150), ("Proverbs", 31), ("Ecclesiastes", 12),
            ("Song of Solomon", 8), ("Isaiah", 66), ("Jeremiah", 52), ("Lamentations", 5),
            ("Ezekiel", 48), ("Daniel", 12), ("Hosea", 14), ("Joel", 3), ("Amos", 9),
            ("Obadiah", 1), ("Jonah", 4), ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3),
            ("Zephaniah", 3), ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4),
        ]
        
        # NT books
        nt_books = [
            ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21), ("Acts", 28),
            ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13), ("Galatians", 6),
            ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4), ("1 Thessalonians", 5),
            ("2 Thessalonians", 3), ("1 Timothy", 6), ("2 Timothy", 4), ("Titus", 3),
            ("Philemon", 1), ("Hebrews", 13), ("James", 5), ("1 Peter", 5), ("2 Peter", 3),
            ("1 John", 5), ("2 John", 1), ("3 John", 1), ("Jude", 1), ("Revelation", 22),
        ]
        
        # Build sequences
        history_seq = []
        for book, count in ot_history:
            history_seq.extend([(book, ch) for ch in range(1, count + 1)])
        
        prophets_poetry_seq = []
        for book, count in ot_prophets_poetry:
            prophets_poetry_seq.extend([(book, ch) for ch in range(1, count + 1)])
        
        nt_seq = []
        for book, count in nt_books:
            nt_seq.extend([(book, ch) for ch in range(1, count + 1)])
        
        # Calculate daily readings (spread each over 365 days)
        history_chapters_per_day = len(history_seq) / 365.0
        prophets_chapters_per_day = len(prophets_poetry_seq) / 365.0
        nt_chapters_per_day = len(nt_seq) / 365.0
        ps_cycle = 150  # Psalms repeat every 150 days
        
        # Reading 1: OT History
        h_start = int((day_index - 1) * history_chapters_per_day)
        h_end = max(int(day_index * history_chapters_per_day), h_start + 1)  # Ensure at least 1 chapter
        if day_index == 365:
            h_end = len(history_seq)
        history_passages = self._compress_chapter_refs(history_seq[h_start:h_end])
        
        # Reading 2: OT Prophets/Poetry (excluding Psalms which are separate)
        pp_start = int((day_index - 1) * prophets_chapters_per_day)
        pp_end = max(int(day_index * prophets_chapters_per_day), pp_start + 1)  # Ensure at least 1 chapter
        if day_index == 365:
            pp_end = len(prophets_poetry_seq)
        prophets_passages = self._compress_chapter_refs(prophets_poetry_seq[pp_start:pp_end])
        
        # Reading 3: New Testament
        nt_start = int((day_index - 1) * nt_chapters_per_day)
        nt_end = max(int(day_index * nt_chapters_per_day), nt_start + 1)  # Ensure at least 1 chapter
        if day_index == 365:
            nt_end = len(nt_seq)
        nt_passages = self._compress_chapter_refs(nt_seq[nt_start:nt_end])
        
        # Reading 4: Psalms (separate cycle)
        ps_num = ((day_index - 1) % 150) + 1
        ps_passages = [f"Psalm {ps_num}"]
        
        passages = history_passages + prophets_passages + nt_passages + ps_passages
        return {
            "passages": passages,
            "theme": "M'Cheyne Plan (4 Readings)",
        }

    def _generate_52_week_genre_plan(self, day_index: int) -> Dict[str, Any]:
        """52 Week Bible Reading Plan organized by genre (Daily Genre Bible Reading Plan)."""
        # All books organized by genre
        all_books_by_genre = {
            "Law": [("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36), ("Deuteronomy", 34)],
            "History": [
                ("Joshua", 24), ("Judges", 21), ("Ruth", 4), ("1 Samuel", 31), ("2 Samuel", 24),
                ("1 Kings", 22), ("2 Kings", 25), ("1 Chronicles", 29), ("2 Chronicles", 36),
                ("Ezra", 10), ("Nehemiah", 13), ("Esther", 10),
            ],
            "Poetry": [("Job", 42), ("Psalms", 150), ("Proverbs", 31), ("Ecclesiastes", 12), ("Song of Solomon", 8)],
            "Prophets": [
                ("Isaiah", 66), ("Jeremiah", 52), ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12),
                ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4),
                ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3), ("Haggai", 2),
                ("Zechariah", 14), ("Malachi", 4),
            ],
            "Gospels": [("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21)],
            "Epistles": [
                ("Acts", 28), ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13), ("Galatians", 6),
                ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4), ("1 Thessalonians", 5), ("2 Thessalonians", 3),
                ("1 Timothy", 6), ("2 Timothy", 4), ("Titus", 3), ("Philemon", 1), ("Hebrews", 13),
                ("James", 5), ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5), ("2 John", 1),
                ("3 John", 1), ("Jude", 1), ("Revelation", 22),
            ],
        }
        
        # Build complete sequence in genre order
        full_sequence = []
        genre_order = ["Law", "History", "Poetry", "Prophets", "Gospels", "Epistles"]
        for genre in genre_order:
            for book, count in all_books_by_genre[genre]:
                full_sequence.extend([(book, ch) for ch in range(1, count + 1)])
        
        # Distribute over 365 days
        total_chapters = len(full_sequence)
        chapters_per_day = total_chapters / 365.0
        
        start_idx = int((day_index - 1) * chapters_per_day)
        end_idx = int(day_index * chapters_per_day)
        if day_index == 365:
            end_idx = total_chapters
        
        day_chapters = full_sequence[start_idx:end_idx]
        passages = self._compress_chapter_refs(day_chapters)
        
        # Determine current genre based on which book we're reading
        current_genre = "Bible"
        if day_chapters:
            first_book = day_chapters[0][0]
            for genre, books in all_books_by_genre.items():
                if any(book == first_book for book, _ in books):
                    current_genre = genre
                    break
        
        return {
            "passages": passages,
            "theme": f"52 Week Plan - {current_genre}",
        }

    def _ensure_plan_complete(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        total_days = int(plan.get("total_days", 365))
        if total_days != 365:
            plan["total_days"] = 365
            total_days = 365

        start_date_str = plan.get("start_date", "2024-01-01")
        try:
            start = date.fromisoformat(start_date_str)
        except Exception:
            start = date(2024, 1, 1)
            plan["start_date"] = start.strftime("%Y-%m-%d")

        readings: Dict[str, Any] = plan.get("readings") or {}
        if len(readings) >= total_days:
            plan["readings"] = readings
            return plan

        for day_offset in range(1, total_days + 1):
            reading_date = start + timedelta(days=day_offset - 1)
            key = reading_date.strftime("%Y-%m-%d")
            if key in readings:
                continue
            readings[key] = {
                "passages": self._passages_for_day_index(day_offset),
                "theme": "Chronological Journey",
            }

        plan["readings"] = readings
        try:
            self.plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        return plan

    def _passages_for_day_index(self, day_index: int) -> List[str]:
        sequence = self._chapter_sequence
        if not sequence:
            return []

        total_chapters = len(sequence)
        base = total_chapters // 365
        extra = total_chapters % 365

        start = 0
        if day_index > 1:
            start = (day_index - 1) * base + min(day_index - 1, extra)
        size = base + (1 if day_index <= extra else 0)
        end = min(start + size, total_chapters)

        day_chapters = sequence[start:end]
        return self._compress_chapter_refs(day_chapters)

    def _compress_chapter_refs(self, chapter_refs: List[tuple[str, int]]) -> List[str]:
        if not chapter_refs:
            return []

        passages: List[str] = []
        current_book, current_start = chapter_refs[0]
        prev_ch = current_start

        def flush(book: str, start_ch: int, end_ch: int) -> None:
            if start_ch == end_ch:
                passages.append(f"{book} {start_ch}")
            else:
                passages.append(f"{book} {start_ch}-{end_ch}")

        for book, ch in chapter_refs[1:]:
            if book == current_book and ch == prev_ch + 1:
                prev_ch = ch
                continue
            flush(current_book, current_start, prev_ch)
            current_book, current_start, prev_ch = book, ch, ch

        flush(current_book, current_start, prev_ch)
        return passages

    def _build_chapter_sequence(self) -> List[tuple[str, int]]:
        books = self._chronological_books_simplified()
        sequence: List[tuple[str, int]] = []
        for book, chapter_count in books:
            for ch in range(1, chapter_count + 1):
                sequence.append((book, ch))
        return sequence

    def _chronological_books_simplified(self) -> List[tuple[str, int]]:
        return [
            ("Genesis", 50),
            ("Job", 42),
            ("Exodus", 40),
            ("Leviticus", 27),
            ("Numbers", 36),
            ("Deuteronomy", 34),
            ("Joshua", 24),
            ("Judges", 21),
            ("Ruth", 4),
            ("1 Samuel", 31),
            ("2 Samuel", 24),
            ("1 Kings", 22),
            ("2 Kings", 25),
            ("1 Chronicles", 29),
            ("2 Chronicles", 36),
            ("Ezra", 10),
            ("Nehemiah", 13),
            ("Esther", 10),
            ("Psalms", 150),
            ("Proverbs", 31),
            ("Ecclesiastes", 12),
            ("Song of Solomon", 8),
            ("Isaiah", 66),
            ("Jeremiah", 52),
            ("Lamentations", 5),
            ("Ezekiel", 48),
            ("Daniel", 12),
            ("Hosea", 14),
            ("Joel", 3),
            ("Amos", 9),
            ("Obadiah", 1),
            ("Jonah", 4),
            ("Micah", 7),
            ("Nahum", 3),
            ("Habakkuk", 3),
            ("Zephaniah", 3),
            ("Haggai", 2),
            ("Zechariah", 14),
            ("Malachi", 4),
            ("Matthew", 28),
            ("Mark", 16),
            ("Luke", 24),
            ("John", 21),
            ("Acts", 28),
            ("James", 5),
            ("Galatians", 6),
            ("1 Thessalonians", 5),
            ("2 Thessalonians", 3),
            ("1 Corinthians", 16),
            ("2 Corinthians", 13),
            ("Romans", 16),
            ("Ephesians", 6),
            ("Philippians", 4),
            ("Colossians", 4),
            ("Philemon", 1),
            ("1 Timothy", 6),
            ("Titus", 3),
            ("2 Timothy", 4),
            ("1 Peter", 5),
            ("2 Peter", 3),
            ("Jude", 1),
            ("Hebrews", 13),
            ("Revelation", 22),
            ("1 John", 5),
            ("2 John", 1),
            ("3 John", 1),
        ]

    def _load_bible_text(self) -> Dict[str, Any]:
        if self.bible_text_file.exists():
            try:
                return json.loads(self.bible_text_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def get_available_versions(self) -> List[Dict[str, str]]:
        sources = self.bible_sources.get("sources", {})
        return [
            {"id": version, "title": info.get("title", version)}
            for version, info in sources.items()
        ]

    def get_passage_text(self, reference: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Basic parser for references like "Genesis 1" or "Psalm 23".
        Returns a dictionary of verses if available in bible_text.json.
        """
        if version:
            source_text = self._load_from_source(reference, version)
            if source_text:
                return source_text

        if self.bible_text:
            return self._load_from_json(reference)
        return {}

    def _load_from_json(self, reference: str) -> Dict[str, Any]:
        parts = reference.split()
        if len(parts) < 2:
            return {}

        book = " ".join(parts[:-1])
        chapter = parts[-1]

        books = self.bible_text.get("books", {})
        book_data = books.get(book)
        if not book_data:
            return {}

        chapters = book_data.get("chapters", {})
        chapter_data = chapters.get(str(chapter))
        if not chapter_data:
            return {}

        return {
            "reference": reference,
            "verses": chapter_data.get("verses", {}),
            "citation": f"{reference} ({self.bible_text.get('version', 'KJV')})",
        }

    def _load_bible_sources(self) -> Dict[str, Any]:
        if self.sources_file.exists():
            try:
                return json.loads(self.sources_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        defaults = self._default_sources()
        self.sources_file.write_text(json.dumps(defaults, indent=2, ensure_ascii=False), encoding="utf-8")
        return defaults

    def _default_sources(self) -> Dict[str, Any]:
        candidates = {
            "YLT": {
                "title": "Young's Literal Translation",
                "path": r"C:\Users\DJMcC\OneDrive\Desktop\bible_in_year\englyt",
                "format": "html",
            },
            "ASV": {
                "title": "American Standard Version",
                "path": r"C:\Users\DJMcC\OneDrive\Desktop\bible_in_year\asv",
                "format": "html",
            },
            "DBY": {
                "title": "Darby Bible",
                "path": r"C:\Users\DJMcC\OneDrive\Desktop\bible_in_year\engDBY",
                "format": "html",
            },
        }

        sources: Dict[str, Any] = {}
        for version, info in candidates.items():
            if Path(info["path"]).exists():
                sources[version] = info

        return {"default_version": "YLT", "sources": sources}

    def _load_commentaries(self, helper: str = "augustine") -> Dict[str, Any]:
        """Load pre-generated commentaries from JSON file.
        
        Args:
            helper: Either "augustine" or "aquinas"
        """
        commentaries_file = (
            self.augustine_commentaries_file if helper == "augustine" else self.aquinas_commentaries_file
        )
        if commentaries_file.exists():
            try:
                return json.loads(commentaries_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _get_commentary_for_passage(
        self, passage: str, day_index: int, helper: str = "augustine", fallback_to_generate: bool = False
    ) -> Optional[str]:
        """Get commentary for a passage (by passage reference or day index).
        
        Args:
            passage: Bible passage reference
            day_index: Day of year (1-365)
            helper: Either "augustine" or "aquinas"
            fallback_to_generate: If True and no pre-generated commentary found, generate on-demand
        """
        commentaries = self.augustine_commentaries if helper == "augustine" else self.aquinas_commentaries
        
        if not commentaries:
            if not fallback_to_generate:
                return None
        
        # Try to find by passage reference first
        if passage in commentaries.get("by_passage", {}):
            commentary = commentaries["by_passage"][passage]
            # Validate commentary quality (should be substantial, not just error messages)
            if commentary and len(commentary.strip()) > 100 and not commentary.startswith("Unable to"):
                return commentary
        
        # Try to find by day index
        day_key = str(day_index)
        if day_key in commentaries.get("by_day", {}):
            day_data = commentaries["by_day"][day_key]
            # Check if this passage is in the day's commentaries
            if passage in day_data.get("commentaries", {}):
                commentary = day_data["commentaries"][passage]
                if commentary and len(commentary.strip()) > 100 and not commentary.startswith("Unable to"):
                    return commentary
        
        # Fallback: generate on-demand if requested
        if fallback_to_generate:
            try:
                from backend.rag_system import RAGSystem
                from backend.ollama_client import OllamaClient
                rag = RAGSystem()
                if not rag._has_cached_data():
                    rag.initialize_default_data()
                ollama = OllamaClient()
                context = rag.get_relevant_context(passage, helper=helper, top_k=3)
                # Get passage text for better context
                passage_text_obj = self.get_passage_text(passage)
                passage_text = passage
                if passage_text_obj and passage_text_obj.get("verses"):
                    verses = passage_text_obj["verses"]
                    verse_lines = [f"{verse}: {text}" for verse, text in list(verses.items())[:30]]
                    passage_text = f"{passage}\n\n" + "\n".join(verse_lines)
                return ollama.generate_commentary(passage=passage_text, context=context, helper=helper)
            except Exception:
                # If generation fails, return None rather than error
                return None
        
        return None

    def _load_from_source(self, reference: str, version: str) -> Dict[str, Any]:
        sources = self.bible_sources.get("sources", {})
        source = sources.get(version)
        if not source:
            return {}

        file_path, citation = self._reference_to_file(reference, source["path"])
        if not file_path.exists():
            return {}

        html = file_path.read_text(encoding="utf-8", errors="ignore")
        verses = self._extract_verses(html)
        if not verses:
            return {}

        version_title = source.get("title", version)
        return {
            "reference": reference,
            "verses": verses,
            "citation": f"{reference} ({version_title})",
        }

    def _reference_to_file(self, reference: str, folder: str) -> Tuple[Path, str]:
        book, chapter = self._parse_reference(reference)
        abbrev = self._book_abbrev(book)
        if not abbrev:
            return Path(folder) / "missing.htm", reference

        # Handle chapter ranges like "19-22" or "1:1-10" - use first chapter
        chapter_clean = re.split(r"[-:]", chapter)[0]
        try:
            chapter_number = int(chapter_clean)
        except ValueError:
            chapter_number = 1

        padding = 3 if abbrev == "PSA" else 2
        chapter_str = str(chapter_number).zfill(padding)
        filename = f"{abbrev}{chapter_str}.htm"
        return Path(folder) / filename, f"{reference}"

    def _parse_reference(self, reference: str) -> Tuple[str, str]:
        parts = reference.strip().split()
        if len(parts) < 2:
            return reference, "1"

        chapter = parts[-1]
        book = " ".join(parts[:-1])
        return book, chapter

    def _book_abbrev(self, book_name: str) -> Optional[str]:
        normalized = re.sub(r"[^a-z0-9 ]", "", book_name.lower()).strip()
        normalized = re.sub(r"\s+", " ", normalized)

        mapping = {
            "genesis": "GEN",
            "exodus": "EXO",
            "leviticus": "LEV",
            "numbers": "NUM",
            "deuteronomy": "DEU",
            "joshua": "JOS",
            "judges": "JDG",
            "ruth": "RUT",
            "1 samuel": "1SA",
            "2 samuel": "2SA",
            "1 kings": "1KI",
            "2 kings": "2KI",
            "1 chronicles": "1CH",
            "2 chronicles": "2CH",
            "ezra": "EZR",
            "nehemiah": "NEH",
            "esther": "EST",
            "job": "JOB",
            "psalm": "PSA",
            "psalms": "PSA",
            "proverbs": "PRO",
            "ecclesiastes": "ECC",
            "song of solomon": "SNG",
            "song of songs": "SNG",
            "isaiah": "ISA",
            "jeremiah": "JER",
            "lamentations": "LAM",
            "ezekiel": "EZK",
            "daniel": "DAN",
            "hosea": "HOS",
            "joel": "JOL",
            "amos": "AMO",
            "obadiah": "OBA",
            "jonah": "JON",
            "micah": "MIC",
            "nahum": "NAM",
            "habakkuk": "HAB",
            "zephaniah": "ZEP",
            "haggai": "HAG",
            "zechariah": "ZEC",
            "malachi": "MAL",
            "matthew": "MAT",
            "mark": "MRK",
            "luke": "LUK",
            "john": "JHN",
            "acts": "ACT",
            "romans": "ROM",
            "1 corinthians": "1CO",
            "2 corinthians": "2CO",
            "galatians": "GAL",
            "ephesians": "EPH",
            "philippians": "PHP",
            "colossians": "COL",
            "1 thessalonians": "1TH",
            "2 thessalonians": "2TH",
            "1 timothy": "1TI",
            "2 timothy": "2TI",
            "titus": "TIT",
            "philemon": "PHM",
            "hebrews": "HEB",
            "james": "JAS",
            "1 peter": "1PE",
            "2 peter": "2PE",
            "1 john": "1JN",
            "2 john": "2JN",
            "3 john": "3JN",
            "jude": "JUD",
            "revelation": "REV",
        }
        return mapping.get(normalized)

    def _extract_verses(self, html: str) -> Dict[str, str]:
        # Match verse spans like: <span class="verse" id="V1">1&#160;</span>
        matches = list(re.finditer(r'<span class="verse" id="V(\d+)">.*?</span>', html))
        if not matches:
            return {}

        verses: Dict[str, str] = {}
        for idx, match in enumerate(matches):
            verse_num = match.group(1)
            start = match.end()
            # Find text until next verse span or end of content div
            end = matches[idx + 1].start() if idx + 1 < len(matches) else html.find("</div>", start)
            if end == -1:
                end = len(html)
            raw = html[start:end]
            # Strip HTML tags
            text = re.sub(r"<[^>]+>", "", raw)
            # Decode HTML entities and clean whitespace
            text = unescape(text).replace("\n", " ").strip()
            text = re.sub(r"\s+", " ", text)
            if text:
                verses[verse_num] = text
        return verses
