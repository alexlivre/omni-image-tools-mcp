# Credits

## Original Project

This project is based on [xkiranj/ollama-vision-mcp](https://github.com/xkiranj/ollama-vision-mcp).

| Field | Value |
|-------|-------|
| **Title** | ollama-vision-mcp |
| **Author** | [xkiranj](https://github.com/xkiranj) |
| **Source** | https://github.com/xkiranj/ollama-vision-mcp |
| **License** | [MIT](https://opensource.org/licenses/MIT) |

## About ollama-vision-mcp

ollama-vision-mcp is an MCP server that provides computer vision to AI models using local Ollama.

## Modifications Made

| Component | Original | This repository |
|------------|----------|------------------|
| Providers | Ollama only | Ollama + OpenRouter + OpenAI + LM Studio + MiniMax |
| Architecture | Monolithic code | Modular (ProviderFactory, ToolRegistry) |
| GPU management | None | GPU Memory Manager |
| Tools | 4 basic | 11 complete tools |
| Documentation | Basic | Complete with examples |

### Tools Added

| Tool | Description |
|------------|-----------|
| `extract_object` | Locates and crops objects automatically |
| `download_image` | Downloads images from the internet |
| `get_provider_info` | Shows the active provider and its limits |
| `prepare_image` | Resizes and optimizes images |
| `get_image_info` | Reads image metadata |
| `crop_image` | Crops specific regions |
| `convert_image_format` | Converts between formats |

### Providers Added

| Provider | Type | Cost |
|----------|------|-------|
| OpenRouter | Cloud | Pay-per-use |
| OpenAI | Cloud | Pay-per-use |
| LM Studio | Local | Free |
| MiniMax | Cloud | Pay-per-use |

## License

This project is licensed under the **MIT**, the same license as the original.

Per the MIT terms:
- ✅ The copyright notice is preserved
- ✅ The full license is included (LICENSE)
- ✅ The warranty disclaimer is preserved

## Copyright Attribution

```
Copyright 2026 Alex Santos
```

## Acknowledgments

We thank xkiranj for creating ollama-vision-mcp, which provided the foundation for this expanded computer-vision MCP server.

---

*This file was added as an attribution best practice, as required by the MIT license.*
