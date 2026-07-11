# Omni-Image-Tools MCP

MCP (Model Context Protocol) com ferramentas de imagem (visão + processamento) para dar capacidade visual a modelos de IA. Suporta múltiplos provedores: OpenRouter, OpenAI, Ollama e LM Studio.

**Baseado em**: https://github.com/xkiranj/ollama-vision-mcp

---

## Conceito

Este projeto permite que modelos de IA sem capacidade visual "enxerguem" através de um MCP server que traduz imagens em descrições textuais. Oferece:
- **Ferramentas de Visão**: analyze, describe, identify, read_text, compare
- **Ferramentas de Processamento**: prepare, info, crop, convert
- **Multi-Provider**: OpenRouter, OpenAI, Ollama, LM Studio

---

## Ferramentas (Tools)

## Regra de Pré-processamento Automático de Imagens

Toda imagem recebida por uma vision tool passa por um pipeline fixo **antes** de qualquer análise ou envio ao modelo. **Não é opt-out.**

- Redimensiona (Lanczos) mantendo proporção: lado maior máx = 1536 px; imagens com lado < 768 px ficam no tamanho original.
- Converte para RGB, salva como JPEG q90 progressivo otimizado.
- Meta: 300 KB–1 MB.
- Cache em tempdir por SHA-256.
- Para `extract_object`, o crop final usa a imagem **original** (não a pré-processada).

Detalhes: ver `docs/PROCESSING.md`.

### MVP (v1)

| Tool | Descrição | Parâmetros |
|------|-----------|-----------|
| `analyze_image` | Análise personalizável de imagem | `image_path`, `prompt`, `model`, `detail_level` |
| `identify_objects` | Lista objetos identificáveis | `image_path`, `include_count`, `include_location`, `categories`, `min_confidence` |
| `read_text` | Extrai texto visível (OCR) | `image_path`, `preserve_formatting`, `language_hint` |

### v2 - Visão

| Tool | Descrição | Parâmetros |
|------|-----------|-----------|
| `compare_images` | Comparar duas imagens | `image_path_1`, `image_path_2`, `comparison_type` |

### v2 - Processamento

| Tool | Descrição | Parâmetros |
|------|-----------|-----------|
| `prepare_image` | Preparar imagem para API (resize, compress) | `image_path`, `max_width`, `max_height`, `format`, `quality` |
| `get_image_info` | Extrair metadata e EXIF | `image_path`, `include_exif` |
| `crop_image` | Cortar região específica | `image_path`, `x`, `y`, `width`, `height` |
| `convert_image_format` | Converter entre formatos | `image_path`, `output_format`, `quality` |

**Detalhes**: See [docs/PROMPTS.md](docs/PROMPTS.md) e [docs/PROCESSING.md](docs/PROCESSING.md)

---

## Provedores Suportados

| Provedor | API Key | URL Base | Tipo |
|----------|---------|----------|------|
| OpenRouter | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1/chat/completions` | Cloud |
| OpenAI | `OPENAI_API_KEY` | `https://api.openai.com/v1/chat/completions` | Cloud |
| Ollama | None | `http://localhost:11434/api/generate` | Local |
| LM Studio | None | `http://localhost:1234/api/generate` | Local |

### Modelos Recomendados (OpenRouter)

| Modelo | Custo | Velocidade |
|--------|-------|------------|
| `google/gemini-2.5-flash` | baixo | rápida |
| `openai/gpt-4o-mini` | baixo | rápida |
| `anthropic/claude-sonnet-4.6` | médio | média |
| `anthropic/claude-opus-4.7` | alto | altíssima |

### Modelos Recomendados (Ollama)

| Modelo | Tamanho | Context | Notes |
|--------|---------|---------|-------|
| `qwen3-vl:4b` | 3.3GB | 256K | ✅ **Default**, Visual Agent, spatial understanding |
| `qwen3-vl:2b` | 1.9GB | 256K | Leve, bom para machines fracas |
| `qwen3-vl:8b` | 6.1GB | 256K | Mais capaz, requer mais RAM |
| `moondream` | ~1GB | 4K | Muito leve, básico |
| `llava` | ~7GB | 4K | Clássico, boa compatibilidade |

> **Req**: Ollama 0.12.7+ para Qwen3-VL

### Modelos Suportados (Ollama)

**Allowlist de modelos seguros:**

| Modelo | Tamanho | Notas |
|--------|---------|-------|
| `qwen3-vl:4b` | 3.3GB | ✅ **Default** |
| `qwen3-vl:2b` | 1.9GB | Leve |

> Modelos adicionais podem ser ativados via env `OLLAMA_ALLOWED_MODELS`, mas não fazem parte do contrato padrão do projeto.

### Config Ollama

| Variável | Default | Descrição |
|----------|---------|-----------|
| `OLLAMA_ALLOWED_MODELS` | lista acima | Modelos permitidos |
| `OLLAMA_AUTO_PULL` | `false` | Auto-download (desligado por segurança) |

**Comportamento:**
- Se `OLLAMA_ALLOWED_MODELS` não definido → usa lista padrão
- Se definido → usa lista do usuário
- Se modelo fora da lista → erro claro
- `OLLAMA_AUTO_PULL: false` por segurança (não baixa GBs sem querer)

---

## Configuração

A configuração vem da **host app** (a aplicação que está usando o MCP) via env vars:

| Aplicação | Arquivo de Config |
|-----------|-------------------|
| OpenCode | `opencode.json` |
| Claude Desktop | `claude_desktop_config.json` |
| Qwen Code | `settings.json` |
| Cursor IDE | `settings.json` |

```json
"omni-image-tools": {
  "command": ["python", "-m", "src.server"],
  "env": {
    "OMNI_VISION_API_KEY": "sk-or-xxx",
    "OMNI_VISION_PROVIDER": "openrouter",
    "OMNI_VISION_DEFAULT_MODEL": "google/gemini-2.5-flash"
  }
}
```

### Environment Variables

| Variável | Obrigatório | Default | Descrição |
|----------|-------------|---------|-----------|
| `OMNI_VISION_API_KEY` | Sim* | - | API key (*exceto local) |
| `OMNI_VISION_PROVIDER` | Sim | - | `openrouter`, `openai`, `ollama`, `lmstudio` |
| `OMNI_VISION_DEFAULT_MODEL` | Não | `qwen3-vl:4b` (ollama), `google/gemini-2.5-flash` (openrouter) | Modelo default |
| `OMNI_VISION_TIMEOUT` | Não | `120` | Timeout em segundos |
| `OLLAMA_BASE_URL` | Não | `http://localhost:11434` | URL do Ollama |
| `OLLAMA_ALLOWED_MODELS` | Não | (lista padrão) | Modelos permitidos |
| `OLLAMA_AUTO_PULL` | Não | `false` | Auto-download modelos |
| `LMSTUDIO_BASE_URL` | Não | `http://localhost:1234` | URL do LM Studio |

### Escolha do Provedor e Modelo

**Global**: Configurado via env vars na host app (provider + default model).

**Per-Call Override**: Usuário pode sobrescrever o modelo por chamada:
```
analyze_image(image_path="...", model="anthropic/claude-opus-4.7")
```

**Validação Estrita**: Modelo incompatível com provider = erro claro.

---

## Setup

### Requirements

| Requisito | Versão | Notas |
|-----------|--------|-------|
| Python | **3.11+** | MCP SDK não suporta 3.14 ainda |
| Ollama | 0.12.7+ | Para Qwen3-VL |
| Git | Any | Para clone |

### Dependencies

```
# Core
mcp>=1.0.0
httpx
pillow>=10.0.0
pydantic>=2.0.0
pyyaml

# Optional (para processing)
ExifRead>=3.0.0
pillow-heif>=0.12.0
```

### Instalação

```bash
# Clone/fork do repo
git clone https://github.com/xkiranj/ollama-vision-mcp omni-image-tools-mcp
cd omni-image-tools-mcp

# Setup venv (Python 3.11)
python -m venv venv
.\venv\Scripts\Activate

# Instalar dependências
pip install -e .
```

---

## Estrutura do Projeto

```
omni-image-tools-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP server + tool registry
│   ├── config.py              # Lê env vars
│   ├── image_handler.py       # Processamento de imagem
│   │
│   ├── providers/             # FACTORY PATTERN
│   │   ├── __init__.py       # ProviderFactory.get()
│   │   ├── base.py           # VisionProvider (ABC)
│   │   ├── openrouter.py
│   │   ├── openai.py
│   │   ├── ollama.py         # Com detecção dinâmica de modelos
│   │   └── lmstudio.py
│   │
│   ├── tools/                # REGISTRY PATTERN
│   │   ├── __init__.py       # ToolRegistry
│   │   ├── vision/
│   │   │   ├── analyze.py
│   │   │   ├── describe.py
│   │   │   ├── identify.py
│   │   │   ├── read_text.py
│   │   │   └── compare.py    # v2
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
├── tests/
│   └── fixtures/              # Imagens para teste
│       ├── simple.jpg
│       ├── complex.jpg
│       ├── text_sample.png
│       └── ...
│
├── docs/
│   ├── PROMPTS.md
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE_DECISION.md
│   ├── PROCESSING.md
│   └── REFERENCE.md
│
├── tasks/
│   └── TODO.md
│
├── pyproject.toml
├── requirements.txt
└── README.md
```

**Detalhes**: See [docs/ARCHITECTURE_DECISION.md](docs/ARCHITECTURE_DECISION.md)

**Detalhes da arquitetura**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Testing Durante Desenvolvimento

Testar cada tool **isoladamente** via CLI, **antes** de integrar com host app.

### CLI Commands

```bash
# Vision tools
python scripts/cli.py analyze --image foto.jpg --provider ollama --model qwen3-vl:4b
python scripts/cli.py describe --image foto.jpg --provider openrouter
python scripts/cli.py identify --image foto.jpg
python scripts/cli.py read-text --image screenshot.png

# Processing tools
python scripts/cli.py info --image foto.jpg
python scripts/cli.py prepare --image foto.jpg --max-size 512

# Benchmark
python scripts/cli.py benchmark --image foto.jpg --providers ollama,openrouter
```

### Imagens de Teste (fixtures)

| Imagem | Uso |
|--------|-----|
| `simple.jpg` | Objeto único |
| `complex.jpg` | Múltiplos objetos |
| `text_sample.png` | OCR |
| `multilanguage.jpg` | Texto multilíngue |

### Tool Design Standards

Tools seguem padrões eficientes para comunicação AI-MCP:

- **Descriptions**: Template com "Use when", Input/Output, Examples
- **Schemas**: Types rigorosos, enums, defaults, examples
- **Responses**: Formato consistente com status, error_code, metadata
- **Errors**: Códigos claros + retryable flag + help messages

**Detalhes**: See [docs/ARCHITECTURE_DECISION.md](docs/ARCHITECTURE_DECISION.md)

---

## Links

- **Spec detalhada**: Este documento
- **Prompts**: [docs/PROMPTS.md](docs/PROMPTS.md)
- **Processamento**: [docs/PROCESSING.md](docs/PROCESSING.md)
- **Arquitetura**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Decisões**: [docs/ARCHITECTURE_DECISION.md](docs/ARCHITECTURE_DECISION.md)
- **Estudo original**: [docs/REFERENCE.md](docs/REFERENCE.md)
- **Progresso**: [tasks/TODO.md](tasks/TODO.md)
- **Plano de Implementação**: [tasks/IMPLEMENTATION_PLAN.md](tasks/IMPLEMENTATION_PLAN.md)

---

## Status

:white_check_mark: Estudo completo
:hourglass: Aguardando fork e implementação