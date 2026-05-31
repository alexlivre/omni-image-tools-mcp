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
- [ ] Forkar o repo de referência
- [ ] Criar estrutura de diretórios
- [ ] Implementar error classes
- [ ] Implementar config parsing
- [ ] Criar fixtures de teste

### Fase 3: Foundation (Fase 2 do Plano)
- [ ] Implementar VisionProvider ABC (providers/base.py)
- [ ] Implementar ProviderFactory (providers/__init__.py)
- [ ] Implementar ToolRegistry (tools/__init__.py)
- [ ] Definir schemas para todas tools
- [ ] Criar prompts/vision.yaml e prompts/processing.yaml
- [ ] CLI com commands (help, providers list, tools list)

### Fase 4: Ollama Provider (Fase 3 do Plano)
- [ ] Implementar OllamaProvider (providers/ollama.py)
- [ ] Teste via CLI
- [ ] Adicionar --debug mode

### Fase 5: Vision MVP (Fase 4 do Plano)
- [ ] Implementar analyze_image
- [ ] Implementar describe_image
- [ ] Implementar identify_objects
- [ ] Implementar read_text

### Fase 6: Vision v2 (Fase 5 do Plano)
- [ ] Implementar compare_images

### Fase 7: Processing (Fase 6 do Plano)
- [ ] Implementar prepare_image
- [ ] Implementar get_image_info
- [ ] Implementar crop_image
- [ ] Implementar convert_image_format

### Fase 8: Cloud Providers (Fase 7 do Plano)
- [ ] Implementar OpenRouterProvider
- [ ] Implementar OpenAIProvider
- [ ] Implementar LMStudioProvider

### Fase 9: Polish (Fase 8 do Plano)
- [ ] README.md
- [ ] Teste final (benchmark)
- [ ] Atualizar docs

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

- [ ] Adicionar cache de resultados?
- [ ] Rate limiting por modelo?
- [ ] Fallback automático entre modelos?
- [ ] Internationalização dos prompts?

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