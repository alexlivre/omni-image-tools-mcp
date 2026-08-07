"""LM Studio vision provider implementation (OpenAI-compatible, local)."""

from typing import Any

from .openai_compatible import OpenAICompatibleProvider


class LMStudioProvider(OpenAICompatibleProvider):
    """LM Studio local server (OpenAI-compatible)."""

    base_url = "http://localhost:1234/v1/models"
    endpoint = "http://localhost:1234/v1/chat/completions"
    default_model = "qwen2.5-vl-7b-instruct"

    def __init__(self, config: Any, debug: bool = False):
        super().__init__(config, debug=debug)
        self.is_local = True
        self.image_limit_per_request = 1
        if config.lmstudio:
            base_url = config.lmstudio.base_url.rstrip("/")
            self.base_url = f"{base_url}/v1/models"
            self.endpoint = f"{base_url}/v1/chat/completions"
            self.default_model = config.lmstudio.default_model
