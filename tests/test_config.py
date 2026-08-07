"""Tests for Config.from_env parsing and validation."""

import pytest

from src.config import Config, ConfigError


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for k in (
        "OMNI_VISION_PROVIDER",
        "OMNI_VISION_API_KEY",
        "OMNI_VISION_DEFAULT_MODEL",
        "OMNI_VISION_TIMEOUT",
        "OLLAMA_ALLOWED_MODELS",
        "OLLAMA_AUTO_PULL",
        "OLLAMA_BASE_URL",
    ):
        monkeypatch.delenv(k, raising=False)


class TestOllamaConfig:
    def test_ollama_no_key_required(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
        cfg = Config.from_env()
        assert cfg.provider == "ollama"
        assert cfg.api_key is None
        assert cfg.timeout == 120
        assert "qwen3-vl:4b" in cfg.ollama.allowed_models

    def test_ollama_allowed_models_custom(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
        monkeypatch.setenv("OLLAMA_ALLOWED_MODELS", "moondream,llava")
        cfg = Config.from_env()
        assert cfg.ollama.allowed_models == ["moondream", "llava"]

    def test_ollama_auto_pull_flag(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
        monkeypatch.setenv("OLLAMA_AUTO_PULL", "yes")
        cfg = Config.from_env()
        assert cfg.ollama.auto_pull is True
        monkeypatch.setenv("OLLAMA_AUTO_PULL", "false")
        assert Config.from_env().ollama.auto_pull is False


class TestCloudConfig:
    def test_openrouter_requires_api_key(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "openrouter")
        with pytest.raises(ConfigError) as exc:
            Config.from_env()
        assert exc.value.missing_key == "OMNI_VISION_API_KEY"

    def test_openai_requires_api_key(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "openai")
        with pytest.raises(ConfigError) as exc:
            Config.from_env()
        assert exc.value.missing_key == "OMNI_VISION_API_KEY"

    def test_openrouter_with_key(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "openrouter")
        monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
        monkeypatch.setenv("OMNI_VISION_DEFAULT_MODEL", "google/gemini-2.5-flash")
        cfg = Config.from_env()
        assert cfg.openrouter is not None
        assert cfg.openrouter.api_key == "sk-test"
        assert cfg.openrouter.default_model == "google/gemini-2.5-flash"

    def test_openai_with_key(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "openai")
        monkeypatch.setenv("OMNI_VISION_API_KEY", "sk-test")
        cfg = Config.from_env()
        assert cfg.openai is not None
        assert cfg.openai.api_key == "sk-test"


class TestProviderValidation:
    def test_missing_provider_raises(self):
        with pytest.raises(ConfigError) as exc:
            Config.from_env()
        assert exc.value.missing_key == "OMNI_VISION_PROVIDER"

    def test_invalid_provider_raises(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "lmstudio")
        with pytest.raises(ConfigError):
            Config.from_env()

    def test_invalid_timeout_raises(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
        monkeypatch.setenv("OMNI_VISION_TIMEOUT", "not-a-number")
        with pytest.raises(ConfigError):
            Config.from_env()

    def test_timeout_parsed(self, monkeypatch):
        monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
        monkeypatch.setenv("OMNI_VISION_TIMEOUT", "60")
        assert Config.from_env().timeout == 60
