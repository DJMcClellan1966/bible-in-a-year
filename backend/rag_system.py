"""
Retrieval Augmented Generation system for AI helpers
Provides contextually relevant information from saints' writings
"""

import json
import math
import re
from typing import List, Dict, Any
from pathlib import Path

class RAGSystem:
    """RAG system for retrieving relevant context from saints' writings"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.models_dir = Path(__file__).parent.parent / "models"
        self.augustine_dir = self.data_dir / "augustine"
        self.index_dir = self.models_dir / "simple_index"

        self.documents_by_helper: Dict[str, List[Dict[str, Any]]] = {
            "augustine": [],
            "aquinas": [],
            "combined": []
        }
        self.load_or_create_indices()

    def load_or_create_indices(self):
        """Load existing indices or create new ones"""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        for helper in ["augustine", "aquinas", "combined"]:
            index_path = self.index_dir / f"{helper}_index.json"
            if index_path.exists():
                try:
                    with open(index_path, "r", encoding="utf-8") as f:
                        self.documents_by_helper[helper] = json.load(f)
                    print(f"Loaded index for {helper}")
                except Exception as e:
                    print(f"Error loading index for {helper}: {e}")
                    self.documents_by_helper[helper] = []

    def process_augustin_documents(self):
        """Process and index Augustine's writings"""
        if not self.augustine_dir.exists():
            print("Augustine directory not found, creating...")
            self.augustine_dir.mkdir(parents=True, exist_ok=True)
            return

        documents = []
        chunk_size = 1000
        chunk_overlap = 200

        # Process text files
        for file_path in self.augustine_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        chunks = self._chunk_text(content, chunk_size, chunk_overlap)
                        for i, chunk in enumerate(chunks):
                            documents.append({
                                "id": f"{file_path.stem}_chunk_{i}",
                                "text": chunk,
                                "source": str(file_path),
                                "author": "augustine",
                                "title": file_path.stem
                            })
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        # Process other formats if available (PDF, DOCX, etc.)
        # Add more loaders as needed

        if documents:
            self._index_documents(documents, "augustine")
            print(f"Processed {len(documents)} chunks from Augustine's writings")

    def _index_documents(self, documents: List[Dict], helper: str):
        """Index documents with a lightweight keyword index"""
        if helper not in self.documents_by_helper:
            self.documents_by_helper[helper] = []

        self.documents_by_helper[helper].extend(documents)
        self._save_index(helper)

        if helper in ["augustine", "aquinas"]:
            self._update_combined_collection()

        print(f"Indexed {len(documents)} documents for {helper}")

    def get_relevant_context(self, query: str, helper: str = "augustine", top_k: int = 5) -> List[Dict]:
        """Retrieve relevant context for a query"""
        if helper not in self.documents_by_helper:
            return []
        return self._search_keyword(query, helper, top_k)

    def _search_keyword(self, query: str, helper: str, top_k: int) -> List[Dict]:
        """Search using simple keyword overlap"""
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored_docs = []
        for doc in self.documents_by_helper.get(helper, []):
            score = self._score_tokens(query_tokens, self._tokenize(doc.get("text", "")))
            if score > 0:
                scored_doc = doc.copy()
                scored_doc["score"] = score
                scored_docs.append(scored_doc)

        scored_docs.sort(key=lambda d: d["score"], reverse=True)
        return scored_docs[:top_k]

    def add_aquinas_documents(self, documents: List[Dict]):
        """Add Aquinas documents to the system"""
        self._index_documents(documents, "aquinas")

        # Update combined collection
        self._update_combined_collection()

    def _update_combined_collection(self):
        """Update the combined collection with both Augustine and Aquinas"""
        combined_docs = []
        for helper in ["augustine", "aquinas"]:
            combined_docs.extend(self.documents_by_helper.get(helper, []))

        self.documents_by_helper["combined"] = combined_docs
        self._save_index("combined")

    def get_helper_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed documents"""
        stats = {}
        for helper, documents in self.documents_by_helper.items():
            stats[helper] = {"document_count": len(documents)}

        return stats

    def initialize_default_data(self):
        """Initialize with any available default data"""
        # Process Augustine documents if they exist
        if self.augustine_dir.exists():
            self.process_augustin_documents()

        # TODO: Add Aquinas data when available
        # TODO: Add Bible text data for reference

    def _save_index(self, helper: str):
        """Persist a helper index to disk"""
        index_path = self.index_dir / f"{helper}_index.json"
        try:
            with open(index_path, "w", encoding="utf-8") as f:
                json.dump(self.documents_by_helper.get(helper, []), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving index for {helper}: {e}")

    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Simple text chunking to avoid heavy dependencies"""
        chunks = []
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
        """Tokenize text into lowercase words"""
        return re.findall(r"[a-zA-Z']+", text.lower())

    def _score_tokens(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        """Compute a simple overlap score"""
        if not doc_tokens:
            return 0.0

        query_set = set(query_tokens)
        doc_set = set(doc_tokens)
        overlap = len(query_set & doc_set)

        if overlap == 0:
            return 0.0

        return overlap / math.sqrt(len(doc_set))