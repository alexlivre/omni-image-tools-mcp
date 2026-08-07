"""Targeted branch coverage for vision tools that need no running provider."""

import importlib
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image

from src.prompts import get_vision_prompt
from src.tools.vision.analyze import analyze_image
from src.tools.vision.read_text import read_text
import src.tools.vision.identify as identify_module


def _save(path, size=(400, 300)):
    Image.new("RGB", size, (100, 150, 200)).save(path)


@pytest.mark.asyncio
async def test_identify_objects_with_count_and_categories(tmp_path):
    src = tmp_path / "scene.jpg"
    _save(src)

    with (
        patch.object(identify_module, "ProviderFactory") as factory_cls,
        patch.object(identify_module, "get_config") as cfg,
        patch.object(
            identify_module.GPUResourceManager,
            "ensure_single_provider",
            new_callable=AsyncMock,
        ),
    ):
        provider = AsyncMock(analyze=AsyncMock(return_value="car x1"))
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "ollama"
        result = await identify_module.identify_objects(
            image_path=str(src),
            include_count=True,
            categories="car",
            min_confidence=0.75,
        )

    assert result["success"] is True
    assert result["options"]["include_count"] is True
    assert result["options"]["categories"] == "car"
    assert result["options"]["min_confidence"] == 0.75
    provider.analyze.assert_awaited_once()


@pytest.mark.asyncio
async def test_read_text_with_formatting_and_language_hint(tmp_path):
    src = tmp_path / "doc.png"
    Image.new("RGBA", (400, 300), (255, 255, 255, 200)).save(src)

    read_text_module = importlib.import_module(read_text.__module__)
    with (
        patch.object(read_text_module.ProviderFactory, "get") as factory,
        patch.object(read_text_module, "get_config") as cfg,
        patch.object(
            read_text_module.GPUResourceManager,
            "ensure_single_provider",
            new_callable=AsyncMock,
        ),
    ):
        provider = AsyncMock(analyze=AsyncMock(return_value="some text"))
        factory.return_value = provider
        cfg.return_value.provider = "ollama"
        result = await read_text(
            image_path=str(src),
            preserve_formatting=True,
            language_hint="pt",
        )

    assert result["success"] is True
    assert result["options"]["preserve_formatting"] is True
    assert result["options"]["language_hint"] == "pt"
    provider.analyze.assert_awaited_once()


@pytest.mark.asyncio
async def test_analyze_image_uses_default_prompt(tmp_path):
    src = tmp_path / "photo.jpg"
    _save(src)

    with (
        patch("src.tools.vision.analyze.ProviderFactory.get") as factory,
        patch("src.tools.vision.analyze.get_config") as cfg,
        patch(
            "src.tools.vision.analyze.GPUResourceManager.ensure_single_provider",
            new_callable=AsyncMock,
        ),
    ):
        provider = AsyncMock(analyze=AsyncMock(return_value="ok"))
        factory.return_value = provider
        cfg.return_value.provider = "ollama"
        cfg.return_value.default_model = "qwen3-vl:4b"
        result = await analyze_image(image_path=str(src))

    assert result["success"] is True
    assert result["model"] == "qwen3-vl:4b"
    provider.analyze.assert_awaited_once()


@pytest.mark.asyncio
async def test_compare_images_requires_at_least_two():
    import src.tools.vision.compare as compare_module

    result = await compare_module.compare_images(image_paths=["a.jpg"])
    assert result["success"] is False
    assert "at least 2" in result["error"]


@pytest.mark.asyncio
async def test_compare_images_max_ten():
    import src.tools.vision.compare as compare_module

    result = await compare_module.compare_images(image_paths=[f"img{i}.jpg" for i in range(11)])
    assert result["success"] is False
    assert "Maximum 10" in result["error"]


def test_get_vision_prompt_without_variant():
    prompt = get_vision_prompt("identify_objects")
    assert isinstance(prompt, str)
