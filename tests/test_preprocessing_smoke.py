"""Smoke test: a real fixture (complex.jpg) flows through the pipeline."""

import io
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_complex_fixture_succeeds_after_preprocess():
    src = FIXTURES / "complex.jpg"
    if not src.exists():
        pytest.skip("complex.jpg fixture missing")

    async def fake_analyze(image_data, prompt, model=None):
        with Image.open(io.BytesIO(image_data)) as im:
            assert im.format == "JPEG"
            assert im.mode == "RGB"
            assert max(im.size) <= 1536
        return "looks complex"

    import src.tools.vision.analyze as analyze_module

    with (
        patch.object(analyze_module, "ProviderFactory") as factory_cls,
        patch.object(analyze_module, "get_config") as cfg,
    ):
        provider = AsyncMock(analyze=fake_analyze)
        factory_cls.get.return_value = provider
        cfg.return_value.provider = "ollama"
        cfg.return_value.default_model = "qwen3-vl:4b"
        from src.tools.vision.analyze import analyze_image

        result = await analyze_image(image_path=str(src), prompt="describe")

    assert result["success"] is True
    assert result["result"] == "looks complex"
