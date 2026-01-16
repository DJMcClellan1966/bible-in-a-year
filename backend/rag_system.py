"""
Lightweight retrieval system for saint writings.
Uses simple keyword overlap by default to avoid heavy dependencies.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class RAGSystem:
    def __init__(self) -> None:
        root = Path(__file__).parent.parent
        self.data_dir = root / "data"
        self.models_dir = root / "models" / "simple_index"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.documents_by_helper: Dict[str, List[Dict[str, Any]]] = {
            "augustine": [],
            "aquinas": [],
            "combined": [],
        }

        self._load_indices()

    def initialize_default_data(self, force: bool = False) -> None:
        """Initialize indices only if they don't already have content."""
        if not force and self._has_cached_data():
            return  # Skip - already indexed

        self.index_helper("augustine", self.data_dir / "augustine", force=force)
        self.index_helper("aquinas", self.data_dir / "aquinas", force=force)
        self._update_combined()

    def _has_cached_data(self) -> bool:
        """Check if we already have indexed documents."""
        for helper in ("augustine", "aquinas"):
            if self.documents_by_helper.get(helper):
                return True
        return False

    def index_helper(self, helper: str, directory: Path, force: bool = False) -> None:
        # Skip if already have docs and not forcing
        if not force and self.documents_by_helper.get(helper):
            return

        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            return

        documents: List[Dict[str, Any]] = []
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip large PDFs on startup (process async later)
            if file_path.suffix.lower() == ".pdf" and file_path.stat().st_size > 5_000_000:
                continue

            text = self._load_text(file_path)
            if not text:
                continue

            chunks = self._chunk_text(text, chunk_size=1000, chunk_overlap=200)
            for i, chunk in enumerate(chunks):
                documents.append(
                    {
                        "id": f"{file_path.stem}_{i}",
                        "text": chunk,
                        "source": str(file_path),
                        "author": helper,
                        "title": file_path.stem,
                    }
                )

        if documents:
            self.documents_by_helper[helper] = documents
            self._save_index(helper)

    def get_relevant_context(self, query: str, helper: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if helper not in self.documents_by_helper:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored_docs: List[Dict[str, Any]] = []
        for doc in self.documents_by_helper.get(helper, []):
            score = self._score_tokens(query_tokens, self._tokenize(doc.get("text", "")))
            if score > 0:
                scored_doc = doc.copy()
                scored_doc["score"] = score
                scored_docs.append(scored_doc)

        scored_docs.sort(key=lambda d: d["score"], reverse=True)
        return scored_docs[:top_k]

    def _update_combined(self) -> None:
        combined: List[Dict[str, Any]] = []
        for helper in ("augustine", "aquinas"):
            combined.extend(self.documents_by_helper.get(helper, []))
        self.documents_by_helper["combined"] = combined
        self._save_index("combined")

    def _load_indices(self) -> None:
        for helper in self.documents_by_helper.keys():
            index_path = self.models_dir / f"{helper}.json"
            if index_path.exists():
                try:
                    with open(index_path, "r", encoding="utf-8") as f:
                        self.documents_by_helper[helper] = json.load(f)
                except Exception:
                    self.documents_by_helper[helper] = []

    def _save_index(self, helper: str) -> None:
        index_path = self.models_dir / f"{helper}.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(self.documents_by_helper.get(helper, []), f, indent=2, ensure_ascii=False)

    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        chunks: List[str] = []
        start = 0
        text_length = len(text)
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = max(end - chunk_overlap, end)
        return chunks

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-Z']+", text.lower())

    def _score_tokens(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        if not doc_tokens:
            return 0.0
        query_set = set(query_tokens)
        doc_set = set(doc_tokens)
        overlap = len(query_set & doc_set)
        if overlap == 0:
            return 0.0
        return overlap / math.sqrt(len(doc_set))

    def _load_text(self, file_path: Path) -> Optional[str]:
        suffix = file_path.suffix.lower()
        try:
            if suffix in {".txt", ".md"}:
                return file_path.read_text(encoding="utf-8", errors="ignore")
            if suffix in {".html", ".htm"}:
                try:
                    from bs4 import BeautifulSoup  # optional
                except Exception:
                    return None
                soup = BeautifulSoup(file_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
                return soup.get_text(separator="\n")
            if suffix == ".pdf":
                try:
                    import fitz  # PyMuPDF, optional
                except Exception:
                    return None
                doc = fitz.open(str(file_path))
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
                return text
            if suffix == ".docx":
                try:
                    import docx  # python-docx, optional
                except Exception:
                    return None
                document = docx.Document(str(file_path))
                return "\n".join(p.text for p in document.paragraphs)
        except Exception:
            return None

        return None
