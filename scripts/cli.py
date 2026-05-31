#!/usr/bin/env python3
"""CLI for omni-image-tools-mcp."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.providers import ProviderFactory
from src.tools import ToolRegistry, register_all_tools, TOOL_SCHEMAS
from src.utils import GPUResourceManager


async def check_gpu_status():
    """Check and display GPU model status for both Ollama and LM Studio."""
    print("\n" + "=" * 50)
    print("CHECKING GPU MODEL STATUS (DUAL PROVIDER VERIFICATION)")
    print("=" * 50)

    status = await GPUResourceManager.check_memory_collision()

    print(f"\nOllama loaded: {len(status['ollama_models'])} model(s)")
    for m in status['ollama_models']:
        print(f"  - {m}")

    print(f"\nLM Studio loaded: {len(status['lmstudio_models'])} model(s)")
    for m in status['lmstudio_models']:
        print(f"  - {m.get('display_name', m.get('key'))} (id: {m.get('instance_id')})")

    print(f"\nTotal: {status['total_count']} model(s)")

    if status['collision_detected']:
        print("\n[!] COLLISION WARNING: Models loaded in BOTH providers!")
        print("   This may exceed GPU memory on residential GPUs.")
        print("   Consider unloading one provider.")
    elif status['total_count'] > 0:
        print("\n[OK] GPU memory check passed")
    else:
        print("\n[OK] No models loaded")

    print("=" * 50 + "\n")
    return status


async def verify_gpu_before_vision():
    """Verify GPU status before vision operations. Shows warning if collision detected."""
    status = await GPUResourceManager.check_memory_collision()

    if status['collision_detected']:
        print("\n[!] GPU MEMORY WARNING [!]")
        print(f"   Ollama: {status['ollama_models']}")
        print(f"   LM Studio: {[m.get('key') for m in status['lmstudio_models']]}")
        print("   Multiple models loaded - may cause OOM on residential GPUs\n")
    elif status['total_count'] > 0:
        provider = os.environ.get("OMNI_VISION_PROVIDER", "unknown")
        models = status['ollama_models'] if provider == "ollama" else [m.get('key') for m in status['lmstudio_models']]
        print(f"\n[INFO] Using {provider}: {models}\n")

    return status


def list_providers():
    """List available providers."""
    providers = ProviderFactory.list_providers()
    print("Available providers:")
    for p in providers:
        print(f"  {p}")
    print()


def list_tools():
    """List available tools with schemas."""
    print("Vision tools:")
    vision_tools = ["analyze_image", "describe_image", "identify_objects", "read_text", "compare_images"]
    for name in vision_tools:
        schema = TOOL_SCHEMAS.get(name, {})
        desc = schema.get("description", "No description")
        print(f"  {name}")
        print(f"    {desc}")
        print()

    print("Processing tools:")
    processing_tools = ["prepare_image", "get_image_info", "crop_image", "convert_image_format"]
    for name in processing_tools:
        schema = TOOL_SCHEMAS.get(name, {})
        desc = schema.get("description", "No description")
        print(f"  {name}")
        print(f"    {desc}")
        print()


def show_tool_schema(tool_name: str):
    """Show detailed schema for a tool."""
    schema = TOOL_SCHEMAS.get(tool_name)
    if not schema:
        print(f"Unknown tool: {tool_name}")
        return

    print(f"Tool: {schema['name']}")
    print(f"Description: {schema['description']}")
    print()
    print("Input Schema:")
    print(json.dumps(schema["inputSchema"], indent=2))


async def analyze_image(args):
    """Analyze an image using the configured provider."""
    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        return 1

    await verify_gpu_before_vision()

    from src.config import Config, ConfigError

    try:
        config = Config.from_env()
    except ConfigError as e:
        print(f"Config error: {e.message}")
        return 1

    debug = getattr(args, 'debug', False)
    provider = ProviderFactory.get(config.provider, config, debug=debug)

    with open(args.image, "rb") as f:
        image_data = f.read()

    prompt = args.prompt
    if args.detail_level:
        from src.prompts import get_vision_prompt
        prompt = get_vision_prompt("analyze_image", args.detail_level)

    try:
        result = await provider.analyze(image_data, prompt, args.model)
        print("Result:")
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def describe_image(args):
    """Describe an image."""
    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        return 1

    await verify_gpu_before_vision()

    from src.config import Config, ConfigError

    try:
        config = Config.from_env()
    except ConfigError as e:
        print(f"Config error: {e.message}")
        return 1

    debug = getattr(args, 'debug', False)
    provider = ProviderFactory.get(config.provider, config, debug=debug)

    with open(args.image, "rb") as f:
        image_data = f.read()

    from src.prompts import get_vision_prompt
    prompt = get_vision_prompt("describe_image", args.type)

    try:
        result = await provider.analyze(image_data, prompt)
        print("Description:")
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def identify_objects(args):
    """Identify objects in an image."""
    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        return 1

    await verify_gpu_before_vision()

    from src.config import Config, ConfigError

    try:
        config = Config.from_env()
    except ConfigError as e:
        print(f"Config error: {e.message}")
        return 1

    debug = getattr(args, 'debug', False)
    provider = ProviderFactory.get(config.provider, config, debug=debug)

    with open(args.image, "rb") as f:
        image_data = f.read()

    prompt = "Identify all objects in this image. List each object you see."

    try:
        result = await provider.analyze(image_data, prompt)
        print("Objects found:")
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def read_text(args):
    """Extract text from an image."""
    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        return 1

    await verify_gpu_before_vision()

    from src.config import Config, ConfigError

    try:
        config = Config.from_env()
    except ConfigError as e:
        print(f"Config error: {e.message}")
        return 1

    debug = getattr(args, 'debug', False)
    provider = ProviderFactory.get(config.provider, config, debug=debug)

    with open(args.image, "rb") as f:
        image_data = f.read()

    if args.preserve_formatting:
        prompt = "Extract all text from this image, preserving the layout and formatting."
    else:
        prompt = "Extract all visible text from this image."

    if args.language_hint:
        prompt += f" (Hint: the text may be in {args.language_hint})"

    try:
        result = await provider.analyze(image_data, prompt)
        print("Extracted text:")
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def compare_images(args):
    """Compare two images."""
    if not os.path.exists(args.image1):
        print(f"Error: Image not found: {args.image1}")
        return 1

    if not os.path.exists(args.image2):
        print(f"Error: Image not found: {args.image2}")
        return 1

    await verify_gpu_before_vision()

    from src.config import Config, ConfigError

    try:
        config = Config.from_env()
    except ConfigError as e:
        print(f"Config error: {e.message}")
        return 1

    from src.tools.vision.compare import compare_images as compare_func

    try:
        result = await compare_func(args.image1, args.image2, args.compare_type)
        print("Comparison result:")
        print(result.get("result", ""))
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def get_image_info(args):
    """Get image metadata."""
    from PIL import Image
    import exifread

    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        return 1

    img = Image.open(args.image)

    print(f"Format: {img.format}")
    print(f"Size: {img.width} x {img.height}")
    print(f"Mode: {img.mode}")

    if hasattr(img, "_getexif") and img._getexif():
        exif = img._getexif()
        if exif:
            print("EXIF data available")

    if args.include_exif:
        with open(args.image, "rb") as f:
            tags = exifread.process_file(f)
            if tags:
                print()
                print("EXIF Tags:")
                for tag, value in list(tags.items())[:10]:
                    print(f"  {tag}: {value}")

    return 0


async def prepare_cmd(args):
    """Prepare/resize an image."""
    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        return 1

    from src.tools.processing.prepare import prepare_image

    try:
        result = await prepare_image(
            args.image,
            max_width=args.max_width,
            max_height=args.max_height,
            format=args.format,
            quality=args.quality,
        )
        if result["success"]:
            print(f"Original size: {result['original_size']}")
            print(f"New size: {result['new_size']}")
            print(f"Format: {result['format']}")
            print(f"Output size: {result['output_size_bytes']} bytes")
            if args.output:
                with open(args.output, "wb") as f:
                    f.write(result["output_data"])
                print(f"Saved to: {args.output}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            return 1
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def crop_cmd(args):
    """Crop a region from an image."""
    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        return 1

    from src.tools.processing.crop import crop_image

    try:
        result = await crop_image(
            args.image,
            x=args.x,
            y=args.y,
            width=args.width,
            height=args.height,
        )
        if result["success"]:
            print(f"Original size: {result['original_size']}")
            print(f"Crop region: {result['crop_region']}")
            print(f"Cropped size: {result['cropped_size']}")
            if args.output:
                with open(args.output, "wb") as f:
                    f.write(result["output_data"])
                print(f"Saved to: {args.output}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            return 1
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def convert_cmd(args):
    """Convert image format."""
    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}")
        return 1

    from src.tools.processing.convert import convert_image_format

    try:
        result = await convert_image_format(
            args.image,
            output_format=args.format,
            quality=args.quality,
        )
        if result["success"]:
            print(f"Original format: {result['original_format']}")
            print(f"New format: {result['new_format']}")
            print(f"Output size: {result['output_size_bytes']} bytes")
            if args.output:
                with open(args.output, "wb") as f:
                    f.write(result["output_data"])
                print(f"Saved to: {args.output}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            return 1
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        prog="omni-image-tools",
        description="MCP server with image tools (vision + processing)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    providers_parser = subparsers.add_parser("providers", help="List providers")
    providers_parser.add_argument("action", nargs="?", choices=["list"], default="list")

    gpu_parser = subparsers.add_parser("gpu-status", help="Check GPU memory status (Ollama + LM Studio)")
    gpu_parser.add_argument("--unload-ollama", metavar="MODEL", help="Unload a specific model from Ollama")
    gpu_parser.add_argument("--unload-lmstudio", metavar="INSTANCE_ID", help="Unload a specific model from LM Studio")

    tools_parser = subparsers.add_parser("tools", help="List tools")
    tools_parser.add_argument("action", nargs="?", choices=["list"], default="list")
    tools_parser.add_argument("--schema", metavar="TOOL", help="Show schema for a specific tool")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze an image")
    analyze_parser.add_argument("--image", required=True, help="Path to image file")
    analyze_parser.add_argument("--prompt", default="Describe this image in detail", help="Analysis prompt")
    analyze_parser.add_argument("--model", help="Model to use")
    analyze_parser.add_argument("--detail-level", choices=["brief", "standard", "detailed"], help="Detail level")
    analyze_parser.add_argument("--debug", action="store_true", help="Enable debug output (request/response/timing)")

    describe_parser = subparsers.add_parser("describe", help="Describe an image")
    describe_parser.add_argument("--image", required=True, help="Path to image file")
    describe_parser.add_argument("--type", choices=["simple", "detailed", "verbose"], default="detailed")
    describe_parser.add_argument("--debug", action="store_true", help="Enable debug output (request/response/timing)")

    identify_parser = subparsers.add_parser("identify", help="Identify objects in an image")
    identify_parser.add_argument("--image", required=True, help="Path to image file")
    identify_parser.add_argument("--include-count", action="store_true", help="Include object counts")
    identify_parser.add_argument("--include-location", action="store_true", help="Include object locations")
    identify_parser.add_argument("--categories", help="Filter by categories (comma-separated)")
    identify_parser.add_argument("--debug", action="store_true", help="Enable debug output (request/response/timing)")

    readtext_parser = subparsers.add_parser("read-text", help="Extract text from an image")
    readtext_parser.add_argument("--image", required=True, help="Path to image file")
    readtext_parser.add_argument("--preserve-formatting", action="store_true", help="Preserve text formatting")
    readtext_parser.add_argument("--language-hint", help="Language hint (e.g., en, pt)")
    readtext_parser.add_argument("--debug", action="store_true", help="Enable debug output (request/response/timing)")

    compare_parser = subparsers.add_parser("compare", help="Compare two images")
    compare_parser.add_argument("--image1", required=True, help="Path to first image")
    compare_parser.add_argument("--image2", required=True, help="Path to second image")
    compare_parser.add_argument("--compare-type", choices=["similarities", "differences", "both"], default="both", help="What to compare")
    compare_parser.add_argument("--debug", action="store_true", help="Enable debug output (request/response/timing)")

    info_parser = subparsers.add_parser("info", help="Get image info")
    info_parser.add_argument("--image", required=True, help="Path to image file")
    info_parser.add_argument("--include-exif", action="store_true", default=True, help="Include EXIF metadata")

    prepare_parser = subparsers.add_parser("prepare", help="Prepare/resize an image")
    prepare_parser.add_argument("--image", required=True, help="Path to image file")
    prepare_parser.add_argument("--max-width", type=int, default=1024, help="Maximum width")
    prepare_parser.add_argument("--max-height", type=int, default=1024, help="Maximum height")
    prepare_parser.add_argument("--format", choices=["JPEG", "PNG", "WEBP"], default="JPEG", help="Output format")
    prepare_parser.add_argument("--quality", type=int, default=85, help="Quality (1-100)")
    prepare_parser.add_argument("--output", help="Output file path")

    crop_parser = subparsers.add_parser("crop", help="Crop a region from an image")
    crop_parser.add_argument("--image", required=True, help="Path to image file")
    crop_parser.add_argument("--x", type=int, required=True, help="X coordinate")
    crop_parser.add_argument("--y", type=int, required=True, help="Y coordinate")
    crop_parser.add_argument("--width", type=int, required=True, help="Width")
    crop_parser.add_argument("--height", type=int, required=True, help="Height")
    crop_parser.add_argument("--output", help="Output file path")

    convert_parser = subparsers.add_parser("convert", help="Convert image format")
    convert_parser.add_argument("--image", required=True, help="Path to image file")
    convert_parser.add_argument("--format", choices=["JPEG", "PNG", "WEBP", "BMP", "GIF"], required=True, help="Target format")
    convert_parser.add_argument("--quality", type=int, default=85, help="Quality (1-100)")
    convert_parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "providers":
        list_providers()
        return 0

    if args.command == "gpu-status":
        if args.unload_ollama:
            print(f"Unloading Ollama model: {args.unload_ollama}")
            success = asyncio.run(GPUResourceManager.unload_ollama_model(args.unload_ollama))
            if success:
                print("[OK] Model unloaded")
            else:
                print("[FAIL] Failed to unload model")
            return 0 if success else 1

        if args.unload_lmstudio:
            print(f"Unloading LM Studio model: {args.unload_lmstudio}")
            success = asyncio.run(GPUResourceManager.unload_lmstudio_model(args.unload_lmstudio))
            if success:
                print("[OK] Model unloaded")
            else:
                print("[FAIL] Failed to unload model")
            return 0 if success else 1

        asyncio.run(check_gpu_status())
        return 0

    if args.command == "tools":
        if args.schema:
            show_tool_schema(args.schema)
        else:
            list_tools()
        return 0

    if args.command == "analyze":
        return asyncio.run(analyze_image(args))

    if args.command == "describe":
        return asyncio.run(describe_image(args))

    if args.command == "identify":
        return asyncio.run(identify_objects(args))

    if args.command == "read-text":
        return asyncio.run(read_text(args))

    if args.command == "compare":
        return asyncio.run(compare_images(args))

    if args.command == "info":
        return get_image_info(args)

    if args.command == "prepare":
        return asyncio.run(prepare_cmd(args))

    if args.command == "crop":
        return asyncio.run(crop_cmd(args))

    if args.command == "convert":
        return asyncio.run(convert_cmd(args))

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
