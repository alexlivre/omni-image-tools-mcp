"""Prompts loader for omni-image-tools-mcp."""

import yaml
from pathlib import Path


def load_prompts(filename: str) -> dict:
    """Load prompts from a YAML file."""
    prompts_path = Path(__file__).parent / filename
    with open(prompts_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_vision_prompt(tool: str, variant: str | None = None) -> str:
    """Get a vision prompt by tool name and optional variant."""
    prompts = load_prompts("vision.yaml")
    tool_prompts = prompts.get(tool, {})
    if variant:
        return tool_prompts.get(variant, tool_prompts.get("default", ""))
    return tool_prompts.get("default", "")


__all__ = [
    "load_prompts",
    "get_vision_prompt",
]
