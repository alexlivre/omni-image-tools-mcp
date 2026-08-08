# Image Processing Tools

Image processing tools to complement the vision tools.

## Python Libraries

| Library | Use | Status |
|------------|-----|--------|
| **Pillow (PIL)** | Resize, crop, convert, compress, thumbnail | ✅ Default, already used in the original |
| **ExifRead** | Extract EXIF from TIFF/JPEG | ✅ Lightweight, pure Python, well maintained |
| **pillow-heif** | HEIC support (iPhone photos) | ✅ Active, supports HEIF/HEIC |

### Dependencies

```txt
Pillow>=10.0.0
ExifRead>=3.0.0
pillow-heif>=0.12.0  # optional
```

---

## Processing Tools (v2)

### 1. `prepare_image`

Prepares an image for sending to vision APIs: resizes, compresses, converts format.

**Parameters:**
```python
prepare_image(
    image_path: str,
    max_width: int = 1024,       # max width
    max_height: int = 1024,      # max height
    format: str = "JPEG",         # "JPEG", "PNG", "WEBP"
    quality: int = 85,           # 1-100 for JPEG
    mode: str = "fit"            # "fit" (keeps aspect), "stretch" (forces dimensions)
) -> str  # path of the processed image
```

**Use:** Reduce the cost of APIs that charge per pixel.

**Example:**
```python
# Prepare image for OpenRouter (max 1024x1024, JPEG 85%)
prepare_image("photo.jpg", max_width=1024, max_height=1024, format="JPEG", quality=85)
```

---

### 2. `get_image_info`

Extracts information and metadata from an image.

**Parameters:**
```python
get_image_info(
    image_path: str,
    include_exif: bool = True    # include EXIF data
) -> dict # image information
```

**Return:**
```json
{
 "path": "photo.jpg",
    "format": "JPEG",
    "mode": "RGB",
    "size": {"width": 1920, "height": 1080},
    "file_size_bytes": 245760,
    "aspect_ratio": 1.78,
    "exif": {
        "Make": "Apple",
        "Model": "iPhone 14 Pro",
        "DateTimeOriginal": "2024:01:15 14:32:00",
        "GPS": {"Latitude": -23.5505, "Longitude": -46.6333}
    }
}
```

---

### 3. `crop_image`

Crops a specific region of the image.

**Parameters:**
```python
crop_image(
    image_path: str,
    x: int,                      # X coordinate of the top-left corner
    y: int,                      # Y coordinate of the top-left corner
    width: int,                  # region width
    height: int,                 # region height
    output_path: str = None     # if None, overwrites the original
) -> str  # path of the cropped image
```

**Use:** Focus analysis on a specific area.

---

### 4. `convert_image_format`

Converts an image between formats.

**Parameters:**
```python
convert_image_format(
    image_path: str,
    output_format: str,          # "JPEG", "PNG", "WEBP", "HEIC"
    output_path: str = None,    # if None, uses the same name with the new extension
    quality: int = 85           # for JPEG/WEBP
) -> str  # path of the converted image
```

---

## Future Tools (v3+)

### `create_thumbnail`
```python
create_thumbnail(
    image_path: str,
    size: tuple = (256, 256),
    output_path: str = None
) -> str
```

### `rotate_image`
```python
rotate_image(
    image_path: str,
    degrees: float,
    output_path: str = None
) -> str
```

### `extract_faces` (using face_recognition or similar)
```python
extract_faces(
    image_path: str,
    output_dir: str = None
) -> list # list of paths of the extracted faces
```

---

## Decisions

- [x] Add processing tools (v2)
- [x] Use Pillow as the main library
- [x] Use ExifRead for EXIF metadata
- [x] Add pillow-heif support for iPhone photos
- [ ] Create thumbnail with Pillow or a separate library?
- [ ] Face detection with face_recognition? (heavy dependency)

---

## Automatic Image Pre-processing

**Mandatory rule** applied to **all** images received by vision tools (`analyze_image`, `read_text`, `identify_objects`, `compare_images`, `extract_object`), **before** any analysis or sending to the model. Not opt-out.

### Fixed pipeline

1. **Resizing** (mandatory)
   - Keeps the original aspect ratio.
   - Maximum longest side = **1536 px**.
   - If the image's longest side is already < 768 px, **keeps the original size** (no upscaling).
   - **Lanczos** filter (high quality).

2. **Conversion and compression** (mandatory)
   - Converts to **RGB** (alpha channel removed if present).
   - Saves as **JPEG quality 90**, `optimize=True`, `progressive=True`.
   - Goal: final file between **300 KB and 1 MB** (preferred; tolerant outside the range for synthetic or very simple images).

### Where it is applied

| Tool | Behavior |
|------|---------------|
| `analyze_image` | Sends the pre-processed version to the model |
| `read_text` | Sends the pre-processed version to the model |
| `identify_objects` | Sends the pre-processed version to the model |
| `compare_images` | Pre-processes **each** image before sending |
| `extract_object` | Pre-processes the image sent to the model; the **final crop is done from the original image** (preserves crop accuracy) |

### Cache

- Results are cached in `<tempdir>/omni-image-tools/preprocessed/<sha256>.jpg`, indexed by the SHA-256 of the original file.
- Repeats with the same image are not reprocessed.

### Constants (not configurable)

```python
MAX_LONGEST_SIDE = 1536
KEEP_BELOW = 768
JPEG_QUALITY = 90
```

### Implementation

- Module: `src/utils/image_preprocessor.py`
- Public function: `preprocess_to_bytes(path: str | Path) -> bytes`
