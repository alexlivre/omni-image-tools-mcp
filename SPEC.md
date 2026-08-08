# Omni-Image-Tools MCP

MCP (Model Context Protocol) with image tools (vision + processing) to give visual capabilities to AI models. Supports multiple providers: OpenRouter, OpenAI, Ollama, LM Studio and MiniMax.

---

## Concept

This project lets AI models without visual capability "see" through an MCP server that translates images into text descriptions. It offers:
- **Vision Tools**: analyze, identify, read_text, compare
- **Processing Tools**: prepare, info, crop, convert
- **Multi-Provider**: OpenRouter, OpenAI, Ollama, LM Studio, MiniMax

---

## Tools

## Automatic Image Preprocessing Rule

Every image received by a vision tool goes through a fixed pipeline **before** any analysis or sending to the model. **Not opt-out.**

- Resizes (Lanczos) keeping the aspect ratio: max longest side = 1536 px; images with a side < 768 px keep the original size.
- Converts to RGB, saves as progressive optimized JPEG q90.
- Target: 300 KB–1 MB.
- Cached in tempdir by SHA-256.
- For `extract_object`, the final crop uses the **original** image (not the preprocessed one).

Details: see `docs/PROCESSING.md`.

### MVP (v1)

| Tool | Description | Parameters |
|------|-----------|-----------|
| `analyze_image` | Customizable image analysis | `image_path`, `prompt`, `model`, `detail_level` |
| `identify_objects` | Lists identifiable objects | `image_path`, `include_count`, `include_location`, `categories`, `min_confidence` |
| `read_text` | Extracts visible text (OCR) | `image_path`, `preserve_formatting`, `language_hint` |

### v2 - Vision

| Tool | Description | Parameters |
|------|-----------|-----------|
| `compare_images` | Compares two images | `image_path_1`, `image_path_2`, `comparison_type` |

### v2 - Processing

| Tool | Description | Parameters |
|------|-----------|-----------|
| `prepare_image` | Prepare image for API (resize, compress) | `image_path`, `max_width`, `max_height`, `format`, `quality` |
| `get_image_info` | Extract metadata and EXIF | `image_path`, `include_exif` |
| `crop_image` | Crop a specific region | `image_path`, `x`, `y`, `width`, `height` |
| `convert_image_format` | Convert between formats | `image_path`, `output_format`, `quality` |

**Details**: See [docs/PROMPTS.md](docs/PROMPTS.md) and [docs/PROCESSING.md](docs/PROCESSING.md)

---

## Supported Providers

| Provider | API Key | Base URL | Type |
|----------|---------|----------|------|
| OpenRouter | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1/chat/completions` | Cloud |
| OpenAI | `OPENAI_API_KEY` | `https://api.openai.com/v1/chat/completions` | Cloud |
| Ollama | None | `http://localhost:11434/api/generate` | Local |
| LM Studio | None | `http://localhost:1234/api/generate` | Local |
| MiniMax | `MINIMAX_API_KEY` | `https://api.minimax.io/v1` | Cloud |

### Recommended Models (OpenRouter)

| Model | Cost | Speed |
|--------|-------|------------|
| `google/gemini-2.5-flash` | low | fast |
| `openai/gpt-4o-mini` | low | fast |
| `anthropic/claude-sonnet-4.6` | medium | medium |
| `anthropic/claude-opus-4.7` | high | very high |

### Recommended Models (Ollama)

| Model | Size | Context | Notes |
|--------|---------|---------|-------|
| `qwen3-vl:4b` | 3.3GB | 256K | ✅ **Default**, Visual Agent, spatial understanding |
| `qwen3-vl:2b` | 1.9GB | 256K | Light, good for weak machines |
| `qwen3-vl:8b` | 6.1GB | 256K | More capable, needs more RAM |
| `moondream` | ~1GB | 4K | Very light, basic |
| `llava` | ~7GB | 4K | Classic, good compatibility |

> **Req**: Ollama 0.12.7+ for Qwen3-VL

### Supported Models (Ollama)

**Safe models allowlist:**

| Model | Size | Notes |
|--------|---------|-------|
| `qwen3-vl:4b` | 3.3GB | ✅ **Default** |
| `qwen3-vl:2b` | 1.9GB | Light |

> Additional models can be enabled via the `OLLAMA_ALLOWED_MODELS` env var, but are not part of the project's standard contract.

### Ollama Config

| Variable | Default | Description |
|----------|---------|-----------|
| `OLLAMA_ALLOWED_MODELS` | list above | Allowed models |
| `OLLAMA_AUTO_PULL` | `false` | Auto-download (off by default for safety) |

**Behavior:**
- If `OLLAMA_ALLOWED_MODELS` is not set → uses the default list
- If set → uses the user's list
- If a model is outside the list → clear error
- `OLLAMA_AUTO_PULL: false` for safety (no accidental GB downloads)

---

## Configuration

Configuration comes from the **host app** (the application using the MCP) via env vars:

| Application | Config File |
|-----------|-------------------|
| OpenCode | `opencode.json` |
| Claude Desktop | `claude_desktop_config.json` |
| Qwen Code | `settings.json` |
| Cursor IDE | `settings.json` |

```json
"omni-image-tools": {
  "command": ["python", "-m", "src.server"],
  "env": {
    "OMNI_VISION_API_KEY": "sk-or-xxx",
    "OMNI_VISION_PROVIDER": "openrouter",
    "OMNI_VISION_DEFAULT_MODEL": "google/gemini-2.5-flash"
  }
}
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|-------------|---------|-----------|
| `OMNI_VISION_API_KEY` | Yes* | - | Provider API key (*except local) |
| `OMNI_VISION_PROVIDER` | Yes | - | `openrouter`, `openai`, `ollama`, `lmstudio`, `minimax` |
| `OMNI_VISION_DEFAULT_MODEL` | No | `qwen3-vl:4b` (ollama), `google/gemini-2.5-flash` (openrouter) | Default model |
| `OMNI_VISION_TIMEOUT` | No | `120` | Timeout in seconds |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama URL |
| `OLLAMA_ALLOWED_MODELS` | No | (default list) | Allowed models |
| `OLLAMA_AUTO_PULL` | No | `false` | Auto-download models |
| `LMSTUDIO_BASE_URL` | No | `http://localhost:1234` | LM Studio URL |
| `MINIMAX_BASE_URL` | No | `https://api.minimax.io/v1` | MiniMax endpoint (China: `https://api.minimaxi.com/v1`) |

### Provider and Model Selection

**Global**: Configured via env vars in the host app (provider + default model).

**Per-Call Override**: Users can override the model per call:
```
analyze_image(image_path="...", model="anthropic/claude-opus-4.7")
```

**Strict Validation**: Model incompatible with provider = clear error.

---

## Setup

### Requirements

| Requirement | Version | Notes |
|-----------|--------|-------|
| Python | **3.11+** | MCP SDK doesn't support 3.14 yet |
| Ollama | 0.12.7+ | For Qwen3-VL |
| Git | Any | For cloning |

### Dependencies

```
# Core
mcp>=1.28.0,<2.0.0
httpx
pillow>=10.0.0
pydantic>=2.0.0
pyyaml

# Optional (for processing)
ExifRead>=3.0.0
pillow-heif>=0.12.0
```

### Installation

```bash
# Clone/fork the repo
git clone https://github.com/xkiranj/ollama-vision-mcp omni-image-tools-mcp
cd omni-image-tools-mcp

# Set up venv (Python 3.11)
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -e .
```

---

## Project Structure

```
omni-image-tools-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP server + tool registry
│   ├── config.py              # Reads env vars
│   │
│   ├── providers/             # FACTORY PATTERN
│   │   ├── __init__.py       # ProviderFactory.get()
│   │   ├── base.py           # VisionProvider (ABC)
│   │   ├── openrouter.py
│   │   ├── openai.py
│   │   ├── ollama.py
│   │   ├── lmstudio.py
│   │   └── minimax.py
│   │
│   ├── tools/                # REGISTRY PATTERN
│   │   ├── __init__.py       # ToolRegistry
│   │   ├── vision/
│   │   │   ├── analyze.py
│   │   │   ├── identify.py
│   │   │   ├── read_text.py
│   │   │   └── compare.py    # v2
│   │   └── processing/
│   │       ├── prepare.py
│   │       ├── info.py
│   │       ├── crop.py
│   │       └── convert.py
│   │
│   └── prompts/
│       ├── vision.yaml
│       └── vision.pt.yaml
│
├── scripts/
│   └── cli.py                 # CLI for dev testing
│
├── tests/
│   └── fixtures/              # Test images
│       ├── simple.jpg
│       ├── complex.jpg
│       ├── text_sample.png
│       └── ...
│
├── docs/
│   ├── PROMPTS.md
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE_DECISION.md
│   ├── PROCESSING.md
│   └── REFERENCE.md
│
├── tasks/
│   └── TODO.md
│
├── pyproject.toml
├── requirements.txt
└── README.md
```

**Details**: See [docs/ARCHITECTURE_DECISION.md](docs/ARCHITECTURE_DECISION.md)

**Architecture details**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Testing During Development

Test each tool **in isolation** via CLI, **before** integrating with the host app.

### CLI Commands

```bash
# Vision tools
python scripts/cli.py analyze --image photo.jpg --provider ollama --model qwen3-vl:4b
python scripts/cli.py identify --image photo.jpg
python scripts/cli.py read-text --image screenshot.png

# Processing tools
python scripts/cli.py info --image photo.jpg
python scripts/cli.py prepare --image photo.jpg --max-size 512

# Benchmark
python scripts/cli.py benchmark --image photo.jpg --providers ollama,openrouter
```

### Test Images (fixtures)

| Image | Use |
|--------|-----|
| `simple.jpg` | Single object |
| `complex.jpg` | Multiple objects |
| `text_sample.png` | OCR |
| `multilanguage.jpg` | Multilingual text |

### Tool Design Standards

Tools follow efficient standards for AI-MCP communication:

- **Descriptions**: Template with "Use when", Input/Output, Examples
- **Schemas**: Rigorous types, enums, defaults, examples
- **Responses**: Consistent format with status, error_code, metadata
- **Errors**: Clear codes + retryable flag + help messages

**Details**: See [docs/ARCHITECTURE_DECISION.md](docs/ARCHITECTURE_DECISION.md)

---

## Links

- **Detailed spec**: This document
- **Prompts**: [docs/PROMPTS.md](docs/PROMPTS.md)
- **Processing**: [docs/PROCESSING.md](docs/PROCESSING.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Decisions**: [docs/ARCHITECTURE_DECISION.md](docs/ARCHITECTURE_DECISION.md)
- **Original study**: [docs/REFERENCE.md](docs/REFERENCE.md)
- **Progress**: [tasks/TODO.md](tasks/TODO.md)
- **Implementation Plan**: [tasks/IMPLEMENTATION_PLAN.md](tasks/IMPLEMENTATION_PLAN.md)

---

## Status

:white_check_mark: Study complete
:hourglass: Awaiting fork and implementation
