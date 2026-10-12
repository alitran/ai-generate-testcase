"""Google Gemini adapter using the Google Gen AI SDK."""
from __future__ import annotations
import os
from typing import Any


class GeminiProvider:
    name = "gemini"

    def __init__(self, client: Any | None = None):
        if client is None:
            from google import genai
            client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY") or None)
        self.client = client

    def generate(self, *, system_prompt: str, user_input: str, model: str) -> str:
        from google.genai import types
        response = self.client.models.generate_content(
            model=model,
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,
            ),
        )
        output = getattr(response, "text", None)
        if not isinstance(output, str) or not output.strip():
            raise RuntimeError("Gemini trả về response.text rỗng.")
        return output.strip()
