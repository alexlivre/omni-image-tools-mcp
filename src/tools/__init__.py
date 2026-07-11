"""Tool registry and schemas for omni-image-tools-mcp."""

import importlib
from typing import Any, Callable


TOOL_SCHEMAS = {
    "analyze_image": {
        "name": "analyze_image",
        "description": "Use when you need to analyze an image with a custom prompt to get detailed information about its contents. IMPORTANT: For local providers (Ollama), only 1 image per request is supported due to GPU memory limits. For online providers (OpenRouter, OpenAI), multiple images are supported. Call get_provider_info first to check current provider limits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file",
                },
                "prompt": {
                    "type": "string",
                    "description": "The prompt/question about the image",
                    "default": "Describe this image in detail",
                },
                "model": {
                    "type": "string",
                    "description": "Model to use (optional, uses default if not specified)",
                },
                "detail_level": {
                    "type": "string",
                    "enum": ["brief", "standard", "detailed"],
                    "default": "standard",
                    "description": "Level of detail in the response",
                },
            },
            "required": ["image_path"],
        },
    },
    "identify_objects": {
        "name": "identify_objects",
        "description": "Use when you need to identify and locate objects in an image. IMPORTANT: For local providers (Ollama), only 1 image per request is supported due to GPU memory limits. For online providers (OpenRouter, OpenAI), multiple images are supported. Call get_provider_info first to check current provider limits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file",
                },
                "include_count": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include count of each object type",
                },
                "categories": {
                    "type": "string",
                    "description": "Filter by categories (comma-separated)",
                },
                "min_confidence": {
                    "type": "number",
                    "default": 0.5,
                    "description": "Minimum confidence threshold (0-1)",
                },
            },
            "required": ["image_path"],
        },
    },
    "read_text": {
        "name": "read_text",
        "description": "Use when you need to extract text from an image (OCR). IMPORTANT: For local providers (Ollama), only 1 image per request is supported due to GPU memory limits. For online providers (OpenRouter, OpenAI), multiple images are supported. Call get_provider_info first to check current provider limits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file",
                },
                "preserve_formatting": {
                    "type": "boolean",
                    "default": False,
                    "description": "Preserve text layout and formatting",
                },
                "language_hint": {
                    "type": "string",
                    "description": "Language hint (e.g., en, pt, es)",
                },
            },
            "required": ["image_path"],
        },
    },
    "compare_images": {
        "name": "compare_images",
        "description": "Use when you need to compare multiple images (2-10) and identify similarities or differences between them. Pass a list of image paths to compare all images at once. IMPORTANT: For local providers (Ollama), this tool requires processing images sequentially and may be slower or less accurate. For online providers (OpenRouter, OpenAI), images are processed together for best results. Call get_provider_info first to check current provider limits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 10,
                    "description": "List of image paths to compare (2-10 images)",
                },
                "compare_type": {
                    "type": "string",
                    "enum": ["similarities", "differences", "both"],
                    "default": "both",
                    "description": "What to compare: similarities (what they have in common), differences (what sets them apart), or both",
                },
            },
            "required": ["image_paths"],
        },
    },
    "prepare_image": {
        "name": "prepare_image",
        "description": "Use when you need to prepare an image for analysis (resize, optimize).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file",
                },
                "max_width": {
                    "type": "integer",
                    "default": 1024,
                    "description": "Maximum width in pixels",
                },
                "max_height": {
                    "type": "integer",
                    "default": 1024,
                    "description": "Maximum height in pixels",
                },
                "format": {
                    "type": "string",
                    "enum": ["JPEG", "PNG", "WEBP"],
                    "default": "JPEG",
                    "description": "Output format",
                },
                "quality": {
                    "type": "integer",
                    "default": 85,
                    "description": "Quality (1-100)",
                },
            },
            "required": ["image_path"],
        },
    },
    "get_image_info": {
        "name": "get_image_info",
        "description": "Use when you need to get metadata information about an image.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file",
                },
                "include_exif": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include EXIF metadata",
                },
            },
            "required": ["image_path"],
        },
    },
    "crop_image": {
        "name": "crop_image",
        "description": "Use when you need to crop a specific region from an image.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file",
                },
                "x": {
                    "type": "integer",
                    "description": "X coordinate of top-left corner",
                },
                "y": {
                    "type": "integer",
                    "description": "Y coordinate of top-left corner",
                },
                "width": {
                    "type": "integer",
                    "description": "Width of crop region",
                },
                "height": {
                    "type": "integer",
                    "description": "Height of crop region",
                },
            },
            "required": ["image_path", "x", "y", "width", "height"],
        },
    },
    "convert_image_format": {
        "name": "convert_image_format",
        "description": "Use when you need to convert an image from one format to another.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file",
                },
                "output_format": {
                    "type": "string",
                    "enum": ["JPEG", "PNG", "WEBP", "BMP", "GIF"],
                    "description": "Target format",
                },
                "quality": {
                    "type": "integer",
                    "default": 85,
                    "description": "Quality (1-100, for JPEG/WebP)",
                },
            },
            "required": ["image_path", "output_format"],
        },
    },
    "get_provider_info": {
        "name": "get_provider_info",
        "description": "Get information about the currently configured vision provider including its type (local/online), image processing limits, and capabilities. Use this to understand what the current provider supports before calling vision tools.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "download_image": {
        "name": "download_image",
        "description": "Download an image from a URL and save it locally. Use this when you need to analyze an image from the web. Returns the local path you can use with other vision tools.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "HTTP or HTTPS URL of the image to download",
                },
            },
            "required": ["url"],
        },
    },
    "extract_object": {
        "name": "extract_object",
        "description": "Locate and crop a specific object from an image. Use this to extract objects like license plates, faces, logos, or any element described in text. Uses AI vision to find the object, then crops and saves the region automatically.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file",
                },
                "object_description": {
                    "type": "string",
                    "description": "Description of the object to locate and extract (e.g., 'license plate', 'cat face', 'car logo')",
                },
                "output_filename": {
                    "type": "string",
                    "description": "Optional filename for the extracted image. If not provided, auto-generates one.",
                },
            },
            "required": ["image_path", "object_description"],
        },
    },
}


class ToolRegistry:
    """Registry for tools."""

    _tools: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, func: Callable, schema: dict[str, Any]) -> None:
        """Register a tool."""
        cls._tools[name] = {
            "func": func,
            "schema": schema,
        }

    @classmethod
    def get_tool(cls, name: str) -> dict[str, Any] | None:
        """Get a tool by name."""
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> list[dict[str, Any]]:
        """List all registered tools."""
        return [{"name": name, "schema": tool["schema"]} for name, tool in cls._tools.items()]

    @classmethod
    def get_all_schemas(cls) -> list[dict[str, Any]]:
        """Get all tool schemas (for MCP server)."""
        return list(cls._tools.values())


def register_all_tools() -> None:
    """Register all tools from schemas."""
    tool_functions = {
        "analyze_image": importlib.import_module("src.tools.vision.analyze").analyze_image,
        "identify_objects": importlib.import_module("src.tools.vision.identify").identify_objects,
        "read_text": importlib.import_module("src.tools.vision.read_text").read_text,
        "compare_images": importlib.import_module("src.tools.vision.compare").compare_images,
        "prepare_image": importlib.import_module("src.tools.processing.prepare").prepare_image,
        "get_image_info": importlib.import_module("src.tools.processing.info").get_image_info,
        "crop_image": importlib.import_module("src.tools.processing.crop").crop_image,
        "convert_image_format": importlib.import_module(
            "src.tools.processing.convert"
        ).convert_image_format,
        "get_provider_info": importlib.import_module(
            "src.tools.system.provider_info"
        ).get_provider_info,
        "download_image": importlib.import_module("src.tools.processing.download").download_image,
        "extract_object": importlib.import_module("src.tools.processing.extract").extract_object,
    }

    for tool_name, tool_schema in TOOL_SCHEMAS.items():
        func = tool_functions.get(tool_name)
        if func is None:

            def create_placeholder(name: str):
                async def placeholder(**kwargs):
                    return {"error": f"Tool '{name}' not yet implemented"}

                return placeholder

            func = create_placeholder(tool_name)

        ToolRegistry.register(
            name=tool_name,
            func=func,
            schema=tool_schema,
        )


__all__ = [
    "ToolRegistry",
    "TOOL_SCHEMAS",
    "register_all_tools",
]
