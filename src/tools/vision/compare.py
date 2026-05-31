"""Compare images tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt
from ...utils.gpu_memory import GPUResourceManager


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

    gpu_status = await GPUResourceManager.ensure_single_provider(config.provider)
    result = await provider.compare(image_datas, prompt, None)

    response = {
        "success": True,
        "result": result,
        "provider": config.provider,
        "compare_type": compare_type,
        "images_count": len(image_paths),
    }

    if gpu_status["warnings"] or gpu_status["unloaded"]:
        response["gpu_status"] = {
            "status": gpu_status["status"],
            "unloaded": gpu_status["unloaded"],
            "warnings": gpu_status["warnings"],
        }

    return response
