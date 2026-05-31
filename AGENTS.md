# Maker Workspace

Workspace para criar e experimentar MCPs (Model Context Protocol servers).

## MCP de Referência

Quando eu falar do **MCP de referência**, estou me referindo ao projeto:
- `ollama-vision-mcp-reference/` — Clone do repo https://github.com/xkiranj/ollama-vision-mcp
- Uso: Somente estudo, não modificar

**Modelo padrão**: `qwen3-vl:4b`
**Provedor**: Ollama local
**Req**: Ollama 0.12.7+

---

## Current Project

- `omni-image-tools-mcp/` — MCP de ferramentas de imagem (visão + processamento)
  - Leia `omni-image-tools-mcp/SPEC.md` para contexto e decisões de design

## MCPs Connected (Ferramentas Principais)

| MCP | Ferramentas | Quando usar |
|-----|-------------|-------------|
| `fetch` | `fetch_fetch` | Ler docs oficiais, buscar URLs |
| `webfetch` | (built-in do opencode) | Busca conteúdo de URLs, retorna markdown |
| `github` | `github_search_*`, `github_get_file_contents`, etc | Buscar repos, código, issues |
| `MiniMax` | `MiniMax_web_search`, `MiniMax_understand_image` | Pesquisas web, analisar imagens |
| `imagehub` | `imagehub_search_images`, etc | Buscar imagens |
| `playwright` | `playwright_browser_*` | Automação browser, screenshots |
| `sequential-thinking` | `sequentialthinking` | Pensamento estruturado |

**⭐ MCPs Favoritos (Stack Completo):** `MiniMax` + `GitHub` + `sequential-thinking`

> Esses três juntos formam um stack poderosa: pesquise → pense → implemente. Sempre use-os em conjunto ANTES de implementar qualquer coisa.

**Regra: NÃO assuma. Pesquise e valide sempre.**

## Como Melhorar Conhecimento e Pensamentos

**ANTES de qualquer implementação, sempre pesquise e combine MCPs.** Este é um passo obrigatório, não opcional.

### Combinações Úteis
| Situação | Combinação |
|----------|------------|
| Criar feature nova | `brainstorming` → pesquisa → `feature-forge` → implement |
| Debugar erro | `systematic-debugging` + `debugging-wizard` |
| MCP server | `mcp-developer` + `github_search_repositories` samples |
| Verificar antes de commit | `verification-before-completion` |
| Pesquisar docs | `fetch` + `MiniMax_web_search` |
| Analisar repo | `github_search_*` + `github_get_file_contents` |

### Guia de MCPs por Categoria (Skills Especializadas)

**Pesquisa & Atualização**: `MiniMax_web_search`, `MiniMax_understand_image`, `fetch`, `github`

**Build & Código**: `mcp-developer`, `python-pro`, `fastapi-expert`, `typescript-pro`, `react-expert`, `nestjs-expert`, `golang-pro`

**UI/Design**: `frontend-design`, `ui-styling`, `ui-ux-pro-max`

**Testing & Quality**: `test-master`, `test-driven-development`, `playwright-expert`, `code-reviewer`

**Architecture & Infra**: `architecture-designer`, `devops-engineer`, `cloud-architect`

**Security**: `secure-code-guardian`, `security-reviewer`

**Workflow**: `brainstorming`, `feature-forge`, `systematic-debugging`, `verification-before-completion`

## MCPs Disponíveis - Guia de Uso

### Pesquisa& Atualização
| MCP | Quando usar |
|-----|-------------|
| `MiniMax_web_search` | Buscar info atualizadas, validar decisões |
| `MiniMax_understand_image` | Analisar diagramas, arquitetura visual |
| `fetch` | Ler docs oficiais, buscar URLs |
| `github` | Buscar repos, código, issues |

### Build & Código
| MCP | Quando usar |
|-----|-------------|
| `mcp-developer` | Build/debug/extender MCP servers |
| `python-pro` | Python 3.11+ com async, type hints |
| `fastapi-expert` | APIs async com Pydantic V2 |
| `typescript-pro` | TypeScript avançado, tRPC |
| `react-expert` | React 18+, Next.js App Router |
| `nestjs-expert` | NestJS modules, controllers, JWT |
| `golang-pro` | Go com goroutines, microservices |

### UI/Design
| MCP | Quando usar |
|-----|-------------|
| `frontend-design` | Interfaces web high design quality |
| `ui-styling` | shadcn/ui, Tailwind, Radix |
| `ui-ux-pro-max` | 50+ estilos, 161 paletas, design system |

### Testing & Quality
| MCP | Quando usar |
|-----|-------------|
| `test-master` | Gerar testes, mocking, coverage |
| `test-driven-development` | TDD antes de implementar |
| `playwright-expert` | E2E tests, browser automation |
| `code-reviewer` | PR reviews, bugs, security |

### Architecture & Infra
| MCP | Quando usar |
|-----|-------------|
| `architecture-designer` | ADRs, diagramas, scalability |
| `devops-engineer` | Docker, CI/CD, Kubernetes |
| `cloud-architect` | AWS/Azure/GCP, Well-Architected |

### Security
| MCP | Quando usar |
|-----|-------------|
| `secure-code-guardian` | Auth, OWASP Top 10, input validation |
| `security-reviewer` | SAST, penetration testing |

### Workflow/Process
| MCP | Quando usar |
|-----|-------------|
| `brainstorming` | **SEMPRE antes de criar features** |
| `feature-forge` | Requirements, user stories, EARS |
| `systematic-debugging` | Bugs, stack traces, root cause |
| `verification-before-completion` | Antes de claim "pronto" |

---

## Processo de Desenvolvimento (OBRIGATÓRIO)

**ANTES de implementar QUALQUER coisa, use:**

1. **`sequential-thinking`** — Sempre que precisar pensar, planejar ou decidir algo
   - Decisões de design
   - Análise de trade-offs
   - Refatoração de código
   - Resolução de bugs

2. **MCPs de Pesquisa** — Sempre que precisar de informação
   - `MiniMax_web_search` — Buscar info atualizadas
   - `MiniMax_understand_image` — Analisar imagens/diagramas
   - `github_search_*` — Buscar código, libs, examples
   - `fetch` — Ler docs oficiais

3. **Combinação Recomendada:**
   ```
   sequential-thinking + MiniMax + GitHub
   = pesquise → pense → implemente
   ```

### Quando USAR:

| Situação | Ação |
|----------|------|
| Decisão de design/arquitetura | `sequential-thinking` |
| Escolher biblioteca | Pesquisa + `sequential-thinking` |
| Implementar feature | Pensar antes (`sequential-thinking`) |
| Resolver bug | `sequential-thinking` + pesquisa |
| Modificar decisão anterior | `sequential-thinking` revisita decisão |
| Adicionar nova tool/provider | Pensar + pesquisar alternatives |

### Quando NÃO PULAR o pensamento:

- ❌ "Vou só implementar rápido..."
- ❌ "Já sei como fazer..."
- ❌ "É só refatorar..."
- ❌ "Vou adicionar esse recurso..."

**Regra de Ouro:** Se você está prestes a implementar algo sem ter pensado estruturadamente, PARE e use `sequential-thinking`.

---

## Planejamento de Implementação

**ANTES de criar qualquer plano de implementação:**

1. Use `sequential-thinking` para estruturar pensamento
2. Use `MiniMax` + `GitHub` para pesquisar alternativas, libs, patterns
3. Combine pesquisa + pensamento iterativamente
4. Só então produza o plano final

**Combinação para planejamento:**
```
sequential-thinking + MiniMax + GitHub
= pesquise → pense → melhore → pesquise novamente → pense novamente
```



## Working Here

1. **Comece pela spec**: antes de implementar, leia a SPEC.md do projeto
2. **Pesquise antes de agir**: use MCPs MiniMax/GitHub/fetch para se atualizar
3. **Não assuma**: linguagens/frameworks evoluem; valide com pesquisa

---

## Git Workflow (OBRIGATÓRIO)

### Regras de Commit

**ANTES de fazer commit, PERGUNTE:**
1. "Este commit é atômico?" (uma mudança por commit)
2. "Posso reverter fácilmente?"
3. "A mensagem descreve O QUE e POR QUE?"

### Formato de Mensagens (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
| Type | Uso |
|------|-----|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `refactor` | Refatoração (sem mudança de behavior) |
| `perf` | Melhoria de performance |
| `test` | Adicionar/modificar testes |
| `chore` | Tarefas de manutenção |
| `revert` | Reverter commit anterior |

**Exemplos:**

```bash
# Boa mensagem - feat
feat(providers): add Ollama provider with model allowlist

- Added OllamaProvider class
- Implemented OLLAMA_ALLOWED_MODELS validation
- Added fallback model support (qwen3-vl:2b)
- Disabled auto-detection for security

# Boa mensagem - fix
fix(vision): correct base64 encoding for large images

- Increased buffer size for images >5MB
- Added proper chunking for API requests
- Added retry logic with exponential backoff

# Boa mensagem - refactor
refactor(tools): extract base tool class

- Created VisionTool base class
- Moved common validation logic
- Simplified tool implementations
```

**Mensagens RUINS (evitar):**
```
❌ "fixes"
❌ "updated code"
❌ "asdfgh"
❌ "WIP"
❌ "stuff"
```

### Quando Fazer Commit

| Situação | Ação |
|----------|------|
| Final de fase | Commit imediatamente |
| Antes de mudança grande | Commit seu estado atual |
| Após implementar feature | Commit + push |
| Antes de dormir | Commit + push |
| Erro bloqueante | Commit para salvar estado |

### Fluxo de Trabalho

```bash
# 1. Verificar status
git status

# 2. Verificar o que mudou
git diff --stat

# 3. Adicionar arquivos relevantes
git add <arquivos>
# OU adicionar tudo (CUIDADO)
git add -A

# 4. Commitar com mensagem descritiva
git commit -m "feat(scope): descrição clara

- detalhe 1
- detalhe 2
- detalhe 3"

# 5. Push IMEDIATAMENTE
git push
```

### .gitignore (Sempre Verificar)

**Python projects DEVEM ignorar:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
.env
.eggs/
*.egg-info/
dist/
build/
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### Restore/Revert

```bash
# Ver commits recentes
git log --oneline -10

# Criar novo commit revertendo (seguro)
git revert <commit-sha>

# Reset HARD (PERIGOSO, só em emergencia)
git reset --hard <commit-sha>
git push --force
```

### Regra de Ouro

> **Commit cedo, commit often.** Commits pequenos e atômicos são mais fáceis de reverter e entender.

---

## Verificar Antes de Commitar

- [ ] Dependências com `pip list` ou `npm ls`
- [ ] Testes passando
- [ ] Lint/typecheck limpo

## Comandos Úteis

### Ambiente Virtual (Python 3.11)

```bash
# Ativar venv
.\.venv\Scripts\Activate.ps1

# Verificar Python
python --version  # deve ser 3.11.x
```

### Python MCP

```bash
# Instalar dependências
pip install -e .

# Rodar MCP server
python -m src.server

# Testes
pytest tests/

# Node MCP
npm install
npm run build
```
