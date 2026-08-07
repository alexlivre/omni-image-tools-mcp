# Tasks

## Progress

### Fase 1: Estudo
- [x] Analisar repo de referência (ollama-vision-mcp)
- [x] Documentar prompts
- [x] Documentar arquitetura
- [x] Criar estrutura de docs
- [x] Entender padrão de configuração (env vars da host app)
- [x] Definir ferramentas (MVP + v2)
- [x] Definir ferramentas de processamento (v2)
- [x] Decidir por arquitetura extensível (ADR-001)
- [x] Tool efficiency standards
- [x] Error handling excellence
- [x] Allowlist de modelos Ollama

### Fase 2: Fork e Setup (Fase 1 do Plano)
- [ ] Forkar o repo de referência (N/A: criado como repo standalone `omni-image-tools-mcp`, não forked)
- [x] Criar estrutura de diretórios
- [x] Implementar error classes
- [x] Implementar config parsing
- [x] Criar fixtures de teste

### Fase 3: Foundation (Fase 2 do Plano)
- [x] Implementar VisionProvider ABC (providers/base.py)
- [x] Implementar ProviderFactory (providers/__init__.py)
- [x] Implementar ToolRegistry (tools/__init__.py)
- [x] Definir schemas para todas tools
- [ ] Criar prompts/vision.yaml e prompts/processing.yaml (vision.yaml ok; processing.yaml não existe — prompts vivem no código)
- [x] CLI com commands (help, providers list, tools list)

### Fase 4: Ollama Provider (Fase 3 do Plano)
- [x] Implementar OllamaProvider (providers/ollama.py)
- [x] Teste via CLI
- [x] Adicionar --debug mode

### Fase 5: Vision MVP (Fase 4 do Plano)
- [x] Implementar analyze_image
- [ ] Implementar describe_image (não implementado como tool; coberto por `analyze_image`)
- [x] Implementar identify_objects
- [x] Implementar read_text

### Fase 6: Vision v2 (Fase 5 do Plano)
- [x] Implementar compare_images

### Fase 7: Processing (Fase 6 do Plano)
- [x] Implementar prepare_image
- [x] Implementar get_image_info
- [x] Implementar crop_image
- [x] Implementar convert_image_format

### Fase 8: Cloud Providers (Fase 7 do Plano)
- [x] Implementar OpenRouterProvider
- [x] Implementar OpenAIProvider
- [x] Implementar LMStudioProvider

### Fase 9: Polish (Fase 8 do Plano)
- [x] README.md
- [x] Teste final (benchmark)
- [x] Atualizar docs

---

## Estrutura Alvo

```
omni-image-tools-mcp/
├── src/
│   ├── server.py              # MCP setup + tool registry
│   ├── config.py              # Env vars + config file
│   ├── image_handler.py       # Mantém do original
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
│   └── cli.py                 # CLI para testes durante dev
│
└── tests/
    └── fixtures/               # Imagens para teste
        ├── simple.jpg
        ├── complex.jpg
        ├── text_sample.png
        └── multilanguage.jpg
```

---

## Dúvidas em Aberto

- [x] Adicionar cache de resultados? (Task 13: `src/utils/result_cache.py`, `OMNI_VISION_CACHE`)
- [x] Rate limiting por modelo? (Task 14: `src/utils/rate_limiter.py`, `OMNI_RATE_LIMIT_PER_MIN`)
- [x] Fallback automático entre modelos? (Task 15: `fallback_models` em `src/config.py` / `openai_compatible.py`, `OMNI_FALLBACK_MODELS`)
- [x] Internationalização dos prompts? (Task 16: `src/prompts/vision.pt.yaml`, `OMNI_LANG`)

---

## Como Adicionar Features

### Nova Tool
1. Criar `src/tools/vision/minha_tool.py`
2. Definir classe com `name`, `description`, `input_schema`, `execute()`
3. Importar e registrar no `tools/__init__.py`

### Novo Provider
1. Criar `src/providers/meu_provider.py`
2. Herdar de `VisionProvider`
3. Implementar `analyze()`
4. Adicionar ao dict em `providers/__init__.py`

### Modificar Prompt
Editar `src/prompts/vision.yaml` — não precisa mexer código.

### Fase 10: Pré-processamento Automático
- [x] Criar `src/utils/image_preprocessor.py` (pipeline fixo, cache por SHA-256)
- [x] Integrar em `analyze_image`, `read_text`, `identify_objects`, `compare_images`
- [x] Integrar em `extract_object` (preprocessa input, crop do original)
- [x] Documentar em `docs/PROCESSING.md` e `SPEC.md`

### Fase 11: Hardening de Segurança e Protocolo
- [x] `src/utils/security.py`: SSRF (`is_safe_url`), path resolution (`resolve_safe_path`), `clamp`, limites
- [x] `download_image`: bloqueio SSRF, redirects revalidados, download streaming com teto 20MB
- [x] `server.py`: `resolve_safe_path` no preflight de `image_path`/`image_paths`; `isError=true` em falhas de tool; exceções específicas
- [x] Annotations + `title` em todas as tools; `tools/list` determinístico (descrições estáticas)
- [x] `instructions` server-level (mitigação de prompt injection)
- [x] `get_image_info`: EXIF desligado por padrão + aviso de GPS
- [x] Debug dos providers roteado para stderr (não corrompe stdio)
- [x] `output_dir` configurável (`OMNI_OUTPUT_DIR`, default `outputs/`)
- [x] DRY: `OpenAICompatibleProvider` (OpenAI/OpenRouter); `is_local` como atributo do provider
- [x] Remover placeholder morto do registry; CLI `list_tools` derivado dos schemas; benchmark filtra providers
- [x] `with` em `Image.open`/`open` (sem resource leak); constantes nomeadas
- [x] Testes: security (26), protocolo (13), config, providers, download; mypy verde; coverage configurado

## Backlog — entregue neste plano

- [x] CI workflow (Task 1): `.github/workflows/ci.yml` (ruff, mypy, pytest + coverage gate)
- [x] FastMCP server (Tasks 10-11): `src/server_fastmcp.py` (progress, meta, entry point em pyproject)
- [x] LM Studio provider (Task 12): `src/providers/lmstudio.py` (OpenAI-compatible, local)
- [x] Cache / rate-limit / fallback / i18n (Tasks 13-16): `result_cache.py`, `rate_limiter.py`, `fallback_models`, `vision.pt.yaml`
- [x] Evaluations runner (Task 17): `scripts/run_evaluations.py` + `scripts/evaluations.xml` (10 QA pairs)