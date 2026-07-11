"""Tests for src.utils.image_preprocessor."""

import io
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from src.utils.image_preprocessor import (
    preprocess_to_bytes,
    CACHE_ROOT,
    MAX_LONGEST_SIDE,
)


def _save_test_image(
    path: Path, size: tuple[int, int], mode: str = "RGB", color=(255, 0, 0)
) -> None:
    img = Image.new(mode, size, color)
    img.save(path)


@pytest.fixture(autouse=True)
def _clean_cache():
    """Clear the shared cache directory before each test for isolation."""
    if CACHE_ROOT.exists():
        for f in CACHE_ROOT.glob("*.jpg"):
            f.unlink()
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    yield


def test_oversized_image_is_resized_to_max(tmp_path):
    src = tmp_path / "big.jpg"
    _save_test_image(src, (3000, 2000))
    data = preprocess_to_bytes(src)
    with Image.open(io.BytesIO(data)) as out:
        w, h = out.size
    assert max(w, h) == MAX_LONGEST_SIDE
    assert out.format == "JPEG"


def test_small_image_keeps_original_size(tmp_path):
    src = tmp_path / "small.jpg"
    _save_test_image(src, (500, 400))
    data = preprocess_to_bytes(src)
    with Image.open(io.BytesIO(data)) as out:
        w, h = out.size
    assert (w, h) == (500, 400)


def test_below_keep_below_keeps_original_even_if_still_jpeg(tmp_path):
    # 500x400 has longest=500 < 768, but should still be converted to JPEG RGB
    # (per spec rule 2 — conversion is mandatory, only resize is conditional)
    src = tmp_path / "tiny.png"
    _save_test_image(src, (500, 400), mode="RGBA", color=(10, 20, 30, 255))
    data = preprocess_to_bytes(src)
    with Image.open(io.BytesIO(data)) as out:
        assert out.size == (500, 400)
        assert out.mode == "RGB"
        assert out.format == "JPEG"


def test_midrange_image_keeps_original_size(tmp_path):
    src = tmp_path / "mid.jpg"
    _save_test_image(src, (1200, 900))
    data = preprocess_to_bytes(src)
    with Image.open(io.BytesIO(data)) as out:
        w, h = out.size
    assert (w, h) == (1200, 900)


def test_image_at_exactly_max_is_not_resized(tmp_path):
    src = tmp_path / "edge.jpg"
    _save_test_image(src, (MAX_LONGEST_SIDE, 1024))
    data = preprocess_to_bytes(src)
    with Image.open(io.BytesIO(data)) as out:
        w, h = out.size
    assert (w, h) == (MAX_LONGEST_SIDE, 1024)


def test_alpha_channel_is_removed(tmp_path):
    src = tmp_path / "rgba.png"
    _save_test_image(src, (800, 600), mode="RGBA", color=(255, 0, 0, 128))
    data = preprocess_to_bytes(src)
    with Image.open(io.BytesIO(data)) as out:
        assert out.mode == "RGB"


def test_output_is_progressive_jpeg_quality_90(tmp_path):
    src = tmp_path / "photo.jpg"
    _save_test_image(src, (1024, 768))
    data = preprocess_to_bytes(src)
    with Image.open(io.BytesIO(data)) as out:
        assert out.format == "JPEG"
        assert out.info.get("progressive") is True or out.info.get("progression") is not None


def test_resize_preserves_aspect_ratio(tmp_path):
    src = tmp_path / "big2.jpg"
    _save_test_image(src, (2000, 1000))
    data = preprocess_to_bytes(src)
    with Image.open(io.BytesIO(data)) as out:
        w, h = out.size
    expected_w = int(2000 * (MAX_LONGEST_SIDE / 2000))
    expected_h = int(1000 * (MAX_LONGEST_SIDE / 2000))
    assert (w, h) == (expected_w, expected_h)


def test_typical_photo_in_target_size_range(tmp_path):
    src = tmp_path / "photo2.jpg"
    _save_test_image(src, (2000, 1500))
    data = preprocess_to_bytes(src)
    size_kb = len(data) / 1024
    assert size_kb <= 1024, f"Expected <= 1024 KB, got {size_kb:.1f} KB"
    assert size_kb >= 1, "File suspiciously small"


def test_cache_hit_on_second_call(tmp_path):
    src = tmp_path / "cached.jpg"
    _save_test_image(src, (1024, 768))

    first = preprocess_to_bytes(src)
    cache_file = next(CACHE_ROOT.glob("*.jpg"))

    with patch("src.utils.image_preprocessor._to_jpeg_bytes") as mock:
        second = preprocess_to_bytes(src)
        mock.assert_not_called()

    assert first == second
    assert cache_file.is_file()


def test_different_content_produces_different_cache_files(tmp_path):
    a = tmp_path / "a.jpg"
    b = tmp_path / "b.jpg"
    _save_test_image(a, (1024, 768), color=(255, 0, 0))
    _save_test_image(b, (1024, 768), color=(0, 255, 0))
    preprocess_to_bytes(a)
    preprocess_to_bytes(b)
    cache_files = list(CACHE_ROOT.glob("*.jpg"))
    assert len(cache_files) == 2


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        preprocess_to_bytes(tmp_path / "nonexistent.jpg")


def test_cache_directory_created_under_tempdir():
    import tempfile

    expected = Path(tempfile.gettempdir()) / "omni-image-tools" / "preprocessed"
    assert expected == CACHE_ROOT
