# Engenharia de IA Aplicada

Pacote de engenharia de software assistida por IA, **vendor-neutral e portátil**. Núcleo genérico; perfis opcionais entram como camadas derivadas. Sem lock-in de LLM/provider, sem vendor, sem Kilo.

Versão: `0.7.0`

## Comece aqui

Numa máquina nova,clone e instale no escopo do projeto (isolado por cliente):

```bash
git clone git@github.com:hernestodf/engenharia-ia-aplicada.git
cd engenharia-ia-aplicada

python3 scripts/install.py                 # 1) DRY-RUN: mostra o plano, não escreve nada
python3 scripts/install.py --apply         # 2) instala DENTRO do clone (padrão --scope project)
python3 scripts/eia.py status       # 3) confirma as skills ativas
python3 scripts/eia.py audit        # 4) auditoria read-only
```

`--apply` é a autorização explícita. Sem ele, nada é escrito. O padrão `--scope project` grava apenas `.opencode/` e `.claude/skills/` **dentro do clone** — nada toca a config global da máquina. Para instalar globalmente, use `--apply --scope user` (faz backup e preserva chaves existentes).

Guia completo: [`docs/guides/INSTALL.md`](docs/guides/INSTALL.md).

## Por que não "clonar já instala sozinho"

Git **não executa hooks** de um repositório recém-clonado (é proteção contra código arbitrário). Então a instalação é sempre **1 comando auditável** e explícito, nunca automático. Se quiser zero comando, use um devcontainer opcional — ainda não fornecido.

## O que é fonte canônica

- `AGENTS.md`, `project.yaml`, `skills/core/`, `skills/upstream/`, `agents/` — **fonte**.
- `adapters/*/generated/` — **derivados**, gerados por `scripts/generate_adapters.py`. Nunca edite na mão.
- `install-manifest.json` — SHA256 da fonte, gerado por `scripts/generate_manifest.py`. A instalação falha fechada se houver drift.

## Comandos do operador

```bash
python3 scripts/eia.py version    # versão do pacote
python3 scripts/eia.py audit      # catálogo + incidentes + JSONs derivados
python3 scripts/eia.py status     # skills ativas na config efetiva (leitura)
python3 scripts/eia.py doctor     # runtimes, configs e backups (leitura)
python3 scripts/eia.py init       # DRY-RUN do gerador de adaptadores
python3 scripts/eia.py update --apply
```

Nenhum comando apaga arquivos, reindexa, faz deploy ou rotaciona segredos.

## Verificação rápida

```bash
python3 scripts/validate_catalog.py
python3 scripts/validate_incidents.py
python3 -m unittest discover -s tests -v        # 66 testes
python3 scripts/run_evals.py --suite tasks --provider none   # baseline + regressão
python3 scripts/verify_adapters.py              # pins, licenças e disabled
python3 scripts/eia.py audit
python3 scripts/generate_manifest.py --check
git diff --check
```

## Documentação

- `AGENTS.md` — fonte canônica de regras
- `docs/architecture/OVERVIEW.md` — mapa dos módulos A–F
- `docs/standards/ENGINEERING_WORKFLOW.md` — ciclo DISCOVER→DELIVER
- `docs/decisions/` — ADRs
- `MANIFESTO.md` — proveniência das skills portadas
- `docs/guides/INSTALL.md` — instalação, rollback e troubleshooting
- `adapters/` — integrações opcionais (pins, licenças, templates MCP desabilitados)
- `scripts/README.md` — catálogo de scripts
- `.github/workflows/README.md` — CI/CD e pins

## Estado

| Fase | Situação |
|---|---|
| 1–9 | concluídas/implementadas conforme ADRs; ver detalhes em `docs/` |
| 10 · Instalador e documentação | implementado; 66 testes OK localmente |
| 12 · Avaliação determinística | implementada; 20 tarefas, 16 determinísticas em 42/42, baseline travado e regressão detectada; 4 tarefas LLM não verificadas sem provider |
| 11 · Integrações opcionais | implementadas; Chrome DevTools MCP, OpenCodeReview e OpenViking em `adapters/`, todos desabilitados por padrão |
| CI/CD | YAMLs implementados com actions pinadas por SHA; execução no GitHub Actions não observada |

Sempre separamos **implementado / testado / pendente / não verificado**. Evidência acima de conclusão. Nada aqui é "testado" em runtime de cliente por padrão.
