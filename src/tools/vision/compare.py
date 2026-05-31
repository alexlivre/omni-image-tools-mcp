"""Compare images tool for omni-image-tools-mcp."""

from typing import Any

from ...config import get_config
from ...providers import ProviderFactory
from ...prompts import get_vision_prompt


async def compare_images(
    image_path1: str,
    image_path2: str,
    compare_type: str = "both",
) -> dict[str, Any]:
    """Compare two images and identify similarities or differences.

    Args:
        image_path1: Path to the first image
        image_path2: Path to the second image
        compare_type: What to compare (similarities, differences, both)

    Returns:
        Dict with comparison result
    """
    config = get_config()
    provider = ProviderFactory.get(config.provider, config, debug=False)

    with open(image_path1, "rb") as f:
        image_data1 = f.read()

    with open(image_path2, "rb") as f:
        image_data2 = f.read()

    prompt = get_vision_prompt("compare_images", compare_type)

    result = await provider.compare(image_data1, image_data2, prompt, None)

    return {
        "success": True,
        "result": result,
        "provider": config.provider,
        "compare_type": compare_type,
    }
