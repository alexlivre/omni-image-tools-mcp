"""OpenAI vision provider implementation."""

import httpx
import base64
import logging
import time
from typing import Any

from .base import VisionProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(VisionProvider):
    """OpenAI API provider for cloud vision models."""

    def __init__(self, config: Any, debug: bool = False):
        super().__init__(config)
        self.api_key = config.api_key
        self.default_model = config.openai.default_model if config.openai else "gpt-5.4-mini"
        self.timeout = config.timeout
        self.debug = debug

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

        if self.debug:
            image_size_kb = len(image_data) / 1024
            print(f"\n{'='*60}")
            print(f"DEBUG MODE - OpenAI Request")
            print(f"{'='*60}")
            print(f"Endpoint: https://api.openai.com/v1/chat/completions")
            print(f"Model: {model}")
            print(f"Image size: {image_size_kb:.1f} KB")
            print(f"Prompt length: {len(prompt)} chars")
            print(f"Timeout: {self.timeout.total}s")
            print(f"{'='*60}\n")

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                elapsed = time.time() - start_time

                if self.debug:
                    print(f"\n{'='*60}")
                    print(f"DEBUG MODE - OpenAI Response")
                    print(f"{'='*60}")
                    print(f"Status: {response.status_code}")
                    print(f"Response time: {elapsed:.2f}s")

                if response.status_code != 200:
                    error_text = await response.text()
                    if self.debug:
                        print(f"Error: {error_text}")
                        print(f"{'='*60}\n")
                    raise httpx.HTTPError(error_text)

                result = response.json()
                response_text = result["choices"][0]["message"]["content"]

                if self.debug:
                    print(f"Response length: {len(response_text)} chars")
                    print(f"\nResponse content:")
                    print(f"  {response_text[:200]}..." if len(response_text) > 200 else f"  {response_text}")
                    print(f"{'='*60}\n")

                return response_text

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
