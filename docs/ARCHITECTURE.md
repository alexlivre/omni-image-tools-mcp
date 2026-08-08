# Architecture

Code structure and architectural decisions.

## Project Structure

```
omni-image-tools-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py           # MCP server (entry point)
│   ├── config.py           # Reads env vars (API_KEY, MODEL, PROVIDER, etc)
│   ├── image_handler.py    # Image processing
│   └── providers/
│       ├── __init__.py    # Factory: returns provider based on config
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

## Components

### `server.py`
- MCP server using `mcp.server.stdio`
- Registers the tools: `analyze_image`, `identify_objects`, `read_text`
- Orchestrates: image_handler → providers

### `config.py`
- Reads configuration from **env vars** (not from a JSON file)
- Provides defaults
- Validates required variables

### `image_handler.py`
- Processes images from multiple sources (local path, URL, base64)
- Validates type and size
- Converts to base64

### `providers/`
- **Factory pattern**: `providers/__init__.py` returns the correct provider based on `PROVIDER`
- Each provider in its own file
- Common interface: `analyze_image(image_data, prompt, model)`

## Providers

| Provider | Auth | URL |
|----------|------|-----|
| OpenRouter | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1/chat/completions` |
| OpenAI | `OPENAI_API_KEY` | `https://api.openai.com/v1/chat/completions` |
| Ollama | None (local) | `http://localhost:11434/api/generate` |
| LM Studio | None (local) | `http://localhost:1234/api/generate` |

## Configuration via Env Vars

Configuration comes from the **host app** (the application using the MCP). The config file name varies by application:

| Application | Config File |
|-----------|-------------------|
| OpenCode | `opencode.json` |
| Claude Desktop | `claude_desktop_config.json` |
| Qwen Code | `settings.json` |
| Cursor IDE | `settings.json` |
| Windsurf | `.windsurf/config.json` |

**The MCP does not know which app is using it.** It only receives env vars. Configuration is done by the host app.

### Generic Example

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

### Common Structure

Most host apps use a similar structure:
- `command`: how to run the MCP
- `args`: command arguments
- `env`: environment variables passed to the MCP
- `enabled`: whether it's enabled

### Environment Variables

| Variable | Required | Default | Description |
|----------|-------------|---------|-----------|
| `OMNI_VISION_API_KEY` | Yes* | - | Provider API key (*except local) |
| `OMNI_VISION_PROVIDER` | Yes | - | `openrouter`, `openai`, `ollama`, `lmstudio` |
| `OMNI_VISION_DEFAULT_MODEL` | No | varies | Default model |
| `OMNI_VISION_TIMEOUT` | No | `120` | Timeout in seconds |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama URL (local) |
| `LMSTUDIO_BASE_URL` | No | `http://localhost:1234` | LM Studio URL (local) |

### Provider and Model Selection

**Level 1 - Global (env vars):**
Configured once in the host app. Defines the default provider and default model.

**Level 2 - Per-Call Override:**
The user can override the model per call:
```
analyze_image(image_path="...", model="anthropic/claude-opus-4.7")
```

**Strict Validation:**
If the model is not compatible with the provider → clear error:
```
"Model claude-opus-4.7 requires provider=openrouter, but provider=ollama is configured"
```

## Data Flow

```
Tool Call → server.py
  → config.py (reads env vars)
  → providers/__init__.py (factory)
  → providers/openrouter.py (example)
      → image_handler.process_image(image_path) → base64
      → HTTP POST → OpenRouter API
 → TextContent response
```

## Decisions

1. **Separate providers**: Each provider in its own file, isolated for easy maintenance and testing

2. **Factory pattern**: `server.py` doesn't know which provider it's using — it just calls `get_provider()` and uses the common interface

3. **Config via env vars**: No config file in the MCP — everything comes from the host app via env vars

4. **Reused image handler**: The same one from ollama-vision-mcp, works well for all providers

5. **STDIO transport**: Uses the MCP standard stdio for communication
