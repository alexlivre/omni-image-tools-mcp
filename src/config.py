import os
from typing import Literal
from pydantic import BaseModel, Field
from .errors import ConfigError


ProviderType = Literal["ollama", "openrouter", "openai"]


class OllamaConfig(BaseModel):
    base_url: str = Field(default="http://localhost:11434")
    allowed_models: list[str] = Field(default=["qwen3-vl:4b", "qwen3-vl:2b"])
    auto_pull: bool = Field(default=False)


class OpenRouterConfig(BaseModel):
    api_key: str
    default_model: str = Field(default="google/gemini-2.5-flash")


class OpenAIConfig(BaseModel):
    api_key: str
    default_model: str = Field(default="gpt-5.4-mini")


class Config(BaseModel):
    provider: ProviderType
    api_key: str | None = None
    default_model: str | None = None
    timeout: int = Field(default=120)

    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    openrouter: OpenRouterConfig | None = None
    openai: OpenAIConfig | None = None

    @classmethod
    def from_env(cls) -> "Config":
        provider = os.getenv("OMNI_VISION_PROVIDER")
        if not provider:
            raise ConfigError(
                message="OMNI_VISION_PROVIDER is required",
                missing_key="OMNI_VISION_PROVIDER",
            )

        if provider not in ["ollama", "openrouter", "openai"]:
            raise ConfigError(
                message=f"Invalid provider: {provider}. Must be one of: ollama, openrouter, openai",
            )

        api_key = os.getenv("OMNI_VISION_API_KEY")
        if not api_key and provider in ["openrouter", "openai"]:
            raise ConfigError(
                message=f"OMNI_VISION_API_KEY is required for provider: {provider}",
                missing_key="OMNI_VISION_API_KEY",
            )

        timeout_str = os.getenv("OMNI_VISION_TIMEOUT", "120")
        try:
            timeout = int(timeout_str)
        except ValueError:
            raise ConfigError(
                message=f"OMNI_VISION_TIMEOUT must be an integer, got: {timeout_str}",
            )

        ollama_allowed = os.getenv("OLLAMA_ALLOWED_MODELS", "qwen3-vl:4b,qwen3-vl:2b")
        ollama_auto_pull_str = os.getenv("OLLAMA_AUTO_PULL", "false").lower()
        ollama_auto_pull = ollama_auto_pull_str in ["true", "1", "yes"]

        config = cls(
            provider=provider,
            api_key=api_key,
            default_model=os.getenv("OMNI_VISION_DEFAULT_MODEL"),
            timeout=timeout,
            ollama=OllamaConfig(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                allowed_models=ollama_allowed.split(","),
                auto_pull=ollama_auto_pull,
            ),
        )

        if provider == "openrouter":
            config.openrouter = OpenRouterConfig(
                api_key=api_key or "",
                default_model=config.default_model or "google/gemini-2.5-flash",
            )
        elif provider == "openai":
            config.openai = OpenAIConfig(
                api_key=api_key or "",
                default_model=config.default_model or "gpt-5.4-mini",
            )

        return config


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def reload_config() -> Config:
    global _config
    _config = Config.from_env()
    return _config
