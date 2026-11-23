# Guia — Instalação, Rollback e Troubleshooting

## Instalação isolada por cliente (padrão)

O instalador grava dentro do próprio clone. Cada cliente tem seu clone, logo cada um tem sua config isolada. Nada é escrito em `$HOME`.

```bash
git clone git@github.com:hernestodf/engenharia-ia-aplicada.git
cd engenharia-ia-aplicada
python3 scripts/install.py                 # DRY-RUN — não escreve nada
python3 scripts/install.py --apply         # aplica no clone (scope project)
python3 scripts/eia.py status
```

Resultado em `<clone>/.opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": [
    "<clone>/skills/core",
    "<clone>/skills/upstream"
  ]
}
```

Os caminhos são **resolvidos a partir do clone local** no momento da instalação. Os artefatos versionados em `adapters/*/generated/` usam o token `__EIA_ROOT__` e nunca contêm caminhos da máquina que os gerou.

## Escopo global (somente quando explicitamente pedido)

```bash
python3 scripts/install.py --apply --scope user
```

Grava em `$HOME/.config/opencode/opencode.json` e `$HOME/.config/opencode/agents`.

- Faz **backup timestampado** (`opencode.json.bak-eia-<UTC>`).
- **Preserva chaves existentes** do JSON — só substitui `$schema` e `skills`.
- **Recusa JSON inválido** (ex.: JSONC com comentários): aborta sem escrever nada.
- Symlinks Claude em `$HOME/.claude/skills` são relativos e nunca sobrescrevem destino existente.

## Integridade (fail-closed)

Antes de qualquer escrita, `scripts/install.py` verifica o SHA256 de 817 arquivos contra `install-manifest.json`. Se qualquer arquivo divergir ou faltar, a instalação aborta com exit 1 e **nenhum arquivo é tocado**.

```bash
python3 scripts/generate_manifest.py --check   # só verifica
python3 scripts/generate_manifest.py           # regera (use após editar fonte canônica)
```

## Rollback

```bash
python3 scripts/install.py --rollback                    # escopo project
python3 scripts/install.py --rollback --scope user        # escopo global
```

Restaura o backup timestampado mais recente de `opencode.json` e dos agentes. Symlinks Claude são aditivos — o instalador nunca apaga destino existente; remova manualmente se quiser.

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `Instalação abortada: fonte canônica divergente` | arquivo versionado foi editado sem regerar o manifesto | `python3 scripts/generate_manifest.py` e rode de novo |
| `Config existente nao e JSON valido` | `opencode.json` tem comentários/JSONC | converta para JSON puro antes de instalar |
| `Skills ativas: 0` no `status` | instalou em escopo errado ou não rodou `--apply` | rode `python3 scripts/install.py --apply` |
| symlinks quebrados em `.claude/skills` | clone foi movido após a instalação | reinstale (`--apply`) — os symlinks são relativos ao clone |
| ID `op-` duplicado | dois clones/packs carregados ao mesmo tempo | aponte a config de cada cliente só para o clone dele |
| `python3` não encontrado | runtime ausente | instale Python 3.11+ |

## Validação pós-instalação

| Verificação | Resultado observado localmente |
|---|---|
| JSON do config válido | ✅ duas raízes |
| IDs únicos (`op-`) | ✅ 772/772 |
| Frontmatter inválido | ✅ 0 |
| Agentes reconhecidos | ✅ 7 (`opencode debug agents`) |
| Symlinks Claude | ✅ 772, 0 quebrados — **CLI ausente**, formato não executado |
| Suite de testes | ✅ 58/58 |
| Adapters opcionais | ✅ 3 pinados, 0 problemas, nenhum habilitado |
| Templates MCP | ✅ 2 entradas listadas com `disabled: true` |

## Integrações opcionais

O instalador **nunca habilita** servidores MCP nem instala CLIs externos. Ele
apenas mescla os templates de `adapters/` com `disabled: true`. Para usar:

| Integração | Pré-requisito | Como habilitar |
|---|---|---|
| Chrome DevTools MCP | Node ≥ 20.19 e Chrome | `adapters/chrome-devtools-mcp/README.md` |
| OpenCodeReview | `ocr` instalado | `adapters/open-code-review/README.md` |
| OpenViking | servidor + API key | `adapters/openviking/README.md` |

As skills `op-chrome-devtools-audit`, `op-open-code-review` e
`op-openviking-context` detectam a necessidade pelo próprio pedido, fazem o
preflight e reportam `pendente` se o pré-requisito não estiver pronto. Elas
**nunca instalam nem habilitam sozinhas**.

Reproduzir:

```bash
python3 scripts/validate_catalog.py
python3 scripts/validate_incidents.py
python3 -m unittest discover -s tests -v
python3 scripts/eia.py audit
```

## Fora do escopo da instalação

- reindexação do Qdrant / criação de collection
- rotação de credenciais
- deploy em produção
- alteração no `.git` de qualquer outro repositório

Todos exigem autorização explícita.

## Não verificado

- CARGA real das skills pelo runtime do OpenCode na máquina cliente (CLI ausente aqui).
- Execução dos workflows no GitHub Actions.
