# Omni-Image-Tools MCP

MCP (Model Context Protocol) server com ferramentas de visão e processamento de imagens. Dá capacidade visual a modelos de IA com suporte a múltiplos provedores.

**11 ferramentas** • **3 provedores** • **GPU Memory Management**

## Ferramentas

### 👁️ Visão

| Ferramenta | Descrição | Limite Local | Limite Online |
|------------|-----------|-------------|---------------|
| `analyze_image` | Análise com prompt customizado | 1 imagem | sem limite |
| `identify_objects` | Identificar e localizar objetos | 1 imagem | sem limite |
| `read_text` | OCR - extrair texto de imagens | 1 imagem | sem limite |
| `compare_images` | Comparar 2-10 imagens | sequencial | paralelo |

### 🛠️ Processamento

| Ferramenta | Descrição |
|------------|-----------|
| `prepare_image` | Redimensionar e otimizar imagem |
| `get_image_info` | Metadados da imagem (formato, dimensões, EXIF) |
| `crop_image` | Recortar região específica |
| `convert_image_format` | Converter entre formatos (JPEG/PNG/WEBP/BMP/GIF) |
| `download_image` | Baixar imagem de URL |
| `extract_object` | Localizar e recortar objeto automaticamente |

### ⚙️ Sistema

| Ferramenta | Descrição |
|------------|-----------|
| `get_provider_info` | Info do provedor e limites atuais |

## Provedores Suportados

| Provedor | Tipo | GPU | API Key | Modelo Padrão |
|----------|------|-----|---------|---------------|
| **Ollama** | Local | Sua GPU | Não | `qwen3-vl:2b` |
| **OpenRouter** | Cloud | Cloud | Sim | `qwen/qwen3-vl-32b-instruct` |
| **OpenAI** | Cloud | Cloud | Sim | `gpt-5.4-mini` |

### Limites por Tipo

**Provedores Locais (Ollama):**
- Máximo **1 imagem por request** (GPU local limitada)
- `compare_images` processa **sequencialmente** (mais lento, confiável)
- GPU Memory Manager monitora e descarrega modelos automaticamente

**Provedores Online (OpenRouter, OpenAI):**
- Sem limite de imagens por request
- `compare_images` processa em **paralelo** (mais rápido)
- GPU gerenciada pelo provedor

## Quick Start

```bash
# 1. Configure o provider
set OMNI_VISION_PROVIDER=ollama
set OMNI_VISION_DEFAULT_MODEL=qwen3-vl:2b

# 2. Analisar imagem
python scripts/cli.py analyze --image foto.jpg --prompt "O que há nesta imagem?"

# 3. Extrair objeto
python scripts/cli.py extract --image carro.jpg --object "license plate"
```

## Instalação

```bash
git clone https://github.com/alexlivre/omni-image-tools-mcp
cd omni-image-tools-mcp

python -m venv venv
.\venv\Scripts\activate

pip install -e .
```

## Configuração

### Variáveis de Ambiente

| Variável | Obrigatório | Default | Descrição |
|----------|-------------|---------|-----------|
| `OMNI_VISION_PROVIDER` | Sim | - | `ollama`, `openrouter`, `openai` |
| `OMNI_VISION_API_KEY` | Cloud* | - | API key (*exceto Ollama) |
| `OMNI_VISION_DEFAULT_MODEL` | Não | varia por provider | Modelo padrão |
| `OMNI_VISION_TIMEOUT` | Não | `120` | Timeout em segundos |

### Modelos Recomendados

**Ollama (local):**
- `qwen3-vl:2b` — 1.9GB, ideal para GPUs residenciais
- `qwen3-vl:4b` — 3.3GB, melhor qualidade

**OpenRouter:**
- `qwen/qwen3-vl-32b-instruct` — bom custo-benefício
- `google/gemini-2.5-flash` — rápido e barato

**OpenAI:**
- `gpt-5.4-mini` — rápido e inteligente
- `gpt-5.4` — melhor qualidade

## Referência de Ferramentas

### analyze_image
Análise flexível com prompt customizado. Suporta `detail_level`: brief, standard, detailed.

```json
{
  "image_path": "foto.jpg",
  "prompt": "Descreva esta imagem",
  "detail_level": "detailed"
}
```

### extract_object
Localiza um objeto na imagem por visão computacional (IA) e recorta automaticamente a região.

```json
{
  "image_path": "carro.jpg",
  "object_description": "license plate",
  "output_filename": "placa.jpg"
}
```

**Retorno:**
```json
{
  "local_path": "test_images/placa.jpg",
  "coordinates": {"x1": 100, "y1": 312, "x2": 150, "y2": 351},
  "extracted_size": [50, 39]
}
```

### download_image
Baixa imagem de URL e salva localmente para uso com outras ferramentas.

```json
{
  "url": "https://exemplo.com/foto.jpg"
}
```

### compare_images
Compara 2-10 imagens. Em provedores locais processa sequencialmente.

```json
{
  "image_paths": ["foto1.jpg", "foto2.jpg"],
  "compare_type": "both"
}
```

### prepare_image
Redimensiona mantendo proporção e otimiza para análise.

```json
{
  "image_path": "foto.jpg",
  "max_width": 1024,
  "quality": 85,
  "format": "JPEG"
}
```

### crop_image
Recorta região específica por coordenadas.

```json
{
  "image_path": "foto.jpg",
  "x": 100, "y": 200, "width": 300, "height": 200
}
```

### read_text
OCR para extrair texto de imagens.

```json
{
  "image_path": "documento.jpg",
  "language_hint": "pt",
  "preserve_formatting": true
}
```

## Integração MCP

### Opencode

```json
{
  "mcp": {
    "omni-image-tools": {
      "type": "local",
      "command": ["caminho/para/venv/Scripts/python.exe", "-m", "src.server"],
      "cwd": "caminho/para/omni-image-tools-mcp",
      "environment": {
        "OMNI_VISION_PROVIDER": "ollama",
        "OMNI_VISION_DEFAULT_MODEL": "qwen3-vl:2b"
      },
      "enabled": true
    }
  }
}
```

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

## GPU Memory Management

Para provedores locais (Ollama), o servidor gerencia automaticamente a memória GPU:

- **Verificação única** na primeira chamada (cacheada)
- **Descarrega automaticamente** modelos não utilizados
- **Previne** ter múltiplos modelos na GPU

```bash
# Verificar status manualmente
python scripts/cli.py gpu-status

# Descarregar modelo específico
python scripts/cli.py gpu-status --unload-ollama qwen3-vl:4b
```

## Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| "Provider não encontrado" | `OMNI_VISION_PROVIDER` não setado | Configure a variável |
| "API Key requerida" | Cloud provider sem key | Adicione `OMNI_VISION_API_KEY` |
| Timeout | Modelo muito lento | Aumente `OMNI_VISION_TIMEOUT` |
| GPU OOM | Múltiplos modelos carregados | GPU Manager gerencia automaticamente |
| Request timed out | Primeira carga do modelo | Ocorre só na primeira vez |

## Arquitetura

```
src/
├── server.py              # Servidor MCP
├── config.py              # Configuração por env vars
├── errors.py              # Error handling
├── providers/
│   ├── base.py            # Classe abstrata VisionProvider
│   ├── ollama.py          # Ollama (local)
│   ├── openrouter.py      # OpenRouter (cloud)
│   └── openai.py          # OpenAI (cloud)
├── tools/
│   ├── vision/            # analyze, identify, read_text, compare
│   ├── processing/        # prepare, info, crop, convert, download, extract
│   └── system/            # get_provider_info
└── utils/
    └── gpu_memory.py      # GPU Resource Manager
```

## License

MIT
