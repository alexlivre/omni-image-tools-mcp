# Architecture

Estrutura do código e decisões arquiteturais.

## Estrutura do Projeto

```
omni-image-tools-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py           # MCP server (entry point)
│   ├── config.py           # Lê env vars (API_KEY, MODEL, PROVIDER, etc)
│   ├── image_handler.py    # Processamento de imagem
│   └── providers/
│       ├── __init__.py    # Factory: retorna provider baseado na config
│       ├── openrouter.py   # OpenRouter client
│       ├── openai.py       # OpenAI client
│       ├── ollama.py       # Ollama client
│       └── lmstudio.py     # LM Studio client
├── docs/
│   ├── PROMPTS.md
│   ├── ARCHITECTURE.md
│   └── REFERENCE.md
├── tasks/
│   └── TODO.md
├── tests/
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Componentes

### `server.py`
- MCP server usando `mcp.server.stdio`
- Registra as tools: `analyze_image`, `describe_image`, `identify_objects`, `read_text`
- Orquestra: image_handler → providers

### `config.py`
- Lê configuração de **env vars** (não de arquivo JSON)
- Fornece defaults
- Valida variáveis obrigatórias

### `image_handler.py`
- Processa imagem de várias fontes (path local, URL, base64)
- Valida tipo e tamanho
- Converte para base64

### `providers/`
- **Factory pattern**: `providers/__init__.py` retorna o provider correto baseado em `PROVIDER`
- Cada provedor em arquivo separado
- Interface comum: `analyze_image(image_data, prompt, model)`

## Providers

| Provider | Auth | URL |
|----------|------|-----|
| OpenRouter | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1/chat/completions` |
| OpenAI | `OPENAI_API_KEY` | `https://api.openai.com/v1/chat/completions` |
| Ollama | None (local) | `http://localhost:11434/api/generate` |
| LM Studio | None (local) | `http://localhost:1234/api/generate` |

## Configuração via Env Vars

A configuração vem da **host app** (a aplicação que está usando o MCP). O nome do arquivo varia conforme a aplicação:

| Aplicação | Arquivo de Config |
|-----------|-------------------|
| OpenCode | `opencode.json` |
| Claude Desktop | `claude_desktop_config.json` |
| Qwen Code | `settings.json` |
| Cursor IDE | `settings.json` |
| Windsurf | `.windsurf/config.json` |

**O MCP não sabe qual app está usando.** Ele apenas recebe env vars. A configuração é feita pela host app.

### Exemplo Genérico

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

### Estrutura Comum

A maioria das host apps usa estrutura similar:
- `command`: como executar o MCP
- `args`: argumentos do command
- `env`: variáveis de ambiente passadas ao MCP
- `enabled`: se está ativo

### Variáveis de Ambiente

| Variável | Obrigatório | Default | Descrição |
|----------|-------------|---------|-----------|
| `OMNI_VISION_API_KEY` | Sim* | - | API key do provedor (*exceto local) |
| `OMNI_VISION_PROVIDER` | Sim | - | `openrouter`, `openai`, `ollama`, `lmstudio` |
| `OMNI_VISION_DEFAULT_MODEL` | Não | varies | Modelo default |
| `OMNI_VISION_TIMEOUT` | Não | `120` | Timeout em segundos |
| `OLLAMA_BASE_URL` | Não | `http://localhost:11434` | URL do Ollama (local) |
| `LMSTUDIO_BASE_URL` | Não | `http://localhost:1234` | URL do LM Studio (local) |

### Escolha do Provedor e Modelo

**Nível 1 - Global (env vars):**
Configurado uma vez na host app. Define o provider default e modelo default.

**Nível 2 - Per-Call Override:**
Usuário pode sobrescrever o modelo por chamada:
```
analyze_image(image_path="...", model="anthropic/claude-opus-4.7")
```

**Validação Estrita:**
Se o modelo não é compatível com o provider → erro claro:
```
"Modelo claude-opus-4.7 requer provider=openrouter, mas provider=ollama está configurado"
```

## Fluxo de Dados

```
Tool Call → server.py
  → config.py (lê env vars)
  → providers/__init__.py (factory)
  → providers/openrouter.py (exemplo)
      → image_handler.process_image(image_path) → base64
      → HTTP POST → OpenRouter API
 → TextContent response
```

## Decisões

1. **Providers separados**: Cada provedor em arquivo próprio, isolado para fácil manutenção e teste

2. **Factory pattern**: `server.py` não sabe qual provedor está usando — apenas chama `get_provider()` e usa interface comum

3. **Config via env vars**: Sem arquivo de config no MCP — tudo vem da host app via env vars

4. **Image handler reutilizado**: Mesmo do ollama-vision-mcp, funciona bem para todos provedores

5. **STDIO transport**: Usa stdio standard do MCP para comunicação