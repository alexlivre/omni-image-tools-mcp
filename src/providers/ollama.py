"""Ollama vision provider implementation."""

import aiohttp
import base64
import logging
import time
from typing import Any

from .base import VisionProvider

logger = logging.getLogger(__name__)


class OllamaProvider(VisionProvider):
    """Ollama provider for local vision models."""

    def __init__(self, config: Any, debug: bool = False):
        super().__init__(config)
        self.base_url = config.ollama.base_url
        self.allowed_models = config.ollama.allowed_models
        self.timeout = aiohttp.ClientTimeout(total=config.timeout)
        self.debug = debug

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
        image_size_kb = len(image_data) / 1024

        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
        }

        if self.debug:
            print(f"\n{'='*60}")
            print(f"DEBUG MODE - Ollama Request")
            print(f"{'='*60}")
            print(f"Endpoint: {self.base_url}/api/generate")
            print(f"Model: {model}")
            print(f"Image size: {image_size_kb:.1f} KB")
            print(f"Prompt length: {len(prompt)} chars")
            print(f"Timeout: {self.timeout.total}s")
            print(f"\nRequest payload:")
            print(f"  model: {payload['model']}")
            print(f"  prompt: {payload['prompt'][:100]}..." if len(payload['prompt']) > 100 else f"  prompt: {payload['prompt']}")
            print(f"  images: [base64 encoded, {len(image_b64)} chars]")
            print(f"{'='*60}\n")

        start_time = time.time()

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                ) as response:
                    elapsed = time.time() - start_time

                    if self.debug:
                        print(f"\n{'='*60}")
                        print(f"DEBUG MODE - Ollama Response")
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
                    response_text = result.get("response", "")

                    if self.debug:
                        print(f"Response length: {len(response_text)} chars")
                        print(f"\nResponse content:")
                        print(f"  {response_text[:200]}..." if len(response_text) > 200 else f"  {response_text}")
                        print(f"{'='*60}\n")

                    return response_text

        except aiohttp.ClientError as e:
            logger.error(f"Ollama API error: {e}")
            raise

    async def compare(
        self,
        image_datas: list[bytes],
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Compare multiple images using Ollama API."""
        model = self.validate_model(model)

        images_b64 = [base64.b64encode(img).decode("utf-8") for img in image_datas]

        payload = {
            "model": model,
            "prompt": prompt,
            "images": images_b64,
            "stream": False,
        }

        if self.debug:
            print(f"\n{'='*60}")
            print(f"DEBUG MODE - Ollama Compare Request")
            print(f"{'='*60}")
            print(f"Model: {model}")
            print(f"Image 1: {len(image_b64_1)} chars")
            print(f"Image 2: {len(image_b64_2)} chars")
            print(f"{'='*60}\n")

        start_time = time.time()

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
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
