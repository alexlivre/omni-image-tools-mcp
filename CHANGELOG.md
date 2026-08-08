# Changelog

All notable changes to **omni-image-tools-mcp** will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- MiniMax provider (MiniMax-M3 multimodal) with support for minimax.io and minimaxi.com (China) via `MINIMAX_BASE_URL`.
- PyPI publication preparation: version 0.6.0, `package-data` with prompt YAMLs, PEP 639 license, `mcp<2` pin, `build`/`twine` dev deps.
- CI workflow (GitHub Actions: ruff, format, mypy, pytest with a 70% coverage gate).

### Changed

- Coverage raised to ~74%.
- `outputSchema` on deterministic tools.
- `structuredContent` in the legacy server handler.

### Fixed

- Retry with exponential backoff and robust `Retry-After` parsing.
- `test_provider_info.py` formatted.

## [0.5.0] - 2026-08-06

First versioned release. MCP server with computer vision (Ollama,
OpenRouter, OpenAI) + processing tools, with security hardening and MCP
protocol compliance.

### Added

- `src/utils/security.py`: SSRF protection (`is_safe_url`), anti-path-traversal
  path resolution (`resolve_safe_path`), `clamp` and named limits.
- `annotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`,
  `openWorldHint`) and `title` on all 11 tools.
- Server-level `instructions` (prompt-injection mitigation).
- `isError=true` on tool failures + structured `CallToolResult`.
- `src/providers/openai_compatible.py`: shared OpenAI/OpenRouter base (DRY).
- `is_local` / `image_limit_per_request` as provider attributes.
- `OMNI_OUTPUT_DIR` (output directory) and `OMNI_ALLOWED_DIRS` (optional
  sandbox for `image_path`) environment variables.
- Tests: security, protocol, config, providers, download, extract.

### Changed

- `download_image`: streaming download with a 20 MB cap and URL validation
  (blocks private/loopback/link-local IPs and revalidates redirects).
- `get_image_info`: EXIF off by default (privacy) + GPS warning.
- Default output directory changed from `test_images/` to `outputs/`.
- Provider debug routed to stderr (does not corrupt the stdio transport).
- `tools/list` with static descriptions (stable client/prompt cache).
- `with` in `Image.open`/`open` (no resource leaks).
- Removed dead placeholder from the registry; CLI `list_tools` derived from schemas.

### Fixed

- SSRF in `download_image` (access to cloud metadata / localhost).
- Arbitrary file reads via `image_path` (path traversal / symlinks).
- Generic exceptions masking real errors.
- `compare_images` now uses the provider's `is_local` (not hardcoded `ollama`).
- Deprecated `Image.LANCZOS` → `Image.Resampling.LANCZOS` (mypy-compatible).

### Security

- `download_image`: blocks URLs to private, loopback, link-local (e.g.
  `169.254.169.254`), multicast, and non-resolving DNS (fail-closed).
- `image_path`: `Path.resolve()` follows symlinks; with `OMNI_ALLOWED_DIRS`
  configured, paths outside the sandbox are rejected.
- Quality: clean ruff, `mypy` with 0 errors (was 35), 103 tests passing.

[0.5.0]: https://github.com/alexlivre/omni-image-tools-mcp/releases/tag/v0.5.0
