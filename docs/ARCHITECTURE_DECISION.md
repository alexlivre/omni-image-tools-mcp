# ADR-001: Extensible Architecture for Omni-Vision-MCP

**Date**: 2026-05-31
**Status**: Approved
**Deciders**: Alex

---

## Context

We are building `omni-image-tools-mcp`, a vision MCP that supports multiple providers (OpenRouter, OpenAI, Ollama, LM Studio) and multiple tools (vision + processing).

We analyzed the reference repo (`ollama-vision-mcp`) and concluded that:
- Code is simple and functional (~500 lines)
- Current structure does not support easy extension
- Adding a new provider or tool = significant refactoring

### Problem

If we invest only in minimal refactoring, we will accumulate tech debt:
- New tools = edit `server.py`
- New providers = refactor client
- Hardcoded prompts = search the code to modify

### Trade-offs considered

| Option | Initial Work | Future Ease | Risk |
|-------|-----------------|-------------------|-------|
| Fork + minimal refactoring | Low | Medium | Tech debt |
| Fork + extensible architecture | Medium (~2x) | High | Over-engineering? |
| Start from scratch | High | High | Loses boilerplate |

---

## Decision

**Do a fork + extensible architecture.**

### Rationale

1. One-time investment of ~2x initial time
2. Positive ROI already by the second or third feature
3. Architecture supports multi-provider + multi-tool from the start
4. Separate prompts = designers/PMs can edit without touching code
5. It's not over-engineering — it's the appropriate architecture for:
   - 4 different providers
   - 8+ tools (vision + processing)
   - Long-term maintenance

---

## Proposed Architecture

```
omni-image-tools-mcp/
├── src/
│   ├── server.py              # MCP setup + tool registry
│   ├── config.py              # Env vars + config file
│   ├── image_handler.py       # Keep from original
│   │
│   ├── providers/              # FACTORY PATTERN
│   │   ├── __init__.py        # ProviderFactory.get()
│   │   ├── base.py            # VisionProvider (ABC)
│   │   ├── openrouter.py
│   │   ├── openai.py
│   │   ├── ollama.py          # Migrate from original
│   │   └── lmstudio.py
│   │
│   ├── tools/                 # REGISTRY PATTERN
│   │   ├── __init__.py        # ToolRegistry
│   │   ├── vision/
│   │   │   ├── analyze.py
│   │   │   ├── describe.py
│   │   │   ├── identify.py
│   │   │   └── read_text.py
│   │   └── processing/
│   │       ├── prepare.py
│   │       ├── info.py
│   │       └── crop.py
│   │
│   └── prompts/
│       ├── vision.yaml
│       └── processing.yaml
```

---

## Components

### 1. Provider Factory

```python
# providers/__init__.py
class ProviderFactory:
    @staticmethod
    def get(provider: str, config: Config) -> VisionProvider:
        providers = {
            "openrouter": OpenRouterProvider,
            "openai": OpenAIProvider,
            "ollama": OllamaProvider,
            "lmstudio": LMStudioProvider,
        }
        return providers[provider](config)
```

```python
# providers/base.py
from abc import ABC, abstractmethod

class VisionProvider(ABC):
    @abstractmethod
    async def analyze(self, image_data: str, prompt: str, model: str) -> str:
        pass
```

**Benefit**: Adding a new provider = create 1 file + add to the dict.

### 2. Tool Registry

```python
# tools/__init__.py
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())
```

```python
# tools/vision/analyze.py
class AnalyzeTool:
    name = "analyze_image"
    description = "Analyze an image..."
    input_schema = {...}

    async def execute(self, image_data: str, prompt: str, model: str) -> str:
        # Logic here
```

**Benefit**: Adding a new tool = create 1 file + call `.register()`.

### 3. Separate Prompts

```yaml
# prompts/vision.yaml
analyze:
  default: "Describe this image in detail"
  detailed: "Provide a comprehensive description..."
  objects: "List all identifiable objects..."
  text: "Extract and transcribe all visible text..."

describe:
  comprehensive: "Provide a comprehensive description..."
  brief: "Give a brief summary..."
```

**Benefit**: Editing prompts = edit YAML, not code.

---

## How to Add Features

### New Vision Tool

1. Create `src/tools/vision/my_tool.py`
2. Define a class with `name`, `description`, `input_schema`, `execute()`
3. Import and register it in `tools/__init__.py`

```python
# src/tools/vision/my_tool.py
class MyTool:
    name = "my_tool"
    description = "..."
    input_schema = {...}

    async def execute(self, **kwargs) -> str:
        ...
```

```python
# src/tools/__init__.py
from .vision.my_tool import MyTool
registry.register(MyTool())
```

### New Provider

1. Create `src/providers/my_provider.py`
2. Inherit from `VisionProvider`
3. Implement `analyze()`
4. Add to the dict in `providers/__init__.py`

```python
# src/providers/my_provider.py
class MyProvider(VisionProvider):
    def __init__(self, config):
        self.config = config

    async def analyze(self, image_data: str, prompt: str, model: str) -> str:
        # API call logic
```

```python
# src/providers/__init__.py
providers["my_provider"] = MyProvider
```

### Modify a Prompt

Edit `src/prompts/vision.yaml` — no code changes needed.

---

## Ollama Dynamic Model Detection

Implement in the Ollama provider:

```python
class OllamaProvider(VisionProvider):
    async def list_models(self) -> List[str]:
        """List models installed on Ollama"""
        response = await self.client.get("/api/tags")
        return [m["name"] for m in response.get("models", [])]

    async def is_vision_model(self, model: str) -> bool:
        """Test if model supports images"""
        # Try simple call with image
        pass

    async def ensure_model(self, model: str) -> bool:
        """Ensure model is available (auto-pull)"""
        available = await self.list_models()
        if model not in available:
            await self.pull_model(model)
        return True
```

Config:
```json
{
  "default_model": "qwen3-vl:4b",
  "allowed_models": ["qwen3-vl:4b", "qwen3-vl:2b", "moondream", "llava"],
  "auto_pull": false
}
```

**Allowlist:** Instead of auto-detection, we use a curated list of safe models to avoid accidental downloads of large models.

---

## Migration from the Original Repo

### Step 1: Fork
```bash
git clone https://github.com/xkiranj/ollama-vision-mcp omni-image-tools-mcp
cd omni-image-tools-mcp
git remote rename origin upstream
```

### Step 2: Create structure
```bash
mkdir -p src/providers
mkdir -p src/tools/vision
mkdir -p src/tools/processing
mkdir -p src/prompts
mkdir -p src/utils
```

### Step 3: Migrate code
- `src/ollama_client.py` → `src/providers/ollama.py`
- `src/config.py` → refactor for multi-provider
- Prompts → `src/prompts/vision.yaml`

### Step 4: Implement factory + registry

### Step 5: Create placeholder providers (openrouter, openai, lmstudio)

### Step 6: Migrate/add tools

---

## Testing During Development

### Principle

Test each tool **in isolation** during dev, **before** integrating with the host app. Ensure everything works without having to configure the MCP in the application.

### Structure

```
omni-image-tools-mcp/
├── scripts/
│   └── cli.py               # Unified CLI for testing
├── tests/
│   └── fixtures/
│       ├── simple.jpg       # Single object
│       ├── complex.jpg      # Multiple objects
│       ├── text_sample.png  # Screenshot/document
│       ├── multilanguage.jpg
│       └── big_photo.heic   # Stress test (iPhone)
└── src/
```

### CLI Commands

```bash
# Vision tools
python scripts/cli.py analyze --image photo.jpg --provider ollama --model qwen3-vl:4b
python scripts/cli.py describe --image photo.jpg --provider openrouter
python scripts/cli.py identify --image photo.jpg
python scripts/cli.py read-text --image screenshot.png
python scripts/cli.py compare --image1 a.jpg --image2 b.jpg

# Processing tools
python scripts/cli.py info --image photo.jpg
python scripts/cli.py prepare --image photo.jpg --max-size 512
python scripts/cli.py crop --image photo.jpg --x 100 --y 100 --w 200 --h 200
python scripts/cli.py convert --image photo.jpg --format WEBP

# Benchmark all providers
python scripts/cli.py benchmark --image photo.jpg --providers ollama,openrouter,openai

# Interactive shell
python scripts/cli.py shell --provider ollama
```

### Test Images (fixtures)

| Image | Use | Description |
|--------|-----|-----------|
| `simple.jpg` | Basic test | Single object on a simple background |
| `complex.jpg` | Multiple objects | Scene with several elements |
| `text_sample.png` | OCR | Screenshot or document with text |
| `multilanguage.jpg` | Multilingual OCR | Text in PT/EN/ES |
| `small.jpg` | Thumbnails | Small image for stress testing |
| `big_photo.heic` | iPhone | Photo in HEIC format |

### Benefits of CLI Testing

| Aspect | Benefit |
|---------|-----------|
| **Speed** | Test tool without starting the MCP server |
| **Debug** | Direct print to output, easy to see errors |
| **Provider** | Test each provider in isolation |
| **Documentation** | CLI = usage documentation |
| **CI/CD** | Scripts can run in automated tests |

### CLI Implementation

```python
# scripts/cli.py
import argparse
import asyncio
from src.providers import ProviderFactory
from src.image_handler import ImageHandler

async def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # analyze command
    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("--image", required=True)
    analyze.add_argument("--provider", default="ollama")
    analyze.add_argument("--model")
    analyze.set_defaults(func=cmd_analyze)

    # ... other commands

    args = parser.parse_args()
    await args.func(args)

async def cmd_analyze(args):
    provider = ProviderFactory.get(args.provider, config)
    image_data = await ImageHandler().process_image(args.image)
    result = await provider.analyze(image_data, "Describe this image", args.model)
    print(result)
```

---

## Tool Efficiency Standards

The MCP must be very efficient in tool/schema communication. The AI should quickly understand:
- What each tool does
- When to use each tool
- How to pass parameters correctly
- How to interpret responses

### 1. Tool Description Template

```
[name]: [one-line summary]

Use when: [when to use this tool]
Input: [required params]
Output: [what returns]

Examples:
  [example1]
  [example2]
```

**Example:**
```python
description="""analyze_image: Analyze image and get description.

Use when: You need to understand what's in an image, identify objects, or extract visual information.
Input: image_path (required) - local path or URL
Output: Text description of image content

Examples:
  analyze_image(image_path="/tmp/photo.jpg")
  analyze_image(image_path="https://example.com/img.png", detail_level="brief")"""
```

### 2. Input Schema Standards

Every tool MUST have:
- All types specified (`string`, `integer`, `boolean`, `enum`)
- Enums for limited values (no free strings)
- Defaults for optional params
- Examples in descriptions
- Required explicitly marked

```python
input_schema = {
    "type": "object",
    "properties": {
        "image_path": {
            "type": "string",
            "description": "Path to image (local or URL)",
            "examples": ["/tmp/photo.jpg", "https://example.com/img.png"]
        },
        "detail_level": {
            "type": "string",
            "enum": ["brief", "standard", "detailed"],
            "default": "standard"
        },
        "model": {
            "type": "string",
            "description": "Model to use (default: config default)"
        }
    },
    "required": ["image_path"]
}
```

### 3. Response Format

All tools return consistent JSON structure:

```json
{
  "status": "success",
  "content": "... | null",
  "error_code": "...",
  "message": "...",
  "metadata": {
    "model_used": "qwen3-vl:4b",
    "tokens_used": 1234,
    "processing_time_ms": 1500
  }
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | `string` | `"success"` or `"error"` |
| `content` | `string\|null` | Result content on success |
| `error_code` | `string` | Machine-readable error code |
| `message` | `string` | Human-readable message |
| `metadata` | `object` | Optional additional info |

### 4. Error Codes

| Code | When | Retryable? |
|------|------|------------|
| `VALIDATION_ERROR` | Invalid params | No |
| `MODEL_NOT_ALLOWED` | Model not in allowlist | No |
| `FILE_NOT_FOUND` | Image file doesn't exist | No |
| `IMAGE_TOO_LARGE` | Image > 20MB | No |
| `UNSUPPORTED_FORMAT` | Unsupported image format | No |
| `PROVIDER_ERROR` | Provider API error | Yes |
| `TIMEOUT` | Request timed out | Yes |
| `RATE_LIMIT` | Rate limit exceeded | Yes |

### 5. Error Handling Excellence

Every error must be:
1. **Understandable** — AI and human can understand the problem
2. **Actionable** — with suggestion on how to fix
3. **Categorized** — error_code for programmatic handling
4. **Consistent** — same structure for all errors

#### Error Response Format

```json
{
  "status": "error",
  "error_code": "MODEL_NOT_ALLOWED",
  "message": "Model 'huge-100b' is not in the allowed list",
  "details": {
    "requested_model": "huge-100b",
    "allowed_models": ["qwen3-vl:4b", "moondream"]
  },
  "help": "Add 'huge-100b' to OLLAMA_ALLOWED_MODELS in your config",
  "retryable": false
}
```

#### Error Class Hierarchy

```python
class OmniVisionError(Exception):
    error_code = "INTERNAL_ERROR"
    retryable = False

    def to_dict(self) -> dict:
        return {
            "status": "error",
            "error_code": self.error_code,
            "message": str(self),
            "details": getattr(self, 'details', {}),
            "help": getattr(self, 'help', None),
            "retryable": self.retryable
        }

class ValidationError(OmniVisionError):
    error_code = "VALIDATION_ERROR"

class ModelNotAllowedError(OmniVisionError):
    error_code = "MODEL_NOT_ALLOWED"

class FileNotFoundError(OmniVisionError):
    error_code = "FILE_NOT_FOUND"

class ImageTooLargeError(OmniVisionError):
    error_code = "IMAGE_TOO_LARGE"

class UnsupportedFormatError(OmniVisionError):
    error_code = "UNSUPPORTED_FORMAT"

class ProviderError(OmniVisionError):
    error_code = "PROVIDER_ERROR"
    retryable = True

class TimeoutError(OmniVisionError):
    error_code = "TIMEOUT"
    retryable = True

class RateLimitError(OmniVisionError):
    error_code = "RATE_LIMIT"
    retryable = True
```

#### Error Code Reference

| Code | When | Retryable | Help Example |
|------|------|-----------|--------------|
| `VALIDATION_ERROR` | Invalid params | No | "Check parameter types and required fields" |
| `MODEL_NOT_ALLOWED` | Not in allowlist | No | "Add model to OLLAMA_ALLOWED_MODELS" |
| `FILE_NOT_FOUND` | File doesn't exist | No | "Verify the file path exists" |
| `IMAGE_TOO_LARGE` | > 20MB | No | "Use prepare_image to resize first" |
| `UNSUPPORTED_FORMAT` | Bad format | No | "Use JPEG, PNG, WEBP or HEIC" |
| `PROVIDER_ERROR` | API failed | Yes | "Retry in a few seconds" |
| `TIMEOUT` | Request timeout | Yes | "Retry with longer timeout" |
| `RATE_LIMIT` | Rate limited | Yes | "Wait before retrying" |

#### Usage Example

```python
try:
    result = await provider.analyze(image_data, prompt, model)
except ModelNotAllowedError as e:
    return error_response(e, help="Add model to OLLAMA_ALLOWED_MODELS")
except FileNotFoundError as e:
    return error_response(e, help="Verify image_path exists")
except ProviderError as e:
    return error_response(e, retryable=True)
```

### 6. CLI Debug Mode

```bash
python scripts/cli.py analyze --image img.jpg --debug
```

Output includes:
- Full request payload
- Full response payload
- Timing breakdown
- Model used

---

## Status

- [x] Decision made
- [x] Testing strategy defined
- [x] Tool efficiency standards defined
- [x] Error handling excellence defined
- [ ] Fork done
- [ ] Structure created
- [ ] CLI implemented
- [ ] Provider factory implemented
- [ ] Tool registry implemented
- [ ] Providers migrated/created
- [ ] Tools migrated/added
- [ ] Prompts separated
- [ ] Test fixtures created

---

## Links

- Original repo: https://github.com/xkiranj/ollama-vision-mcp
- Spec: [SPEC.md](../SPEC.md)
- Tasks: [tasks/TODO.md](../tasks/TODO.md)
