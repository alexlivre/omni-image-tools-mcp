"""LM Studio vision provider implementation."""

import aiohttp
import base64
import logging
from typing import Any

from .base import VisionProvider

logger = logging.getLogger(__name__)


class LMStudioProvider(VisionProvider):
    """LM Studio provider for local vision models."""

    def __init__(self, config: Any):
        super().__init__(config)
        self.base_url = config.lmstudio.base_url
        self.timeout = aiohttp.ClientTimeout(total=config.timeout)

    async def analyze(
        self,
        image_data: bytes,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Analyze image using LM Studio API."""
        model = model or "qwen3-vl:4b"

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
                    response.raise_for_status()
                    result = await response.json()
                    return result.get("response", "")

        except aiohttp.ClientError as e:
            logger.error(f"LM Studio API error: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if LM Studio is running."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/models") as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"LM Studio health check failed: {e}")
            return False
