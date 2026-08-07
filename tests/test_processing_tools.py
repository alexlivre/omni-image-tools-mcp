import pytest
from PIL import Image
from src.tools.processing.crop import crop_image
from src.tools.processing.convert import convert_image_format
from src.tools.processing.prepare import prepare_image
from src.tools.processing.info import get_image_info


def _make(path, size=(200, 100), mode="RGB", color=(10, 20, 30)):
    Image.new(mode, size, color).save(path)
    return path


@pytest.mark.asyncio
async def test_crop_success(tmp_path):
    p = _make(tmp_path / "a.jpg")
    r = await crop_image(str(p), x=0, y=0, width=50, height=50)
    assert r["success"] is True
    assert r["cropped_size"] == (50, 50)


@pytest.mark.asyncio
async def test_crop_out_of_bounds_fails(tmp_path):
    p = _make(tmp_path / "a.jpg")
    r = await crop_image(str(p), x=0, y=0, width=500, height=50)
    assert r["success"] is False
    assert "outside" in r["error"].lower()


@pytest.mark.asyncio
async def test_convert_rgba_to_jpeg(tmp_path):
    p = _make(tmp_path / "a.png", mode="RGBA")
    r = await convert_image_format(str(p), "JPEG", quality=80)
    assert r["success"] is True
    assert r["new_format"] == "JPEG"
    assert r["output_size_bytes"] > 0


@pytest.mark.asyncio
async def test_convert_unsupported_format_fails(tmp_path):
    p = _make(tmp_path / "a.jpg")
    r = await convert_image_format(str(p), "TIFF")
    assert r["success"] is False


@pytest.mark.asyncio
async def test_prepare_scales_down(tmp_path):
    p = _make(tmp_path / "big.jpg", size=(4000, 2000))
    r = await prepare_image(str(p), max_width=1000, max_height=1000)
    assert r["success"] is True
    assert max(r["new_size"]) <= 1000


@pytest.mark.asyncio
async def test_get_image_info_no_exif_by_default(tmp_path):
    p = _make(tmp_path / "a.png", mode="RGBA")
    r = await get_image_info(str(p))
    assert r["success"] is True
    assert r["has_transparency"] is True
    assert "exif" not in r
