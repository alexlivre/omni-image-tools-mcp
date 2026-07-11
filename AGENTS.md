# AGENTS.md

MCP server giving vision capabilities to AI models. Python 3.10+, MIT license.

## Quick Commands

```bash
# Install (uv)
uv sync
uv sync --extra dev

# Test (pytest)
uv run pytest tests/ -v

# CLI for manual testing
python scripts/cli.py analyze --image test.jpg --prompt "Describe this"
python scripts/cli.py gpu-status
python scripts/cli.py benchmark --image test.jpg

# Lint / Format
ruff check src/ tests/
ruff format src/ tests/
black src/ tests/ --line-length 100
mypy src/ --python-version 3.10
```

## Architecture

- **Entry point**: `src/server.py` — MCP stdio server via `mcp` SDK
- **Providers**: Factory pattern in `src/providers/` — Ollama, OpenRouter, OpenAI
- **Tools**: Registry pattern in `src/tools/` — `ToolRegistry` class, schemas in `TOOL_SCHEMAS` dict
- **Image preprocessing**: Mandatory for all vision tools — `src/utils/image_preprocessor.py` (resize to max 1536px longest side, JPEG q90 progressive, cached by SHA-256 in tempdir)
- **Config**: All from env vars via `src/config.py` → `Config.from_env()`

## Key Patterns

- Vision tools call `preprocess_to_bytes()` BEFORE sending to provider
- `extract_object` crops from ORIGINAL image (not preprocessed)
- GPU memory management: `GPUResourceManager.ensure_single_provider()` before vision calls
- Provider per-call model override supported via `model` param on vision tools
- All tool functions return `dict` with `success` bool and `result` or `error`

## Env Vars

`OMNI_VISION_PROVIDER` (required: `ollama`|`openrouter`|`openai`), `OMNI_VISION_API_KEY` (cloud only), `OMNI_VISION_DEFAULT_MODEL`, `OMNI_VISION_TIMEOUT` (default 120s)

## Gotchas

- Ollama: 1 image per request (GPU memory limit). Cloud providers: unlimited
- `extract_object` output goes to `test_images/` directory
- `describe_image` tool exists in CLI but not in TOOL_SCHEMAS registry — may be WIP
- Tests require a running provider for integration tests; unit tests in `tests/` work standalone
