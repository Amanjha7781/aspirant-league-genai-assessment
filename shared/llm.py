"""Minimal OpenAI-compatible chat client with bounded timeouts and no content logging."""

from __future__ import annotations

import json
import os
from typing import Any, Protocol

import httpx
from dotenv import load_dotenv

load_dotenv()


class ModelUnavailable(RuntimeError):
    """Raised when a configured language model cannot be reached or used."""


class ModelOutputInvalid(RuntimeError):
    """Raised when a reachable model returns malformed or unsafe output."""


class JSONChatClient(Protocol):
    async def json_chat(self, *, system: str, user: str) -> dict[str, Any]: ...


class LLMClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "")
        self.timeout = min(max(float(os.getenv("LLM_TIMEOUT_SECONDS", "30")), 1), 60)

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.model)

    async def json_chat(self, *, system: str, user: str) -> dict[str, Any]:
        if not self.configured:
            raise ModelUnavailable("LLM is not configured. Set LLM_BASE_URL and LLM_MODEL.")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=payload
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                value = json.loads(content)
        except httpx.HTTPError as exc:
            # Do not attach the response body: it could contain document text or secrets.
            raise ModelUnavailable(f"LLM request failed ({type(exc).__name__}).") from None
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            raise ModelOutputInvalid("LLM response did not contain valid JSON content.") from None
        if not isinstance(value, dict):
            raise ModelOutputInvalid("LLM response must be a JSON object.")
        return value
