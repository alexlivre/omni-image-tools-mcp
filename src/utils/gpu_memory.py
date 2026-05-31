"""GPU Memory Manager for Ollama model monitoring.

Provides centralized monitoring of models loaded in Ollama
to prevent GPU memory overflow on residential GPUs.
"""

import aiohttp
import logging
from typing import Any

logger = logging.getLogger(__name__)


class GPUResourceManager:
    """Centralized manager for GPU memory on Ollama."""

    OLLAMA_PS_ENDPOINT = "/api/ps"

    _gpu_verified: bool = False

    @staticmethod
    async def get_ollama_loaded_models(base_url: str = "http://localhost:11434") -> list[str]:
        """Get list of currently loaded models in Ollama."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{base_url}{GPUResourceManager.OLLAMA_PS_ENDPOINT}") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        return [m.get("name", "") for m in models if m.get("name")]
                    return []
        except Exception as e:
            logger.warning(f"Failed to get Ollama models: {e}")
            return []

    @staticmethod
    async def unload_ollama_model(
        model_name: str,
        base_url: str = "http://localhost:11434"
    ) -> bool:
        """Unload a specific model from Ollama by setting keep_alive to 0."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    f"{base_url}/api/chat",
                    json={"model": model_name, "keep_alive": 0}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Ollama model unloaded: {model_name}")
                        return True
                    error = await response.text()
                    logger.error(f"Ollama unload failed: {error}")
                    return False
        except Exception as e:
            logger.error(f"Ollama unload error: {e}")
            return False

    @staticmethod
    async def ensure_single_provider(
        provider: str,
        model: str | None = None,
        ollama_url: str = "http://localhost:11434",
    ) -> dict[str, Any]:
        """Ensure Ollama has only the required model loaded.

        Checks current loaded models and unloads different ones if needed.
        Only applies to Ollama (local GPU) provider.
        """
        if GPUResourceManager._gpu_verified:
            return {
                "status": "ok",
                "current_provider_loaded": [],
                "warnings": [],
            }

        warnings = []
        unloaded = []
        same_model_loaded = False

        if provider == "ollama":
            current_models = await GPUResourceManager.get_ollama_loaded_models(ollama_url)
        else:
            current_models = []

        current_model_names = [m if isinstance(m, str) else m.get("name", "?") for m in current_models]

        if model and model in current_model_names:
            same_model_loaded = True

        status = "same_model" if same_model_loaded else "ok"

        if current_models and not same_model_loaded:
            for m in current_models:
                model_name = m if isinstance(m, str) else m.get("name", "")
                success = await GPUResourceManager.unload_ollama_model(model_name, ollama_url)
                if success:
                    unloaded.append(model_name)
                else:
                    warnings.append(f"Failed to unload {model_name} from Ollama")
            status = "unloaded"

        if same_model_loaded:
            warnings.append(
                f"Ollama already has model '{model}' loaded. Reusing existing model."
            )

        for w in warnings:
            logger.warning(w)

        GPUResourceManager._gpu_verified = True

        return {
            "status": status,
            "current_provider_loaded": current_models,
            "same_model_loaded": same_model_loaded,
            "unloaded": unloaded,
            "warnings": warnings,
        }

    @staticmethod
    async def check_memory_collision(
        ollama_url: str = "http://localhost:11434",
    ) -> dict[str, Any]:
        """Check Ollama's current loaded models."""
        ollama_models = await GPUResourceManager.get_ollama_loaded_models(ollama_url)

        return {
            "ollama_models": ollama_models,
            "total_count": len(ollama_models),
            "warning": None,
        }

    @staticmethod
    async def get_loaded_models_summary(
        ollama_url: str = "http://localhost:11434",
    ) -> str:
        """Get a human-readable summary of loaded models in Ollama."""
        status = await GPUResourceManager.check_memory_collision(ollama_url)

        lines = ["=" * 50, "GPU MODEL STATUS", "=" * 50]

        if status["ollama_models"]:
            lines.append(f"\nOllama ({len(status['ollama_models'])} loaded):")
            for model in status["ollama_models"]:
                lines.append(f"  - {model}")
        else:
            lines.append("\nOllama: No models loaded")

        lines.append("=" * 50)

        return "\n".join(lines)

    @staticmethod
    def reset_gpu_verification() -> None:
        """Reset the GPU verification flag.

        Forces re-verification on the next tool call if provider changes.
        """
        GPUResourceManager._gpu_verified = False
