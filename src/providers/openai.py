"""OpenAI vision provider implementation."""

import httpx
import base64
import logging
from typing import Any

from .base import VisionProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(VisionProvider):
    """OpenAI API provider for cloud vision models."""

    def __init__(self, config: Any):
        super().__init__(config)
        self.api_key = config.api_key
        self.default_model = config.openai.default_model if config.openai else "gpt-4o"
        self.timeout = config.timeout

    async def analyze(
        self,
        image_data: bytes,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Analyze image using OpenAI API."""
        model = model or self.default_model

        is_valid, error_msg = self.validate_image(image_data)
        if not is_valid:
            raise ValueError(error_msg)

        image_b64 = base64.b64encode(image_data).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                    ],
                }
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        except httpx.HTTPError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://api.openai.com/v1/models")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False
