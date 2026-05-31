"""Provider info tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config


def get_provider_info() -> dict[str, Any]:
    """Get information about the current provider and its capabilities.

    Returns:
        Dict with provider info including name, type, and image limits
    """
    config = get_config()

    provider = config.provider
    is_local = provider in ["ollama", "lmstudio"]
    is_online = provider in ["openrouter", "openai"]

    info = {
        "provider": provider,
        "type": "local" if is_local else "online",
        "image_limit_per_request": 1 if is_local else None,
        "supports_multiple_images": not is_local,
        "default_model": config.default_model or "unknown",
        "description": _get_provider_description(provider, is_local),
        "limits": {
            "local_providers": {
                "image_limit_per_request": 1,
                "reason": "GPU memory constraints on local hardware",
            },
            "online_providers": {
                "image_limit_per_request": None,
                "reason": "Cloud GPU has sufficient memory",
            },
        },
    }

    return {
        "success": True,
        **info,
    }


def _get_provider_description(provider: str, is_local: bool) -> str:
    """Get human-readable provider description."""
    descriptions = {
        "ollama": "Ollama local vision model (qwen3-vl series)",
        "lmstudio": "LM Studio local vision model (OpenAI-compatible API)",
        "openrouter": "OpenRouter cloud API (multiple vision models)",
        "openai": "OpenAI cloud API (GPT-4 Vision)",
    }
    base = descriptions.get(provider, provider)
    if is_local:
        base += " - LIMIT: 1 image per request due to local GPU memory"
    else:
        base += " - No image limit (cloud GPU)"
    return base
