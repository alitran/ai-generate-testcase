"""Adapter for OpenAI-compatible chat-completions endpoints (for example, some hosted gateways or local model servers)."""
from __future__ import annotations
import os
from typing import Any


class OpenAICompatibleProvider:
    name = "openai_compatible"

    def __init__(self, client: Any | None = None):
        if client is None:
            from openai import OpenAI
            base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "").strip()
            if not base_url:
                raise ValueError(
                    "Thiếu OPENAI_COMPATIBLE_BASE_URL. Hãy điền endpoint do nhà cung cấp cung cấp."
                )
            client = OpenAI(
                api_key=os.getenv("OPENAI_COMPATIBLE_API_KEY") or "local-no-key",
                base_url=base_url,
            )
        self.client = client

    def generate(self, *, system_prompt: str, user_input: str, model: str) -> str:
        request = {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        }
        # Ollama supports JSON mode through its OpenAI-compatible API.
        # Disable with OPENAI_COMPATIBLE_JSON_MODE=false for endpoints that do not support it.
        json_mode = os.getenv("OPENAI_COMPATIBLE_JSON_MODE", "true").strip().lower()
        if json_mode in {"1", "true", "yes", "on"}:
            request["response_format"] = {"type": "json_object"}
        response = self.client.chat.completions.create(**request)
        choices = getattr(response, "choices", None) or []
        output = choices[0].message.content if choices else None
        if not isinstance(output, str) or not output.strip():
            raise RuntimeError(
                "OpenAI-compatible endpoint trả về nội dung rỗng hoặc không đúng format chat.completions."
            )
        return output.strip()
