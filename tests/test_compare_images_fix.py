"""Tests for compare_images sequential mode fix (no image sent in final call)."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_compare_sequential_calls_analyze_without_image(tmp_path):
    a = tmp_path / "a.jpg"
    b = tmp_path / "b.jpg"
    from PIL import Image

    Image.new("RGB", (3000, 2000), (255, 0, 0)).save(a)
    Image.new("RGB", (2400, 1800), (0, 255, 0)).save(b)

    analyze_calls = []

    async def fake_analyze(image_data, prompt, model=None):
        analyze_calls.append({"image_data": image_data, "prompt_snippet": prompt[:50]})
        if len(analyze_calls) <= 2:
            return f"Description of image {len(analyze_calls)}"
        return "These images are different."

    import src.tools.vision.compare as compare_module

    with (
        patch.object(compare_module, "ProviderFactory") as factory_cls,
        patch.object(compare_module, "get_config") as cfg,
    ):
        provider = AsyncMock(analyze=fake_analyze)
        provider.is_local = True
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "ollama"
        cfg.return_value.default_model = "qwen3-vl:4b"
        cfg.return_value.timeout = 120
        result = await compare_module.compare_images(
            image_paths=[str(a), str(b)],
            compare_type="both",
        )

    assert result["success"] is True
    assert result["processing_mode"] == "sequential"

    assert len(analyze_calls) == 3
    assert analyze_calls[0]["image_data"] is not None
    assert analyze_calls[1]["image_data"] is not None
    assert analyze_calls[2]["image_data"] is None


@pytest.mark.asyncio
async def test_compare_parallel_still_sends_images(tmp_path):
    a = tmp_path / "a.jpg"
    b = tmp_path / "b.jpg"
    from PIL import Image

    Image.new("RGB", (3000, 2000), (255, 0, 0)).save(a)
    Image.new("RGB", (2400, 1800), (0, 255, 0)).save(b)

    compare_calls = []

    async def fake_compare(image_datas, prompt, model=None):
        compare_calls.append(len(image_datas))
        return "These images are different."

    import src.tools.vision.compare as compare_module

    with (
        patch.object(compare_module, "ProviderFactory") as factory_cls,
        patch.object(compare_module, "get_config") as cfg,
    ):
        provider = AsyncMock(compare=fake_compare)
        provider.is_local = False
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "openrouter"
        cfg.return_value.default_model = "google/gemini-2.5-flash"
        cfg.return_value.timeout = 120
        result = await compare_module.compare_images(
            image_paths=[str(a), str(b)],
            compare_type="both",
        )

    assert result["success"] is True
    assert result["processing_mode"] == "parallel"
    assert compare_calls == [2]
