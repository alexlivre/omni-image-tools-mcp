"""Provider factory and registry."""

from typing import Any

from .base import VisionProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider
from .openai import OpenAIProvider
from .lmstudio import LMStudioProvider


class ProviderFactory:
    """Factory for creating vision providers."""

    _providers: dict[str, type[VisionProvider]] = {
        "ollama": OllamaProvider,
        "openrouter": OpenRouterProvider,
        "openai": OpenAIProvider,
        "lmstudio": LMStudioProvider,
    }

    @classmethod
    def get(cls, name: str, config: Any) -> VisionProvider:
        """
        Get a provider instance by name.

        Args:
            name: Provider name (ollama, openrouter, openai, lmstudio)
            config: Configuration object

        Returns:
            VisionProvider instance

        Raises:
            ValueError: If provider name is unknown
        """
        if name not in cls._providers:
            available = list(cls._providers.keys())
            raise ValueError(f"Unknown provider '{name}'. Available: {available}")

        provider_class = cls._providers[name]
        return provider_class(config)

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all available provider names."""
        return list(cls._providers.keys())

    @classmethod
    def register(cls, name: str, provider_class: type[VisionProvider]) -> None:
        """Register a new provider."""
        cls._providers[name] = provider_class


__all__ = [
    "VisionProvider",
    "ProviderFactory",
    "OllamaProvider",
    "OpenRouterProvider",
    "OpenAIProvider",
    "LMStudioProvider",
]
