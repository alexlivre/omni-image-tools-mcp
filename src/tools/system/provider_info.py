"""Provider info tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config
from ...providers import ProviderFactory


def get_provider_info() -> dict[str, Any]:
    """Get information about the current provider and its capabilities.

    Reads provider metadata (is_local, image_limit) from the provider instance
    rather than hardcoding provider names, so new providers stay consistent.
    """
    config = get_config()
    provider = ProviderFactory.get(config.provider, config, debug=False)
    is_local = provider.is_local
    image_limit = provider.image_limit_per_request

    info = {
        "provider": config.provider,
        "type": "local" if is_local else "online",
        "image_limit_per_request": image_limit,
        "supports_multiple_images": image_limit is None or image_limit > 1,
        "default_model": config.default_model or "unknown",
        "description": _get_provider_description(config.provider, is_local, image_limit),
        "limits": {
            "local_providers": {
                "image_limit_per_request": 1,
                "compare_processing": "sequential (images analyzed one at a time, then compared)",
                "reason": "GPU memory constraints on local hardware",
            },
            "online_providers": {
                "image_limit_per_request": None,
                "compare_processing": "parallel (all images processed together)",
                "reason": "Cloud GPU has sufficient memory",
            },
        },
        "warnings": {
            "local": "LOCAL PROVIDER: 1 image per request limit enforced. compare_images uses sequential processing (slower but reliable).",
            "online": "ONLINE PROVIDER: No image limit. All images processed in parallel for best results.",
        },
    }

    return {
        "success": True,
        **info,
    }


def _get_provider_description(provider: str, is_local: bool, image_limit: int | None) -> str:
    """Get human-readable provider description."""
    descriptions = {
        "ollama": "Ollama local vision model",
        "openrouter": "OpenRouter cloud API",
        "openai": "OpenAI cloud API",
        "lmstudio": "LM Studio local server",
    }
    base = descriptions.get(provider, provider)
    if is_local:
        base += f" | LIMIT: {image_limit} image/request (GPU memory) | compare: sequential"
    else:
        base += " | No image limit | compare: parallel"
    return base
