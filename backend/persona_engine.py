"""
AI Persona Conversation Engine.
Enables natural conversations with historical figures like Augustine and Aquinas.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ollama_client import OllamaClient
from .rag_system import RAGSystem


class PersonaEngine:
    """Manages AI persona conversations with memory and character consistency."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.conversations_dir = self.data_dir / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        
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
    
    def chat_with_persona(
        self,
        persona: str,
        message: str,
        conversation_id: Optional[str] = None,
        context_passage: Optional[str] = None,
        max_history: int = 10
    ) -> Dict[str, Any]:
        """Have a conversation with an AI persona."""
        # Load conversation history
        conversation = self._load_conversation(conversation_id) if conversation_id else []
        
        # Get RAG context
        rag_context = self._get_rag().get_relevant_context(
            message if not context_passage else f"{context_passage} {message}",
            helper=persona,
            top_k=5
        )
        
        # Build persona-specific system prompt
        system_prompt = self._get_persona_prompt(persona)
        
        # Build conversation context
        conversation_context = self._build_conversation_context(
            conversation[-max_history:] if len(conversation) > max_history else conversation,
            context_passage
        )
        
        # Add RAG context to prompt
        rag_text = self._format_rag_context(rag_context)
        
        # Build full prompt
        if context_passage:
            prompt = f"""Context: We are discussing {context_passage}.

{conversation_context}

You said: "{message}"

Please respond in character, drawing from your writings and teachings."""
        else:
            prompt = f"""{conversation_context}

You said: "{message}"

Please respond in character."""
        
        if rag_text:
            prompt = f"{rag_text}\n\n{prompt}"
        
        # Generate response
        response = self._get_ollama()._generate(
            prompt=prompt,
            system=system_prompt,
            model=self._get_ollama().default_model
        )
        
        # Save conversation
        conversation.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if conversation_id:
            self._save_conversation(conversation_id, conversation)
        
        return {
            "response": response,
            "persona": persona,
            "conversation_id": conversation_id or self._generate_conversation_id(persona),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_persona_prompt(self, persona: str) -> str:
        """Get system prompt for a specific persona."""
        prompts = {
            "augustine": (
                "You are Saint Augustine of Hippo, Bishop and Doctor of the Church. "
                "You are having a personal conversation with a seeker. Speak naturally, "
                "warmly, and with deep spiritual insight. Reference your actual writings "
                "(Confessions, City of God, On Christian Doctrine) naturally. Be conversational "
                "but maintain your theological depth. Answer questions from your historical "
                "perspective, but apply timeless wisdom to the person's situation. You don't "
                "know about events after your death (430 AD), but you can offer timeless wisdom."
            ),
            "aquinas": (
                "You are Saint Thomas Aquinas, Doctor Angelicus. You are having a scholarly "
                "conversation, but you are warm and pastoral. You explain things with clarity "
                "and reason, drawing from your Summa Theologica and other works. Be systematic "
                "but accessible. You value both faith and reason. You don't know about events "
                "after your death (1274 AD), but your theological principles are timeless."
            ),
            "combined": (
                "You represent the combined wisdom of Saints Augustine and Aquinas. "
                "Blend Augustine's spiritual depth and passion with Aquinas's clarity and "
                "systematic thought. Offer balanced, comprehensive guidance that draws from "
                "both traditions."
            )
        }
        return prompts.get(persona, prompts["augustine"])
    
    def _build_conversation_context(
        self,
        conversation: List[Dict[str, Any]],
        context_passage: Optional[str] = None
    ) -> str:
        """Build conversation context from history."""
        if not conversation:
            if context_passage:
                return f"We are discussing the Bible passage: {context_passage}."
            return ""
        
        context_parts = []
        if context_passage:
            context_parts.append(f"Context: We are discussing {context_passage}.")
        
        context_parts.append("\nRecent conversation:")
        for msg in conversation[-6:]:  # Last 6 messages (3 exchanges)
            role = "You" if msg["role"] == "user" else "I"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def _format_rag_context(self, rag_context: List[Dict[str, Any]]) -> str:
        """Format RAG context for prompt."""
        if not rag_context:
            return ""
        
        texts = []
        for item in rag_context[:3]:
            snippet = item.get("text", "")[:500]
            if snippet:
                texts.append(f"- {snippet}")
        
        if texts:
            return "From your writings:\n" + "\n".join(texts)
        return ""
    
    def _load_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Load conversation history."""
        filepath = self.conversations_dir / f"{conversation_id}.json"
        if filepath.exists():
            try:
                return json.loads(filepath.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []
    
    def _save_conversation(self, conversation_id: str, conversation: List[Dict[str, Any]]) -> None:
        """Save conversation history."""
        filepath = self.conversations_dir / f"{conversation_id}.json"
        filepath.write_text(
            json.dumps(conversation, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    
    def _generate_conversation_id(self, persona: str) -> str:
        """Generate unique conversation ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{persona}_{timestamp}"
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get summary of a conversation."""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return {"exists": False}
        
        return {
            "exists": True,
            "message_count": len(conversation),
            "start_time": conversation[0]["timestamp"] if conversation else None,
            "last_message": conversation[-1]["content"][:100] if conversation else None,
            "topics": self._extract_topics(conversation)
        }
    
    def _extract_topics(self, conversation: List[Dict[str, Any]]) -> List[str]:
        """Extract main topics from conversation."""
        # Simple keyword extraction - could be enhanced with AI
        all_text = " ".join([msg["content"] for msg in conversation])
        # Common Bible/faith topics
        topics = []
        keywords = {
            "grace": "Grace",
            "sin": "Sin and Redemption",
            "faith": "Faith",
            "prayer": "Prayer",
            "salvation": "Salvation",
            "love": "Love",
            "scripture": "Scripture Study"
        }
        all_text_lower = all_text.lower()
        for keyword, topic in keywords.items():
            if keyword in all_text_lower:
                topics.append(topic)
        return list(set(topics))[:5]
    
    def debate_mode(
        self,
        question: str,
        persona1: str,
        persona2: str,
        context_passage: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get debate-style responses from two personas on a question."""
        ollama = self._get_ollama()
        rag = self._get_rag()
        
        # Get context for both personas
        context1 = rag.get_relevant_context(question, helper=persona1, top_k=3)
        context2 = rag.get_relevant_context(question, helper=persona2, top_k=3)
        
        context_text1 = "\n".join([item.get("text", "")[:300] for item in context1])
        context_text2 = "\n".join([item.get("text", "")[:300] for item in context2])
        
        # Generate response from persona 1
        prompt1 = f"""You are {persona1}. A question has been posed: {question}

Context from your writings:
{context_text1[:800]}

Provide your perspective (200-300 words). Be clear and direct."""
        
        system1 = ollama._system_prompt(persona1)
        response1 = ollama._generate(prompt1, system1, ollama.default_model)
        
        # Generate response from persona 2 (with awareness of persona 1's response)
        prompt2 = f"""You are {persona2}. A question has been posed: {question}

{persona1} has responded:
{response1[:400]}

Context from your writings:
{context_text2[:800]}

Provide your perspective (200-300 words). You may agree, disagree, or offer a different angle."""
        
        system2 = ollama._system_prompt(persona2)
        response2 = ollama._generate(prompt2, system2, ollama.default_model)
        
        return {
            "question": question,
            "persona1": persona1,
            "persona2": persona2,
            "response1": response1,
            "response2": response2,
            "mode": "debate"
        }
    
    def panel_discussion(
        self,
        question: str,
        personas: List[str],
        context_passage: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get panel-style responses from multiple personas."""
        ollama = self._get_ollama()
        rag = self._get_rag()
        
        responses = {}
        
        # Collect all responses first
        for persona in personas:
            context = rag.get_relevant_context(question, helper=persona, top_k=3)
            context_text = "\n".join([item.get("text", "")[:300] for item in context])
            
            prompt = f"""You are {persona}. In a panel discussion, this question was asked: {question}

Context from your writings:
{context_text[:800]}

Provide your perspective (150-200 words). Be concise and insightful."""
            
            system = ollama._system_prompt(persona)
            response = ollama._generate(prompt, system, ollama.default_model)
            responses[persona] = response
        
        # Generate moderator summary
        all_responses = "\n\n".join([f"{p}: {r[:200]}" for p, r in responses.items()])
        summary_prompt = f"""Summarize this panel discussion on: {question}

Panel responses:
{all_responses}

Provide a brief summary (100-150 words) highlighting key points and areas of agreement or disagreement."""
        
        summary = ollama._generate(summary_prompt, "You are a theological moderator.", ollama.default_model)
        
        return {
            "question": question,
            "personas": personas,
            "responses": responses,
            "moderator_summary": summary,
            "mode": "panel"
        }
    
    def historical_qa(
        self,
        question: str,
        historical_figure: str,
        time_period: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get response from a historical figure with period-appropriate knowledge."""
        ollama = self._get_ollama()
        rag = self._get_rag()
        
        context = rag.get_relevant_context(question, helper=historical_figure, top_k=5)
        context_text = "\n".join([item.get("text", "")[:300] for item in context])
        
        period_context = f" (Historical context: {time_period})" if time_period else ""
        
        prompt = f"""You are {historical_figure}{period_context}. Answer this question as you would have in your time:

{question}

Context from your writings:
{context_text[:1000]}

Provide a thoughtful answer (200-300 words) that reflects your historical perspective and knowledge."""
        
        system = ollama._system_prompt(historical_figure)
        response = ollama._generate(prompt, system, ollama.default_model)
        
        return {
            "question": question,
            "historical_figure": historical_figure,
            "time_period": time_period,
            "response": response,
            "mode": "historical_qa"
        }
