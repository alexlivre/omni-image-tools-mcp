#!/usr/bin/env python3
"""CLI for omni-image-tools-mcp."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="omni-image-tools",
        description="MCP server with image tools (vision + processing)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    providers_parser = subparsers.add_parser("providers", help="List providers")
    providers_parser.add_argument("action", nargs="?", choices=["list"], default="list")

    tools_parser = subparsers.add_parser("tools", help="List tools")
    tools_parser.add_argument("action", nargs="?", choices=["list"], default="list")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze an image")
    analyze_parser.add_argument("--image", required=True, help="Path to image file")
    analyze_parser.add_argument("--provider", default="ollama", help="Provider to use")
    analyze_parser.add_argument("--model", help="Model to use")
    analyze_parser.add_argument("--prompt", default="Describe this image", help="Analysis prompt")
    analyze_parser.add_argument("--debug", action="store_true", help="Enable debug output")

    describe_parser = subparsers.add_parser("describe", help="Describe an image")
    describe_parser.add_argument("--image", required=True, help="Path to image file")
    describe_parser.add_argument("--type", choices=["simple", "detailed", "verbose"], default="detailed")
    describe_parser.add_argument("--provider", default="ollama", help="Provider to use")

    identify_parser = subparsers.add_parser("identify", help="Identify objects in an image")
    identify_parser.add_argument("--image", required=True, help="Path to image file")
    identify_parser.add_argument("--provider", default="ollama", help="Provider to use")
    identify_parser.add_argument("--include-count", action="store_true", help="Include object counts")
    identify_parser.add_argument("--include-location", action="store_true", help="Include object locations")
    identify_parser.add_argument("--categories", help="Filter by categories (comma-separated)")

    readtext_parser = subparsers.add_parser("read-text", help="Extract text from an image")
    readtext_parser.add_argument("--image", required=True, help="Path to image file")
    readtext_parser.add_argument("--preserve-formatting", action="store_true", help="Preserve text formatting")
    readtext_parser.add_argument("--language-hint", help="Language hint (e.g., en, pt)")
    readtext_parser.add_argument("--provider", default="ollama", help="Provider to use")

    info_parser = subparsers.add_parser("info", help="Get image info")
    info_parser.add_argument("--image", required=True, help="Path to image file")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "providers":
        print("Available providers:")
        print("  ollama      - Local Ollama server (default)")
        print("  openrouter  - OpenRouter API")
        print("  openai      - OpenAI API")
        print("  lmstudio    - LM Studio local server")
        return

    if args.command == "tools":
        print("Vision tools:")
        print("  analyze_image   - Analyze image with custom prompt")
        print("  describe_image  - Get image description")
        print("  identify_objects - Identify objects in image")
        print("  read_text       - Extract text from image")
        print()
        print("Processing tools:")
        print("  prepare_image    - Prepare image for analysis")
        print("  get_image_info   - Get image metadata")
        print("  crop_image       - Crop image to region")
        print("  convert_image_format - Convert image format")
        return

    if args.command == "analyze":
        print(f"Analyze: {args.image}")
        print(f"Provider: {args.provider}")
        print(f"Model: {args.model or 'default'}")
        print(f"Prompt: {args.prompt}")
        print("(Not yet implemented - Phase 3+)")
        return

    if args.command == "describe":
        print(f"Describe: {args.image}")
        print(f"Type: {args.type}")
        print(f"Provider: {args.provider}")
        print("(Not yet implemented - Phase 4)")
        return

    if args.command == "identify":
        print(f"Identify objects: {args.image}")
        print(f"Provider: {args.provider}")
        print(f"Include count: {args.include_count}")
        print(f"Include location: {args.include_location}")
        print("(Not yet implemented - Phase 4)")
        return

    if args.command == "read-text":
        print(f"Read text: {args.image}")
        print(f"Preserve formatting: {args.preserve_formatting}")
        print(f"Language hint: {args.language_hint}")
        print("(Not yet implemented - Phase 4)")
        return

    if args.command == "info":
        print(f"Image info: {args.image}")
        print("(Not yet implemented - Phase 6)")
        return


if __name__ == "__main__":
    main()
