#!/usr/bin/env python3
"""Generate test fixtures for omni-image-tools-mcp."""

from PIL import Image, ImageDraw, ImageFont
import os


def create_simple_jpg(output_path: str) -> None:
    img = Image.new("RGB", (400, 300), color=(135, 206, 235))
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 300, 200], fill=(255, 165, 0), outline=(0, 0, 0))
    draw.ellipse([200, 150, 280, 230], fill=(255, 0, 0), outline=(0, 0, 0))
    img.save(output_path, "JPEG", quality=85)
    print(f"Created: {output_path}")


def create_complex_jpg(output_path: str) -> None:
    img = Image.new("RGB", (800, 600), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    for i in range(10):
        x = 50 + i * 70
        draw.rectangle([x, 100, x + 50, 150], fill=(255, 100, 100), outline=(0, 0, 0))
        draw.ellipse([x + 10, 200, x + 40, 230], fill=(100, 200, 100), outline=(0, 0, 0))
    draw.text((300, 300), "Complex Scene", fill=(0, 0, 0))
    img.save(output_path, "JPEG", quality=85)
    print(f"Created: {output_path}")


def create_text_sample_png(output_path: str) -> None:
    img = Image.new("RGB", (600, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 550, 350], outline=(0, 0, 0), width=2)
    draw.text((70, 80), "Hello World!", fill=(0, 0, 0))
    draw.text((70, 120), "Hello Brasil!", fill=(0, 0, 128))
    draw.text((70, 160), "Python 3.10", fill=(128, 0, 0))
    draw.text((70, 200), "MCP Server", fill=(0, 128, 0))
    img.save(output_path, "PNG")
    print(f"Created: {output_path}")


def create_multilanguage_jpg(output_path: str) -> None:
    img = Image.new("RGB", (500, 300), color=(255, 248, 220))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Hello (English)", fill=(0, 0, 0))
    draw.text((50, 90), "Hola (Spanish)", fill=(0, 0, 255))
    draw.text((50, 130), "Bonjour (French)", fill=(255, 0, 0))
    draw.text((50, 170), "Ola (Portuguese)", fill=(0, 128, 0))
    draw.text((50, 210), "Hallo (German)", fill=(128, 0, 128))
    img.save(output_path, "JPEG", quality=85)
    print(f"Created: {output_path}")


def create_big_photo_png(output_path: str) -> None:
    img = Image.new("RGB", (1200, 800), color=(70, 130, 180))
    draw = ImageDraw.Draw(img)
    draw.ellipse([400, 200, 800, 600], fill=(255, 215, 0), outline=(0, 0, 0))
    draw.text((500, 380), "iPhone Photo", fill=(255, 255, 255))
    img.save(output_path, "PNG")
    print(f"Created: {output_path}")


def main():
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)

    create_simple_jpg(os.path.join(fixtures_dir, "simple.jpg"))
    create_complex_jpg(os.path.join(fixtures_dir, "complex.jpg"))
    create_text_sample_png(os.path.join(fixtures_dir, "text_sample.png"))
    create_multilanguage_jpg(os.path.join(fixtures_dir, "multilanguage.jpg"))
    create_big_photo_png(os.path.join(fixtures_dir, "big_photo.png"))

    print("\nAll fixtures created successfully!")


if __name__ == "__main__":
    main()
