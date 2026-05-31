"""Read text tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt
from ...utils.gpu_memory import GPUResourceManager


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

    with open(image_path, "rb") as f:
        image_data = f.read()

    if preserve_formatting:
        prompt = get_vision_prompt("read_text", "with_formatting")
    else:
        prompt = get_vision_prompt("read_text", "default")

    if language_hint:
        prompt += f" (Hint: the text may be in {language_hint})"

    gpu_status = await GPUResourceManager.ensure_single_provider(config.provider)
    result = await provider.analyze(image_data, prompt)

    response = {
        "success": True,
        "result": result,
        "provider": config.provider,
        "options": {
            "preserve_formatting": preserve_formatting,
            "language_hint": language_hint,
        },
    }

    if gpu_status["warnings"] or gpu_status["unloaded"]:
        response["gpu_status"] = {
            "status": gpu_status["status"],
            "unloaded": gpu_status["unloaded"],
            "warnings": gpu_status["warnings"],
        }

    return response
