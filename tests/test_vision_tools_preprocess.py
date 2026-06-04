"""Integration tests: vision tools must send preprocessed bytes to the provider."""

import io
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image


def _save_test_image(path: Path, size=(1024, 768)) -> None:
    Image.new("RGB", size, (100, 150, 200)).save(path)


@pytest.mark.asyncio
async def test_analyze_image_sends_preprocessed_bytes(tmp_path):
    src = tmp_path / "photo.jpg"
    _save_test_image(src, (3000, 2000))

    captured = {}

    async def fake_analyze(image_data, prompt, model=None):
        captured["image_data"] = image_data
        captured["size"] = len(image_data)
        with Image.open(io.BytesIO(image_data)) as im:
            captured["dim"] = im.size
            captured["format"] = im.format
        return "ok"

    with patch("src.providers.ProviderFactory.get") as factory:
        provider = AsyncMock()
        provider.analyze = fake_analyze
        factory.return_value = provider

        with patch("src.config.get_config") as cfg:
            cfg.return_value.provider = "ollama"
            cfg.return_value.default_model = "qwen3-vl:4b"
            from src.tools.vision.analyze import analyze_image
            await analyze_image(image_path=str(src), prompt="describe")

    assert captured["format"] == "JPEG"
    assert max(captured["dim"]) <= 1536
    # Original was 3000x2000 -> resized to 1536x1024
    assert captured["dim"] == (1536, 1024)
