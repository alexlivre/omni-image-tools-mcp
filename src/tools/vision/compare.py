"""Compare images tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config, ProviderType
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt
from ...utils.gpu_memory import GPUResourceManager


def _is_local_provider(provider: ProviderType) -> bool:
    """Check if provider is local (has GPU memory limits)."""
    return provider in ["ollama", "lmstudio"]


async def compare_images(
    image_paths: list[str],
    compare_type: str = "both",
) -> dict[str, Any]:
    """Compare multiple images and identify similarities or differences.

    Args:
        image_paths: List of image paths to compare (2-10 images)
        compare_type: What to compare (similarities, differences, both)

    Returns:
        Dict with comparison result
    """
    if len(image_paths) < 2:
        return {
            "success": False,
            "error": "Need at least 2 images to compare",
        }
    if len(image_paths) > 10:
        return {
            "success": False,
            "error": "Maximum 10 images can be compared",
        }

    config = get_config()
    provider = ProviderFactory.get(config.provider, config, debug=False)

    image_datas = []
    for path in image_paths:
        with open(path, "rb") as f:
            image_datas.append(f.read())

    prompt = get_vision_prompt("compare_images", compare_type)

    await GPUResourceManager.ensure_single_provider(config.provider)

    is_local = _is_local_provider(config.provider)

    if is_local and len(image_datas) > 1:
        result = await _compare_sequential(provider, image_datas, compare_type, prompt)
    else:
        result = await provider.compare(image_datas, prompt, None)

    return {
        "success": True,
        "result": result,
        "provider": config.provider,
        "compare_type": compare_type,
        "images_count": len(image_paths),
        "processing_mode": "sequential" if is_local else "parallel",
    }


async def _compare_sequential(
    provider: Any,
    image_datas: list[bytes],
    compare_type: str,
    base_prompt: str,
) -> str:
    """Compare images sequentially for local providers with GPU memory limits.

    Local providers (Ollama, LM Studio) can only process 1 image at a time.
    This function analyzes each image separately, then compares the results.
    """
    descriptions = []

    analysis_prompt = "Describe this image concisely for comparison purposes."

    for i, image_data in enumerate(image_datas):
        desc = await provider.analyze(image_data, analysis_prompt, None)
        descriptions.append(f"Image {i+1}: {desc}")

    combined_descriptions = "\n\n".join(descriptions)

    comparison_prompt = f"""You are comparing the descriptions of multiple images.

{combined_descriptions}

Based on these descriptions, {base_prompt}

Provide a clear, structured comparison."""

    import httpx
    comparison_result = await provider.analyze(
        image_datas[0],
        comparison_prompt,
        None
    )

    return comparison_result
