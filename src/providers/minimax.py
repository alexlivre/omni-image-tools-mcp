"""MiniMax vision provider implementation (OpenAI-compatible, cloud).

Supports both MiniMax platforms through a configurable base_url:
- International: https://api.minimax.io/v1 (default)
- China: https://api.minimaxi.com/v1

MiniMax-M3 enables reasoning by default, which leaks <think>...</think>
blocks into message.content on the OpenAI-compatible endpoint. Vision
analysis wants direct answers, so the payload sends thinking disabled and
the response is defensively stripped of any leftover thinking tags.
"""

import re
from typing import Any

import httpx

from .openai_compatible import OpenAICompatibleProvider

THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

MINIMAX_BASE_RESP_ERRORS = {
    1002: "rate limit exceeded",
    1004: "authentication failed (invalid API key)",
    1008: "insufficient balance",
    1013: "internal server error",
    1039: "token limit exceeded",
    2013: "parameter error",
}


class MinimaxProvider(OpenAICompatibleProvider):
    """MiniMax API provider for cloud vision models (MiniMax-M3)."""

    base_url = "https://api.minimax.io/v1/models"
    endpoint = "https://api.minimax.io/v1/chat/completions"
    default_model = "MiniMax-M3"

    def __init__(self, config: Any, debug: bool = False):
        super().__init__(config, debug=debug)
        if config.minimax:
            base_url = config.minimax.base_url.rstrip("/")
            self.base_url = f"{base_url}/models"
            self.endpoint = f"{base_url}/chat/completions"
            self.default_model = config.minimax.default_model

    def _extra_payload_fields(self) -> dict[str, Any]:
        return {"thinking": {"type": "disabled"}}

    def _extract_text(self, result: dict[str, Any]) -> str:
        base_resp = result.get("base_resp")
        if base_resp and base_resp.get("status_code", 0) != 0:
            code = base_resp.get("status_code", 0)
            msg = base_resp.get("status_msg", "")
            hint = MINIMAX_BASE_RESP_ERRORS.get(code, "unknown error")
            raise httpx.HTTPError(f"MiniMax base_resp error {code} ({hint}): {msg}")
        text = result["choices"][0]["message"]["content"]
        return THINK_BLOCK_RE.sub("", text).strip()
