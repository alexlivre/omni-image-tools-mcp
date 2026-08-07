"""OpenRouter vision provider implementation (OpenAI-compatible)."""

from typing import Any

from .openai_compatible import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    """OpenRouter API provider for cloud vision models."""

    base_url = "https://openrouter.ai/api/v1/models"
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    default_model = "google/gemini-2.5-flash"

    def __init__(self, config: Any, debug: bool = False):
        super().__init__(config, debug=debug)
        if config.openrouter and config.openrouter.default_model:
            self.default_model = config.openrouter.default_model
