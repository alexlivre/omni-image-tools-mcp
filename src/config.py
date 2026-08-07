import os
from typing import Literal, cast
from pydantic import BaseModel, Field
from .errors import ConfigError


ProviderType = Literal["ollama", "openrouter", "openai", "lmstudio"]


class OllamaConfig(BaseModel):
    base_url: str = Field(default="http://localhost:11434")
    # Lista intencionalmente estreita. Curada para os modelos
    # documentados no README. Expandir via env: OLLAMA_ALLOWED_MODELS.
    allowed_models: list[str] = Field(default=["qwen3-vl:4b", "qwen3-vl:2b"])
    auto_pull: bool = Field(default=False)


class OpenRouterConfig(BaseModel):
    api_key: str
    default_model: str = Field(default="google/gemini-2.5-flash")


class OpenAIConfig(BaseModel):
    api_key: str
    default_model: str = Field(default="gpt-5.4-mini")


class LMStudioConfig(BaseModel):
    base_url: str = Field(default="http://localhost:1234")
    default_model: str = Field(default="qwen2.5-vl-7b-instruct")


class Config(BaseModel):
    provider: ProviderType
    api_key: str | None = None
    default_model: str | None = None
    timeout: int = Field(default=120)
    max_retries: int = Field(default=3)

    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    openrouter: OpenRouterConfig | None = None
    openai: OpenAIConfig | None = None
    lmstudio: LMStudioConfig | None = None

    @classmethod
    def from_env(cls) -> "Config":
        provider = os.getenv("OMNI_VISION_PROVIDER")
        if not provider:
            raise ConfigError(
                message="OMNI_VISION_PROVIDER is required",
                missing_key="OMNI_VISION_PROVIDER",
            )

        if provider not in ["ollama", "openrouter", "openai", "lmstudio"]:
            raise ConfigError(
                message=f"Invalid provider: {provider}. Must be one of: ollama, openrouter, openai, lmstudio",
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

        max_retries_str = os.getenv("OMNI_VISION_MAX_RETRIES", "3")
        try:
            max_retries = int(max_retries_str)
        except ValueError:
            raise ConfigError(
                message=f"OMNI_VISION_MAX_RETRIES must be an integer, got: {max_retries_str}",
            )

        ollama_allowed = os.getenv("OLLAMA_ALLOWED_MODELS", "qwen3-vl:4b,qwen3-vl:2b")
        ollama_auto_pull_str = os.getenv("OLLAMA_AUTO_PULL", "false").lower()
        ollama_auto_pull = ollama_auto_pull_str in ["true", "1", "yes"]

        config = cls(
            provider=cast(ProviderType, provider),
            api_key=api_key,
            default_model=os.getenv("OMNI_VISION_DEFAULT_MODEL"),
            timeout=timeout,
            max_retries=max_retries,
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
        elif provider == "lmstudio":
            config.lmstudio = LMStudioConfig(
                base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234"),
                default_model=config.default_model or "qwen2.5-vl-7b-instruct",
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
