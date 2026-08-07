# Omni-Image-Tools MCP

Um servidor MCP que dá **visão computacional** para modelos de IA. Ele permite que a IA "veja" imagens: descrever, comparar, extrair texto, recortar objetos e muito mais.

**11 ferramentas** · **3 provedores** · **Funciona com Opencode, Claude, Cursor**

---

## 🤔 Qual provedor usar?

### Se você tem GPU (placa de vídeo) → Ollama

> O modelo roda **no seu computador**, usando sua placa de vídeo. Grátis, privado, sem depender de internet.

**Limite:** sua GPU tem memória finita — por isso só **1 imagem por vez** e modelos menores.

### Se você não tem GPU ou quer mais qualidade → Nuvem

> O modelo roda **na nuvem** (OpenAI, OpenRouter). Pago por uso, precisa de API key, sem limites de imagem.

---

## Escolha seu modelo

| Para quem... | Use | Tamanho | Onde roda |
|-------------|-----|---------|-----------|
| PC fraco ou só testar | `qwen3-vl:2b` | 1.9GB 🟢 | Seu computador (Ollama) |
| PC mediano | `qwen3-vl:4b` | 3.3GB 🟡 | Seu computador (Ollama) |
| Qualidade profissional | `gpt-5.4-mini` | ☁️ | Nuvem (OpenAI, pago) |
| Melhor custo-benefício | `qwen/qwen3-vl-32b-instruct` | ☁️ | Nuvem (OpenRouter, barato) |

> ⚠️ **Memória importa:** Se você tem 4GB de VRAM, use `qwen3-vl:2b`. Com 6GB+, pode usar `qwen3-vl:4b`. Os modelos de nuvem não usam sua GPU.

---

## 🚀 Início Rápido

```bash
# 1. Baixar e instalar (requer uv: https://docs.astral.sh/uv/)
git clone https://github.com/alexlivre/omni-image-tools-mcp
cd omni-image-tools-mcp
uv sync
uv sync --extra dev

# 2. Se for usar Ollama (grátis, local):
set OMNI_VISION_PROVIDER=ollama
set OMNI_VISION_DEFAULT_MODEL=qwen3-vl:2b

# 3. Testar
uv run python scripts/cli.py analyze --image foto.jpg --prompt "O que tem nesta imagem?"
```

> 💡 **Dica:** Se quiser usar nuvem, veja a seção [Como configurar cada provedor](#-como-configurar-cada-provedor) mais abaixo.

---

## 🧰 Ferramentas

### 👁️ Visão (usam inteligência artificial)

| Ferramenta | Pra que serve | Com Ollama | Com Nuvem |
|------------|--------------|------------|-----------|
| `analyze_image` | Analisar imagem com prompt livre | 1 imagem por vez | Várias imagens |
| `identify_objects` | Detectar objetos na imagem | 1 imagem por vez | Várias imagens |
| `read_text` | Extrair texto (OCR) | 1 imagem por vez | Várias imagens |
| `compare_images` | Comparar 2 a 10 imagens | Processa uma por uma | Processa tudo junto |

> **Por que o Ollama tem limite de 1 imagem?** Porque a memória da GPU é limitada. Enviar várias imagens de uma vez pode estourar a memória e travar tudo. O sistema **automaticamente** gerencia isso — na nuvem não tem esse problema.

### 🛠️ Processamento (não usam IA, são rápidas)

| Ferramenta | Pra que serve |
|------------|--------------|
| `prepare_image` | Redimensionar e otimizar foto |
| `get_image_info` | Ver dados da foto (tamanho, formato, etc) |
| `crop_image` | Recortar uma parte da foto |
| `convert_image_format` | Mudar formato (JPEG, PNG, WEBP...) |
| `download_image` | Baixar foto da internet |
| `extract_object` | **Achar e recortar um objeto automaticamente** |

### ⚙️ Sistema

| Ferramenta | Pra que serve |
|------------|--------------|
| `get_provider_info` | Mostra qual provedor está ativo e seus limites |

---

## 🌟 Ferramenta Destaque: `extract_object`

Essa ferramenta é **inteligente**: você diz o que quer recortar e ela acha sozinha.

```bash
uv run python scripts/cli.py extract --image carro.jpg --object "license plate"
```

**O que acontece por dentro:**
1. A IA localiza o objeto na imagem → coordenadas
2. O sistema recorta automaticamente a região
3. Salva o recorte em `outputs/` (ou o diretório definido por `OMNI_OUTPUT_DIR`)

Útil para: placas de carro, rostos, logotipos, textos específicos, qualquer objeto visível.

---

## ⚙️ Como configurar cada provedor

### Opção A: Ollama (gratuito, local)

> Requer: [Ollama](https://ollama.com) instalado e o modelo baixado (`ollama pull qwen3-vl:2b`)

```bash
set OMNI_VISION_PROVIDER=ollama
set OMNI_VISION_DEFAULT_MODEL=qwen3-vl:2b
```

### Opção B: OpenAI (nuvem, pago)

> Requer: [API key da OpenAI](https://platform.openai.com/api-keys)

```bash
set OMNI_VISION_PROVIDER=openai
set OMNI_VISION_API_KEY=sk-proj-sua-chave-aqui
set OMNI_VISION_DEFAULT_MODEL=gpt-5.4-mini
```

### Opção C: OpenRouter (nuvem, barato)

> Requer: [API key do OpenRouter](https://openrouter.ai/keys)

```bash
set OMNI_VISION_PROVIDER=openrouter
set OMNI_VISION_API_KEY=sk-or-v1-sua-chave-aqui
set OMNI_VISION_DEFAULT_MODEL=qwen/qwen3-vl-32b-instruct
```

### Todas as opções

| Variável | Obrigatório | Padrão | O que faz |
|----------|-------------|--------|-----------|
| `OMNI_VISION_PROVIDER` | ✅ Sim | — | `ollama`, `openrouter` ou `openai` |
| `OMNI_VISION_API_KEY` | Só nuvem | — | Sua chave do provedor |
| `OMNI_VISION_DEFAULT_MODEL` | ❌ Não | Varia | Qual modelo usar |
| `OMNI_VISION_TIMEOUT` | ❌ Não | 120s | Tempo máximo de espera |
| `OLLAMA_ALLOWED_MODELS` | ❌ Não | `qwen3-vl:4b,qwen3-vl:2b` | Modelos permitidos no Ollama (CSV) |
| `OMNI_OUTPUT_DIR` | ❌ Não | `./outputs` | Onde `extract_object`/`download_image` gravam arquivos |
| `OMNI_ALLOWED_DIRS` | ❌ Não | (vazio = sem sandbox) | Lista de diretórios permitidos para `image_path` (separados por `;`) — proteção contra path traversal |

### 🔒 Segurança embutida

- **SSRF:** `download_image` bloqueia IPs privados/loopback/link-local (ex.: `169.254.169.254`), hosts que resolvam para eles, e revalida cada redirect.
- **Path traversal:** todos os `image_path` são resolvidos (`resolve()` segue symlinks); com `OMNI_ALLOWED_DIRS` configurado, caminhos fora do sandbox são rejeitados.
- **Downloads limitados:** download é em streaming com teto de 20 MB (Content-Length + contador de bytes).
- **Privacidade:** `get_image_info` retorna EXIF desligado por padrão (`include_exif`); se ativado e houver GPS, um aviso é adicionado.

---

## 🔌 Integração com Opencode

> **Nota (v0.6.0):** o servidor agora roda sobre o **FastMCP**, o que adiciona relatório de progresso, saída estruturada (`structuredContent`/`outputSchema`) e timeouts por ferramenta. O console script `omni-image-tools` usa o novo entry point `src.server_fastmcp:main`. O antigo `src/server.py` permanece como fallback (`python -m src.server`) por uma release.

Adicione no arquivo `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "omni-image-tools": {
      "type": "local",
      "command": ["C:\\caminho\\omni-image-tools-mcp\\.venv\\Scripts\\python.exe", "-m", "src.server"],
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

#### Ollama (local, gratuito)

```json
"environment": {
  "OMNI_VISION_PROVIDER": "ollama",
  "OMNI_VISION_DEFAULT_MODEL": "qwen3-vl:2b"
}
```

#### OpenAI (nuvem, pago)

Requer [API key](https://platform.openai.com/api-keys).

```json
"environment": {
  "OMNI_VISION_PROVIDER": "openai",
  "OMNI_VISION_API_KEY": "sk-proj-sua-chave-aqui",
  "OMNI_VISION_DEFAULT_MODEL": "gpt-5.4-mini"
}
```

#### OpenRouter (nuvem, barato)

Requer [API key](https://openrouter.ai/keys).

```json
"environment": {
  "OMNI_VISION_PROVIDER": "openrouter",
  "OMNI_VISION_API_KEY": "sk-or-v1-sua-chave-aqui",
  "OMNI_VISION_DEFAULT_MODEL": "qwen/qwen3-vl-32b-instruct"
}
```

> **Lembrete:** O `command` deve apontar para o `python.exe` da pasta `.venv` do projeto. Depois de alterar, **reinicie o opencode**.

Também funciona no [Claude Desktop](https://claude.ai/download) e [Cursor IDE](https://cursor.sh).

---

## 🖥️ Gerenciamento de Memória GPU

**Só se aplica se você usa Ollama (local).**

Quando você usa Ollama, o modelo fica carregado na memória da placa de vídeo. Se você pedir para carregar outro modelo, o sistema **automaticamente descarrega o anterior** antes de carregar o novo — evitando que a memória estoure.

```bash
uv run python scripts/cli.py gpu-status                    # Ver o que está carregado
uv run python scripts/cli.py gpu-status --unload-ollama modelo  # Forçar descarregar
```

Isso tudo acontece **automagicamente** — você não precisa se preocupar.

---

## ❓ Problemas Comuns

| Problema | Por que acontece | Como resolver |
|----------|-----------------|---------------|
| "Provider não encontrado" | Você não configurou o provedor | Configure `OMNI_VISION_PROVIDER` |
| "API Key requerida" | Provider de nuvem sem chave | Adicione `OMNI_VISION_API_KEY` |
| Demora muito para responder | Modelo grande em PC fraco | Aumente `OMNI_VISION_TIMEOUT` ou use modelo menor |
| "Request timed out" | Primeira vez usando o modelo | O modelo precisa carregar na GPU (só na primeira vez) |
| GPU sem memória | Muitos modelos carregados | O sistema gerencia automaticamente |

---

## 📁 Estrutura do Projeto

```
src/
├── server.py              # Servidor que se comunica com a IA
├── config.py              # Configurações
├── providers/
│   ├── ollama.py          # Conexão com Ollama (local)
│   ├── openrouter.py      # Conexão com OpenRouter (nuvem)
│   └── openai.py          # Conexão com OpenAI (nuvem)
├── tools/
│   ├── vision/            # Ferramentas de visão (IA)
│   └── processing/        # Ferramentas de processamento (PIL)
└── utils/
    └── gpu_memory.py      # Controle de memória da GPU
```

---

## 📄 Licença

MIT