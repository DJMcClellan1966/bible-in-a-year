"""
Loader for Bible commentary files (PDF, JSON, etc.)
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class CommentaryLoader:
    """Load and parse commentary files from various formats."""
    
    def __init__(self, commentary_dir: Optional[Path] = None):
        if commentary_dir is None:
            commentary_dir = Path(__file__).parent.parent / "data" / "commentary"
        self.commentary_dir = commentary_dir
        self.commentary_dir.mkdir(parents=True, exist_ok=True)
    
    def load_all_commentaries(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all commentary files and organize by book/chapter."""
        commentaries: Dict[str, List[Dict[str, Any]]] = {}
        
        for file_path in self.commentary_dir.iterdir():
            if not file_path.is_file():
                continue
            
            try:
                if file_path.suffix.lower() == ".json":
                    content = self._load_json_commentary(file_path)
                elif file_path.suffix.lower() == ".pdf":
                    content = self._load_pdf_commentary(file_path)
                else:
                    continue
                
                if content:
                    # Extract book/chapter info and organize
                    book = self._extract_book(content, file_path.stem)
                    if book:
                        if book not in commentaries:
                            commentaries[book] = []
                        commentaries[book].append({
                            "source": file_path.stem,
                            "file": str(file_path),
                            "content": content,
                            "type": file_path.suffix.lower(),
                        })
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        return commentaries
    
    def _load_json_commentary(self, file_path: Path) -> Optional[str]:
        """Load text from JSON commentary file."""
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            
            # Handle Sefaria-style JSON (nested arrays)
            if isinstance(data, dict) and "text" in data:
                text_array = data["text"]
                return self._extract_text_from_nested_array(text_array)
            
            # Handle simple JSON arrays
            if isinstance(data, list):
                return self._extract_text_from_nested_array(data)
            
            # Handle dict with string values
            if isinstance(data, dict):
                return json.dumps(data, indent=2, ensure_ascii=False)
            
            return str(data)
        except Exception as e:
            print(f"Error parsing JSON {file_path}: {e}")
            return None
    
    def _extract_text_from_nested_array(self, arr: Any, depth: int = 0) -> str:
        """Recursively extract text from nested arrays (Sefaria format)."""
        if depth > 10:  # Safety limit
            return ""
        
        texts = []
        if isinstance(arr, list):
            for item in arr:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, list):
                    nested = self._extract_text_from_nested_array(item, depth + 1)
                    if nested:
                        texts.append(nested)
        elif isinstance(arr, str):
            texts.append(arr)
        
        return "\n".join(texts)
    
    def _load_pdf_commentary(self, file_path: Path) -> Optional[str]:
        """Load text from PDF commentary file."""
        if not HAS_PYMUPDF:
            return None
        
        try:
            doc = fitz.open(str(file_path))
            text_parts = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            doc.close()
            return "\n".join(text_parts)
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")
            return None
    
    def _extract_book(self, content: str, filename: str) -> Optional[str]:
        """Extract book name from content or filename."""
        # Check filename first
        filename_lower = filename.lower()
        if "genesis" in filename_lower:
            return "genesis"
        
        # Check content
        content_lower = content.lower()
        if "genesis" in content_lower:
            return "genesis"
        
        # Could extend for other books
        return None
    
    def get_commentaries_for_chapter(self, book: str, chapter: int) -> List[Dict[str, Any]]:
        """Get commentaries relevant to a specific chapter."""
        all_commentaries = self.load_all_commentaries()
        book_commentaries = all_commentaries.get(book.lower(), [])
        
        # Filter and extract relevant sections
        relevant = []
        for comm in book_commentaries:
            content = comm.get("content", "")
            # Try to find chapter-specific content
            chapter_text = self._extract_chapter_content(content, chapter)
            if chapter_text:
                relevant.append({
                    "source": comm["source"],
                    "content": chapter_text,
                })
            elif chapter == 1:  # Include general content for chapter 1
                # Take first 5000 chars as likely relevant
                relevant.append({
                    "source": comm["source"],
                    "content": content[:5000] + ("..." if len(content) > 5000 else ""),
                })
        
        return relevant
    
    def _extract_chapter_content(self, content: str, chapter: int) -> Optional[str]:
        """Extract content relevant to a specific chapter."""
        # Look for chapter markers
        patterns = [
            rf"(?i)chapter\s+{chapter}\b",
            rf"(?i)ch\.\s*{chapter}\b",
            rf"(?i)genesis\s+{chapter}\b",
            rf"(?i)gen\.\s+{chapter}\b",
        ]
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, content))
            if matches:
                # Extract text around the match
                start_idx = max(0, matches[0].start() - 200)
                # Find next chapter or end
                next_chapter = re.search(rf"(?i)chapter\s+{chapter + 1}\b", content[matches[0].end():])
                if next_chapter:
                    end_idx = matches[0].end() + next_chapter.start()
                else:
                    end_idx = min(len(content), matches[0].end() + 5000)
                
                return content[start_idx:end_idx]
        
        return None
