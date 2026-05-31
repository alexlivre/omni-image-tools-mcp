"""Ollama vision provider implementation."""

import aiohttp
import base64
import logging
from typing import Any

from .base import VisionProvider

logger = logging.getLogger(__name__)


class OllamaProvider(VisionProvider):
    """Ollama provider for local vision models."""

    def __init__(self, config: Any):
        super().__init__(config)
        self.base_url = config.ollama.base_url
        self.allowed_models = config.ollama.allowed_models
        self.timeout = aiohttp.ClientTimeout(total=config.timeout)

    def validate_model(self, model: str | None) -> str:
        """Validate and return the model to use."""
        if model is None:
            model = self.allowed_models[0] if self.allowed_models else "qwen3-vl:4b"

        if model not in self.allowed_models:
            raise ValueError(
                f"Model '{model}' not in allowed list: {self.allowed_models}"
            )

        return model

    async def analyze(
        self,
        image_data: bytes,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Analyze image using Ollama API."""
        model = self.validate_model(model)

        is_valid, error_msg = self.validate_image(image_data)
        if not is_valid:
            raise ValueError(error_msg)

        image_b64 = base64.b64encode(image_data).decode("utf-8")

        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            response.request_info,
                            response.history,
                            status=response.status,
                            message=error_text,
                        )

                    result = await response.json()
                    return result.get("response", "")

        except aiohttp.ClientError as e:
            logger.error(f"Ollama API error: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
