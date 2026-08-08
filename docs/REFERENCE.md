# Reference - Repo Original

Análise do repo clonado: `ollama-vision-mcp`

## Origem

- **Repo**: https://github.com/xkiranj/ollama-vision-mcp
- **Clone**: `C:\code\mcp-servers\maker\ollama-vision-mcp-reference`
- **Uso**: Somente estudo, não modificar

## Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| `src/server.py` | MCP server com 4 tools |
| `src/ollama_client.py` | Cliente Ollama API |
| `src/image_handler.py` | Processamento de imagem |
| `src/config.py` | Configuração |

## O que aprendemos

### 1. MCP SDK
- Usa `mcp.server.stdio` para comunicação stdio
- `types.Tool` para definir tools
- `Server` class base

### 2. API Ollama
- Endpoint: `POST /api/generate`
- Body: `{"model": "...", "prompt": "...", "images": [base64], "stream": false}`
- Response: `{"response": "..."}`

### 3. Image Handling
- Suporta: path local, URL, base64
- Valida tipo (jpg, png, etc)
- Limite 20MB
- Converte RGBA → RGB

### 4. Prompts
- See `docs/PROMPTS.md`

## Diferenças para Omni-Vision

1. **Provedor**: Ollama local vs Multi-provider (OpenRouter, OpenAI, Ollama, LM Studio, MiniMax)
2. **Auth**: Sem auth vs Bearer token (cloud)
3. **API format**: `/api/generate` vs `/api/v1/chat/completions`
4. **Image format**: `images: [base64]` vs `content: [{type: 'image_url'}]`
5. **Modelo default**: `llava-phi3` (reference) vs `qwen3-vl:4b` (nosso)

## Código Relevante Extraído

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