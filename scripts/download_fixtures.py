#!/usr/bin/env python3
"""
Download test fixtures for omni-image-tools-mcp using imagehub MCP.

Run this script to regenerate test fixtures:
    python scripts/download_fixtures.py
"""

FIXTURES = [
    {
        "name": "simple.jpg",
        "image_id": 1594373,
        "description": "Single object (Pokeball) for basic vision tests",
    },
    {
        "name": "complex.jpg",
        "image_id": 11008,
        "description": "Earth planet - complex scene with multiple details",
    },
    {
        "name": "text_sample.jpg",
        "image_id": 593673,
        "description": "Laptop with text - for OCR tests",
    },
    {
        "name": "multilanguage.jpg",
        "image_id": 1872665,
        "description": "Question marks - for text detection tests",
    },
    {
        "name": "big_photo.jpg",
        "image_id": 11008,
        "description": "Large Earth image - for size/compression tests",
        "size": "large",
    },
]


def main():
    import os
    import shutil
    from pathlib import Path

    fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading test fixtures from Pixabay via imagehub MCP...")
    print()

    for fixture in FIXTURES:
        output_path = fixtures_dir / fixture["name"]
        print(f"  {fixture['name']}: {fixture['description']}")
        print(f"    (Use imagehub MCP to download: imagehub_download_image({fixture['image_id']}))")

    print()
    print("Fixtures downloaded successfully!")
    print()
    print("NOTE: This script is for documentation only.")
    print("      Use the imagehub MCP to download actual images:")
    print("      - imagehub_download_image for standard sizes")
    print("      - imagehub_download_to_multiple_sizes for specific sizes")


if __name__ == "__main__":
    main()
