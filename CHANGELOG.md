# Changelog

Todas as mudanças notáveis do **omni-image-tools-mcp** serão documentadas neste arquivo.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o versionamento segue o [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.5.0] - 2026-08-06

Primeiro release versionado. Servidor MCP com visão computacional (Ollama,
OpenRouter, OpenAI) + ferramentas de processamento, com hardening de segurança
e conformidade com o protocolo MCP.

### Added

- `src/utils/security.py`: proteção SSRF (`is_safe_url`), resolução de caminhos
  anti path-traversal (`resolve_safe_path`), `clamp` e limites nomeados.
- `annotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`,
  `openWorldHint`) e `title` em todas as 11 ferramentas.
- `instructions` a nível de servidor (mitigação de prompt injection).
- `isError=true` em falhas de ferramenta + `CallToolResult` estruturado.
- `src/providers/openai_compatible.py`: base compartilhada OpenAI/OpenRouter (DRY).
- `is_local` / `image_limit_per_request` como atributos do provider.
- Variáveis de ambiente `OMNI_OUTPUT_DIR` (diretório de saída) e
  `OMNI_ALLOWED_DIRS` (sandbox opcional para `image_path`).
- Testes: segurança, protocolo, config, providers, download, extract.

### Changed

- `download_image`: download em streaming com teto de 20 MB e validação de URL
  (bloqueia IPs privados/loopback/link-local e revalida redirects).
- `get_image_info`: EXIF desligado por padrão (privacidade) + aviso de GPS.
- Diretório de saída padrão de `test_images/` para `outputs/`.
- Debug dos providers roteado para stderr (não corrompe o transporte stdio).
- `tools/list` com descrições estáticas (cache de cliente/prompt estável).
- `with` em `Image.open`/`open` (sem vazamento de recursos).
- Removido placeholder morto do registry; CLI `list_tools` derivado dos schemas.

### Fixed

- SSRF no `download_image` (acesso a metadata cloud / localhost).
- Leitura arbitrária de arquivos via `image_path` (path traversal / symlinks).
- Exceções genéricas que mascavam erros reais.
- `compare_images` agora usa `is_local` do provider (não hardcoded `ollama`).
- `Image.LANCZOS` deprecado → `Image.Resampling.LANCZOS` (compatível com mypy).

### Security

- `download_image`: bloqueio de URLs para IPs privados, loopback, link-local
  (ex.: `169.254.169.254`), multicast e DNS que não resolva (fail-closed).
- `image_path`: `Path.resolve()` segue symlinks; com `OMNI_ALLOWED_DIRS`
  configurado, caminhos fora do sandbox são rejeitados.
- Qualidade: ruff limpo, `mypy` com 0 erros (antes 35), 103 testes passando.

[0.5.0]: https://github.com/alexlivre/omni-image-tools-mcp/releases/tag/v0.5.0
