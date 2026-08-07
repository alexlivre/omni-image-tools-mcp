"""Tests for download_image: SSRF protection, size limits, payload checks."""

from unittest.mock import AsyncMock, patch

import pytest

from src.tools.processing.download import _guess_extension, download_image


class TestGuessExtension:
    def test_known_formats(self):
        assert _guess_extension("JPEG") == ".jpg"
        assert _guess_extension("PNG") == ".png"
        assert _guess_extension("WEBP") == ".webp"

    def test_unknown_falls_back_to_jpg(self):
        assert _guess_extension("UNKNOWN") == ".jpg"


class TestDownloadSsrf:
    @pytest.mark.asyncio
    async def test_blocks_metadata_endpoint(self):
        # Avoid hitting real network: the URL is rejected before any request.
        with patch("src.tools.processing.download.httpx.AsyncClient") as client_cls:
            client_cls.return_value.__aenter__ = AsyncMock()
            result = await download_image("http://169.254.169.254/latest/meta-data/")

        assert result["success"] is False
        assert "blocked" in result["error"].lower() or "private" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_blocks_localhost(self):
        result = await download_image("http://localhost:11434/api/tags")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_blocks_non_http_scheme(self):
        result = await download_image("file:///etc/passwd")
        assert result["success"] is False


class TestDownloadSizeLimit:
    @pytest.mark.asyncio
    async def test_blocks_oversize_content_length(self):
        class FakeResponse:
            status_code = 200
            headers = {"content-length": str(30 * 1024 * 1024)}

            async def aiter_bytes(self, chunk_size=1):
                yield b"x" * 1024

            async def aread(self):
                return b"x"

            def raise_for_status(self):
                pass

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            def stream(self, *a, **k):
                class Ctx:
                    def __enter__(self_inner):
                        return FakeResponse()

                    def __exit__(self_inner, *a):
                        return False

                return Ctx()

            async def get(self, *a, **k):
                return FakeResponse()

        with patch("src.tools.processing.download.httpx.AsyncClient", return_value=FakeClient()):
            result = await download_image("https://example.com/big.jpg")

        assert result["success"] is False
        assert "too large" in result["error"].lower()
