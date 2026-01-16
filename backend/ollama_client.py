"""
Ollama client for AI model integration
Supports both local and internet Ollama instances
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests

class OllamaClient:
    """Client for interacting with Ollama AI models"""

    def __init__(self):
        self.local_url = "http://localhost:11434"
        self.internet_url = None  # Can be configured for remote Ollama instances
        self.default_model = "llama2:7b"  # Default model, can be changed
        self.timeout = aiohttp.ClientTimeout(total=120)  # 2 minute timeout

        # Helper configurations
        self.helper_configs = {
            "augustine": {
                "model": "llama2:7b",
                "system_prompt": """You are Saint Augustine of Hippo, one of the greatest Christian theologians and philosophers.
                Draw from your writings like Confessions, City of God, and other works to provide spiritual guidance.
                Your responses should be:
                - Deeply spiritual and reflective
                - Rooted in Scripture and Christian tradition
                - Focused on God's grace, human nature, and the journey to truth
                - Personal and pastoral in tone
                - Intellectually rigorous but accessible
                Always respond as Augustine, using first-person language and drawing from your own experiences and teachings.""",

                "personality": "Wise, contemplative, deeply spiritual, occasionally autobiographical"
            },
            "aquinas": {
                "model": "llama2:7b",
                "system_prompt": """You are Saint Thomas Aquinas, the Doctor Angelicus, renowned for your systematic theology in the Summa Theologica.
                Your responses should be:
                - Logically structured and reasoned
                - Grounded in both faith and natural reason
                - Focused on objective truth and divine wisdom
                - Systematic in approach, often using question-and-answer format
                - Deeply philosophical yet accessible
                - Drawing from Aristotelian philosophy integrated with Christian theology
                Always respond as Aquinas, maintaining intellectual rigor and clarity.""",

                "personality": "Intellectual, systematic, philosophical, methodical, truth-seeking"
            },
            "combined": {
                "model": "llama2:13b",  # Larger model for combined insights
                "system_prompt": """You are a synthesis of wisdom from Saints Augustine and Aquinas, representing the rich tradition of Christian theology.
                Your responses should:
                - Combine Augustine's spiritual depth with Aquinas's systematic reasoning
                - Bridge personal experience with intellectual analysis
                - Provide comprehensive biblical and theological insights
                - Balance contemplation with logical analysis
                - Offer guidance that is both spiritually nourishing and intellectually sound
                Draw from both traditions while maintaining coherence and depth.""",

                "personality": "Comprehensive, balanced, integrative, wise, pastoral yet intellectual"
            }
        }

    async def _make_request(self, endpoint: str, payload: Dict, use_internet: bool = False) -> Dict:
        """Make a request to Ollama API"""
        url = f"{self.internet_url if use_internet else self.local_url}/{endpoint}"

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error {response.status}: {error_text}")
        except aiohttp.ClientError as e:
            if not use_internet:
                print(f"Local Ollama not available, trying internet: {e}")
                if self.internet_url:
                    return await self._make_request(endpoint, payload, use_internet=True)
            raise Exception(f"Ollama connection failed: {e}")

    def check_ollama_status(self) -> Dict[str, Any]:
        """Check if Ollama is running and get available models"""
        try:
            # Check local first
            response = requests.get(f"{self.local_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "status": "available",
                    "source": "local",
                    "models": [model["name"] for model in models]
                }
        except:
            pass

        # Check internet if configured
        if self.internet_url:
            try:
                response = requests.get(f"{self.internet_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return {
                        "status": "available",
                        "source": "internet",
                        "models": [model["name"] for model in models]
                    }
            except:
                pass

        return {"status": "unavailable", "models": []}

    async def generate_commentary(self, passage: str, context: List[Dict],
                                helper: str = "augustine", personalized: bool = False) -> str:
        """Generate AI commentary on a Bible passage"""

        config = self.helper_configs.get(helper, self.helper_configs["augustine"])

        # Prepare context
        context_text = ""
        if context:
            context_text = "\n\nRelevant teachings for reference:\n" + "\n".join([
                f"- {item['text'][:200]}..." for item in context[:3]
            ])

        # Build prompt
        system_prompt = config["system_prompt"]

        user_prompt = f"""Please provide commentary on this Bible passage:

{passage}

{context_text}

Please offer spiritual insights, explain the meaning in context, and provide guidance for personal reflection."""

        if personalized:
            user_prompt += "\n\nConsider this as guidance for someone on a spiritual journey, much like my own path to faith."

        payload = {
            "model": config["model"],
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 500
            }
        }

        try:
            response = await self._make_request("api/generate", payload)
            return response.get("response", "Unable to generate commentary at this time.")
        except Exception as e:
            return f"I apologize, but I am unable to provide commentary at this moment. Error: {str(e)}"

    async def generate_answer(self, question: str, context: List[Dict],
                            helper: str = "augustine", additional_context: Optional[str] = None) -> str:
        """Generate an answer to a user's question"""

        config = self.helper_configs.get(helper, self.helper_configs["augustine"])

        # Prepare context
        context_text = ""
        if context:
            context_text = "\n\nRelevant teachings for reference:\n" + "\n".join([
                f"- {item['text'][:200]}..." for item in context[:3]
            ])

        if additional_context:
            context_text += f"\n\nAdditional context: {additional_context}"

        # Build prompt
        system_prompt = config["system_prompt"]

        user_prompt = f"""A seeker asks: "{question}"

{context_text}

Please provide a thoughtful, spiritually nourishing answer drawing from your wisdom and experience."""

        payload = {
            "model": config["model"],
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 600
            }
        }

        try:
            response = await self._make_request("api/generate", payload)
            return response.get("response", "Unable to generate answer at this time.")
        except Exception as e:
            return f"I apologize, but I am unable to answer at this moment. Error: {str(e)}"

    async def generate_personalized_insight(self, user_data: Dict, helper: str = "augustine") -> str:
        """Generate personalized spiritual insights based on user patterns"""

        config = self.helper_configs.get(helper, self.helper_configs["augustine"])

        # Analyze user data for patterns
        reading_streak = user_data.get("reading_streak", 0)
        favorite_themes = user_data.get("favorite_themes", [])
        recent_questions = user_data.get("recent_questions", [])

        user_prompt = f"""Based on this person's spiritual journey:
- Reading streak: {reading_streak} days
- Themes they've engaged with: {', '.join(favorite_themes)}
- Recent questions: {', '.join(recent_questions[:3])}

Please offer personalized spiritual guidance and encouragement for their continued journey."""

        payload = {
            "model": config["model"],
            "system": config["system_prompt"],
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "num_predict": 400
            }
        }

        try:
            response = await self._make_request("api/generate", payload)
            return response.get("response", "Unable to generate personalized insight.")
        except Exception as e:
            return f"Unable to generate personalized insight at this moment. Error: {str(e)}"

    def set_internet_url(self, url: str):
        """Set internet Ollama URL for fallback"""
        self.internet_url = url.rstrip('/')

    def set_default_model(self, model: str):
        """Set the default model to use"""
        self.default_model = model

        # Update all helper configs to use this model
        for config in self.helper_configs.values():
            config["model"] = model