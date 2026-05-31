# Implementation Plan

**Projeto:** omni-image-tools-mcp
**Data:** 2026-05-31
**Status:** Aprovado, aguardando execução

---

## Visão Geral

| Fase | Nome | Tarefas | Checkpoint |
|------|------|---------|------------|
| 1 | Setup + Base | 5 | ✅ Projeto executa |
| 2 | Foundation | 6 | ✅ CLI com tools funciona |
| 3 | Ollama Provider | 3 | ✅ Provider Ollama funciona |
| 4 | Vision MVP | 4 | ✅ 4 tools vision funcionam |
| 5 | Vision v2 | 1 | ✅ compare tool funciona |
| 6 | Processing | 4 | ✅ 4 tools processing funcionam |
| 7 | Cloud Providers | 3 | ✅ Todos providers funcionam |
| 8 | Polish | 3 | ✅ Pronto |

---

## Detalhamento por Fase

### FASE 1: Setup + Base

**Objetivo:** Projeto ejecuta, estrutura criada, foundation sólida.

```
1.1 Fork do repo de referência
    - git clone https://github.com/xkiranj/ollama-vision-mcp omni-image-tools-mcp
    - git remote rename origin upstream

1.2 Criar estrutura de diretórios
    - src/providers/
    - src/tools/vision/
    - src/tools/processing/
    - src/prompts/
    - scripts/
    - tests/fixtures/

1.3 Implementar error classes
    - OmniVisionError (base)
    - ValidationError, ModelNotAllowedError, FileNotFoundError
    - ImageTooLargeError, UnsupportedFormatError
    - ProviderError, TimeoutError, RateLimitError

1.4 Implementar config parsing
    - OMNI_VISION_PROVIDER, OMNI_VISION_API_KEY, etc
    - OLLAMA_BASE_URL, OLLAMA_ALLOWED_MODELS, OLLAMA_AUTO_PULL
    - LMSTUDIO_BASE_URL

1.5 Criar fixtures de teste
    - simple.jpg (objeto único)
    - complex.jpg (múltiplos objetos)
    - text_sample.png (screenshot com texto)
    - multilanguage.jpg (texto PT/EN)
    - big_photo.heic (iPhone photo)
```

**Checkpoint:** `python -m src.server` ou `python scripts/cli.py --help` funciona

---

### FASE 2: Foundation

**Objetivo:** Provider base + Tool System + CLI integrados.

```
2.1 Implementar VisionProvider ABC (providers/base.py)
    - @abstractmethod analyze(image_data, prompt, model) -> str

2.2 Implementar ProviderFactory (providers/__init__.py)
    - ProviderFactory.get(provider_name, config) -> VisionProvider
    - dict de providers: ollama, openrouter, openai, lmstudio

2.3 Implementar ToolRegistry (tools/__init__.py)
    - register(tool), get_tool(name), list_tools()
    - herda de tools/vision/*.py e tools/processing/*.py

2.4 Definir schemas para todas tools
    - analyze_image, describe_image, identify_objects, read_text
    - compare_images
    - prepare_image, get_image_info, crop_image, convert_image_format

2.5 Criar prompts.yaml
    - prompts/vision.yaml (todos os prompts de visão)
    - prompts/processing.yaml (todos os prompts de processamento)

2.6 CLI com commands
    - python scripts/cli.py --help
    - python scripts/cli.py providers list
    - python scripts/cli.py tools list
```

**Checkpoint:** `python scripts/cli.py tools list` lista 8 tools e CLI responde comandos

---

### FASE 3: Ollama Provider

**Objetivo:** Provider Ollama funcional (referência do original).

```
3.1 Implementar OllamaProvider (providers/ollama.py)
    - Base: src/ollama_client.py do original
    - With: allowlist check, error handling, config
    - Endpoint: http://localhost:11434/api/generate
    - Format: {"model": "...", "prompt": "...", "images": [base64], "stream": false}

3.2 Teste via CLI
    - python scripts/cli.py analyze --image tests/fixtures/simple.jpg --provider ollama
    - Verificar que retorna descrição

3.3 Adicionar --debug mode
    - python scripts/cli.py analyze --image foto.jpg --debug
    - Output: request, response, timing
```

**Checkpoint:** analyze_image funciona com Ollama local via CLI

---

### FASE 4: Vision MVP

**Objetivo:** 4 tools de visão funcionando.

```
4.1 Implementar analyze_image
    - tools/vision/analyze.py
    - CLI: python scripts/cli.py analyze

4.2 Implementar describe_image
    - tools/vision/describe.py
    - CLI: python scripts/cli.py describe

4.3 Implementar identify_objects
    - tools/vision/identify.py
    - CLI: python scripts/cli.py identify

4.4 Implementar read_text
    - tools/vision/read_text.py
    - CLI: python scripts/cli.py read-text
```

**Checkpoint:** Todas 4 tools funcionam via CLI com Ollama

---

### FASE 5: Vision v2

**Objetivo:** compare_images funcional.

```
5.1 Implementar compare_images
    - tools/vision/compare.py
    - CLI: python scripts/cli.py compare --image1 a.jpg --image2 b.jpg
```

**Checkpoint:** compare funciona

---

### FASE 6: Processing Tools

**Objetivo:** 4 tools de processamento funcionando.

```
6.1 Implementar prepare_image
    - tools/processing/prepare.py
    - CLI: python scripts/cli.py prepare --image foto.jpg --max-size 512

6.2 Implementar get_image_info
    - tools/processing/info.py
    - CLI: python scripts/cli.py info --image foto.jpg

6.3 Implementar crop_image
    - tools/processing/crop.py
    - CLI: python scripts/cli.py crop --image foto.jpg --x 100 --y 100 --w 200 --h 200

6.4 Implementar convert_image_format
    - tools/processing/convert.py
    - CLI: python scripts/cli.py convert --image foto.jpg --format WEBP
```

**Checkpoint:** Todas 4 tools funcionam

---

### FASE 7: Cloud Providers

**Objetivo:** Todos providers funcionando.

```
7.1 Implementar OpenRouterProvider
    - providers/openrouter.py
    - API: https://openrouter.ai/api/v1/chat/completions
    - Auth: Bearer token (OPENROUTER_API_KEY)
    - Format: {"model": "...", "messages": [{"role": "user", "content": [...]}]}

7.2 Implementar OpenAIProvider
    - providers/openai.py
    - API: https://api.openai.com/v1/chat/completions
    - Auth: Bearer token (OPENAI_API_KEY)

7.3 Implementar LMStudioProvider
    - providers/lmstudio.py
    - API: http://localhost:1234/api/generate
    - No auth (local)
```

**Checkpoint:** benchmark --providers all funciona com todas

---

### FASE 8: Polish + Docs

**Objetivo:** Projeto pronto para uso.

```
8.1 README.md completo
    - Instalação
    - Configuração
    - Uso (CLI + MCP)
    - Exemplos

8.2 Teste final
    - Benchmark: mesma imagem em todos providers
    - Verificar error handling

8.3 Atualizar docs
    - SPEC.md
    - ARCHITECTURE_DECISION.md
    - Se precisar
```

**Checkpoint:** ✅ Pronto para uso

---

## Resumo

| Aspecto | Valor |
|---------|-------|
| Total fases | 8 |
| Total tarefas | ~30 |
| Checkpoints | 8 (um por fase) |
| Primeiro checkpoint | Fase 1 (projeto executa) |

---

## Dependências Entre Fases

```
Fase 1 (independent)
  ↓
Fase 2 (depends on 1)
  ↓
Fase 3 (depends on 2)
  ↓
Fase 4 (depends on 2+3)
  ↓
Fase 5 (depends on 4)
Fase 6 (depends on 4)
  ↓
Fase 7 (depends on 2+3)
  ↓
Fase 8 (depends on 4+5+6+7)
```

---

## Como Executar

```bash
# Verificar progresso
cat tasks/IMPLEMENTATION_PLAN.md

# Após cada fase, testar checkpoint

# Fase 1 - Projeto executa:
python scripts/cli.py --help

# Fase 2 - Tools list:
python scripts/cli.py tools list

# Fase 3 - Provider Ollama:
python scripts/cli.py analyze --image tests/fixtures/simple.jpg --provider ollama

# Fase 4 - Todas vision tools:
python scripts/cli.py tools list

# Fase 6 - Processing:
python scripts/cli.py info --image tests/fixtures/simple.jpg

# Fase 7 - Benchmark:
python scripts/cli.py benchmark --image tests/fixtures/simple.jpg --providers all
```

---

## Status

- [x] Fase 1: Setup + Base (2026-05-31)
- [x] Fase 2: Foundation (2026-05-31)
- [x] Fase 3: Ollama Provider (2026-05-31) - ✅ FULL COMPLETE
  - OllamaProvider implemented with allowlist check
  - Tested with Ollama local (qwen3-vl:2b) - describe, analyze working
  - OpenRouter also tested successfully
  - --debug mode implemented
- [x] Fase 4: Vision MVP (2026-05-31) - ✅ FULL COMPLETE
  - Implemented analyze_image, describe_image, identify_objects, read_text
  - All tools integrated with ToolRegistry
  - Tested via CLI with LM Studio (qwen3-vl-4b)
- [x] Fase 5: Vision v2 (2026-05-31) - ✅ FULL COMPLETE
  - Implemented compare_images tool
  - CLI: compare --image1 --image2 --compare-type
  - Tested: simple.jpg vs complex.jpg - similarities/differences detected
- [x] Fase 6: Processing (2026-05-31) - ✅ FULL COMPLETE
  - Implemented 4 processing tools: prepare, info, crop, convert
  - All integrated with ToolRegistry and CLI
  - Tested: prepare (resize), crop, convert, info (metadata)
- [x] Fase 7: Cloud Providers (2026-05-31) - ✅ FULL COMPLETE
  - OpenRouterProvider, OpenAIProvider, LMStudioProvider, OllamaProvider
  - All 4 providers tested and working
  - Benchmark command: benchmark --image --providers (tests all providers)
- [x] Fase 8: Polish (2026-05-31) - ✅ FULL COMPLETE
  - README.md rewritten - multi-provider architecture documented
  - CLI commands reference added
  - Error handling verified (file not found, invalid provider)
  - GPU memory management documented
- [ ] Fase 8: Polish