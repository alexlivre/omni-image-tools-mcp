"""Read text tool for omni-image-tools-mcp."""

import hashlib
from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt
from ...utils import preprocess_to_bytes
from ...utils.gpu_memory import GPUResourceManager
from ...utils.result_cache import cache_result, cached, make_key

_CACHE_TOOL = "read_text"


async def read_text(
    image_path: str,
    preserve_formatting: bool = False,
    language_hint: str | None = None,
) -> dict[str, Any]:
    """Extract visible text from an image (OCR).

    Args:
        image_path: Path to the image file
        preserve_formatting: Preserve text layout and formatting
        language_hint: Language hint (e.g., en, pt, es)

    Returns:
        Dict with extracted text
    """
    config = get_config()
    provider = ProviderFactory.get(config.provider, config, debug=False)

    image_data = preprocess_to_bytes(image_path)
    image_sha = hashlib.sha256(image_data).hexdigest()

    if preserve_formatting:
        prompt = get_vision_prompt("read_text", "with_formatting")
    else:
        prompt = get_vision_prompt("read_text", "default")

    if language_hint:
        prompt += f" (Hint: the text may be in {language_hint})"

    effective_model = config.default_model or "unknown"
    key = make_key(_CACHE_TOOL, image_sha, prompt, effective_model)

    cached_result = cached(key)
    if cached_result is not None:
        return {
            "success": True,
            "result": cached_result,
            "provider": config.provider,
            "options": {
                "preserve_formatting": preserve_formatting,
                "language_hint": language_hint,
            },
            "cached": True,
        }

    await GPUResourceManager.ensure_single_provider(config.provider)
    result = await provider.analyze(image_data, prompt)
    cache_result(key, result)

    return {
        "success": True,
        "result": result,
        "provider": config.provider,
        "options": {
            "preserve_formatting": preserve_formatting,
            "language_hint": language_hint,
        },
    }
