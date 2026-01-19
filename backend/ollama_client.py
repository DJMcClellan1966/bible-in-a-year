"""
Ollama client supporting local and remote instances.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

import requests


class OllamaClient:
    def __init__(self) -> None:
        self.local_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.remote_url = os.getenv("OLLAMA_REMOTE_URL")
        # Allow different models for different tasks
        self.default_model = os.getenv("OLLAMA_MODEL", "llama2:7b")
        self.fast_model = os.getenv("OLLAMA_FAST_MODEL", "llama3.2:1b")  # Faster model for quick tasks
        self.quality_model = os.getenv("OLLAMA_QUALITY_MODEL", "llama2:7b")  # Higher quality for complex tasks

    def generate_commentary(
        self,
        passage: str,
        context: List[Dict[str, Any]],
        helper: str,
        personalized: bool = False,
    ) -> str:
        system_prompt = self._system_prompt(helper)
        context_text = self._format_context(context)
        
        # Enhanced prompt for Augustine that emphasizes interpretive commentary
        if helper == "augustine":
            prompt = (
                f"Write a profound commentary on this Bible passage:\n\n{passage}\n\n"
                f"{context_text}\n\n"
                "Drawing from your own theological writings and style, provide: "
                "1) Deep exegetical interpretation of the text's meaning, "
                "2) Spiritual and theological insights that illuminate the passage, "
                "3) Connections to broader themes in Scripture, "
                "4) Pastoral wisdom for spiritual growth. "
                "Do not simply paraphrase or repeat the text. Instead, offer your own "
                "thoughtful analysis and interpretation in your characteristic style—"
                "reflective, profound, and spiritually enriching. Write as if composing "
                "a new commentary that reveals deeper meanings the reader might not see."
            )
        else:
            prompt = (
                f"Provide commentary on this Bible passage:\n\n{passage}\n\n"
                f"{context_text}\n\n"
                "Offer spiritual insights, explain the meaning in context, and provide guidance for reflection."
            )
        
        if personalized:
            prompt += "\n\nOffer pastoral guidance tailored to a daily spiritual journey."
        
        # Use quality model for commentaries (important content)
        return self._generate(prompt, system_prompt, model=self.quality_model)

    def generate_modern_language_explanation(
        self,
        passage: str,
        passage_text: str
    ) -> str:
        """Generate modern language explanation - can use faster model."""
        prompt = f"""Explain this Bible passage in modern, everyday language:

PASSAGE: {passage}

TEXT:
{passage_text}

Provide:
1. A clear, modern paraphrase
2. Explanation of any archaic terms or cultural references
3. What this passage means in today's context

Write in simple, accessible language that anyone can understand."""
        
        system = "You are a Bible teacher who explains Scripture in clear, modern language."
        
        # Use fast model for simple explanations
        return self._generate(prompt, system, model=self.fast_model)

    def _generate(
        self,
        prompt: str,
        system: str,
        model: Optional[str] = None,
        num_predict: int = 1500,
    ) -> str:
        """Generate text using Ollama."""
        if model is None:
            model = self.default_model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "num_predict": num_predict,
                "temperature": 0.7,
            },
        }
        
        response = self._post("/api/generate", payload)
        return response.get("response", "")

    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format RAG context for prompts."""
        if not context:
            return ""
        
        texts = []
        for item in context[:3]:  # Limit to 3 snippets for speed
            snippet = item.get("text", "")[:400]  # Shorter snippets
            if snippet:
                texts.append(f"- {snippet}")
        
        if texts:
            return "Relevant context from writings:\n" + "\n".join(texts)
        return ""

    def _system_prompt(self, helper: str) -> str:
        """Get system prompt for a helper."""
        prompts = {
            "augustine": (
                "You are Saint Augustine of Hippo, Bishop and Doctor of the Church. "
                "Write commentary in your characteristic style: profound, reflective, "
                "spiritually rich, drawing from your theological insights on grace, "
                "predestination, original sin, and the relationship between faith and reason."
            ),
            "aquinas": (
                "You are Saint Thomas Aquinas, Doctor Angelicus. Write commentary with "
                "clarity, systematic thought, and logical structure. Emphasize natural "
                "theology, the harmony of faith and reason, and provide clear, accessible "
                "explanations of complex theological concepts."
            ),
        }
        return prompts.get(helper, "You are a biblical scholar providing insightful commentary.")

    def _post(self, endpoint: str, payload: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:

        for attempt in range(max_retries):
            try:
                url = f"{self.local_url}{endpoint}"
                response = requests.post(url, json=payload, timeout=300)  # 5 min for slower machines
                response.raise_for_status()
                return response.json()
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Cannot connect to Ollama at {self.local_url}. Is Ollama running? Error: {e}"
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))  # Exponential backoff
                    continue
            except requests.exceptions.Timeout:
                error_msg = "Ollama request timed out. The model may be loading or the request is too complex."
                if attempt < max_retries - 1:
                    time.sleep(10 * (attempt + 1))
                    continue
            except Exception as e:
                error_msg = f"Ollama local request failed: {type(e).__name__}: {e}"
                if attempt < max_retries - 1:
                    time.sleep(3 * (attempt + 1))
                    continue

        # Try remote if local failed
        if self.remote_url:
            for attempt in range(max_retries):
                try:
                    response = requests.post(f"{self.remote_url}{endpoint}", json=payload, timeout=180)
                    response.raise_for_status()
                    return response.json()
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                    error_msg = f"Ollama remote request also failed: {type(e).__name__}: {e}"

        raise RuntimeError(error_msg)
