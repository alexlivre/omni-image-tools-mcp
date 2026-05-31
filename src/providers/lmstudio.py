"""LM Studio vision provider implementation."""

import aiohttp
import base64
import logging
import time
from typing import Any

from .base import VisionProvider

logger = logging.getLogger(__name__)


class LMStudioProvider(VisionProvider):
    """LM Studio provider for local vision models (OpenAI-compatible API)."""

    def __init__(self, config: Any, debug: bool = False):
        super().__init__(config)
        self.base_url = config.lmstudio.base_url
        self.timeout = aiohttp.ClientTimeout(total=config.timeout)
        self.debug = debug

    async def analyze(
        self,
        image_data: bytes,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Analyze image using LM Studio API (OpenAI-compatible)."""
        model = model or "qwen/qwen3-vl-4b"

        is_valid, error_msg = self.validate_image(image_data)
        if not is_valid:
            raise ValueError(error_msg)

        image_b64 = base64.b64encode(image_data).decode("utf-8")
        image_size_kb = len(image_data) / 1024

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
            print(f"\n{'='*60}")
            print(f"DEBUG MODE - LM Studio Request")
            print(f"{'='*60}")
            print(f"Endpoint: {self.base_url}/v1/chat/completions")
            print(f"Model: {model}")
            print(f"Image size: {image_size_kb:.1f} KB")
            print(f"Prompt length: {len(prompt)} chars")
            print(f"Timeout: {self.timeout.total}s")
            print(f"\nRequest payload:")
            print(f"  model: {payload['model']}")
            print(f"  messages[0].content: [{len(payload['messages'][0]['content'])} items]")
            print(f"    text: {payload['messages'][0]['content'][0]['text'][:100]}..." if len(payload['messages'][0]['content'][0]['text']) > 100 else f"    text: {payload['messages'][0]['content'][0]['text']}")
            print(f"    image_url: [base64 encoded, {len(image_b64)} chars]")
            print(f"{'='*60}\n")

        start_time = time.time()

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                ) as response:
                    elapsed = time.time() - start_time

                    if self.debug:
                        print(f"\n{'='*60}")
                        print(f"DEBUG MODE - LM Studio Response")
                        print(f"{'='*60}")
                        print(f"Status: {response.status}")
                        print(f"Response time: {elapsed:.2f}s")

                    if response.status != 200:
                        error_text = await response.text()
                        if self.debug:
                            print(f"Error: {error_text}")
                            print(f"{'='*60}\n")
                        raise aiohttp.ClientResponseError(
                            response.request_info,
                            response.history,
                            status=response.status,
                            message=error_text,
                        )

                    result = await response.json()
                    response_text = result["choices"][0]["message"]["content"]

                    if self.debug:
                        print(f"Response length: {len(response_text)} chars")
                        print(f"\nResponse content:")
                        print(f"  {response_text[:200]}..." if len(response_text) > 200 else f"  {response_text}")
                        print(f"{'='*60}\n")

                    return response_text

        except aiohttp.ClientError as e:
            logger.error(f"LM Studio API error: {e}")
            raise

    async def compare(
        self,
        image_data1: bytes,
        image_data2: bytes,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Compare two images using LM Studio API."""
        model = model or "qwen/qwen3-vl-4b"

        image_b64_1 = base64.b64encode(image_data1).decode("utf-8")
        image_b64_2 = base64.b64encode(image_data2).decode("utf-8")

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64_1}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64_2}"}},
                    ],
                }
            ],
        }

        if self.debug:
            print(f"\n{'='*60}")
            print(f"DEBUG MODE - LM Studio Compare Request")
            print(f"{'='*60}")
            print(f"Model: {model}")
            print(f"{'='*60}\n")

        start_time = time.time()

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                ) as response:
                    elapsed = time.time() - start_time

                    if self.debug:
                        print(f"Status: {response.status}")
                        print(f"Response time: {elapsed:.2f}s")

                    if response.status != 200:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            response.request_info,
                            response.history,
                            status=response.status,
                            message=error_text,
                        )

                    result = await response.json()
                    return result["choices"][0]["message"]["content"]

        except aiohttp.ClientError as e:
            logger.error(f"LM Studio API error: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if LM Studio is running."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/v1/models") as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"LM Studio health check failed: {e}")
            return False
