"""
Great Thinkers System - Synthesizing wisdom from church history.
Combines insights from Augustine, Aquinas, and other great Christian thinkers
to answer life's profound questions.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .rag_system import RAGSystem
from .ollama_client import OllamaClient
from .web_scraper import BibleWebScraper


@dataclass
class ThinkerInsight:
    """Insight from a great Christian thinker."""
    thinker: str
    era: str
    tradition: str
    insight: str
    source: Optional[str] = None


@dataclass
class SynthesizedWisdom:
    """Combined wisdom from multiple thinkers on a question."""
    question: str
    thinkers: List[ThinkerInsight]
    synthesized_answer: str
    key_themes: List[str]


class GreatThinkersSystem:
    """Synthesizes wisdom from great Christian thinkers throughout history."""
    
    # Core thinkers we have data for
    CORE_THINKERS = {
        "Augustine": {
            "era": "Early Church (4th-5th century)",
            "tradition": "Patristic",
            "focus": "Grace, predestination, original sin, Christian philosophy"
        },
        "Aquinas": {
            "era": "Medieval (13th century)",
            "tradition": "Scholastic",
            "focus": "Natural theology, systematic theology, faith and reason"
        }
    }
    
    # Additional great thinkers to find via web scraping
    HISTORICAL_THINKERS = [
        "Tertullian", "Origen", "John Chrysostom", "Jerome",
        "Gregory the Great", "Anselm of Canterbury", "Bonaventure",
        "Martin Luther", "John Calvin", "John Wesley",
        "Thomas Merton", "C.S. Lewis", "G.K. Chesterton"
    ]
    
    # Profound questions people struggle with
    PROFOUND_QUESTIONS = [
        "What is the purpose of life?",
        "Why do we suffer?",
        "What happens after death?",
        "How can we know God?",
        "What is love?",
        "How should we live?",
        "What is truth?",
        "What is the meaning of suffering?",
        "How do faith and reason relate?",
        "What is human nature?",
        "What is sin?",
        "What is salvation?",
        "How should we treat others?",
        "What is prayer?",
        "What is the church?",
        "How do we find peace?",
        "What is hope?",
        "What is forgiveness?",
        "What is justice?",
        "What is wisdom?"
    ]
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.thinkers_file = self.data_dir / "great_thinkers_wisdom.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.rag_system: Optional[RAGSystem] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.web_scraper: Optional[BibleWebScraper] = None
    
    def _get_rag_system(self) -> RAGSystem:
        if self.rag_system is None:
            self.rag_system = RAGSystem()
            if not self.rag_system._has_cached_data():
                self.rag_system.initialize_default_data()
        return self.rag_system
    
    def _get_ollama(self) -> OllamaClient:
        if self.ollama_client is None:
            self.ollama_client = OllamaClient()
        return self.ollama_client
    
    def _get_web_scraper(self) -> BibleWebScraper:
        if self.web_scraper is None:
            self.web_scraper = BibleWebScraper()
        return self.web_scraper
    
    def synthesize_wisdom_on_question(
        self, 
        question: str, 
        thinkers: Optional[List[str]] = None,
        scrape_web: bool = True
    ) -> SynthesizedWisdom:
        """Synthesize wisdom from great thinkers on a profound question."""
        if thinkers is None:
            thinkers = list(self.CORE_THINKERS.keys())
        
        thinker_insights = []
        
        # Get insights from core thinkers (via RAG)
        for thinker in thinkers:
            if thinker in self.CORE_THINKERS:
                insights = self._get_thinker_insights(thinker, question)
                for insight_text in insights:
                    thinker_insights.append(ThinkerInsight(
                        thinker=thinker,
                        era=self.CORE_THINKERS[thinker]["era"],
                        tradition=self.CORE_THINKERS[thinker]["tradition"],
                        insight=insight_text
                    ))
        
        # Get insights from web scraping for additional thinkers
        if scrape_web:
            web_insights = self._scrape_thinker_insights(question, self.HISTORICAL_THINKERS[:5])  # Limit to 5 for speed
            thinker_insights.extend(web_insights)
        
        # Synthesize all insights into unified answer
        synthesized = self._synthesize_insights(question, thinker_insights)
        
        # Extract key themes
        key_themes = self._extract_themes(thinker_insights)
        
        return SynthesizedWisdom(
            question=question,
            thinkers=thinker_insights,
            synthesized_answer=synthesized,
            key_themes=key_themes
        )
    
    def _get_thinker_insights(self, thinker: str, question: str, top_k: int = 3) -> List[str]:
        """Get insights from a thinker via RAG system."""
        try:
            helper = "augustine" if thinker == "Augustine" else "aquinas"
            rag = self._get_rag_system()
            
            # Search for relevant context related to the question
            # Use the question as a search query
            context = rag.get_relevant_context(question, helper=helper, top_k=top_k)
            
            # Extract insights from context
            insights = []
            for item in context:
                text = item.get("text", "")
                if text and len(text) > 50:  # Substantial insight
                    insights.append(text[:500])  # Limit length
            
            return insights[:top_k]
        except Exception as e:
            print(f"Error getting {thinker} insights: {e}")
            return []
    
    def _scrape_thinker_insights(self, question: str, thinkers: List[str]) -> List[ThinkerInsight]:
        """Scrape web for insights from historical thinkers."""
        insights = []
        
        try:
            scraper = self._get_web_scraper()
            
            for thinker in thinkers:
                # Search for thinker + question
                search_query = f"{thinker} Christian {question}"
                results = scraper.search_commentary(search_query, max_results=2)
                
                if results:
                    for result in results[:1]:  # One result per thinker for speed
                        text = result.get("text", "")
                        if text and len(text) > 100:
                            insights.append(ThinkerInsight(
                                thinker=thinker,
                                era=self._get_thinker_era(thinker),
                                tradition=self._get_thinker_tradition(thinker),
                                insight=text[:500],
                                source=result.get("url", "")
                            ))
        except Exception as e:
            print(f"Error scraping thinker insights: {e}")
        
        return insights
    
    def _get_thinker_era(self, thinker: str) -> str:
        """Get historical era for a thinker."""
        eras = {
            "Tertullian": "Early Church (2nd-3rd century)",
            "Origen": "Early Church (2nd-3rd century)",
            "John Chrysostom": "Early Church (4th century)",
            "Jerome": "Early Church (4th-5th century)",
            "Gregory the Great": "Early Middle Ages (6th century)",
            "Anselm of Canterbury": "Medieval (11th century)",
            "Bonaventure": "Medieval (13th century)",
            "Martin Luther": "Reformation (16th century)",
            "John Calvin": "Reformation (16th century)",
            "John Wesley": "Modern (18th century)",
            "Thomas Merton": "Modern (20th century)",
            "C.S. Lewis": "Modern (20th century)",
            "G.K. Chesterton": "Modern (20th century)"
        }
        return eras.get(thinker, "Christian Tradition")
    
    def _get_thinker_tradition(self, thinker: str) -> str:
        """Get theological tradition for a thinker."""
        traditions = {
            "Tertullian": "Early Church Father",
            "Origen": "Early Church Father",
            "John Chrysostom": "Eastern Orthodox",
            "Jerome": "Early Church Father",
            "Gregory the Great": "Roman Catholic",
            "Anselm of Canterbury": "Scholastic",
            "Bonaventure": "Franciscan",
            "Martin Luther": "Protestant/Lutheran",
            "John Calvin": "Protestant/Reformed",
            "John Wesley": "Methodist",
            "Thomas Merton": "Catholic Contemplative",
            "C.S. Lewis": "Anglican/Apologist",
            "G.K. Chesterton": "Catholic Apologist"
        }
        return traditions.get(thinker, "Christian Tradition")
    
    def _synthesize_insights(self, question: str, insights: List[ThinkerInsight]) -> str:
        """Synthesize multiple insights into a unified answer using Ollama."""
        try:
            ollama = self._get_ollama()
            
            # Format insights by thinker
            insights_text = []
            for i, insight in enumerate(insights, 1):
                insights_text.append(
                    f"{insight.thinker} ({insight.era}, {insight.tradition}):\n"
                    f"{insight.insight}\n"
                )
            
            insights_formatted = "\n".join(insights_text)
            
            prompt = f"""Synthesize the wisdom from these great Christian thinkers to answer this profound question:

QUESTION: {question}

THINKERS' INSIGHTS:
{insights_formatted}

Provide a synthesized answer that:
1. Draws from the collective wisdom of all these thinkers
2. Shows how different traditions and eras address the question
3. Identifies common themes and complementary perspectives
4. Offers practical wisdom for living today
5. Is comprehensive yet accessible (400-600 words)

Format as a coherent answer that weaves together these perspectives."""
            
            system = """You are a theological scholar who synthesizes wisdom from great Christian thinkers across history. You present their insights respectfully, show how they complement each other, and offer practical wisdom for today's questions."""
            
            synthesized = ollama._generate(prompt, system, ollama.default_model)
            return synthesized
        except Exception as e:
            print(f"Error synthesizing insights: {e}")
            return f"Combined wisdom from {len(insights)} great Christian thinkers on: {question}"
    
    def _extract_themes(self, insights: List[ThinkerInsight]) -> List[str]:
        """Extract key themes from insights."""
        # Simple theme extraction - could be enhanced
        themes = []
        all_text = " ".join([i.insight.lower() for i in insights])
        
        theme_keywords = {
            "grace": "Divine Grace",
            "love": "Love",
            "faith": "Faith",
            "hope": "Hope",
            "suffering": "Suffering & Redemption",
            "salvation": "Salvation",
            "purpose": "Purpose & Calling",
            "truth": "Truth",
            "wisdom": "Wisdom",
            "prayer": "Prayer & Contemplation",
            "community": "Community & Church",
            "virtue": "Virtue & Character",
            "justice": "Justice",
            "forgiveness": "Forgiveness & Mercy"
        }
        
        for keyword, theme in theme_keywords.items():
            if keyword in all_text and theme not in themes:
                themes.append(theme)
        
        return themes[:5]  # Top 5 themes
    
    def answer_profound_question(self, question: str, include_web: bool = True) -> Dict[str, Any]:
        """Answer a profound question using synthesized wisdom from great thinkers."""
        wisdom = self.synthesize_wisdom_on_question(question, scrape_web=include_web)
        
        return {
            "question": wisdom.question,
            "synthesized_answer": wisdom.synthesized_answer,
            "thinkers": [
                {
                    "name": t.thinker,
                    "era": t.era,
                    "tradition": t.tradition,
                    "insight": t.insight[:200] + "..." if len(t.insight) > 200 else t.insight,
                    "source": t.source
                }
                for t in wisdom.thinkers
            ],
            "key_themes": wisdom.key_themes,
            "thinker_count": len(wisdom.thinkers)
        }
    
    def get_available_questions(self) -> List[str]:
        """Get list of profound questions that can be answered."""
        return self.PROFOUND_QUESTIONS.copy()
