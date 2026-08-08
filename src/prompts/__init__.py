"""Prompts loader for omni-image-tools-mcp."""

import os
import yaml
from pathlib import Path


def load_prompts(filename: str) -> dict:
    """Load prompts from a YAML file."""
    prompts_path = Path(__file__).parent / filename
    with open(prompts_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_vision_prompt(tool: str, variant: str | None = None, lang: str | None = None) -> str:
    """Get a vision prompt by tool name, optional variant, and locale."""
    lang = lang or os.getenv("OMNI_LANG", "en")
    filename = f"vision.{lang}.yaml" if lang != "en" else "vision.yaml"
    if not (Path(__file__).parent / filename).exists():
        filename = "vision.yaml"
    prompts = load_prompts(filename)
    tool_prompts: dict = prompts.get(tool, {})
    if variant:
        return str(tool_prompts.get(variant, tool_prompts.get("default", "")))
    return str(tool_prompts.get("default", ""))


__all__ = [
    "load_prompts",
    "get_vision_prompt",
]
