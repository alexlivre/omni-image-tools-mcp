# Tasks

## Progress

### Phase 1: Study
- [x] Review reference repo (ollama-vision-mcp)
- [x] Document prompts
- [x] Document architecture
- [x] Create docs structure
- [x] Understand configuration pattern (host app env vars)
- [x] Define tools (MVP + v2)
- [x] Define processing tools (v2)
- [x] Decide on extensible architecture (ADR-001)
- [x] Tool efficiency standards
- [x] Error handling excellence
- [x] Ollama model allowlist

### Phase 2: Fork and Setup (Phase 1 of the Plan)
- [ ] Fork the reference repo (N/A: created as standalone repo `omni-image-tools-mcp`, not forked)
- [x] Create directory structure
- [x] Implement error classes
- [x] Implement config parsing
- [x] Create test fixtures

### Phase 3: Foundation (Phase 2 of the Plan)
- [x] Implement VisionProvider ABC (providers/base.py)
- [x] Implement ProviderFactory (providers/__init__.py)
- [x] Implement ToolRegistry (tools/__init__.py)
- [x] Define schemas for all tools
- [ ] Create prompts/vision.yaml and prompts/processing.yaml (vision.yaml ok; processing.yaml doesn't exist — prompts live in code)
- [x] CLI with commands (help, providers list, tools list)

### Phase 4: Ollama Provider (Phase 3 of the Plan)
- [x] Implement OllamaProvider (providers/ollama.py)
- [x] Test via CLI
- [x] Add --debug mode

### Phase 5: Vision MVP (Phase 4 of the Plan)
- [x] Implement analyze_image
- [ ] Implement describe_image (not implemented as a tool; covered by `analyze_image`)
- [x] Implement identify_objects
- [x] Implement read_text

### Phase 6: Vision v2 (Phase 5 of the Plan)
- [x] Implement compare_images

### Phase 7: Processing (Phase 6 of the Plan)
- [x] Implement prepare_image
- [x] Implement get_image_info
- [x] Implement crop_image
- [x] Implement convert_image_format

### Phase 8: Cloud Providers (Phase 7 of the Plan)
- [x] Implement OpenRouterProvider
- [x] Implement OpenAIProvider
- [x] Implement LMStudioProvider

### Phase 9: Polish (Phase 8 of the Plan)
- [x] README.md
- [x] Final test (benchmark)
- [x] Update docs

---

## Target Structure

```
omni-image-tools-mcp/
├── src/
│   ├── server.py              # MCP setup + tool registry
│   ├── config.py              # Env vars + config file
│   ├── image_handler.py       # Kept from the original
│   ├── errors.py              # Error classes
│   │
│   ├── providers/             # FACTORY PATTERN
│   │   ├── __init__.py        # ProviderFactory.get()
│   │   ├── base.py            # VisionProvider (ABC)
│   │   ├── openrouter.py
│   │   ├── openai.py
│   │   ├── ollama.py
│   │   └── lmstudio.py
│   │
│   ├── tools/                 # REGISTRY PATTERN
│   │   ├── __init__.py        # ToolRegistry
│   │   ├── vision/
│   │   │   ├── analyze.py
│   │   │   ├── describe.py
│   │   │   ├── identify.py
│   │   │   ├── read_text.py
│   │   │   └── compare.py
│   │   └── processing/
│   │       ├── prepare.py
│   │       ├── info.py
│   │       ├── crop.py
│   │       └── convert.py
│   │
│   └── prompts/
│       ├── vision.yaml
│       └── processing.yaml
│
├── scripts/
│   └── cli.py                 # CLI for testing during dev
│
└── tests/
    └── fixtures/               # Images for testing
        ├── simple.jpg
        ├── complex.jpg
        ├── text_sample.png
        └── multilanguage.jpg
```

---

## Open Questions

- [x] Add result caching? (Task 13: `src/utils/result_cache.py`, `OMNI_VISION_CACHE`)
- [x] Per-model rate limiting? (Task 14: `src/utils/rate_limiter.py`, `OMNI_RATE_LIMIT_PER_MIN`)
- [x] Automatic model fallback? (Task 15: `fallback_models` in `src/config.py` / `openai_compatible.py`, `OMNI_FALLBACK_MODELS`)
- [x] Prompt internationalization? (Task 16: `src/prompts/vision.pt.yaml`, `OMNI_LANG`)

---

## How to Add Features

### New Tool
1. Create `src/tools/vision/my_tool.py`
2. Define a class with `name`, `description`, `input_schema`, `execute()`
3. Import and register in `tools/__init__.py`

### New Provider
1. Create `src/providers/my_provider.py`
2. Inherit from `VisionProvider`
3. Implement `analyze()`
4. Add to the dict in `providers/__init__.py`

### Modify Prompt
Edit `src/prompts/vision.yaml` — no code changes needed.

### Phase 10: Automatic Preprocessing
- [x] Create `src/utils/image_preprocessor.py` (fixed pipeline, SHA-256 cache)
- [x] Integrate into `analyze_image`, `read_text`, `identify_objects`, `compare_images`
- [x] Integrate into `extract_object` (preprocess input, crop from original)
- [x] Document in `docs/PROCESSING.md` and `SPEC.md`

### Phase 11: Security and Protocol Hardening
- [x] `src/utils/security.py`: SSRF (`is_safe_url`), path resolution (`resolve_safe_path`), `clamp`, limits
- [x] `download_image`: SSRF blocking, revalidated redirects, streaming download capped at 20MB
- [x] `server.py`: `resolve_safe_path` in `image_path`/`image_paths` preflight; `isError=true` on tool failures; specific exceptions
- [x] Annotations + `title` on all tools; deterministic `tools/list` (static descriptions)
- [x] `instructions` server-level (prompt injection mitigation)
- [x] `get_image_info`: EXIF off by default + GPS warning
- [x] Provider debug routed to stderr (doesn't corrupt stdio)
- [x] Configurable `output_dir` (`OMNI_OUTPUT_DIR`, default `outputs/`)
- [x] DRY: `OpenAICompatibleProvider` (OpenAI/OpenRouter); `is_local` as a provider attribute
- [x] Remove dead registry placeholder; CLI `list_tools` derived from schemas; benchmark filters providers
- [x] `with` on `Image.open`/`open` (no resource leaks); named constants
- [x] Tests: security (26), protocol (13), config, providers, download; mypy green; coverage configured

## Backlog — delivered in this plan

- [x] CI workflow (Task 1): `.github/workflows/ci.yml` (ruff, mypy, pytest + coverage gate)
- [x] FastMCP server (Tasks 10-11): `src/server_fastmcp.py` (progress, meta, entry point in pyproject)
- [x] LM Studio provider (Task 12): `src/providers/lmstudio.py` (OpenAI-compatible, local)
- [x] Cache / rate-limit / fallback / i18n (Tasks 13-16): `result_cache.py`, `rate_limiter.py`, `fallback_models`, `vision.pt.yaml`
- [x] Evaluations runner (Task 17): `scripts/run_evaluations.py` + `scripts/evaluations.xml` (10 QA pairs)
