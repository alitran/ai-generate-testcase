"""Native OpenAI Responses API adapter."""
from __future__ import annotations
import os
from typing import Any


class OpenAIProvider:
    name = "openai"

    def __init__(self, client: Any | None = None):
        if client is None:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or None)
        self.client = client

    def generate(self, *, system_prompt: str, user_input: str, model: str) -> str:
        response = self.client.responses.create(
            model=model,
            instructions=system_prompt,
            input=user_input,
        )
        output = getattr(response, "output_text", None)
        if not isinstance(output, str) or not output.strip():
            raise RuntimeError("OpenAI trả về output_text rỗng.")
        return output.strip()
