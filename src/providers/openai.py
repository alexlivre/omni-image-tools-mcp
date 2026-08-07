"""OpenAI vision provider implementation (OpenAI-compatible)."""

from typing import Any

from .openai_compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI API provider for cloud vision models."""

    base_url = "https://api.openai.com/v1"
    endpoint = "https://api.openai.com/v1/chat/completions"
    default_model = "gpt-4o-mini"

    def __init__(self, config: Any, debug: bool = False):
        super().__init__(config, debug=debug)
        if config.openai and config.openai.default_model:
            self.default_model = config.openai.default_model
