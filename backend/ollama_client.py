"""
Ollama client supporting local and remote instances.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests


class OllamaClient:
    def __init__(self) -> None:
        self.local_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.remote_url = os.getenv("OLLAMA_REMOTE_URL")
        self.default_model = os.getenv("OLLAMA_MODEL", "llama2:7b")

    def generate_commentary(
        self,
        passage: str,
        context: List[Dict[str, Any]],
        helper: str,
        personalized: bool = False,
    ) -> str:
        system_prompt = self._system_prompt(helper)
        context_text = self._format_context(context)
        prompt = (
            f"Provide commentary on this Bible passage:\n\n{passage}\n\n"
            f"{context_text}\n\n"
            "Offer spiritual insights, explain the meaning in context, and provide guidance for reflection."
        )
        if personalized:
            prompt += "\n\nOffer pastoral guidance tailored to a daily spiritual journey."
        return self._generate(prompt, system_prompt, model=self.default_model)

    def generate_answer(
        self,
        question: str,
        context: List[Dict[str, Any]],
        helper: str,
        additional_context: Optional[str] = None,
    ) -> str:
        system_prompt = self._system_prompt(helper)
        context_text = self._format_context(context)
        if additional_context:
            context_text += f"\n\nAdditional context: {additional_context}"
        prompt = (
            f"A seeker asks: \"{question}\"\n\n{context_text}\n\n"
            "Provide a thoughtful, spiritually nourishing answer."
        )
        return self._generate(prompt, system_prompt, model=self.default_model)

    def _generate(self, prompt: str, system: str, model: str) -> str:
        payload = {
            "model": model,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 400,  # Reduced for faster response
            },
        }

        response = self._post("/api/generate", payload)
        return response.get("response", "Unable to generate a response at this time.")

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            url = f"{self.local_url}{endpoint}"
            response = requests.post(url, json=payload, timeout=300)  # 5 min for slower machines
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Cannot connect to Ollama at {self.local_url}. Is Ollama running? Error: {e}"
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out. The model may be loading or the request is too complex."
        except Exception as e:
            error_msg = f"Ollama local request failed: {type(e).__name__}: {e}"

        if self.remote_url:
            try:
                response = requests.post(f"{self.remote_url}{endpoint}", json=payload, timeout=180)
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                return {"response": f"Both local and remote Ollama failed. Local: {error_msg}. Remote: {exc}"}

        return {"response": error_msg}

    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        if not context:
            return ""
        lines = []
        for item in context[:2]:  # Reduced from 3 to 2 for faster generation
            snippet = item.get("text", "")
            if len(snippet) > 200:  # Reduced from 280
                snippet = snippet[:200] + "..."
            lines.append(f"- {snippet}")
        return "Drawing from these teachings:\n" + "\n".join(lines)

    def _system_prompt(self, helper: str) -> str:
        if helper == "aquinas":
            return (
                "You are Saint Thomas Aquinas. Respond with clarity and reason, "
                "grounded in Scripture and theology. Be systematic, pastoral, and concise."
            )
        if helper == "combined":
            return (
                "You provide combined wisdom from Saints Augustine and Aquinas, "
                "blending spiritual depth with clear reasoning."
            )
        return (
            "You are Saint Augustine. Respond with reflective, pastoral guidance grounded in Scripture."
        )
