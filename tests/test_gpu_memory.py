from unittest.mock import patch

import pytest

from src.utils.gpu_memory import GPUResourceManager


class FakeResp:
    def __init__(self, status, data=None):
        self.status = status
        self._data = data or {}

    async def json(self):
        return self._data

    async def text(self):
        return "err"


class FakeCM:
    def __init__(self, resp):
        self._resp = resp

    async def __aenter__(self):
        return self._resp

    async def __aexit__(self, *a):
        return False


class FakeSession:
    def __init__(self, resp):
        self._resp = resp

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    def get(self, *a, **k):
        return FakeCM(self._resp)

    def post(self, *a, **k):
        return FakeCM(self._resp)


@pytest.mark.asyncio
async def test_get_loaded_models_parses_names():
    resp = FakeResp(200, {"models": [{"name": "a"}, {"name": "b"}]})
    with patch("src.utils.gpu_memory.aiohttp.ClientSession", return_value=FakeSession(resp)):
        models = await GPUResourceManager.get_ollama_loaded_models()
    assert models == ["a", "b"]


@pytest.mark.asyncio
async def test_get_loaded_models_empty_on_error():
    resp = FakeResp(500)
    with patch("src.utils.gpu_memory.aiohttp.ClientSession", return_value=FakeSession(resp)):
        models = await GPUResourceManager.get_ollama_loaded_models()
    assert models == []


@pytest.mark.asyncio
async def test_ensure_single_provider_unloads_other_model():
    GPUResourceManager.reset_gpu_verification()
    resp = FakeResp(200, {"models": [{"name": "other"}]})
    with patch("src.utils.gpu_memory.aiohttp.ClientSession", return_value=FakeSession(resp)):
        result = await GPUResourceManager.ensure_single_provider("ollama", model="qwen3-vl:4b")
    assert result["status"] == "unloaded"


@pytest.mark.asyncio
async def test_ensure_single_provider_reuses_same_model():
    GPUResourceManager.reset_gpu_verification()
    resp = FakeResp(200, {"models": [{"name": "qwen3-vl:4b"}]})
    with patch("src.utils.gpu_memory.aiohttp.ClientSession", return_value=FakeSession(resp)):
        result = await GPUResourceManager.ensure_single_provider("ollama", model="qwen3-vl:4b")
    assert result["status"] == "same_model"
