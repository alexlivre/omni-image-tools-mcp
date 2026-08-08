"""Tests for providers: validate_image, model allowlist, is_local attributes."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.config import Config
from src.providers import MinimaxProvider, OllamaProvider, OpenAIProvider, OpenRouterProvider


def _ollama_config(monkeypatch, **overrides):
    monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
    for k, v in overrides.items():
        monkeypatch.setenv(k, str(v))
    return Config.from_env()


class TestValidateImage:
    def _prov(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
        monkeypatch.setenv("OLLAMA_ALLOWED_MODELS", "qwen3-vl:4b,qwen3-vl:2b")
        return OllamaProvider(Config.from_env())

    def test_empty_is_invalid(self, monkeypatch):
        valid, _ = self._prov(monkeypatch).validate_image(b"")
        assert valid is False

    def test_too_large_is_invalid(self, monkeypatch):
        valid, msg = self._prov(monkeypatch).validate_image(b"x" * (10 * 1024 * 1024 + 1))
        assert valid is False
        assert "too large" in msg.lower()

    def test_normal_is_valid(self, monkeypatch):
        valid, _ = self._prov(monkeypatch).validate_image(b"x" * 1024)
        assert valid is True


class TestOllamaAllowlist:
    def test_validate_model_rejects_unknown(self, monkeypatch):
        cfg = _ollama_config(monkeypatch, OLLAMA_ALLOWED_MODELS="qwen3-vl:4b,qwen3-vl:2b")
        prov = OllamaProvider(cfg)
        with pytest.raises(ValueError, match="not in allowed"):
            prov.validate_model("huge-100b")

    def test_validate_model_uses_default(self, monkeypatch):
        cfg = _ollama_config(monkeypatch, OLLAMA_ALLOWED_MODELS="qwen3-vl:4b,qwen3-vl:2b")
        prov = OllamaProvider(cfg)
        assert prov.validate_model(None) in cfg.ollama.allowed_models

    def test_validate_model_allows_listed(self, monkeypatch):
        cfg = _ollama_config(monkeypatch, OLLAMA_ALLOWED_MODELS="qwen3-vl:4b,qwen3-vl:2b")
        prov = OllamaProvider(cfg)
        assert prov.validate_model("qwen3-vl:2b") == "qwen3-vl:2b"


class TestProviderAttributes:
    def test_ollama_is_local(self, monkeypatch):
        prov = OllamaProvider(_ollama_config(monkeypatch))
        assert prov.is_local is True
        assert prov.image_limit_per_request == 1

    def test_openrouter_is_cloud(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "openrouter")
        monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
        prov = OpenRouterProvider(Config.from_env())
        assert prov.is_local is False
        assert prov.image_limit_per_request is None

    def test_openai_is_cloud(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "openai")
        monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
        prov = OpenAIProvider(Config.from_env())
        assert prov.is_local is False
        assert prov.endpoint.startswith("https://api.openai.com")


class TestOpenAICompatibleCompare:
    @pytest.mark.asyncio
    async def test_compare_sends_all_images(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "openrouter")
        monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
        prov = OpenRouterProvider(Config.from_env())

        captured = {}

        class FakeResp:
            status_code = 200

            def json(self):
                return {"choices": [{"message": {"content": "diff"}}]}

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, url, headers, json):
                captured["content_parts"] = len(json["messages"][0]["content"])
                captured["url"] = url
                return FakeResp()

        with patch("src.providers.openai_compatible.httpx.AsyncClient", return_value=FakeClient()):
            result = await prov.compare([b"img1", b"img2"], "compare")
        assert result == "diff"
        assert captured["content_parts"] == 3
        assert "openrouter.ai" in captured["url"]


@pytest.mark.asyncio
async def test_retry_succeeds_after_transient_errors(monkeypatch):
    monkeypatch.setenv("OMNI_VISION_PROVIDER", "openrouter")
    monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
    monkeypatch.setenv("OMNI_VISION_MAX_RETRIES", "3")
    prov = OpenRouterProvider(Config.from_env())

    class FlakyResp:
        def __init__(self, code):
            self.status_code = code
            self.headers = {}

        def json(self):
            return {"choices": [{"message": {"content": "ok"}}]}

        @property
        def text(self):
            return "flaky"

    class FlakyClient:
        def __init__(self):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, headers, json):
            self.calls += 1
            if self.calls < 3:
                return FlakyResp(429)
            return FlakyResp(200)

    flaky = FlakyClient()
    with patch("src.providers.openai_compatible.httpx.AsyncClient", return_value=flaky):
        result = await prov.analyze(b"img", "prompt")
    assert result == "ok"
    assert flaky.calls == 3


@pytest.mark.asyncio
async def test_retry_http_date_retry_after_does_not_crash(monkeypatch):
    monkeypatch.setenv("OMNI_VISION_PROVIDER", "openrouter")
    monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
    monkeypatch.setenv("OMNI_VISION_MAX_RETRIES", "2")
    prov = OpenRouterProvider(Config.from_env())

    class DateRetryResp:
        def __init__(self, code):
            self.status_code = code
            self.headers = {"retry-after": "Wed, 21 Oct 2015 07:28:00 GMT"} if code == 429 else {}

        def json(self):
            return {"choices": [{"message": {"content": "ok"}}]}

        @property
        def text(self):
            return "rate limited"

    class FlakyClient:
        def __init__(self):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, headers, json):
            self.calls += 1
            if self.calls == 1:
                return DateRetryResp(429)
            return DateRetryResp(200)

    flaky = FlakyClient()
    with patch("src.providers.openai_compatible.httpx.AsyncClient", return_value=flaky):
        with patch("src.providers.openai_compatible.asyncio.sleep", AsyncMock()):
            result = await prov.analyze(b"img", "prompt")
    assert result == "ok"
    assert flaky.calls == 2


@pytest.mark.asyncio
async def test_retry_disabled_raises_on_429(monkeypatch):
    monkeypatch.setenv("OMNI_VISION_PROVIDER", "openrouter")
    monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
    monkeypatch.setenv("OMNI_VISION_MAX_RETRIES", "0")
    prov = OpenRouterProvider(Config.from_env())

    class FlakyResp:
        status_code = 429
        headers = {}

        @property
        def text(self):
            return "rate limited"

    class FlakyClient:
        def __init__(self):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, headers, json):
            self.calls += 1
            return FlakyResp()

    flaky = FlakyClient()
    with patch("src.providers.openai_compatible.httpx.AsyncClient", return_value=flaky):
        with pytest.raises(httpx.HTTPError):
            await prov.analyze(b"img", "prompt")
    assert flaky.calls == 1


def test_lmstudio_provider_is_local(monkeypatch):
    from src.providers import ProviderFactory
    from src.config import Config

    monkeypatch.setenv("OMNI_VISION_PROVIDER", "lmstudio")
    monkeypatch.setenv("LMSTUDIO_BASE_URL", "http://localhost:1234")
    cfg = Config.from_env()
    prov = ProviderFactory.get("lmstudio", cfg)
    assert prov.is_local is True
    assert prov.image_limit_per_request == 1
    assert prov.endpoint == "http://localhost:1234/v1/chat/completions"


class TestMinimaxProvider:
    def _prov(self, monkeypatch, base_url="https://api.minimax.io/v1", model=None):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "minimax")
        monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
        if model:
            monkeypatch.setenv("OMNI_VISION_DEFAULT_MODEL", model)
        cfg = Config.from_env()
        if base_url:
            monkeypatch.setenv("MINIMAX_BASE_URL", base_url)
            cfg = Config.from_env()
        return MinimaxProvider(cfg)

    def test_minimax_is_cloud(self, monkeypatch):
        prov = self._prov(monkeypatch)
        assert prov.is_local is False
        assert prov.image_limit_per_request is None
        assert prov.endpoint == "https://api.minimax.io/v1/chat/completions"

    def test_minimax_china_base_url(self, monkeypatch):
        prov = self._prov(monkeypatch, base_url="https://api.minimaxi.com/v1")
        assert prov.endpoint == "https://api.minimaxi.com/v1/chat/completions"

    def test_minimax_default_model(self, monkeypatch):
        prov = self._prov(monkeypatch)
        assert prov.default_model == "MiniMax-M3"

    def test_minimax_custom_model(self, monkeypatch):
        prov = self._prov(monkeypatch, model="MiniMax-M2.7")
        assert prov.default_model == "MiniMax-M2.7"

    @pytest.mark.asyncio
    async def test_minimax_payload_has_thinking_disabled(self, monkeypatch):
        prov = self._prov(monkeypatch)
        captured = {}

        class FakeResp:
            status_code = 200

            def json(self):
                return {"choices": [{"message": {"content": "ok"}}]}

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, url, headers, json):
                captured["payload"] = json
                return FakeResp()

        with patch("src.providers.openai_compatible.httpx.AsyncClient", return_value=FakeClient()):
            await prov.analyze(b"img", "prompt")
        assert captured["payload"]["thinking"] == {"type": "disabled"}
        assert captured["payload"]["model"] == "MiniMax-M3"

    @pytest.mark.asyncio
    async def test_minimax_strips_think_blocks(self, monkeypatch):
        prov = self._prov(monkeypatch)

        class FakeResp:
            status_code = 200

            def json(self):
                content = "<think>Let me analyze...</think>The image shows a cat."
                return {"choices": [{"message": {"content": content}}]}

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, url, headers, json):
                return FakeResp()

        with patch("src.providers.openai_compatible.httpx.AsyncClient", return_value=FakeClient()):
            result = await prov.analyze(b"img", "prompt")
        assert result == "The image shows a cat."

    @pytest.mark.asyncio
    async def test_minimax_base_resp_error_raises(self, monkeypatch):
        prov = self._prov(monkeypatch)

        class FakeResp:
            status_code = 200

            def json(self):
                return {"base_resp": {"status_code": 1004, "status_msg": "bad key"}}

            @property
            def text(self):
                return ""

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, url, headers, json):
                return FakeResp()

        with patch("src.providers.openai_compatible.httpx.AsyncClient", return_value=FakeClient()):
            with pytest.raises(httpx.HTTPError, match="1004"):
                await prov.analyze(b"img", "prompt")


@pytest.mark.asyncio
async def test_fallback_switches_model_on_error(monkeypatch):
    monkeypatch.setenv("OMNI_VISION_PROVIDER", "openrouter")
    monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
    monkeypatch.setenv("OMNI_VISION_MAX_RETRIES", "0")
    monkeypatch.setenv("OMNI_VISION_DEFAULT_MODEL", "model-a")
    monkeypatch.setenv("OMNI_FALLBACK_MODELS", "model-b")
    prov = OpenRouterProvider(Config.from_env())

    seen = []

    class ErrResp:
        status_code = 500

        @property
        def text(self):
            return "fail"

    class Resp:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": "ok-b"}}]}

    class Client:
        def __init__(self):
            self.responses = {}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, headers, json):
            seen.append(json["model"])
            if json["model"] == "model-a":
                return ErrResp()
            return Resp()

    with patch("src.providers.openai_compatible.httpx.AsyncClient", return_value=Client()):
        result = await prov.analyze(b"img", "p")
    assert result == "ok-b"
    assert seen == ["model-a", "model-b"]
