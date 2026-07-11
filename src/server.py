#!/usr/bin/env python3
"""
Omni-Image-Tools MCP Server
MCP server providing image vision and processing tools.
Supports: Ollama, OpenRouter, OpenAI
"""

import asyncio
import os
import sys
import logging
from typing import Any, Dict, List, Optional, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .config import Config, ConfigError
from .tools import register_all_tools, TOOL_SCHEMAS
from .utils import GPUResourceManager
from .tools.system.provider_info import get_provider_info

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OmniImageToolsServer:
    def __init__(self):
        self.server = Server("omni-image-tools-mcp")
        self._config: Optional[Config] = None
        self._setup_handlers()

    @property
    def config(self) -> Config:
        if self._config is None:
            self._config = Config.from_env()
        return self._config

    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List all available tools"""
            try:
                provider_info = get_provider_info()
                provider_suffix = (
                    f"\n\n⚡ Current provider: {provider_info.get('provider', '?')} "
                    f"({provider_info.get('type', '?')})"
                    f"\n📷 Image limit: {provider_info.get('image_limit_per_request', 'no limit') or 'no limit'} per request"
                )
                if provider_info.get("warnings", {}).get("local"):
                    provider_suffix += f"\n{provider_info['warnings']['local']}"
            except Exception:
                provider_suffix = ""

            tools = []
            for tool_name, schema in TOOL_SCHEMAS.items():
                input_schema = schema.get("inputSchema", {})
                description = schema.get("description", "")

                if tool_name not in ("get_provider_info",):
                    description += provider_suffix

                tools.append(
                    types.Tool(
                        name=schema.get("name", tool_name),
                        description=description,
                        inputSchema=input_schema,
                    )
                )
            return tools

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Optional[Dict[str, Any]] = None
        ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool execution"""
            try:
                if arguments is None:
                    arguments = {}

                image_path = arguments.get("image_path")
                if image_path and not os.path.exists(image_path):
                    raise ValueError(f"Image not found: {image_path}")

                from .tools import ToolRegistry

                tool = ToolRegistry.get_tool(name)

                if not tool:
                    raise ValueError(f"Unknown tool: {name}")

                func = tool["func"]

                if asyncio.iscoroutinefunction(func):
                    result = await func(**arguments)
                else:
                    result = func(**arguments)

                if isinstance(result, dict):
                    if result.get("success"):
                        text = result.get("result", str(result))
                    else:
                        error_msg = result.get("error", "Unknown error")
                        text = f"Error: {error_msg}"
                else:
                    text = str(result)

                return [types.TextContent(type="text", text=text)]

            except ConfigError as e:
                logger.error(f"Config error: {e}")
                return [types.TextContent(type="text", text=f"Config error: {e.message}")]
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Omni-Image-Tools MCP Server...")
        logger.info(f"Provider: {self.config.provider}")

        await GPUResourceManager.check_memory_collision()

        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="omni-image-tools-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


def main():
    """Main entry point"""
    try:
        register_all_tools()
        server = OmniImageToolsServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except ConfigError as e:
        logger.error(f"Config error: {e.message}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
