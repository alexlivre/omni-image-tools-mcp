from unittest.mock import patch

from src.tools.system.provider_info import get_provider_info


class FakeConfig:
    provider = "ollama"
    default_model = "qwen3-vl:4b"
    api_key = None


class FakeLocalProvider:
    is_local = True
    image_limit_per_request = 1


class FakeCloudProvider:
    is_local = False
    image_limit_per_request = None


def test_provider_info_local():
    with (
        patch("src.tools.system.provider_info.get_config", return_value=FakeConfig()),
        patch(
            "src.tools.system.provider_info.ProviderFactory.get", return_value=FakeLocalProvider()
        ),
    ):
        info = get_provider_info()
    assert info["success"] is True
    assert info["type"] == "local"
    assert info["image_limit_per_request"] == 1


def test_provider_info_cloud():
    cfg = FakeConfig()
    cfg.provider = "openrouter"
    with (
        patch("src.tools.system.provider_info.get_config", return_value=cfg),
        patch(
            "src.tools.system.provider_info.ProviderFactory.get", return_value=FakeCloudProvider()
        ),
    ):
        info = get_provider_info()
    assert info["type"] == "online"
    assert info["image_limit_per_request"] is None
