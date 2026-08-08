# Prompts Engineering

Prompts used in each MCP tool.

## Complete Prompts Analysis (ollama-vision-mcp-reference)

### Prompts Extracted from the Original Code

| Tool | Prompt | Line |
|------|--------|-------|
| `analyze_image` | `"Describe this image in detail"` (default) | server.py:132 |
| `identify_objects` | `"List all identifiable objects in this image. Format as a bulleted list"` | server.py:141 |
| `read_text` | `"Extract and transcribe all visible text in this image. If no text is visible, say 'No text found'"` | server.py:145 |

---

## Omni-Vision MCP Tools

### MVP (v1) — Improve the Existing Ones

| Tool | Description | New Parameters |
|------|-----------|------------------|
| `analyze_image` | Customizable image analysis | `detail_level`, `focus` |
| `identify_objects` | Lists identifiable objects | `include_count`, `include_location`, `categories`, `min_confidence` |
| `read_text` | Extracts visible text (OCR) | `preserve_formatting`, `language_hint` |

### v2 — New Tools

| Tool | Description |
|------|-------------|
| `compare_images` | Compare two images (differences/similarities) |

---

## Improved Prompts (v1)

### 1. `analyze_image`

**Signals:**
- `detail_level`: "brief" | "standard" | "detailed"
- `focus`: "all" | "objects" | "scene" | "text" | "colors"

**Base prompt + detail_level:**
| detail_level | Prompt |
|--------------|--------|
| brief | "Briefly describe this image." |
| standard | "Describe this image in detail." |
| detailed | "Provide a highly detailed and thorough description of this image, including all elements, patterns, and nuances." |

**Focus adds:**
| focus | Added to the prompt |
|-------|-------------------|
| objects | "Focus on identifying and describing each distinct object." |
| scene | "Focus on describing the overall scene, setting, and atmosphere." |
| text | "Focus on any text, labels, or written content." |
| colors | "Focus on colors, color harmonies, and color relationships." |
| all | (nothing added) |

**Parameters:**
```python
analyze_image(
    image_path: str,
    prompt: str = None, # custom prompt
    model: str = None,            # override model
    detail_level: str = "standard",  # "brief" | "standard" | "detailed"
    focus: str = "all"              # "all" | "objects" | "scene" | "text" | "colors"
)
```

### 2. `identify_objects`

**Signals:**
- `include_count`: bool — how many of each object
- `include_location`: bool — position in the image
- `categories`: list — filter (["people", "vehicles", "animals", etc)
- `min_confidence`: float — 0-1, ignore detections with low confidence

**Base prompt:**
```
"List all identifiable objects in this image. Format as a bulleted list."
```

**With include_count=True:**
```
"List all identifiable objects in this image. For each type of object, indicate how many instances appear. Format as a bulleted list with counts."
```

**With include_location=True:**
```
"List all identifiable objects in this image. For each object, indicate its approximate location in the image (e.g., 'top-left', 'center', 'bottom-right'). Format as a bulleted list."
```

**With categories filter:**
```
"Focus on identifying objects in these categories: [categories]. List all identifiable objects from these categories in this image. Format as a bulleted list."
```

**Parameters:**
```python
identify_objects(
    image_path: str,
    include_count: bool = False,
    include_location: bool = False,
    categories: list = None,        # ["people", "vehicles", "animals", "text", "electronics"]
    min_confidence: float = 0.5    # 0.0 to 1.0
)
```

### 4. `read_text`

**Signals:**
- `preserve_formatting`: bool — keep layout
- `language_hint`: str — "en", "pt", "es", etc

**Base prompt:**
```
"Extract and transcribe all visible text in this image. If no text is visible, say 'No text found'."
```

**With preserve_formatting=True:**
```
"Extract and transcribe all visible text in this image, preserving the original formatting, layout, and structure as much as possible. If no text is visible, say 'No text found'."
```

**With language_hint:**
```
"Extract and transcribe all visible text in this image. The text appears to be in [language_hint]. If no text is visible, say 'No text found'."
```

**Parameters:**
```python
read_text(
    image_path: str,
    preserve_formatting: bool = False,
    language_hint: str = None  # "en", "pt", "es", "fr", "de", etc
)
```

---

## Future Tools (v2+)

### `compare_images` (v2)

**Signals:**
- `comparison_type`: "differences" | "similarities" | "both"

**Prompt:**
| comparison_type | Prompt |
|-----------------|--------|
| differences | "Analyze these two images and describe the key differences between them." |
| similarities | "Analyze these two images and describe their key similarities." |
| both | "Analyze these two images and describe both their key differences and similarities." |

**Parameters:**
```python
compare_images(
    image_path_1: str,
    image_path_2: str,
    comparison_type: str = "both"  # "differences" | "similarities" | "both"
)
```

### `detect_faces` (future)

**Prompt:**
```
"Detect all faces in this image. For each face, provide: approximate age estimate, gender (if identifiable), and dominant emotion if clearly visible."
```

### `extract_chart_data` (future)

**Prompt:**
```
"Extract and transcribe all data visible in this chart or graph. Include axis labels, values, and any text annotations. Format the data in a structured way."
```

---

## Decisions

- [x] Keep the 4 original tools with improvements (v1)
- [x] Add `compare_images` (v2)
- [x] Prompts in English (model responds in the user's language)
- [ ] Internationalization of the prompts?
- [ ] System prompt for general behavior?
