"""Anthropic Claude Messages API adapter."""
from __future__ import annotations
import os
from typing import Any


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, client: Any | None = None):
        if client is None:
            from anthropic import Anthropic
            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY") or None)
        self.client = client

    def generate(self, *, system_prompt: str, user_input: str, model: str) -> str:
        response = self.client.messages.create(
            model=model,
            system=system_prompt,
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "8192")),
            messages=[{"role": "user", "content": user_input}],
        )
        parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
        output = "\n".join(parts).strip()
        if not output:
            raise RuntimeError("Anthropic trả về nội dung text rỗng.")
        return output
