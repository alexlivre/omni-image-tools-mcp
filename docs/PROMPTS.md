# Prompts Engineering

Prompts usados em cada tool do MCP.

## Análise Completa dos Prompts (ollama-vision-mcp-reference)

### Prompts Extraídos do Código Original

| Tool | Prompt | Linha |
|------|--------|-------|
| `analyze_image` | `"Describe this image in detail"` (default) | server.py:132 |
| `describe_image` | `"Provide a comprehensive description of this image, including all visible elements, colors, composition, and any notable details"` | server.py:137 |
| `identify_objects` | `"List all identifiable objects in this image. Format as a bulleted list"` | server.py:141 |
| `read_text` | `"Extract and transcribe all visible text in this image. If no text is visible, say 'No text found'"` | server.py:145 |

---

## Ferramentas do Omni-Vision MCP

### MVP (v1) — Melhorar as Existentes

| Tool | Descrição | Novos Parâmetros |
|------|-----------|------------------|
| `analyze_image` | Análise personalizável de imagem | `detail_level`, `focus` |
| `describe_image` | Descrição completa do conteúdo | `description_type` |
| `identify_objects` | Lista objetos identificáveis | `include_count`, `include_location`, `categories`, `min_confidence` |
| `read_text` | Extrai texto visível (OCR) | `preserve_formatting`, `language_hint` |

### v2 — Novas Ferramentas

| Tool | Descrição |
|------|-------------|
| `compare_images` | Comparar duas imagens (diferenças/semelhanças) |

---

## Prompts Melhorados (v1)

### 1. `analyze_image`

**Sinais:**
- `detail_level`: "brief" | "standard" | "detailed"
- `focus`: "all" | "objects" | "scene" | "text" | "colors"

**Prompt base + detail_level:**
| detail_level | Prompt |
|--------------|--------|
| brief | "Briefly describe this image." |
| standard | "Describe this image in detail." |
| detailed | "Provide a highly detailed and thorough description of this image, including all elements, patterns, and nuances." |

**Focus adiciona:**
| focus | Adicional ao prompt |
|-------|-------------------|
| objects | "Focus on identifying and describing each distinct object." |
| scene | "Focus on describing the overall scene, setting, and atmosphere." |
| text | "Focus on any text, labels, or written content." |
| colors | "Focus on colors, color harmonies, and color relationships." |
| all | (sem adicional) |

**Parâmetros:**
```python
analyze_image(
    image_path: str,
    prompt: str = None, # custom prompt
    model: str = None,            # override model
    detail_level: str = "standard",  # "brief" | "standard" | "detailed"
    focus: str = "all"              # "all" | "objects" | "scene" | "text" | "colors"
)
```

### 2. `describe_image`

**Sinais:**
- `description_type`: "technical" | "artistic" | "simple"

**Prompt base + description_type:**
| description_type | Prompt |
|------------------|--------|
| technical | "Provide a detailed technical description of this image, including dimensions, composition, colors, and technical aspects." |
| artistic | "Describe this image from an artistic perspective, focusing on aesthetics, mood, and creative elements." |
| simple | "Describe this image in simple, everyday language that anyone can understand." |

**Parâmetros:**
```python
describe_image(
    image_path: str,
    description_type: str = "standard"  # "technical" | "artistic" | "simple"
)
```

### 3. `identify_objects`

**Sinais:**
- `include_count`: bool — quantos de cada objeto
- `include_location`: bool — posição na imagem
- `categories`: list — filtro (["people", "vehicles", "animals", etc)
- `min_confidence`: float — 0-1, ignorar detecções com baixa confiança

**Prompt base:**
```
"List all identifiable objects in this image. Format as a bulleted list."
```

**Com include_count=True:**
```
"List all identifiable objects in this image. For each type of object, indicate how many instances appear. Format as a bulleted list with counts."
```

**Com include_location=True:**
```
"List all identifiable objects in this image. For each object, indicate its approximate location in the image (e.g., 'top-left', 'center', 'bottom-right'). Format as a bulleted list."
```

**Com categories filter:**
```
"Focus on identifying objects in these categories: [categories]. List all identifiable objects from these categories in this image. Format as a bulleted list."
```

**Parâmetros:**
```python
identify_objects(
    image_path: str,
    include_count: bool = False,
    include_location: bool = False,
    categories: list = None,        # ["people", "vehicles", "animals", "text", "electronics"]
    min_confidence: float = 0.5    # 0.0 to 1.0
)
```

### 4. `read_text`

**Sinais:**
- `preserve_formatting`: bool — manter layout
- `language_hint`: str — "en", "pt", "es", etc

**Prompt base:**
```
"Extract and transcribe all visible text in this image. If no text is visible, say 'No text found'."
```

**Com preserve_formatting=True:**
```
"Extract and transcribe all visible text in this image, preserving the original formatting, layout, and structure as much as possible. If no text is visible, say 'No text found'."
```

**Com language_hint:**
```
"Extract and transcribe all visible text in this image. The text appears to be in [language_hint]. If no text is visible, say 'No text found'."
```

**Parâmetros:**
```python
read_text(
    image_path: str,
    preserve_formatting: bool = False,
    language_hint: str = None  # "en", "pt", "es", "fr", "de", etc
)
```

---

## Ferramentas Futuras (v2+)

### `compare_images` (v2)

**Sinais:**
- `comparison_type`: "differences" | "similarities" | "both"

**Prompt:**
| comparison_type | Prompt |
|-----------------|--------|
| differences | "Analyze these two images and describe the key differences between them." |
| similarities | "Analyze these two images and describe their key similarities." |
| both | "Analyze these two images and describe both their key differences and similarities." |

**Parâmetros:**
```python
compare_images(
    image_path_1: str,
    image_path_2: str,
    comparison_type: str = "both"  # "differences" | "similarities" | "both"
)
```

### `detect_faces` (futuro)

**Prompt:**
```
"Detect all faces in this image. For each face, provide: approximate age estimate, gender (if identifiable), and dominant emotion if clearly visible."
```

### `extract_chart_data` (futuro)

**Prompt:**
```
"Extract and transcribe all data visible in this chart or graph. Include axis labels, values, and any text annotations. Format the data in a structured way."
```

---

## Decisões

- [x] Manter 4 ferramentas originais com melhorias (v1)
- [x] Adicionar `compare_images` (v2)
- [x] Prompts em inglês (modelo responde no idioma do usuário)
- [ ] Internacionalização dos prompts?
- [ ] System prompt para comportamento geral?