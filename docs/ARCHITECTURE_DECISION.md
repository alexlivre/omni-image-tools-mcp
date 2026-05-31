# ADR-001: Arquitetura Extensível para Omni-Vision-MCP

**Data**: 2026-05-31
**Status**: Aprovado
**Decisores**: Alex

---

## Contexto

Estamos criando o `omni-image-tools-mcp`, um MCP de visão que suporta múltiplos provedores (OpenRouter, OpenAI, Ollama, LM Studio) e múltiplas ferramentas (visão + processamento).

Analisamos o repo de referência (`ollama-vision-mcp`) e concluímos que:
- Código é simples e funcional (~500 linhas)
- Estrutura atual não suporta extensão fácil
- Adicionar novo provider ou tool = refatoração significativa

### Problema

Se investirmos apenas na refatoração mínima, acumularemos tech debt:
- Novas tools = editar `server.py`
- Novos providers = refatorar cliente
- Prompts hardcoded = procurar no código para modificar

### Trade-offs considered

| Opção | Trabalho Inicial | Facilidade Futura | Risco |
|-------|-----------------|-------------------|-------|
| Fork + refatoração mínima | Baixo | Média | Tech debt |
| Fork + arquitetura extensível | Médio (~2x) | Alta | Over-engineering? |
| Começar do zero | Alto | Alta | Perde boilerplate |

---

## Decisão

**Fazer fork + arquitetura extensível.**

### Rationale

1. Investimento único de ~2x tempo inicial
2. ROI positivo já na segunda ou terceira feature
3. Arquitetura suporta multi-provider + multi-tool desde o início
4. Prompts separados = designers/PMs podem editar sem mexer código
5. Não é over-engineering — é arquitetura apropriada para:
   - 4 provedores diferentes
   - 8+ tools (visão + processamento)
   - Manutenção a longo prazo

---

## Arquitetura Proposta

```
omni-image-tools-mcp/
├── src/
│   ├── server.py              # MCP setup + tool registry
│   ├── config.py              # Env vars + config file
│   ├── image_handler.py       # Mantém do original
│   │
│   ├── providers/              # FACTORY PATTERN
│   │   ├── __init__.py        # ProviderFactory.get()
│   │   ├── base.py            # VisionProvider (ABC)
│   │   ├── openrouter.py
│   │   ├── openai.py
│   │   ├── ollama.py          # Migrate do original
│   │   └── lmstudio.py
│   │
│   ├── tools/                 # REGISTRY PATTERN
│   │   ├── __init__.py        # ToolRegistry
│   │   ├── vision/
│   │   │   ├── analyze.py
│   │   │   ├── describe.py
│   │   │   ├── identify.py
│   │   │   └── read_text.py
│   │   └── processing/
│   │       ├── prepare.py
│   │       ├── info.py
│   │       └── crop.py
│   │
│   └── prompts/
│       ├── vision.yaml
│       └── processing.yaml
```

---

## Componentes

### 1. Provider Factory

```python
# providers/__init__.py
class ProviderFactory:
    @staticmethod
    def get(provider: str, config: Config) -> VisionProvider:
        providers = {
            "openrouter": OpenRouterProvider,
            "openai": OpenAIProvider,
            "ollama": OllamaProvider,
            "lmstudio": LMStudioProvider,
        }
        return providers[provider](config)
```

```python
# providers/base.py
from abc import ABC, abstractmethod

class VisionProvider(ABC):
    @abstractmethod
    async def analyze(self, image_data: str, prompt: str, model: str) -> str:
        pass
```

**Benefício**: Adicionar novo provider = criar 1 arquivo + adicionar ao dict.

### 2. Tool Registry

```python
# tools/__init__.py
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())
```

```python
# tools/vision/analyze.py
class AnalyzeTool:
    name = "analyze_image"
    description = "Analyze an image..."
    input_schema = {...}

    async def execute(self, image_data: str, prompt: str, model: str) -> str:
        # Logic here
```

**Benefício**: Adicionar nova tool = criar 1 arquivo + chamar `.register()`.

### 3. Prompts Separados

```yaml
# prompts/vision.yaml
analyze:
  default: "Describe this image in detail"
  detailed: "Provide a comprehensive description..."
  objects: "List all identifiable objects..."
  text: "Extract and transcribe all visible text..."

describe:
  comprehensive: "Provide a comprehensive description..."
  brief: "Give a brief summary..."
```

**Benefício**: Editar prompts = editar YAML, não código.

---

## Como Adicionar Features

### Nova Tool de Visão

1. Criar `src/tools/vision/minha_tool.py`
2. Definir classe com `name`, `description`, `input_schema`, `execute()`
3. Importar e registrar no `tools/__init__.py`

```python
# src/tools/vision/minha_tool.py
class MinhaTool:
    name = "minha_tool"
    description = "..."
    input_schema = {...}

    async def execute(self, **kwargs) -> str:
        ...
```

```python
# src/tools/__init__.py
from .vision.minha_tool import MinhaTool
registry.register(MinhaTool())
```

### Novo Provider

1. Criar `src/providers/meu_provider.py`
2. Herdar de `VisionProvider`
3. Implementar `analyze()`
4. Adicionar ao dict em `providers/__init__.py`

```python
# src/providers/meu_provider.py
class MeuProvider(VisionProvider):
    def __init__(self, config):
        self.config = config

    async def analyze(self, image_data: str, prompt: str, model: str) -> str:
        # API call logic
```

```python
# src/providers/__init__.py
providers["meu_provider"] = MeuProvider
```

### Modificar Prompt

Editar `src/prompts/vision.yaml` — não precisa mexer código.

---

## Detecção Dinâmica de Modelos Ollama

Implementar no provider Ollama:

```python
class OllamaProvider(VisionProvider):
    async def list_models(self) -> List[str]:
        """Lista modelos instalados no Ollama"""
        response = await self.client.get("/api/tags")
        return [m["name"] for m in response.get("models", [])]

    async def is_vision_model(self, model: str) -> bool:
        """Testa se modelo suporta imagem"""
        # Tentar chamada simples com image
        pass

    async def ensure_model(self, model: str) -> bool:
        """Garante que modelo está disponível (auto-pull)"""
        available = await self.list_models()
        if model not in available:
            await self.pull_model(model)
        return True
```

Config:
```json
{
  "default_model": "qwen3-vl:4b",
  "allowed_models": ["qwen3-vl:4b", "qwen3-vl:2b", "moondream", "llava"],
  "auto_pull": false
}
```

**Allowlist:** Em vez de auto-detecção, usamos lista curated de modelos seguros para evitar downloads acidentais de modelos grandes.

---

## Migração do Repo Original

### Passo 1: Fork
```bash
git clone https://github.com/xkiranj/ollama-vision-mcp omni-image-tools-mcp
cd omni-image-tools-mcp
git remote rename origin upstream
```

### Passo 2: Criar estrutura
```bash
mkdir -p src/providers
mkdir -p src/tools/vision
mkdir -p src/tools/processing
mkdir -p src/prompts
mkdir -p src/utils
```

### Passo 3: Migrar código
- `src/ollama_client.py` → `src/providers/ollama.py`
- `src/config.py` → refatorar para multi-provider
- Prompts → `src/prompts/vision.yaml`

### Passo 4: Implementar factory + registry

### Passo 5: Criar providers placeholder (openrouter, openai, lmstudio)

### Passo 6: Migrar/adicionar tools

---

## Testing Durante Desenvolvimento

### Princípio

Testar cada tool **isoladamente** durante dev, **antes** de integrar com host app. Garantir que tudo funcione sem precisar configurar o MCP na aplicação.

### Estrutura

```
omni-image-tools-mcp/
├── scripts/
│   └── cli.py               # CLI unificada para testes
├── tests/
│   └── fixtures/
│       ├── simple.jpg       # Objeto único
│       ├── complex.jpg      # Múltiplos objetos
│       ├── text_sample.png  # Screenshot/documento
│       ├── multilanguage.jpg
│       └── big_photo.heic   # Stress test (iPhone)
└── src/
```

### CLI Commands

```bash
# Tools de visão
python scripts/cli.py analyze --image foto.jpg --provider ollama --model qwen3-vl:4b
python scripts/cli.py describe --image foto.jpg --provider openrouter
python scripts/cli.py identify --image foto.jpg
python scripts/cli.py read-text --image screenshot.png
python scripts/cli.py compare --image1 a.jpg --image2 b.jpg

# Tools de processamento
python scripts/cli.py info --image foto.jpg
python scripts/cli.py prepare --image foto.jpg --max-size 512
python scripts/cli.py crop --image foto.jpg --x 100 --y 100 --w 200 --h 200
python scripts/cli.py convert --image foto.jpg --format WEBP

# Benchmark todos providers
python scripts/cli.py benchmark --image foto.jpg --providers ollama,openrouter,openai

# Shell interativo
python scripts/cli.py shell --provider ollama
```

### Imagens de Teste (fixtures)

| Imagem | Uso | Descrição |
|--------|-----|-----------|
| `simple.jpg` | Teste básico | Objeto único em fundo simples |
| `complex.jpg` | Múltiplos objetos | Cena com vários elementos |
| `text_sample.png` | OCR | Screenshot ou documento com texto |
| `multilanguage.jpg` | OCR multilíngue | Texto em PT/EN/ES |
| `small.jpg` | Thumbnails | Imagem pequena para stress test |
| `big_photo.heic` | iPhone | Foto em formato HEIC |

### Benefícios do CLI Testing

| Aspecto | Benefício |
|---------|-----------|
| **Velocidade** | Testa tool sem subir MCP server |
| **Debug** | Print direto no output, fácil ver erros |
| **Provider** | Testa cada provider isolado |
| **Documentação** | CLI = documentação de uso |
| **CI/CD** | Scripts podem rodar em automated tests |

### Implementação CLI

```python
# scripts/cli.py
import argparse
import asyncio
from src.providers import ProviderFactory
from src.image_handler import ImageHandler

async def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # analyze command
    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("--image", required=True)
    analyze.add_argument("--provider", default="ollama")
    analyze.add_argument("--model")
    analyze.set_defaults(func=cmd_analyze)

    # ... other commands

    args = parser.parse_args()
    await args.func(args)

async def cmd_analyze(args):
    provider = ProviderFactory.get(args.provider, config)
    image_data = await ImageHandler().process_image(args.image)
    result = await provider.analyze(image_data, "Describe this image", args.model)
    print(result)
```

---

## Tool Efficiency Standards

O MCP deve ser muito eficiente na comunicação tool/schema. AI deve entender rapidamente:
- O que cada tool faz
- Quando usar cada tool
- Como passar parâmetros corretamente
- Como interpretar responses

### 1. Tool Description Template

```
[name]: [one-line summary]

Use when: [when to use this tool]
Input: [required params]
Output: [what returns]

Examples:
  [example1]
  [example2]
```

**Exemplo:**
```python
description="""analyze_image: Analyze image and get description.

Use when: You need to understand what's in an image, identify objects, or extract visual information.
Input: image_path (required) - local path or URL
Output: Text description of image content

Examples:
  analyze_image(image_path="/tmp/photo.jpg")
  analyze_image(image_path="https://example.com/img.png", detail_level="brief")"""
```

### 2. Input Schema Standards

Every tool MUST have:
- All types specified (`string`, `integer`, `boolean`, `enum`)
- Enums for limited values (no free strings)
- Defaults for optional params
- Examples in descriptions
- Required explicitly marked

```python
input_schema = {
    "type": "object",
    "properties": {
        "image_path": {
            "type": "string",
            "description": "Path to image (local or URL)",
            "examples": ["/tmp/photo.jpg", "https://example.com/img.png"]
        },
        "detail_level": {
            "type": "string",
            "enum": ["brief", "standard", "detailed"],
            "default": "standard"
        },
        "model": {
            "type": "string",
            "description": "Model to use (default: config default)"
        }
    },
    "required": ["image_path"]
}
```

### 3. Response Format

All tools return consistent JSON structure:

```json
{
  "status": "success",
  "content": "... | null",
  "error_code": "...",
  "message": "...",
  "metadata": {
    "model_used": "qwen3-vl:4b",
    "tokens_used": 1234,
    "processing_time_ms": 1500
  }
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | `string` | `"success"` or `"error"` |
| `content` | `string\|null` | Result content on success |
| `error_code` | `string` | Machine-readable error code |
| `message` | `string` | Human-readable message |
| `metadata` | `object` | Optional additional info |

### 4. Error Codes

| Code | When | Retryable? |
|------|------|------------|
| `VALIDATION_ERROR` | Invalid params | No |
| `MODEL_NOT_ALLOWED` | Model not in allowlist | No |
| `FILE_NOT_FOUND` | Image file doesn't exist | No |
| `IMAGE_TOO_LARGE` | Image > 20MB | No |
| `UNSUPPORTED_FORMAT` | Unsupported image format | No |
| `PROVIDER_ERROR` | Provider API error | Yes |
| `TIMEOUT` | Request timed out | Yes |
| `RATE_LIMIT` | Rate limit exceeded | Yes |

### 5. Error Handling Excellence

Every error must be:
1. **Understandable** — AI and human can understand the problem
2. **Actionable** — with suggestion on how to fix
3. **Categorized** — error_code for programmatic handling
4. **Consistent** — same structure for all errors

#### Error Response Format

```json
{
  "status": "error",
  "error_code": "MODEL_NOT_ALLOWED",
  "message": "Model 'huge-100b' is not in the allowed list",
  "details": {
    "requested_model": "huge-100b",
    "allowed_models": ["qwen3-vl:4b", "moondream"]
  },
  "help": "Add 'huge-100b' to OLLAMA_ALLOWED_MODELS in your config",
  "retryable": false
}
```

#### Error Class Hierarchy

```python
class OmniVisionError(Exception):
    error_code = "INTERNAL_ERROR"
    retryable = False

    def to_dict(self) -> dict:
        return {
            "status": "error",
            "error_code": self.error_code,
            "message": str(self),
            "details": getattr(self, 'details', {}),
            "help": getattr(self, 'help', None),
            "retryable": self.retryable
        }

class ValidationError(OmniVisionError):
    error_code = "VALIDATION_ERROR"

class ModelNotAllowedError(OmniVisionError):
    error_code = "MODEL_NOT_ALLOWED"

class FileNotFoundError(OmniVisionError):
    error_code = "FILE_NOT_FOUND"

class ImageTooLargeError(OmniVisionError):
    error_code = "IMAGE_TOO_LARGE"

class UnsupportedFormatError(OmniVisionError):
    error_code = "UNSUPPORTED_FORMAT"

class ProviderError(OmniVisionError):
    error_code = "PROVIDER_ERROR"
    retryable = True

class TimeoutError(OmniVisionError):
    error_code = "TIMEOUT"
    retryable = True

class RateLimitError(OmniVisionError):
    error_code = "RATE_LIMIT"
    retryable = True
```

#### Error Code Reference

| Code | When | Retryable | Help Example |
|------|------|-----------|--------------|
| `VALIDATION_ERROR` | Invalid params | No | "Check parameter types and required fields" |
| `MODEL_NOT_ALLOWED` | Not in allowlist | No | "Add model to OLLAMA_ALLOWED_MODELS" |
| `FILE_NOT_FOUND` | File doesn't exist | No | "Verify the file path exists" |
| `IMAGE_TOO_LARGE` | > 20MB | No | "Use prepare_image to resize first" |
| `UNSUPPORTED_FORMAT` | Bad format | No | "Use JPEG, PNG, WEBP or HEIC" |
| `PROVIDER_ERROR` | API failed | Yes | "Retry in a few seconds" |
| `TIMEOUT` | Request timeout | Yes | "Retry with longer timeout" |
| `RATE_LIMIT` | Rate limited | Yes | "Wait before retrying" |

#### Usage Example

```python
try:
    result = await provider.analyze(image_data, prompt, model)
except ModelNotAllowedError as e:
    return error_response(e, help="Add model to OLLAMA_ALLOWED_MODELS")
except FileNotFoundError as e:
    return error_response(e, help="Verify image_path exists")
except ProviderError as e:
    return error_response(e, retryable=True)
```

### 6. CLI Debug Mode

```bash
python scripts/cli.py analyze --image img.jpg --debug
```

Output includes:
- Full request payload
- Full response payload
- Timing breakdown
- Model used

---

## Status

- [x] Decisão tomada
- [x] Testing strategy definida
- [x] Tool efficiency standards definidos
- [x] Error handling excellence definido
- [ ] Fork realizado
- [ ] Estrutura criada
- [ ] CLI implementada
- [ ] Provider factory implementado
- [ ] Tool registry implementado
- [ ] Providers migrados/criados
- [ ] Tools migradas/adicionadas
- [ ] Prompts separados
- [ ] Fixtures de teste criados

---

## Links

- Repo original: https://github.com/xkiranj/ollama-vision-mcp
- Spec: [SPEC.md](../SPEC.md)
- Tasks: [tasks/TODO.md](../tasks/TODO.md)
