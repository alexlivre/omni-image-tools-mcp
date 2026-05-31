# Image Processing Tools

Ferramentas de processamento de imagem para complementar as ferramentas de visão.

## Bibliotecas Python

| Biblioteca | Uso | Status |
|------------|-----|--------|
| **Pillow (PIL)** | Resize, crop, convert, compress, thumbnail | ✅ Padrão, já usado no original |
| **ExifRead** | Extrair EXIF de TIFF/JPEG | ✅ Leve, puro Python, bem mantido |
| **pillow-heif** | Suporte HEIC (fotos iPhone) | ✅ Ativo, suporta HEIF/HEIC |

### Dependencies

```txt
Pillow>=10.0.0
ExifRead>=3.0.0
pillow-heif>=0.12.0  # opcional
```

---

## Ferramentas de Processamento (v2)

### 1. `prepare_image`

Prepara imagem para envio a APIs de visão: resize, comprime, converte formato.

**Parâmetros:**
```python
prepare_image(
    image_path: str,
    max_width: int = 1024,       # largura máxima
    max_height: int = 1024,      # altura máxima
    format: str = "JPEG",         # "JPEG", "PNG", "WEBP"
    quality: int = 85,           #1-100 para JPEG
    mode: str = "fit"            # "fit" (mantém aspect), "stretch" (força dimensões)
) -> str  # path da imagem processada
```

**Uso:** Reduzir custo de APIs que cobram por pixel.

**Exemplo:**
```python
# Preparar imagem para OpenRouter (max1024x1024, JPEG 85%)
prepare_image("photo.jpg", max_width=1024, max_height=1024, format="JPEG", quality=85)
```

---

### 2. `get_image_info`

Extrai informações e metadata de uma imagem.

**Parâmetros:**
```python
get_image_info(
    image_path: str,
    include_exif: bool = True    # incluir dados EXIF
) -> dict # informações da imagem
```

**Retorno:**
```json
{
 "path": "photo.jpg",
    "format": "JPEG",
    "mode": "RGB",
    "size": {"width": 1920, "height": 1080},
    "file_size_bytes": 245760,
    "aspect_ratio": 1.78,
    "exif": {
        "Make": "Apple",
        "Model": "iPhone 14 Pro",
        "DateTimeOriginal": "2024:01:15 14:32:00",
        "GPS": {"Latitude": -23.5505, "Longitude": -46.6333}
    }
}
```

---

### 3. `crop_image`

Corta uma região específica da imagem.

**Parâmetros:**
```python
crop_image(
    image_path: str,
    x: int,                      # coordenada X do canto superior esquerdo
    y: int,                      # coordenada Y do canto superior esquerdo
    width: int,                  # largura da região
    height: int,                 # altura da região
    output_path: str = None     # se None, sobrescreve original
) -> str  # path da imagem recortada
```

**Uso:** Focar análise em área específica.

---

### 4. `convert_image_format`

Converte imagem entre formatos.

**Parâmetros:**
```python
convert_image_format(
    image_path: str,
    output_format: str,          # "JPEG", "PNG", "WEBP", "HEIC"
    output_path: str = None,    # se None, usa mesmo nome com nova extensão
    quality: int = 85           # para JPEG/WEBP
) -> str  # path da imagem convertida
```

---

## Ferramentas Futuras (v3+)

### `create_thumbnail`
```python
create_thumbnail(
    image_path: str,
    size: tuple = (256, 256),
    output_path: str = None
) -> str
```

### `rotate_image`
```python
rotate_image(
    image_path: str,
    degrees: float,
    output_path: str = None
) -> str
```

### `extract_faces` (usando face_recognition ou similar)
```python
extract_faces(
    image_path: str,
    output_dir: str = None
) -> list # lista de paths das faces extraídas
```

---

## Decisões

- [x] Adicionar ferramentas de processamento (v2)
- [x] Usar Pillow como biblioteca principal
- [x] Usar ExifRead para metadata EXIF
- [x] Adicionar suporte pillow-heif para fotos iPhone
- [ ] Criar thumbnail com Pillow ou lib separada?
- [ ] Detecção de faces com face_recognition? (heavy dependency)