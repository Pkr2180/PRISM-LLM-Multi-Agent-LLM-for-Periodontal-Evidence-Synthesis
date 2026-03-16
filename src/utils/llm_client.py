"""
PRISM-LLM: Unified LLM Client
Supports Anthropic Claude, OpenAI, and local HuggingFace models.
"""

import json
import os
from typing import Optional
from loguru import logger


class LLMClient:
    """Unified LLM client for PRISM-LLM pipeline."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.backend = self.config.get("backbone", "claude-sonnet-4-20250514")
        self._client = None

    def _get_client(self):
        if self._client is None:
            if "claude" in self.backend:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY", self.config.get("api_key", ""))
                )
            elif "gpt" in self.backend:
                import openai
                self._client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY", self.config.get("api_key", ""))
                )
        return self._client

    def generate(self, system_prompt: str, user_prompt: str) -> dict:
        """Generate a response from the LLM. Returns parsed JSON if possible."""
        client = self._get_client()
        max_tokens = self.config.get("max_tokens", 1000)
        temperature = self.config.get("temperature", 0.0)

        try:
            if "claude" in self.backend:
                response = client.messages.create(
                    model=self.backend,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                text = "".join(
                    block.text for block in response.content if hasattr(block, "text")
                )
            elif "gpt" in self.backend:
                response = client.chat.completions.create(
                    model=self.backend,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                text = response.choices[0].message.content
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")

            # Try to parse as JSON
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            return json.loads(cleaned)

        except json.JSONDecodeError:
            logger.warning("LLM response was not valid JSON, returning raw text")
            return {"_raw": text}
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {"_error": str(e)}

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a plain text response (no JSON parsing)."""
        result = self.generate(system_prompt, user_prompt)
        if "_raw" in result:
            return result["_raw"]
        return json.dumps(result)
