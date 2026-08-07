"""Tests for config module-level get_config/reload_config caching."""

import pytest

import src.config as config_module


@pytest.fixture(autouse=True)
def _reset_cache_and_env(monkeypatch):
    config_module._config = None
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


def test_get_config_builds_on_first_call(monkeypatch):
    monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
    cfg = config_module.get_config()
    assert cfg.provider == "ollama"
    assert config_module._config is cfg


def test_get_config_caches_second_call(monkeypatch):
    monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
    first = config_module.get_config()
    second = config_module.get_config()
    assert first is second


def test_reload_config_rebuilds(monkeypatch):
    monkeypatch.setenv("OMNI_VISION_PROVIDER", "ollama")
    config_module.get_config()

    monkeypatch.setenv("OMNI_VISION_DEFAULT_MODEL", "qwen3-vl:2b")
    reloaded = config_module.reload_config()
    assert reloaded.default_model == "qwen3-vl:2b"
    assert config_module._config is reloaded
