# Omni-Image-Tools MCP

MCP server com ferramentas de visão e processamento de imagens para modelos de IA.
**11 ferramentas** · **3 provedores** · **GPU Memory Management**

---

## Início Rápido

```bash
# 1. Instalar
git clone https://github.com/alexlivre/omni-image-tools-mcp
cd omni-image-tools-mcp
python -m venv venv && .\venv\Scripts\activate && pip install -e .

# 2. Configurar provider
set OMNI_VISION_PROVIDER=ollama
set OMNI_VISION_DEFAULT_MODEL=qwen3-vl:2b

# 3. Usar
python scripts/cli.py analyze --image foto.jpg --prompt "O que há nesta imagem?"
python scripts/cli.py extract --image carro.jpg --object "license plate"
```

---

## Ferramentas

### 👁️ Visão (usam IA)

| Ferramenta | Descrição | Local | Online |
|------------|-----------|-------|--------|
| `analyze_image` | Análise com prompt customizado | 1 img | sem limite |
| `identify_objects` | Identificar objetos na imagem | 1 img | sem limite |
| `read_text` | OCR - extrair texto | 1 img | sem limite |
| `compare_images` | Comparar 2-10 imagens | sequencial | paralelo |

### 🛠️ Processamento (PIL)

| Ferramenta | Descrição |
|------------|-----------|
| `prepare_image` | Redimensionar e otimizar |
| `get_image_info` | Metadados (formato, dimensões, EXIF) |
| `crop_image` | Recortar por coordenadas |
| `convert_image_format` | Converter formato (JPEG/PNG/WEBP/BMP/GIF) |
| `download_image` | Baixar imagem de URL |
| `extract_object` | Localizar e recortar objeto automaticamente |

### ⚙️ Sistema

| Ferramenta | Descrição |
|------------|-----------|
| `get_provider_info` | Info do provedor e limites atuais |

---

## Provedores

| Provedor | Tipo | GPU | API Key | Modelo padrão |
|----------|------|-----|---------|---------------|
| **Ollama** | Local | Sua GPU | — | `qwen3-vl:2b` |
| **OpenRouter** | Cloud | Cloud | ✅ | `qwen/qwen3-vl-32b-instruct` |
| **OpenAI** | Cloud | Cloud | ✅ | `gpt-5.4-mini` |

**Local (Ollama):** 1 imagem/request, compare sequencial, GPU gerenciada automaticamente
**Online (OpenRouter/OpenAI):** sem limite de imagens, compare paralelo, GPU do provedor

---

## Configuração

### Variáveis de Ambiente

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `OMNI_VISION_PROVIDER` | Sim | — | `ollama`, `openrouter`, `openai` |
| `OMNI_VISION_API_KEY` | Cloud* | — | API key do provedor |
| `OMNI_VISION_DEFAULT_MODEL` | Não | provider.dependente | Modelo padrão |
| `OMNI_VISION_TIMEOUT` | Não | `120` | Timeout em segundos |

### Modelos Recomendados

**Ollama:** `qwen3-vl:2b` (1.9GB) · `qwen3-vl:4b` (3.3GB)
**OpenRouter:** `qwen/qwen3-vl-32b-instruct` · `google/gemini-2.5-flash`
**OpenAI:** `gpt-5.4-mini` · `gpt-5.4`

---

## Referência Rápida

| Tool | Parâmetros principais | Exemplo |
|------|----------------------|---------|
| `analyze_image` | `image_path`, `prompt`, `detail_level` | `analyze_image("foto.jpg", "Descreva", "detailed")` |
| `extract_object` | `image_path`, `object_description`, `output_filename` | `extract_object("carro.jpg", "license plate")` |
| `download_image` | `url` | `download_image("https://exemplo.com/img.jpg")` |
| `compare_images` | `image_paths[]`, `compare_type` | `compare_images(["a.jpg","b.jpg"], "both")` |
| `identify_objects` | `image_path`, `include_count`, `categories` | `identify_objects("foto.jpg")` |
| `read_text` | `image_path`, `language_hint`, `preserve_formatting` | `read_text("doc.jpg", "pt")` |
| `prepare_image` | `image_path`, `max_width`, `quality`, `format` | `prepare_image("foto.jpg", 1024)` |
| `crop_image` | `image_path`, `x`, `y`, `width`, `height` | `crop_image("foto.jpg", 100, 200, 300, 200)` |
| `convert_image_format` | `image_path`, `output_format`, `quality` | `convert_image_format("foto.png", "JPEG")` |
| `get_image_info` | `image_path`, `include_exif` | `get_image_info("foto.jpg")` |
| `get_provider_info` | — | `get_provider_info()` |

---

## Integração MCP

Adicione ao seu arquivo de configuração MCP (substitua os caminhos):

### Opencode (`~/.config/opencode/opencode.json`)

```json
{
  "mcp": {
    "omni-image-tools": {
      "type": "local",
      "command": ["C:\\caminho\\venv\\Scripts\\python.exe", "-m", "src.server"],
      "cwd": "C:\\caminho\\omni-image-tools-mcp",
      "environment": {
        "OMNI_VISION_PROVIDER": "ollama",
        "OMNI_VISION_DEFAULT_MODEL": "qwen3-vl:2b"
      },
      "enabled": true
    }
  }
}
```

> **Troque o provider** alterando `environment`:
> - OpenAI: `"OMNI_VISION_PROVIDER": "openai"` + `"OMNI_VISION_API_KEY": "sk-proj-..."`
> - OpenRouter: `"OMNI_VISION_PROVIDER": "openrouter"` + `"OMNI_VISION_API_KEY": "sk-or-..."`

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "omni-image-tools": {
      "command": "C:\\caminho\\venv\\Scripts\\python.exe",
      "args": ["-m", "src.server"],
      "cwd": "C:\\caminho\\omni-image-tools-mcp",
      "env": {
        "OMNI_VISION_PROVIDER": "openrouter",
        "OMNI_VISION_API_KEY": "sk-or-..."
      }
    }
  }
}
```

---

## GPU Memory Management

Para Ollama, o servidor gerencia automaticamente a GPU:

- **Verificação única** na primeira chamada (cacheada)
- **Descarrega** automaticamente modelos diferentes ao trocar
- **Previne** múltiplos modelos na GPU

```bash
python scripts/cli.py gpu-status                    # Ver status
python scripts/cli.py gpu-status --unload-ollama qwen3-vl:4b  # Descarregar
```

---

## Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| Provider não encontrado | `OMNI_VISION_PROVIDER` não setado | Configure a variável |
| API Key requerida | Cloud sem key | Adicione `OMNI_VISION_API_KEY` |
| Timeout | Modelo lento | Aumente `OMNI_VISION_TIMEOUT` |
| GPU OOM | Múltiplos modelos | GPU Manager gerencia automaticamente |
| Request timed out | Primeira carga | Ocorre só na primeira vez |

---

## Arquitetura

```
src/
├── server.py              # Servidor MCP
├── config.py              # Configuração por env vars
├── errors.py              # Error handling
├── providers/
│   ├── base.py            # Classe abstrata
│   ├── ollama.py          # Local
│   ├── openrouter.py      # Cloud
│   └── openai.py          # Cloud
├── tools/
│   ├── vision/            # analyze, identify, read_text, compare
│   ├── processing/        # prepare, info, crop, convert, download, extract
│   └── system/            # get_provider_info
└── utils/
    └── gpu_memory.py      # GPU Resource Manager
```

---

## License

MIT
