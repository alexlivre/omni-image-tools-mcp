# Créditos

## Projeto Original

Este projeto é baseado no [xkiranj/ollama-vision-mcp](https://github.com/xkiranj/ollama-vision-mcp).

| Campo | Valor |
|-------|-------|
| **Título** | ollama-vision-mcp |
| **Autor** | [xkiranj](https://github.com/xkiranj) |
| **Fonte** | https://github.com/xkiranj/ollama-vision-mcp |
| **Licença** | [MIT](https://opensource.org/licenses/MIT) |

## Sobre o ollama-vision-mcp

O ollama-vision-mcp é um servidor MCP que fornece visão computacional para modelos de IA usando Ollama local.

## Modificações Realizadas

| Componente | Original | Este repositório |
|------------|----------|------------------|
| Provedores | Apenas Ollama | Ollama + OpenRouter + OpenAI |
| Arquitetura | Código monolítico | Modular (ProviderFactory, ToolRegistry) |
| Gerenciamento GPU | Não tinha | GPU Memory Manager |
| Ferramentas | 4 básicas | 11 ferramentas completas |
| Documentação | Básica | Completa com exemplos |

### Ferramentas Adicionadas

| Ferramenta | Descrição |
|------------|-----------|
| xtract_object | Localiza e recorta objetos automaticamente |
| download_image | Baixa imagens da internet |
| get_provider_info | Mostra provedor ativo e limites |
| prepare_image | Redimensiona e otimiza imagens |
| get_image_info | Obtém metadados de imagens |
| crop_image | Recorta regiões específicas |
| convert_image_format | Converte entre formatos |

### Provedores Adicionados

| Provedor | Tipo | Custo |
|----------|------|-------|
| OpenRouter | Nuvem | Pago por uso |
| OpenAI | Nuvem | Pago por uso |
| LM Studio | Local | Gratuito |

## Licença

Este projeto é licenciado sob a **MIT**, a mesma licença do original.

Conforme os termos da MIT:
- ✅ O aviso de copyright é mantido
- ✅ A licença completa é incluída (LICENSE)
- ✅ A isenção de garantia é mantida

## Atribuição de Copyright

`
Copyright 2026 Alex Breno
Copyright 2024 xkiranj (ollama-vision-mcp original)
`

## Reconhecimentos

Agradecemos ao xkiranj por criar o ollama-vision-mcp, que forneceu a base para este servidor MCP de visão computacional expandido.

---

*Este arquivo foi adicionado como boa prática de atribuição, conforme exigido pela licença MIT.*