# Implementation Plan

**Project:** omni-image-tools-mcp
**Date:** 2026-05-31
**Status:** Approved, awaiting execution

---

## Overview

| Phase | Name | Tasks | Checkpoint |
|------|------|---------|------------|
| 1 | Setup + Base | 5 | ✅ Project runs |
| 2 | Foundation | 6 | ✅ CLI with tools works |
| 3 | Ollama Provider | 3 | ✅ Ollama Provider works |
| 4 | Vision MVP | 4 | ✅ 4 vision tools work |
| 5 | Vision v2 | 1 | ✅ compare tool works |
| 6 | Processing | 4 | ✅ 4 processing tools work |
| 7 | Cloud Providers | 3 | ✅ All providers work |
| 8 | Polish | 3 | ✅ Ready |

---

## Phase Breakdown

### PHASE 1: Setup + Base

**Objective:** Project runs, structure created, solid foundation.

```
1.1 Fork the reference repo
    - git clone https://github.com/xkiranj/ollama-vision-mcp omni-image-tools-mcp
    - git remote rename origin upstream

1.2 Create directory structure
    - src/providers/
    - src/tools/vision/
    - src/tools/processing/
    - src/prompts/
    - scripts/
    - tests/fixtures/

1.3 Implement error classes
    - OmniVisionError (base)
    - ValidationError, ModelNotAllowedError, FileNotFoundError
    - ImageTooLargeError, UnsupportedFormatError
    - ProviderError, TimeoutError, RateLimitError

1.4 Implement config parsing
    - OMNI_VISION_PROVIDER, OMNI_VISION_API_KEY, etc
    - OLLAMA_BASE_URL, OLLAMA_ALLOWED_MODELS, OLLAMA_AUTO_PULL
    - LMSTUDIO_BASE_URL

1.5 Create test fixtures
    - simple.jpg (single object)
    - complex.jpg (multiple objects)
    - text_sample.png (screenshot with text)
    - multilanguage.jpg (PT/EN text)
    - big_photo.heic (iPhone photo)
```

**Checkpoint:** `python -m src.server` or `python scripts/cli.py --help` works

---

### PHASE 2: Foundation

**Objective:** Base provider + Tool System + CLI integrated.

```
2.1 Implement VisionProvider ABC (providers/base.py)
    - @abstractmethod analyze(image_data, prompt, model) -> str

2.2 Implement ProviderFactory (providers/__init__.py)
    - ProviderFactory.get(provider_name, config) -> VisionProvider
    - provider dict: ollama, openrouter, openai, lmstudio

2.3 Implement ToolRegistry (tools/__init__.py)
    - register(tool), get_tool(name), list_tools()
    - inherits from tools/vision/*.py and tools/processing/*.py

2.4 Define schemas for all tools
    - analyze_image, identify_objects, read_text
    - compare_images
    - prepare_image, get_image_info, crop_image, convert_image_format

2.5 Create prompts.yaml
    - prompts/vision.yaml (all vision prompts)
    - prompts/processing.yaml (all processing prompts)

2.6 CLI with commands
    - python scripts/cli.py --help
    - python scripts/cli.py providers list
    - python scripts/cli.py tools list
```

**Checkpoint:** `python scripts/cli.py tools list` lists 8 tools and the CLI responds to commands

---

### PHASE 3: Ollama Provider

**Objective:** Working Ollama provider (reference of the original).

```
3.1 Implement OllamaProvider (providers/ollama.py)
    - Base: src/ollama_client.py from the original
    - With: allowlist check, error handling, config
    - Endpoint: http://localhost:11434/api/generate
    - Format: {"model": "...", "prompt": "...", "images": [base64], "stream": false}

3.2 Test via CLI
    - python scripts/cli.py analyze --image tests/fixtures/simple.jpg --provider ollama
    - Verify it returns a description

3.3 Add --debug mode
    - python scripts/cli.py analyze --image foto.jpg --debug
    - Output: request, response, timing
```

**Checkpoint:** analyze_image works with local Ollama via CLI

---

### PHASE 4: Vision MVP

**Objective:** 4 vision tools working.

```
4.1 Implement analyze_image
    - tools/vision/analyze.py
    - CLI: python scripts/cli.py analyze

4.3 Implement identify_objects
    - tools/vision/identify.py
    - CLI: python scripts/cli.py identify

4.4 Implement read_text
    - tools/vision/read_text.py
    - CLI: python scripts/cli.py read-text
```

**Checkpoint:** All 4 tools work via CLI with Ollama

---

### PHASE 5: Vision v2

**Objective:** compare_images functional.

```
5.1 Implement compare_images
    - tools/vision/compare.py
    - CLI: python scripts/cli.py compare --image1 a.jpg --image2 b.jpg
```

**Checkpoint:** compare works

---

### PHASE 6: Processing Tools

**Objective:** 4 processing tools working.

```
6.1 Implement prepare_image
    - tools/processing/prepare.py
    - CLI: python scripts/cli.py prepare --image foto.jpg --max-size 512

6.2 Implement get_image_info
    - tools/processing/info.py
    - CLI: python scripts/cli.py info --image foto.jpg

6.3 Implement crop_image
    - tools/processing/crop.py
    - CLI: python scripts/cli.py crop --image foto.jpg --x 100 --y 100 --w 200 --h 200

6.4 Implement convert_image_format
    - tools/processing/convert.py
    - CLI: python scripts/cli.py convert --image foto.jpg --format WEBP
```

**Checkpoint:** All 4 tools work

---

### PHASE 7: Cloud Providers

**Objective:** All providers working.

```
7.1 Implement OpenRouterProvider
    - providers/openrouter.py
    - API: https://openrouter.ai/api/v1/chat/completions
    - Auth: Bearer token (OPENROUTER_API_KEY)
    - Format: {"model": "...", "messages": [{"role": "user", "content": [...]}]}

7.2 Implement OpenAIProvider
    - providers/openai.py
    - API: https://api.openai.com/v1/chat/completions
    - Auth: Bearer token (OPENAI_API_KEY)

7.3 Implement LMStudioProvider
    - providers/lmstudio.py
    - API: http://localhost:1234/api/generate
    - No auth (local)
```

**Checkpoint:** benchmark --providers all works with all

---

### PHASE 8: Polish + Docs

**Objective:** Project ready for use.

```
8.1 Complete README.md
    - Installation
    - Configuration
    - Usage (CLI + MCP)
    - Examples

8.2 Final test
    - Benchmark: same image across all providers
    - Verify error handling

8.3 Update docs
    - SPEC.md
    - ARCHITECTURE_DECISION.md
    - If needed
```

**Checkpoint:** ✅ Ready for use

---

## Summary

| Aspect | Value |
|---------|-------|
| Total phases | 8 |
| Total tasks | ~30 |
| Checkpoints | 8 (one per phase) |
| First checkpoint | Phase 1 (project runs) |

---

## Dependencies Between Phases

```
Phase 1 (independent)
  ↓
Phase 2 (depends on 1)
  ↓
Phase 3 (depends on 2)
  ↓
Phase 4 (depends on 2+3)
  ↓
Phase 5 (depends on 4)
Phase 6 (depends on 4)
  ↓
Phase 7 (depends on 2+3)
  ↓
Phase 8 (depends on 4+5+6+7)
```

---

## How to Run

```bash
# Check progress
cat tasks/IMPLEMENTATION_PLAN.md

# After each phase, test the checkpoint

# Phase 1 - Project runs:
python scripts/cli.py --help

# Phase 2 - Tools list:
python scripts/cli.py tools list

# Phase 3 - Ollama provider:
python scripts/cli.py analyze --image tests/fixtures/simple.jpg --provider ollama

# Phase 4 - All vision tools:
python scripts/cli.py tools list

# Phase 6 - Processing:
python scripts/cli.py info --image tests/fixtures/simple.jpg

# Phase 7 - Benchmark:
python scripts/cli.py benchmark --image tests/fixtures/simple.jpg --providers all
```

---

## Status

- [x] Phase 1: Setup + Base (2026-05-31)
- [x] Phase 2: Foundation (2026-05-31)
- [x] Phase 3: Ollama Provider (2026-05-31) - ✅ FULL COMPLETE
  - OllamaProvider implemented with allowlist check
  - Tested with Ollama local (qwen3-vl:2b) - describe, analyze working
  - OpenRouter also tested successfully
  - --debug mode implemented
- [x] Phase 4: Vision MVP (2026-05-31) - ✅ FULL COMPLETE
  - Implemented analyze_image, identify_objects, read_text
  - All tools integrated with ToolRegistry
  - Tested via CLI with LM Studio (qwen3-vl-4b)
- [x] Phase 5: Vision v2 (2026-05-31) - ✅ FULL COMPLETE
  - Implemented compare_images tool
  - CLI: compare --image1 --image2 --compare-type
  - Tested: simple.jpg vs complex.jpg - similarities/differences detected
- [x] Phase 6: Processing (2026-05-31) - ✅ FULL COMPLETE
  - Implemented 4 processing tools: prepare, info, crop, convert
  - All integrated with ToolRegistry and CLI
  - Tested: prepare (resize), crop, convert, info (metadata)
- [x] Phase 7: Cloud Providers (2026-05-31) - ✅ FULL COMPLETE
  - OpenRouterProvider, OpenAIProvider, LMStudioProvider, OllamaProvider
  - All 4 providers tested and working
  - Benchmark command: benchmark --image --providers (tests all providers)
- [x] Phase 8: Polish (2026-05-31) - ✅ FULL COMPLETE
  - README.md rewritten - multi-provider architecture documented
  - CLI commands reference added
  - Error handling verified (file not found, invalid provider)
  - GPU memory management documented
- [ ] Phase 8: Polish
