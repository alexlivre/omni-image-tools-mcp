"""OpenAI-compatible vision provider base.

Both OpenAI and OpenRouter speak the /chat/completions content format
(text + image_url parts). This base centralizes request building, response
parsing, debug tracing (to stderr), and health checks; concrete providers
only declare endpoint, default model, and headers.
"""

import asyncio
import base64
import logging
import sys
import time
from typing import Any

import httpx

from ..utils.rate_limiter import RATE_LIMITER
from .base import VisionProvider

logger = logging.getLogger(__name__)

RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _dbg(*args: Any, **kwargs: Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


class OpenAICompatibleProvider(VisionProvider):
    """Shared implementation for OpenAI-compatible chat-completions vision APIs."""

    base_url: str = ""
    endpoint: str = ""
    default_model: str = ""

    def __init__(self, config: Any, debug: bool = False):
        super().__init__(config)
        self.api_key = config.api_key
        self.timeout = config.timeout
        self.debug = debug
        self.is_local = False
        self.image_limit_per_request: int | None = None

    def _resolve_model(self, model: str | None) -> str:
        return model or self.default_model

    def _fallback_models(self, model: str | None) -> list[str]:
        """Resolved model followed by configured fallbacks, deduplicated in order."""
        primary = self._resolve_model(model)
        return list(dict.fromkeys([primary, *getattr(self.config, "fallback_models", [])]))

    def _extra_payload_fields(self) -> dict[str, Any]:
        """Provider-specific top-level payload fields (e.g. MiniMax thinking)."""
        return {}

    def _extract_text(self, result: dict[str, Any]) -> str:
        """Extract assistant text from a Chat Completions response."""
        content: str = result["choices"][0]["message"]["content"]
        return content

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _post(self, client: httpx.AsyncClient, payload: dict[str, Any]) -> httpx.Response:
        """POST with exponential backoff retry for transient status codes."""
        await RATE_LIMITER.acquire(type(self).__name__, str(payload["model"]))
        max_retries = getattr(self.config, "max_retries", 3)
        for attempt in range(max_retries + 1):
            try:
                response = await client.post(self.endpoint, headers=self._headers(), json=payload)
            except httpx.HTTPError:
                if attempt >= max_retries:
                    raise
                await asyncio.sleep(2**attempt)
                continue
            if response.status_code in RETRYABLE_STATUS and attempt < max_retries:
                retry_after = response.headers.get("retry-after")
                try:
                    delay = float(retry_after) if retry_after else 2**attempt
                except ValueError:
                    delay = 2**attempt
                await asyncio.sleep(delay)
                continue
            return response
        raise httpx.HTTPError("exhausted retries")

    @staticmethod
    def _image_part(image_data: bytes) -> dict[str, Any]:
        b64 = base64.b64encode(image_data).decode("utf-8")
        return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}

    async def analyze(
        self,
        image_data: bytes | None = None,
        prompt: str = "",
        model: str | None = None,
    ) -> str:
        models = self._fallback_models(model)
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        if image_data is not None:
            is_valid, error_msg = self.validate_image(image_data)
            if not is_valid:
                raise ValueError(error_msg)
            content.append(self._image_part(image_data))

        if self.debug:
            _dbg(f"[{type(self).__name__}] analyze models={models} img={len(image_data or b'')}")
        for index, current_model in enumerate(models):
            payload = {
                "model": current_model,
                "messages": [{"role": "user", "content": content}],
                **self._extra_payload_fields(),
            }
            start = time.time()
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await self._post(client, payload)
                    elapsed = time.time() - start
                    if self.debug:
                        _dbg(
                            f"[{type(self).__name__}] model={current_model} "
                            f"status={response.status_code} elapsed={elapsed:.2f}s"
                        )
                    if response.status_code != 200:
                        raise httpx.HTTPError(self._masked_error(response))
                    result = response.json()
                    return self._extract_text(result)
            except httpx.HTTPError as e:
                if index < len(models) - 1:
                    logger.warning(
                        f"{type(self).__name__} model {current_model} failed ({e}); trying next"
                    )
                    continue
                logger.error(f"{type(self).__name__} API error: {e}")
                raise
        raise httpx.HTTPError("no model succeeded")

    async def compare(
        self,
        image_datas: list[bytes],
        prompt: str,
        model: str | None = None,
    ) -> str:
        models = self._fallback_models(model)
        parts = [{"type": "text", "text": prompt}]
        parts.extend(self._image_part(d) for d in image_datas)
        if self.debug:
            _dbg(f"[{type(self).__name__}] compare models={models} images={len(image_datas)}")
        for index, current_model in enumerate(models):
            payload = {
                "model": current_model,
                "messages": [{"role": "user", "content": parts}],
                **self._extra_payload_fields(),
            }
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await self._post(client, payload)
                    if response.status_code != 200:
                        raise httpx.HTTPError(self._masked_error(response))
                    result = response.json()
                    return self._extract_text(result)
            except httpx.HTTPError as e:
                if index < len(models) - 1:
                    logger.warning(
                        f"{type(self).__name__} model {current_model} failed ({e}); trying next"
                    )
                    continue
                logger.error(f"{type(self).__name__} API error: {e}")
                raise
        raise httpx.HTTPError("no model succeeded")

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(self.base_url, headers=self._headers())
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"{type(self).__name__} health check failed: {e}")
            return False

    def _masked_error(self, response: httpx.Response) -> str:
        try:
            return response.text
        except Exception:
            return f"HTTP {response.status_code}"
