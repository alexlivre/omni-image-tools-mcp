"""Integration tests: vision tools must send preprocessed bytes to the provider."""

import importlib
import io
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image

import src.tools.vision.analyze  # noqa: F401
import src.tools.vision.read_text  # noqa: F401
from src.tools.vision.analyze import analyze_image
from src.tools.vision.read_text import read_text


def _save_test_image(path: Path, size) -> None:
    Image.new("RGB", size, (100, 150, 200)).save(path)


@pytest.mark.asyncio
async def test_analyze_image_sends_preprocessed_bytes(tmp_path):
    src = tmp_path / "photo.jpg"
    _save_test_image(src, (3000, 2000))

    captured = {}

    async def fake_analyze(image_data, prompt, model=None):
        captured["image_data"] = image_data
        with Image.open(io.BytesIO(image_data)) as im:
            captured["dim"] = im.size
            captured["format"] = im.format
        return "ok"

    with (
        patch("src.tools.vision.analyze.ProviderFactory.get") as factory,
        patch("src.tools.vision.analyze.get_config") as cfg,
    ):
        provider = AsyncMock(analyze=fake_analyze)
        factory.return_value = provider
        cfg.return_value.provider = "ollama"
        cfg.return_value.default_model = "qwen3-vl:4b"
        await analyze_image(image_path=str(src), prompt="describe")

    assert captured["format"] == "JPEG"
    assert max(captured["dim"]) <= 1536
    assert captured["dim"] == (1536, 1024)
    assert len(captured["image_data"]) > 0


@pytest.mark.asyncio
async def test_read_text_sends_preprocessed_bytes(tmp_path):
    src = tmp_path / "doc.png"
    Image.new("RGBA", (2400, 1800), (255, 255, 255, 200)).save(src)

    captured = {}

    async def fake_analyze(image_data, prompt, model=None):
        with Image.open(io.BytesIO(image_data)) as im:
            captured["dim"] = im.size
            captured["format"] = im.format
        return "text"

    read_text_module = importlib.import_module(read_text.__module__)
    with (
        patch.object(read_text_module.ProviderFactory, "get") as factory,
        patch.object(read_text_module, "get_config") as cfg,
    ):
        provider = AsyncMock(analyze=fake_analyze)
        factory.return_value = provider
        cfg.return_value.provider = "ollama"
        await read_text(image_path=str(src))

    assert max(captured["dim"]) <= 1536
    assert captured["format"] == "JPEG"


@pytest.mark.asyncio
async def test_identify_objects_sends_preprocessed_bytes(tmp_path):
    src = tmp_path / "scene.jpg"
    Image.new("RGB", (1800, 1200), (100, 150, 200)).save(src)

    captured = {}

    async def fake_analyze(image_data, prompt, model=None):
        with Image.open(io.BytesIO(image_data)) as im:
            captured["dim"] = im.size
        return "[]"

    import src.tools.vision.identify as identify_module

    with (
        patch.object(identify_module, "ProviderFactory") as factory_cls,
        patch.object(identify_module, "get_config") as cfg,
    ):
        provider = AsyncMock(analyze=fake_analyze)
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "ollama"
        await identify_module.identify_objects(image_path=str(src))

    assert max(captured["dim"]) <= 1536


@pytest.mark.asyncio
async def test_compare_images_sends_all_preprocessed(tmp_path):
    a = tmp_path / "a.jpg"
    b = tmp_path / "b.jpg"
    Image.new("RGB", (3000, 2000), (255, 0, 0)).save(a)
    Image.new("RGB", (2400, 1800), (0, 255, 0)).save(b)

    captured = []

    async def fake_compare(image_datas, prompt, model=None):
        for d in image_datas:
            with Image.open(io.BytesIO(d)) as im:
                captured.append((im.size, im.format))
        return "diff"

    import src.tools.vision.compare as compare_module

    with (
        patch.object(compare_module, "ProviderFactory") as factory_cls,
        patch.object(compare_module, "get_config") as cfg,
    ):
        provider = AsyncMock(compare=fake_compare)
        provider.is_local = False
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "openrouter"
        await compare_module.compare_images(image_paths=[str(a), str(b)])

    assert len(captured) == 2
    for dim, fmt in captured:
        assert max(dim) <= 1536
        assert fmt == "JPEG"


@pytest.mark.asyncio
async def test_extract_object_preprocesses_for_vision_but_crops_original(tmp_path):
    src = tmp_path / "scene.png"
    Image.new("RGBA", (3000, 2000), (50, 200, 100, 255)).save(src)

    sent_to_vision = {}

    async def fake_analyze(image_data, prompt, model=None):
        with Image.open(io.BytesIO(image_data)) as im:
            sent_to_vision["dim"] = im.size
            sent_to_vision["format"] = im.format
        return '{"bbox_2d": [100, 100, 500, 500]}'

    import src.tools.processing.extract as extract_module

    with (
        patch.object(extract_module, "ProviderFactory") as factory_cls,
        patch.object(extract_module, "get_config") as cfg,
    ):
        provider = AsyncMock(analyze=fake_analyze)
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "ollama"
        result = await extract_module.extract_object(
            image_path=str(src),
            object_description="thing",
            output_filename=str(tmp_path / "out.png"),
        )

    assert max(sent_to_vision["dim"]) <= 1536
    assert sent_to_vision["format"] == "JPEG"

    assert result["success"] is True
    assert result["original_size"] == (3000, 2000)
    assert result["extracted_size"] == (1200, 800)
