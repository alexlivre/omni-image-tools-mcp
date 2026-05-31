"""GPU Memory Manager for dual-provider model monitoring.

This module provides centralized monitoring of models loaded in Ollama
and LM Studio to prevent GPU memory overflow on residential GPUs.

Rules:
- ALWAYS check BOTH Ollama and LM Studio before loading new models
- If both providers have models loaded, warn the user
- Provide methods to unload models when needed
"""

import aiohttp
import logging
from typing import Any

logger = logging.getLogger(__name__)


class GPUResourceManager:
    """Centralized manager for GPU memory across Ollama and LM Studio."""

    OLLAMA_PS_ENDPOINT = "/api/ps"
    LMSTUDIO_MODELS_ENDPOINT = "/api/v1/models"
    LMSTUDIO_UNLOAD_ENDPOINT = "/api/v1/models/unload"

    @staticmethod
    async def get_ollama_loaded_models(base_url: str = "http://localhost:11434") -> list[str]:
        """Get list of currently loaded models in Ollama.

        Args:
            base_url: Ollama server URL

        Returns:
            List of model names currently in memory
        """
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
    async def get_lmstudio_loaded_models(base_url: str = "http://localhost:1234") -> list[dict]:
        """Get list of currently loaded models in LM Studio.

        Args:
            base_url: LM Studio server URL

        Returns:
            List of dicts with 'key' and 'instance_id' for each loaded model
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{base_url}{GPUResourceManager.LMSTUDIO_MODELS_ENDPOINT}") as response:
                    if response.status == 200:
                        data = await response.json()
                        loaded = []
                        for model in data.get("models", []):
                            for instance in model.get("loaded_instances", []):
                                loaded.append({
                                    "key": model.get("key", ""),
                                    "instance_id": instance.get("id", ""),
                                    "display_name": model.get("display_name", ""),
                                })
                        return loaded
                    return []
        except Exception as e:
            logger.warning(f"Failed to get LM Studio models: {e}")
            return []

    @staticmethod
    async def unload_lmstudio_model(
        instance_id: str,
        base_url: str = "http://localhost:1234"
    ) -> bool:
        """Unload a specific model from LM Studio.

        Args:
            instance_id: The instance ID to unload
            base_url: LM Studio server URL

        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    f"{base_url}{GPUResourceManager.LMSTUDIO_UNLOAD_ENDPOINT}",
                    json={"instance_id": instance_id}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"LM Studio model unloaded: {instance_id}")
                        return True
                    error = await response.text()
                    logger.error(f"LM Studio unload failed: {error}")
                    return False
        except Exception as e:
            logger.error(f"LM Studio unload error: {e}")
            return False

    @staticmethod
    async def unload_ollama_model(
        model_name: str,
        base_url: str = "http://localhost:11434"
    ) -> bool:
        """Unload a specific model from Ollama by setting keep_alive to 0.

        Args:
            model_name: Name of the model to unload
            base_url: Ollama server URL

        Returns:
            True if successful, False otherwise
        """
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
    async def check_for_provider(
        provider: str,
        model: str | None = None,
        ollama_url: str = "http://localhost:11434",
        lmstudio_url: str = "http://localhost:1234"
    ) -> dict[str, Any]:
        """Check loaded models in THIS and OTHER providers before loading a new one.

        Call this BEFORE making a vision request to avoid GPU memory overflow.
        Checks:
        1. If THIS provider already has a DIFFERENT model loaded (conflict)
        2. If OTHER provider has any models loaded (collision)

        Args:
            provider: Current provider name ("ollama" or "lmstudio")
            model: The model being requested (to check if same model already loaded)
            ollama_url: Ollama server URL
            lmstudio_url: LM Studio server URL

        Returns:
            Dict with:
                - can_proceed: True if safe to load model
                - current_provider_loaded: Models in current provider
                - other_provider_models: Models in other provider
                - same_model_loaded: True if same model already in current provider
                - warnings: List of warning messages
        """
        warnings = []
        same_model_loaded = False

        if provider == "ollama":
            other_provider = "lmstudio"
            current_models = await GPUResourceManager.get_ollama_loaded_models(ollama_url)
            other_models = await GPUResourceManager.get_lmstudio_loaded_models(lmstudio_url)
        else:
            other_provider = "ollama"
            current_models = await GPUResourceManager.get_lmstudio_loaded_models(lmstudio_url)
            other_models = await GPUResourceManager.get_ollama_loaded_models(ollama_url)

        if current_models:
            current_model_names = [m.get("display_name") or m.get("key") or m or "?" for m in current_models]
            if model and model in current_model_names:
                same_model_loaded = True
            else:
                warnings.append(
                    f"{provider.capitalize()} already has model(s) loaded: {', '.join(current_model_names)}. "
                    f"Requesting model '{model}' will replace the current model."
                )

        if other_models:
            other_model_names = [m.get("display_name") or m.get("key") or m or "?" for m in other_models]
            warnings.append(
                f"GPU WARNING: {other_provider.capitalize()} has {len(other_models)} model(s) loaded: {', '.join(other_model_names)}. "
                f"Loading in {provider} may cause GPU memory overflow on residential GPUs."
            )

        can_proceed = len(warnings) == 0 or same_model_loaded

        for w in warnings:
            logger.warning(w)

        return {
            "can_proceed": can_proceed,
            "current_provider_loaded": current_models,
            "other_provider_models": other_models,
            "other_provider": other_provider,
            "same_model_loaded": same_model_loaded,
            "warnings": warnings,
        }

    @staticmethod
    async def check_memory_collision(
        ollama_url: str = "http://localhost:11434",
        lmstudio_url: str = "http://localhost:1234"
    ) -> dict[str, Any]:
        """Check for GPU memory collision - models loaded in both providers.

        This is the PRIMARY method to call before any vision operation.
        It verifies BOTH providers and returns their status.

        Args:
            ollama_url: Ollama server URL
            lmstudio_url: LM Studio server URL

        Returns:
            Dict with:
                - ollama_models: list of loaded model names
                - lmstudio_models: list of loaded model dicts
                - total_count: total models across both providers
                - collision_detected: True if models in both providers
                - warning: Warning message if collision detected
        """
        ollama_models = await GPUResourceManager.get_ollama_loaded_models(ollama_url)
        lmstudio_models = await GPUResourceManager.get_lmstudio_loaded_models(lmstudio_url)

        total_count = len(ollama_models) + len(lmstudio_models)
        collision_detected = len(ollama_models) > 0 and len(lmstudio_models) > 0

        result = {
            "ollama_models": ollama_models,
            "lmstudio_models": lmstudio_models,
            "total_count": total_count,
            "collision_detected": collision_detected,
            "warning": None,
        }

        if collision_detected:
            result["warning"] = (
                f"GPU MEMORY WARNING: {len(ollama_models)} model(s) in Ollama "
                f"and {len(lmstudio_models)} model(s) in LM Studio. "
                f"Total: {total_count} models loaded. This may exceed GPU memory "
                f"on residential GPUs. Consider unloading one provider."
            )
            logger.warning(result["warning"])

        return result

    @staticmethod
    async def get_loaded_models_summary(
        ollama_url: str = "http://localhost:11434",
        lmstudio_url: str = "http://localhost:1234"
    ) -> str:
        """Get a human-readable summary of loaded models across both providers.

        Args:
            ollama_url: Ollama server URL
            lmstudio_url: LM Studio server URL

        Returns:
            Formatted string with loaded models info
        """
        status = await GPUResourceManager.check_memory_collision(ollama_url, lmstudio_url)

        lines = ["=" * 50, "GPU MODEL STATUS", "=" * 50]

        if status["ollama_models"]:
            lines.append(f"\nOllama ({len(status['ollama_models'])} loaded):")
            for model in status["ollama_models"]:
                lines.append(f"  - {model}")
        else:
            lines.append("\nOllama: No models loaded")

        if status["lmstudio_models"]:
            lines.append(f"\nLM Studio ({len(status['lmstudio_models'])} loaded):")
            for model in status["lmstudio_models"]:
                lines.append(f"  - {model.get('display_name', model.get('key'))} ({model.get('instance_id')})")
        else:
            lines.append("\nLM Studio: No models loaded")

        lines.append(f"\nTotal: {status['total_count']} model(s)")

        if status["collision_detected"]:
            lines.append("\n⚠️  COLLISION DETECTED - Multiple providers loaded!")

        lines.append("=" * 50)

        return "\n".join(lines)
