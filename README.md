# omni-image-tools-mcp

> A Model Context Protocol (MCP) server that gives **computer vision** to AI models. It lets AI "see" images: describe, compare, extract text, crop objects, and more.

[![PyPI version](https://img.shields.io/pypi/v/omni-image-tools-mcp.svg)](https://pypi.org/project/omni-image-tools-mcp/)
[![PyPI downloads](https://img.shields.io/pypi/dm/omni-image-tools-mcp.svg)](https://pypi.org/project/omni-image-tools-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![CI](https://github.com/alexlivre/omni-image-tools-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/alexlivre/omni-image-tools-mcp/actions)

**11 tools** · **5 providers** · **Works with opencode, Claude, Cursor**

---

## Table of Contents

- [Why this exists](#why-this-exists)
- [Which provider to use?](#which-provider-to-use)
- [Pick your model](#pick-your-model)
- [Quickstart](#quickstart)
- [Installation](#installation)
- [Tools](#tools)
- [Configuration](#configuration)
- [Provider setup](#provider-setup)
- [Security](#security)
- [GPU memory management](#gpu-memory-management)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

---

## Why this exists

If you use an MCP-aware LLM client and want your AI to **see** images, you need a local bridge between the client and a vision model. This server is that bridge:

- Speaks MCP over **stdio** (works with any compliant client)
- Supports **local** (Ollama, LM Studio) and **cloud** (OpenAI, OpenRouter, MiniMax) vision providers
- Preprocesses images automatically (resize, compress, cache) before sending them upstream
- Exposes both **AI vision** tools (describe, OCR, object detection, compare) and **deterministic processing** tools (crop, convert, resize, download)
- `extract_object` finds and crops any object described in text — automatically

## Which provider to use?

### If you have a GPU → Ollama

> The model runs **on your computer**, using your graphics card. Free, private, no internet needed.

**Limit:** your GPU has finite memory — that's why it's **1 image at a time** with smaller models.

### If you have no GPU or want more quality → Cloud

> The model runs **in the cloud** (OpenAI, OpenRouter, MiniMax). Pay-per-use, needs an API key, no image limits.

## Pick your model

| For... | Use | Size | Where it runs |
|--------|-----|------|---------------|
| Weak PC or just testing | `qwen3-vl:2b` | 1.9GB 🟢 | Your computer (Ollama) |
| Mid-range PC | `qwen3-vl:4b` | 3.3GB 🟡 | Your computer (Ollama) |
| Professional quality | `gpt-5.4-mini` | ☁️ | Cloud (OpenAI, paid) |
| Best value | `qwen/qwen3-vl-32b-instruct` | ☁️ | Cloud (OpenRouter, cheap) |
| Multimodal frontier | `MiniMax-M3` | ☁️ | Cloud (MiniMax) |

> ⚠️ **Memory matters:** with 4GB of VRAM use `qwen3-vl:2b`; with 6GB+ you can use `qwen3-vl:4b`. Cloud models don't touch your GPU.

## Quickstart

```bash
# 1. Install via pip (requires uv: https://docs.astral.sh/uv/)
pip install omni-image-tools-mcp

# 2. If using Ollama (free, local):
export OMNI_VISION_PROVIDER=ollama
export OMNI_VISION_DEFAULT_MODEL=qwen3-vl:2b

# 3. Configure your MCP client (see below) and restart it
```

> 💡 **Tip:** want to use the cloud? See [Provider setup](#provider-setup) below. The `omni-image-tools` console script starts the MCP server over stdio and waits for the client to connect.

## Installation

### Prerequisites

- **Python 3.10+**
- A vision provider: [Ollama](https://ollama.com) installed locally, or an API key for one of the cloud providers

### Option A — From PyPI (recommended for end users)

```bash
pip install omni-image-tools-mcp
```

The `omni-image-tools` console script is installed automatically. Configure your MCP client (examples below), then **restart it**.

### Option B — From source (for contributors)

```bash
git clone https://github.com/alexlivre/omni-image-tools-mcp.git
cd omni-image-tools-mcp
uv sync
uv sync --extra dev
```

## Tools

### 👁️ Vision (use AI)

| Tool | What it does | With Ollama | With Cloud |
|------|--------------|-------------|------------|
| `analyze_image` | Analyze an image with a free prompt | 1 image at a time | Multiple images |
| `identify_objects` | Detect objects in an image | 1 image at a time | Multiple images |
| `read_text` | Extract text (OCR) | 1 image at a time | Multiple images |
| `compare_images` | Compare 2–10 images | Processes one by one | Processes all together |

> **Why does Ollama have a 1-image limit?** Because GPU memory is limited. Sending several images at once can blow the memory and freeze everything. The system **automatically** manages this — no such problem in the cloud.

### 🛠️ Processing (no AI, fast)

| Tool | What it does |
|------|--------------|
| `prepare_image` | Resize and optimize an image |
| `get_image_info` | Read image metadata (size, format, etc.) |
| `crop_image` | Crop a region of an image |
| `convert_image_format` | Convert format (JPEG, PNG, WEBP...) |
| `download_image` | Download an image from the web |
| `extract_object` | **Find and crop an object automatically** |

### ⚙️ System

| Tool | What it does |
|------|--------------|
| `get_provider_info` | Shows the active provider and its limits |

## Configuration

### Environment variables

| Variable | Required | Default | What it does |
|----------|----------|---------|--------------|
| `OMNI_VISION_PROVIDER` | ✅ | — | `ollama`, `openrouter`, `openai`, `lmstudio` or `minimax` |
| `OMNI_VISION_API_KEY` | Cloud only | — | Your provider key |
| `MINIMAX_API_KEY` | MiniMax fallback | — | MiniMax key used when `OMNI_VISION_API_KEY` is unset |
| `MINIMAX_BASE_URL` | ❌ | `https://api.minimax.io/v1` | MiniMax endpoint (China: `https://api.minimaxi.com/v1`) |
| `OMNI_VISION_DEFAULT_MODEL` | ❌ | Varies | Which model to use |
| `OMNI_VISION_TIMEOUT` | ❌ | 120s | Max wait time |
| `OLLAMA_ALLOWED_MODELS` | ❌ | `qwen3-vl:4b,qwen3-vl:2b` | Allowed Ollama models (CSV) |
| `OMNI_OUTPUT_DIR` | ❌ | `./outputs` | Where `extract_object`/`download_image` write files |
| `OMNI_ALLOWED_DIRS` | ❌ | (empty = no sandbox) | Allowed directories for `image_path` (separated by `;`) — path-traversal protection |

## Provider setup

### Option A: Ollama (free, local)

> Requires [Ollama](https://ollama.com) installed and the model pulled (`ollama pull qwen3-vl:2b`)

```bash
export OMNI_VISION_PROVIDER=ollama
export OMNI_VISION_DEFAULT_MODEL=qwen3-vl:2b
```

### Option B: OpenAI (cloud, paid)

> Requires an [OpenAI API key](https://platform.openai.com/api-keys)

```bash
export OMNI_VISION_PROVIDER=openai
export OMNI_VISION_API_KEY=sk-proj-your-key-here
export OMNI_VISION_DEFAULT_MODEL=gpt-5.4-mini
```

### Option C: OpenRouter (cloud, cheap)

> Requires an [OpenRouter API key](https://openrouter.ai/keys)

```bash
export OMNI_VISION_PROVIDER=openrouter
export OMNI_VISION_API_KEY=sk-or-v1-your-key-here
export OMNI_VISION_DEFAULT_MODEL=qwen/qwen3-vl-32b-instruct
```

### Option D: MiniMax (cloud, MiniMax-M3 multimodal)

> Requires a [MiniMax API key](https://platform.minimax.io). Supports both platforms:
> - **International (minimax.io)** — default, no extra config
> - **China (minimaxi.com)** — set `MINIMAX_BASE_URL=https://api.minimaxi.com/v1`

```bash
# International (default)
export OMNI_VISION_PROVIDER=minimax
export MINIMAX_API_KEY=your-key-here

# China (optional)
export MINIMAX_BASE_URL=https://api.minimaxi.com/v1
```

> 💡 The key can come from `OMNI_VISION_API_KEY` or `MINIMAX_API_KEY` (the latter is used as a fallback — handy if it's already in your system environment variables).

### LM Studio (local)

> Requires [LM Studio](https://lmstudio.ai) running with the server enabled on port 1234.

```bash
export OMNI_VISION_PROVIDER=lmstudio
export LMSTUDIO_BASE_URL=http://localhost:1234
export OMNI_VISION_DEFAULT_MODEL=qwen2.5-vl-7b-instruct
```

## Configuring MCP clients

### opencode

Add to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "omni-image-tools": {
      "type": "local",
      "command": ["omni-image-tools"],
      "environment": {
        "OMNI_VISION_PROVIDER": "ollama",
        "OMNI_VISION_DEFAULT_MODEL": "qwen3-vl:2b"
      },
      "enabled": true
    }
  }
}
```

#### MiniMax example

```json
{
  "mcp": {
    "omni-image-tools": {
      "type": "local",
      "command": ["omni-image-tools"],
      "environment": {
        "OMNI_VISION_PROVIDER": "minimax",
        "MINIMAX_API_KEY": "{env:MINIMAX_API_KEY}",
        "OMNI_VISION_DEFAULT_MODEL": "MiniMax-M3"
      },
      "enabled": true
    }
  }
}
```

> **Note:** if the server is installed in a virtualenv, point `command` at the `omni-image-tools` executable inside that venv. After changing config, **restart opencode**.

Also works with [Claude Desktop](https://claude.ai/download) and [Cursor](https://cursor.sh).

## Security

- **SSRF:** `download_image` blocks private/loopback/link-local IPs (e.g. `169.254.169.254`), hosts that resolve to them, and revalidates every redirect.
- **Path traversal:** all `image_path` values are resolved (`resolve()` follows symlinks); with `OMNI_ALLOWED_DIRS` configured, paths outside the sandbox are rejected.
- **Limited downloads:** download is streamed with a 20 MB cap (Content-Length + byte counter).
- **Privacy:** `get_image_info` returns EXIF off by default (`include_exif`); if enabled and GPS is present, a warning is added.

## GPU memory management

**Only applies if you use Ollama (local).**

When you use Ollama, the model stays loaded in your GPU memory. If you ask to load another model, the system **automatically unloads the previous one** first — preventing memory overflow.

```bash
omni-image-tools gpu-status                    # See what's loaded
omni-image-tools gpu-status --unload-ollama model  # Force unload
```

This all happens **automagically** — you don't need to worry about it.

## Troubleshooting

| Problem | Why it happens | How to fix |
|---------|----------------|------------|
| "Provider not found" | You didn't configure the provider | Set `OMNI_VISION_PROVIDER` |
| "API key required" | Cloud provider without a key | Add `OMNI_VISION_API_KEY` |
| Takes too long to respond | Big model on a weak PC | Increase `OMNI_VISION_TIMEOUT` or use a smaller model |
| "Request timed out" | First time using the model | The model needs to load into GPU (only the first time) |
| No GPU memory | Too many models loaded | The system manages automatically |

## Development

```bash
uv sync
uv sync --extra dev

# Test (pytest)
uv run pytest tests/ -v

# Lint / format / type
uv run ruff check src/ tests/
uv run black src/ tests/ --line-length 100
uv run mypy src/ --python-version 3.10

# CLI for manual testing
uv run python scripts/cli.py analyze --image test.jpg --prompt "Describe this"
```

## License

[MIT](./LICENSE) © 2026 [Alex Santos](https://alexlivre.dev/) ([@alexlivre](https://github.com/alexlivre))
