"""
Living Commentary System.
Commentaries that evolve, version, and improve over time with user feedback.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ollama_client import OllamaClient
from .rag_system import RAGSystem


@dataclass
class CommentaryVersion:
    """A version of a commentary."""
    version: int
    passage: str
    content: str
    helper: str
    generated_at: str
    quality_score: float
    user_feedback: List[Dict[str, Any]]
    improvements: List[str]


@dataclass
class CommentaryConflict:
    """A conflict between different commentary perspectives."""
    passage: str
    issue: str
    augustine_view: str
    aquinas_view: str
    modern_view: Optional[str]
    resolution: Optional[str]


class LivingCommentarySystem:
    """Manages evolving, versioned commentaries with feedback and improvements."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.commentaries_dir = self.data_dir / "living_commentaries"
        self.commentaries_dir.mkdir(parents=True, exist_ok=True)
        
        self.versions_file = self.commentaries_dir / "commentary_versions.json"
        self.conflicts_file = self.commentaries_dir / "commentary_conflicts.json"
        
        self.ollama_client: Optional[OllamaClient] = None
        self.rag_system: Optional[RAGSystem] = None
    
    def _get_ollama(self) -> OllamaClient:
        if self.ollama_client is None:
            self.ollama_client = OllamaClient()
        return self.ollama_client
    
    def _get_rag(self) -> RAGSystem:
        if self.rag_system is None:
            self.rag_system = RAGSystem()
            self.rag_system.initialize_default_data()
        return self.rag_system
    
    def generate_commentary_version(
        self,
        passage: str,
        helper: str,
        previous_version: Optional[CommentaryVersion] = None,
        improvement_hints: Optional[List[str]] = None
    ) -> CommentaryVersion:
        """Generate a new version of a commentary, optionally improving on previous."""
        rag = self._get_rag()
        ollama = self._get_ollama()
        
        # Get RAG context
        context = rag.get_relevant_context(passage, helper=helper, top_k=5)
        
        # Get passage text - use BibleReader directly
        from .bible_reader import BibleReader
        bible_reader = BibleReader()
        passage_text_obj = bible_reader.get_passage_text(passage)
        passage_text = passage
        if passage_text_obj and passage_text_obj.get("verses"):
            verse_texts = [f"{v}: {t}" for v, t in list(passage_text_obj["verses"].items())[:20]]
            passage_text = "\n".join(verse_texts)
        
        # Build prompt with improvement hints
        improvement_context = ""
        if previous_version:
            improvement_context = f"\n\nPrevious version (v{previous_version.version}):\n{previous_version.content[:500]}"
            if previous_version.user_feedback:
                feedback_summary = "\n".join([f"- {fb.get('comment', '')}" for fb in previous_version.user_feedback[-3:]])
                improvement_context += f"\n\nUser feedback:\n{feedback_summary}"
        
        if improvement_hints:
            improvement_context += f"\n\nImprovement hints:\n" + "\n".join(improvement_hints)
        
        context_text = "\n".join([item.get("text", "")[:300] for item in context[:3]])
        
        prompt = f"""Write a commentary on {passage}:
        
{passage_text[:1000]}

Context from {helper}'s writings:
{context_text[:800]}

{improvement_context}

Write a comprehensive, insightful commentary. If this is an improved version, address previous feedback and make enhancements."""
        
        system = ollama._system_prompt(helper)
        
        content = ollama._generate(prompt, system, ollama.default_model)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(content, previous_version)
        
        version_num = (previous_version.version + 1) if previous_version else 1
        
        version = CommentaryVersion(
            version=version_num,
            passage=passage,
            content=content,
            helper=helper,
            generated_at=datetime.utcnow().isoformat(),
            quality_score=quality_score,
            user_feedback=[],
            improvements=self._identify_improvements(content, previous_version)
        )
        
        # Save version
        self._save_version(version)
        
        return version
    
    def add_feedback(
        self,
        passage: str,
        helper: str,
        feedback: str,
        rating: Optional[int] = None,
        version: Optional[int] = None
    ) -> CommentaryVersion:
        """Add user feedback to a commentary version."""
        versions = self._load_versions()
        key = f"{passage}::{helper}"
        
        if key not in versions:
            # Generate initial version
            version_obj = self.generate_commentary_version(passage, helper)
        else:
            version_list = versions[key]
            if version and version <= len(version_list):
                version_obj = CommentaryVersion(**version_list[version - 1])
            else:
                version_obj = CommentaryVersion(**version_list[-1])
        
        # Add feedback
        feedback_entry = {
            "comment": feedback,
            "rating": rating,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update version object (create new one with feedback)
        updated_version = CommentaryVersion(
            version=version_obj.version,
            passage=version_obj.passage,
            content=version_obj.content,
            helper=version_obj.helper,
            generated_at=version_obj.generated_at,
            quality_score=version_obj.quality_score,
            user_feedback=version_obj.user_feedback + [feedback_entry],
            improvements=version_obj.improvements
        )
        
        # Save updated version
        self._save_version(updated_version)
        
        # Check if improvement is needed
        if rating and rating < 3:
            # Generate improved version
            improvement_hints = [feedback]
            if version_obj.improvements:
                improvement_hints.extend(version_obj.improvements)
            
            return self.generate_commentary_version(
                passage, helper, version_obj, improvement_hints
            )
        
        return updated_version
    
    def detect_conflicts(
        self,
        passage: str,
        include_modern: bool = False
    ) -> List[CommentaryConflict]:
        """Detect conflicts between different commentary perspectives."""
        # Get Augustine commentary
        augustine_version = self.get_latest_version(passage, "augustine")
        # Get Aquinas commentary
        aquinas_version = self.get_latest_version(passage, "aquinas")
        
        if not augustine_version or not aquinas_version:
            return []
        
        ollama = self._get_ollama()
        
        prompt = f"""Compare these two commentaries on {passage}:

Augustine's view:
{augustine_version.content[:800]}

Aquinas's view:
{aquinas_version.content[:800]}

Identify:
1. Any contradictions or tensions
2. Different emphases or approaches
3. Complementary insights
4. Areas where they agree or disagree

If there are conflicts, describe them. If they are complementary, note that."""
        
        system = "You are a theological scholar comparing different commentary perspectives."
        
        try:
            response = ollama._generate(prompt, system, ollama.default_model)
            
            # Check if conflicts are mentioned
            conflict_keywords = ["contradict", "differ", "disagree", "tension", "conflict"]
            has_conflict = any(keyword in response.lower() for keyword in conflict_keywords)
            
            if has_conflict or "complement" in response.lower():
                return [
                    CommentaryConflict(
                        passage=passage,
                        issue=response[:300],
                        augustine_view=augustine_version.content[:500],
                        aquinas_view=aquinas_version.content[:500],
                        modern_view=None,
                        resolution=None
                    )
                ]
        except Exception:
            pass
        
        return []
    
    def get_latest_version(self, passage: str, helper: str) -> Optional[CommentaryVersion]:
        """Get the latest version of a commentary."""
        versions = self._load_versions()
        key = f"{passage}::{helper}"
        
        if key not in versions or not versions[key]:
            return None
        
        # Get latest version (highest version number)
        version_list = versions[key]
        latest = max(version_list, key=lambda v: v.get("version", 0))
        
        return CommentaryVersion(**latest)
    
    def get_all_versions(self, passage: str, helper: str) -> List[CommentaryVersion]:
        """Get all versions of a commentary."""
        versions = self._load_versions()
        key = f"{passage}::{helper}"
        
        if key not in versions:
            return []
        
        return [CommentaryVersion(**v) for v in sorted(versions[key], key=lambda x: x.get("version", 0))]
    
    def _calculate_quality_score(
        self,
        content: str,
        previous: Optional[CommentaryVersion] = None
    ) -> float:
        """Calculate quality score for commentary."""
        # Simple heuristics - could be enhanced
        score = 0.5  # Base score
        
        # Length check
        if len(content) > 500:
            score += 0.1
        if len(content) > 1000:
            score += 0.1
        
        # Improvement over previous
        if previous:
            if len(content) > len(previous.content):
                score += 0.1
            if previous.quality_score < 0.7 and len(content) > 800:
                score += 0.1
        
        # User feedback average
        if previous and previous.user_feedback:
            ratings = [fb.get("rating", 3) for fb in previous.user_feedback if fb.get("rating")]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                score += (avg_rating - 3) * 0.05  # Adjust based on feedback
        
        return min(1.0, max(0.0, score))
    
    def _identify_improvements(
        self,
        content: str,
        previous: Optional[CommentaryVersion]
    ) -> List[str]:
        """Identify improvements made in this version."""
        improvements = []
        
        if not previous:
            return improvements
        
        if len(content) > len(previous.content) * 1.2:
            improvements.append("Expanded coverage")
        
        if previous.user_feedback:
            improvements.append("Addressed user feedback")
        
        return improvements
    
    def _load_versions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all commentary versions."""
        if self.versions_file.exists():
            try:
                return json.loads(self.versions_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}
    
    def _save_version(self, version: CommentaryVersion) -> None:
        """Save a commentary version."""
        versions = self._load_versions()
        key = f"{version.passage}::{version.helper}"
        
        if key not in versions:
            versions[key] = []
        
        # Convert to dict
        version_dict = {
            "version": version.version,
            "passage": version.passage,
            "content": version.content,
            "helper": version.helper,
            "generated_at": version.generated_at,
            "quality_score": version.quality_score,
            "user_feedback": version.user_feedback,
            "improvements": version.improvements
        }
        
        # Remove old version if exists, add new
        versions[key] = [v for v in versions[key] if v.get("version") != version.version]
        versions[key].append(version_dict)
        
        self.versions_file.write_text(
            json.dumps(versions, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
