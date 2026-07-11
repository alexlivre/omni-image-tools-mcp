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
    is_local = provider == "ollama"

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


def _get_provider_description(provider: str, is_local: bool) -> str:
    """Get human-readable provider description."""
    descriptions = {
        "ollama": "Ollama local vision model",
        "openrouter": "OpenRouter cloud API",
        "openai": "OpenAI cloud API",
    }
    base = descriptions.get(provider, provider)
    if is_local:
        base += " | LIMIT: 1 image/request (GPU memory) | compare: sequential"
    else:
        base += " | No image limit | compare: parallel"
    return base
