# Reference - Original Repo

Analysis of the cloned repo: `ollama-vision-mcp`

## Origin

- **Repo**: https://github.com/xkiranj/ollama-vision-mcp
- **Clone**: `C:\code\mcp-servers\maker\ollama-vision-mcp-reference`
- **Use**: Study only, do not modify

## Main Files

| File | Description |
|---------|-----------|
| `src/server.py` | MCP server with 4 tools |
| `src/ollama_client.py` | Ollama API client |
| `src/image_handler.py` | Image processing |
| `src/config.py` | Configuration |

## What we learned

### 1. MCP SDK
- Uses `mcp.server.stdio` for stdio communication
- `types.Tool` to define tools
- `Server` base class

### 2. Ollama API
- Endpoint: `POST /api/generate`
- Body: `{"model": "...", "prompt": "...", "images": [base64], "stream": false}`
- Response: `{"response": "..."}`

### 3. Image Handling
- Supports: local path, URL, base64
- Validates type (jpg, png, etc)
- 20MB limit
- Converts RGBA → RGB

### 4. Prompts
- See `docs/PROMPTS.md`

## Differences from Omni-Vision

1. **Provider**: Local Ollama vs Multi-provider (OpenRouter, OpenAI, Ollama, LM Studio, MiniMax)
2. **Auth**: No auth vs Bearer token (cloud)
3. **API format**: `/api/generate` vs `/api/v1/chat/completions`
4. **Image format**: `images: [base64]` vs `content: [{type: 'image_url'}]`
5. **Default model**: `llava-phi3` (reference) vs `qwen3-vl:4b` (ours)

## Relevant Extracted Code

### Ollama Request Format
```python
payload = {
    "model": model,
    "prompt": prompt,
    "images": [image_data],  # base64 string
    "stream": False
}
```

### OpenRouter Request Format
```python
payload = {
    "model": "anthropic/claude-sonnet-4.6",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64}"}}
        ]
    }]
}
```
