"""Tests for extract_object hallucination guard and output_dir parameter."""

from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image


@pytest.mark.asyncio
async def test_bbox_covers_entire_image_returns_failure(tmp_path):
    img_path = tmp_path / "scene.jpg"
    Image.new("RGB", (2000, 1500), (100, 100, 100)).save(img_path)

    async def fake_analyze(image_data, prompt, model=None):
        return '{"bbox_2d": [0, 0, 1000, 1000]}'

    import src.tools.processing.extract as extract_module

    with patch.object(extract_module, "ProviderFactory") as factory_cls, \
            patch.object(extract_module, "get_config") as cfg:
        provider = AsyncMock(analyze=fake_analyze)
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "ollama"
        cfg.return_value.default_model = "qwen3-vl:4b"
        result = await extract_module.extract_object(
            image_path=str(img_path),
            object_description="a green elephant",
        )

    assert result["success"] is False
    error_msg = result["error"].lower()
    assert "hallucination" in error_msg or "not found" in error_msg or "could not locate" in error_msg


@pytest.mark.asyncio
async def test_valid_bbox_succeeds(tmp_path):
    img_path = tmp_path / "scene.jpg"
    Image.new("RGB", (2000, 1500), (100, 100, 100)).save(img_path)

    async def fake_analyze(image_data, prompt, model=None):
        return '{"bbox_2d": [200, 200, 600, 600]}'

    import src.tools.processing.extract as extract_module

    with patch.object(extract_module, "ProviderFactory") as factory_cls, \
            patch.object(extract_module, "get_config") as cfg:
        provider = AsyncMock(analyze=fake_analyze)
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "ollama"
        cfg.return_value.default_model = "qwen3-vl:4b"
        result = await extract_module.extract_object(
            image_path=str(img_path),
            object_description="object in middle",
        )

    assert result["success"] is True
    assert "local_path" in result
    assert result["object_description"] == "object in middle"


@pytest.mark.asyncio
async def test_output_dir_respected(tmp_path):
    img_path = tmp_path / "scene.jpg"
    custom_dir = tmp_path / "my_output"
    custom_dir.mkdir()
    Image.new("RGB", (1000, 1000), (50, 50, 50)).save(img_path)

    async def fake_analyze(image_data, prompt, model=None):
        return '{"bbox_2d": [100, 100, 900, 900]}'

    import src.tools.processing.extract as extract_module

    with patch.object(extract_module, "ProviderFactory") as factory_cls, \
            patch.object(extract_module, "get_config") as cfg:
        provider = AsyncMock(analyze=fake_analyze)
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "ollama"
        cfg.return_value.default_model = "qwen3-vl:4b"
        result = await extract_module.extract_object(
            image_path=str(img_path),
            object_description="center region",
            output_dir=str(custom_dir),
        )

    assert result["success"] is True
    assert str(custom_dir) in result["local_path"]
    import os
    assert os.path.isfile(result["local_path"])


@pytest.mark.asyncio
async def test_small_bbox_returns_failure(tmp_path):
    """The pre-existing small-region guard should still work."""
    img_path = tmp_path / "scene.jpg"
    Image.new("RGB", (1000, 1000), (100, 100, 100)).save(img_path)

    async def fake_analyze(image_data, prompt, model=None):
        return '{"bbox_2d": [500, 500, 502, 502]}'

    import src.tools.processing.extract as extract_module

    with patch.object(extract_module, "ProviderFactory") as factory_cls, \
            patch.object(extract_module, "get_config") as cfg:
        provider = AsyncMock(analyze=fake_analyze)
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "ollama"
        result = await extract_module.extract_object(
            image_path=str(img_path),
            object_description="tiny thing",
        )

    assert result["success"] is False
    assert "small" in result["error"].lower() or "visible" in result["error"].lower()