"""Tests for Ollama model allowlist validation."""

from unittest.mock import MagicMock

import pytest

from src.providers.ollama import OllamaProvider


def _make_config(allowed_models=None, default_model=None):
    config = MagicMock()
    config.provider = "ollama"
    config.default_model = default_model or "qwen3-vl:4b"
    config.timeout = 120
    config.ollama.allowed_models = allowed_models or ["qwen3-vl:4b", "qwen3-vl:2b"]
    config.ollama.base_url = "http://localhost:11434"
    return config


def test_allowlist_default_models_accepted():
    cfg = _make_config()
    provider = OllamaProvider(cfg)
    assert provider.validate_model("qwen3-vl:4b") == "qwen3-vl:4b"
    assert provider.validate_model("qwen3-vl:2b") == "qwen3-vl:2b"


def test_allowlist_outside_list_raises():
    cfg = _make_config()
    provider = OllamaProvider(cfg)
    with pytest.raises(ValueError, match="not in allowed list"):
        provider.validate_model("qwen3-vl:8b")

    with pytest.raises(ValueError, match="not in allowed list"):
        provider.validate_model("moondream")

    with pytest.raises(ValueError, match="not in allowed list"):
        provider.validate_model("llava:7b")


def test_allowlist_override_via_env():
    cfg = _make_config(allowed_models=["qwen3-vl:4b", "qwen3-vl:2b", "qwen3-vl:8b"])
    provider = OllamaProvider(cfg)
    assert provider.validate_model("qwen3-vl:8b") == "qwen3-vl:8b"
    with pytest.raises(ValueError, match="not in allowed list"):
        provider.validate_model("moondream")


def test_allowlist_none_model_uses_default():
    cfg = _make_config()
    provider = OllamaProvider(cfg)
    result = provider.validate_model(None)
    assert result == "qwen3-vl:4b"


def test_allowlist_single_model():
    cfg = _make_config(allowed_models=["qwen3-vl:4b"])
    provider = OllamaProvider(cfg)
    assert provider.validate_model("qwen3-vl:4b") == "qwen3-vl:4b"
    with pytest.raises(ValueError, match="not in allowed list"):
        provider.validate_model("qwen3-vl:2b")
