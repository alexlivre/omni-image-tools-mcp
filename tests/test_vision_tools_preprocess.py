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

    with patch("src.tools.vision.analyze.ProviderFactory.get") as factory, \
         patch("src.tools.vision.analyze.get_config") as cfg:
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
    with patch.object(read_text_module.ProviderFactory, "get") as factory, \
         patch.object(read_text_module, "get_config") as cfg:
        provider = AsyncMock(analyze=fake_analyze)
        factory.return_value = provider
        cfg.return_value.provider = "ollama"
        await read_text(image_path=str(src))

    assert max(captured["dim"]) <= 1536
    assert captured["format"] == "JPEG"
