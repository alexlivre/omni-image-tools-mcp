# Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install

```bash
pip install omni-image-tools-mcp
```

Requires Python 3.10+. For development, use [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/alexlivre/omni-image-tools-mcp
cd omni-image-tools-mcp
uv sync
uv sync --extra dev
```

### 2. Pick a provider

**Local (Ollama):**
```bash
# Make sure Ollama is running and the model is pulled
ollama serve
ollama pull qwen3-vl:2b
```

**Cloud (MiniMax):**
```bash
export OMNI_VISION_PROVIDER=minimax
export MINIMAX_API_KEY=your-key
```

See the [README](./README.md) for all providers (Ollama, OpenAI, OpenRouter, LM Studio, MiniMax).

### 3. Configure your MCP client

The `omni-image-tools` console script starts the server over stdio. Point your client at it:

```json
{
  "mcp": {
    "omni-image-tools": {
      "type": "local",
      "command": ["omni-image-tools"],
      "environment": {
        "OMNI_VISION_PROVIDER": "ollama",
        "OMNI_VISION_DEFAULT_MODEL": "qwen3-vl:2b"
      },
      "enabled": true
    }
  }
}
```

For **opencode**, add that block to `~/.config/opencode/opencode.json`. For Claude Desktop, use `%APPDATA%\Claude\claude_desktop_config.json` with the `mcpServers` key.

### 4. Restart your client

Close and reopen your MCP client to load the new server.

### 5. Test it!

- "Describe the image at C:/path/to/your/image.jpg"
- "What objects are in this image: C:/path/to/photo.png"
- "Read the text from C:/path/to/document.png"

## ✅ Success Indicators

You'll know it's working when:
1. The vision tools (`analyze_image`, `identify_objects`, `read_text`) appear in your client
2. `get_provider_info` shows the active provider
3. The AI can analyze your images

## 🔧 Troubleshooting

**"Provider not found"**
```bash
# Set the provider
export OMNI_VISION_PROVIDER=ollama
```

**"API key required"**
```bash
# Cloud providers need a key
export OMNI_VISION_API_KEY=your-key
```

**"Cannot connect to Ollama"**
```bash
# Make sure Ollama is running
ollama serve
```

**"Request timed out"**
```bash
# First use loads the model into GPU; increase the timeout if needed
export OMNI_VISION_TIMEOUT=180
```
