# AGENTS.md

MCP server giving vision capabilities to AI models. Python 3.10+, MIT license, published on PyPI.

## Quick Commands

```bash
uv sync                  # install
uv sync --extra dev      # + dev deps (pytest, ruff, mypy, build, twine)

uv run --no-sync pytest tests/ -v      # tests (see Gotchas re: --no-sync)
uv run --no-sync pytest tests/test_providers.py::TestMinimaxProvider -v  # single test

# Manual CLI (dev harness, distinct from the MCP server):
uv run --no-sync python scripts/cli.py analyze --image test.jpg --prompt "Describe this"
uv run --no-sync python scripts/cli.py gpu-status
uv run --no-sync python scripts/cli.py benchmark --image test.jpg

# Lint / Format / Types (CI runs ruff format --check, NOT black)
uv run --no-sync ruff check src/ tests/
uv run --no-sync ruff format --check src/ tests/ scripts/
uv run --no-sync mypy src/ --python-version 3.10
```

## Architecture

- **Entry point**: `src/server_fastmcp.py` — `omni-image-tools` console script → `src.server_fastmcp:main`, FastMCP over stdio. `src/server.py` is the legacy fallback (emits `structuredContent`/`outputSchema`); keep it working but prefer FastMCP.
- **Providers**: Factory pattern in `src/providers/` — `ollama`, `openrouter`, `openai`, `lmstudio`, `minimax`. Cloud providers (OpenAI/OpenRouter/MiniMax) share `OpenAICompatibleProvider` base in `openai_compatible.py`.
- **Tools**: Registry pattern in `src/tools/` — `ToolRegistry` + `TOOL_SCHEMAS` dict in `src/tools/__init__.py`; handlers live in `src/tools/{vision,processing,system}/`.
- **Image preprocessing**: Mandatory for all vision tools — `src/utils/image_preprocessor.py` (`preprocess_to_bytes()`, max 1536px longest side, JPEG q90 progressive, SHA-256 cache in tempdir).
- **Config**: All from env vars via `src/config.py` → `Config.from_env()`. Prompts load from `src/prompts/*.yaml` at runtime (included in the wheel via `package-data`).

## Key Patterns

- Vision tools call `preprocess_to_bytes()` BEFORE sending to provider.
- `extract_object` crops from the ORIGINAL image (not the preprocessed one).
- GPU memory: `GPUResourceManager.ensure_single_provider()` before vision calls.
- Provider per-call model override via `model` param on vision tools.
- All tool functions return `dict` with `success` bool and `result` or `error`.
- MiniMax provider sends `thinking: {"type":"disabled"}` and strips `<think>...` blocks (they leak on the OpenAI-compatible endpoint); also validates `base_resp.status_code` even on HTTP 200.

## Env Vars

- `OMNI_VISION_PROVIDER` (required): `ollama` | `openrouter` | `openai` | `lmstudio` | `minimax`
- `OMNI_VISION_API_KEY` (cloud only). MiniMax falls back to `MINIMAX_API_KEY` when unset.
- `MINIMAX_BASE_URL` (default `https://api.minimax.io/v1`; China = `https://api.minimaxi.com/v1`)
- `OMNI_VISION_DEFAULT_MODEL`, `OMNI_VISION_TIMEOUT` (default 120), `OMNI_VISION_MAX_RETRIES` (default 3)
- `OMNI_FALLBACK_MODELS` (CSV), `OMNI_VISION_CACHE`, `OMNI_RATE_LIMIT_PER_MIN`, `OMNI_LANG`
- `OLLAMA_BASE_URL`, `OLLAMA_ALLOWED_MODELS` (default `qwen3-vl:4b,qwen3-vl:2b`), `OLLAMA_AUTO_PULL`
- `LMSTUDIO_BASE_URL` (default `http://localhost:1234`)
- `OMNI_OUTPUT_DIR` (default `./outputs`), `OMNI_ALLOWED_DIRS` (sandbox, `;`-separated)

## Gotchas

- **`uv run pytest` can fail with "file in use" (`os error 32`) on Windows** if the `omni-image-tools.exe` in `.venv/Scripts` is running (e.g. an opencode session has the MCP server loaded). Use `uv run --no-sync pytest` to skip the resync that tries to overwrite the exe.
- Ollama/LM Studio: 1 image per request (GPU memory). Cloud providers: unlimited.
- `extract_object` / `download_image` write to `OMNI_OUTPUT_DIR` (default `outputs/`), NOT `test_images/`.
- Security is mandatory: `download_image` blocks SSRF (private/loopback/link-local IPs, redirects revalidated); `image_path` is resolved (symlinks) and checked against `OMNI_ALLOWED_DIRS`.
- Tests need a running provider only for integration tests; unit tests in `tests/` run standalone.
- Publishing: `pip install` via PyPI (trusted publishing workflow `.github/workflows/publish.yml`). A pushed tag `vX.Y.Z` must match `version` in `pyproject.toml` or the workflow fails — bump the version first.
