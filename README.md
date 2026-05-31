# Omni-Image-Tools MCP

MCP (Model Context Protocol) server com ferramentas de imagem (visão + processamento) que dá capacidade visual a modelos de IA. Suporta múltiplos provedores: **OpenRouter**, **OpenAI**, **Ollama** e **LM Studio**.

## Funcionalidades

### Ferramentas de Visão
- `analyze_image` - Análise customizável com prompt
- `describe_image` - Descrição detalhada do conteúdo
- `identify_objects` - Identificar e localizar objetos
- `read_text` - Extrair texto de imagens (OCR)
- `compare_images` - Comparar duas imagens

### Ferramentas de Processamento
- `prepare_image` - Preparar imagem (resize, otimizar)
- `get_image_info` - Metadata e EXIF
- `crop_image` - Cortar região específica
- `convert_image_format` - Converter entre formatos

### Provedores Suportados

| Provedor | Tipo | API Key |
|----------|------|---------|
| Ollama | Local | Não |
| LM Studio | Local | Não |
| OpenRouter | Cloud | Sim |
| OpenAI | Cloud | Sim |

## Quick Start

### 1. Configurar Provider

```bash
# .env
OMNI_VISION_PROVIDER=ollama          # ou openrouter, openai, lmstudio
OMNI_VISION_API_KEY=your-api-key     # necessário para cloud
OMNI_VISION_DEFAULT_MODEL=qwen3-vl:4b
```

### 2. Testar via CLI

```bash
# Listar tools
python scripts/cli.py tools list

# Descrever imagem
python scripts/cli.py describe --image foto.jpg

# Analisar com prompt customizado
python scripts/cli.py analyze --image foto.jpg --prompt "O que há nesta imagem?"

# Comparar duas imagens
python scripts/cli.py compare --image1 a.jpg --image2 b.jpg

# Benchmarks entre providers
python scripts/cli.py benchmark --image foto.jpg --providers ollama,lmstudio
```

## Instalação

```bash
# Clone
git clone https://github.com/alexlivre/omni-image-tools-mcp
cd omni-image-tools-mcp

# Crie venv
python -m venv venv
.\venv\Scripts\activate

# Instale
pip install -e .
```

## Configuração

| Variável | Obrigatório | Default | Descrição |
|----------|-------------|---------|-----------|
| `OMNI_VISION_PROVIDER` | Sim | - | `ollama`, `openrouter`, `openai`, `lmstudio` |
| `OMNI_VISION_API_KEY` | Cloud* | - | API key (*exceto local) |
| `OMNI_VISION_DEFAULT_MODEL` | Não | varies | Modelo default por provider |
| `OMNI_VISION_TIMEOUT` | Não | `120` | Timeout em segundos |

### Modelos Recomendados

**OpenRouter:**
- `qwen/qwen3-vl-32b-instruct` - Bom custo-benefício
- `google/gemini-2.5-flash` - Rápido e barato

**OpenAI:**
- `gpt-5.4-mini` - Rápido e inteligente

**Ollama/LM Studio:**
- `qwen3-vl:4b` - 3.3GB, boa performance
- `qwen3-vl:2b` - 1.9GB, para machines fracas

## Integração MCP

### Claude Desktop

```json
{
  "mcpServers": {
    "omni-image-tools": {
      "command": "python",
      "args": ["-m", "src.server"],
      "env": {
        "OMNI_VISION_PROVIDER": "openrouter",
        "OMNI_VISION_API_KEY": "sk-or-..."
      }
    }
  }
}
```

### Cursor IDE

```json
{
  "mcp.servers": {
    "omni-image-tools": {
      "command": "python",
      "args": ["-m", "src.server"]
    }
  }
}
```

## GPU Memory Management

O servidor monitora automaticamente modelos carregados em **Ollama** e **LM Studio** para evitar estouro de memória em GPUs residenciais.

```bash
# Verificar status
python scripts/cli.py gpu-status

# Descarregar modelo específico
python scripts/cli.py gpu-status --unload-ollama qwen3-vl:4b
python scripts/cli.py gpu-status --unload-lmstudio qwen/qwen3-vl-4b
```

## Troubleshooting

**Erro: "Provider não encontrado"**
- Verifique `OMNI_VISION_PROVIDER` está setado

**Erro: "API Key requerida"**
- Cloud providers precisam de API key no `.env`

**Timeout**
- Aumente `OMNI_VISION_TIMEOUT`

**OOM (Out of Memory)**
- Use `gpu-status` para verificar modelos carregados
- Descarregue modelos não utilizados

## License

MIT
