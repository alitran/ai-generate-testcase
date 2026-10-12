"""Factory and model configuration for supported providers."""
from __future__ import annotations
import os
from typing import Any


PROVIDER_MODEL_ENV = {
    "openai": "OPENAI_MODEL",
    "anthropic": "ANTHROPIC_MODEL",
    "gemini": "GEMINI_MODEL",
    "openai_compatible": "OPENAI_COMPATIBLE_MODEL",
}
SUPPORTED_PROVIDERS = tuple(PROVIDER_MODEL_ENV)


def resolve_model(provider: str, explicit_model: str | None = None) -> str:
    """Model precedence: CLI --model, AI_MODEL override, provider-specific model."""
    provider = provider.lower().strip()
    if provider not in PROVIDER_MODEL_ENV:
        raise ValueError(
            f"Provider '{provider}' không được hỗ trợ. Chọn một trong: {', '.join(SUPPORTED_PROVIDERS)}"
        )
    model = (explicit_model or os.getenv("AI_MODEL") or os.getenv(PROVIDER_MODEL_ENV[provider], "")).strip()
    if not model or model.lower().startswith(("your_", "replace_", "put_")):
        raise ValueError(
            f"Chưa cấu hình model cho '{provider}'. Hãy đặt {PROVIDER_MODEL_ENV[provider]} trong .env "
            "hoặc truyền --model <model-name>. Dùng model ID có quyền truy cập ở nhà cung cấp đó."
        )
    return model


def build_provider(name: str, *, client: Any | None = None):
    """Build a provider adapter by name. Optional client is useful for unit tests."""
    provider = name.lower().strip()
    if provider == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider(client=client)
    if provider == "anthropic":
        from .anthropic_provider import AnthropicProvider
        return AnthropicProvider(client=client)
    if provider == "gemini":
        from .gemini_provider import GeminiProvider
        return GeminiProvider(client=client)
    if provider == "openai_compatible":
        from .openai_compatible_provider import OpenAICompatibleProvider
        return OpenAICompatibleProvider(client=client)
    raise ValueError(
        f"Provider '{provider}' không được hỗ trợ. Chọn một trong: {', '.join(SUPPORTED_PROVIDERS)}"
    )
