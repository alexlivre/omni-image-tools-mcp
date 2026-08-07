"""
Omni-Image-Tools MCP Server
MCP server for image vision and processing.
Supports: Ollama, OpenRouter, OpenAI
"""

__version__ = "0.5.0"

from .server import OmniImageToolsServer, main
from .config import Config
from .providers import ProviderFactory
from .tools import register_all_tools, ToolRegistry

__all__ = [
    "OmniImageToolsServer",
    "Config",
    "ProviderFactory",
    "ToolRegistry",
    "register_all_tools",
    "main",
]
