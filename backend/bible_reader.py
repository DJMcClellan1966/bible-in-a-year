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
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._chapter_sequence = self._build_chapter_sequence()
        self.reading_plan = self._load_plan()
        self.bible_text = self._load_bible_text()
        self.bible_sources = self._load_bible_sources()

    def get_reading_for_date(self, reading_date: date) -> Optional[Dict[str, Any]]:
        date_key = reading_date.strftime("%Y-%m-%d")
        reading = self.reading_plan["readings"].get(date_key)
        if reading:
            return reading

        return self._generate_dynamic_reading(reading_date)

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

        chapter_number = int(chapter)
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
