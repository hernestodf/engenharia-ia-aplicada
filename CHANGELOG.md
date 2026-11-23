# Changelog

Todas as mudanças relevantes do Godnaterra são registradas aqui.
Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [0.3.0] — 2026-11-23

Integrações opcionais descobertas pelo agente, nunca auto-habilitadas.

### Adicionado

- `adapters/chrome-devtools-mcp/`: referência pinada ao `chrome-devtools-mcp@1.13.0` (Apache-2.0, shasum `e76ecc…`) e template MCP com `disabled: true`.
- `adapters/open-code-review/`: referência pinada ao `@alibaba-group/open-code-review@1.14.2` (Apache-2.0, shasum `4459a7…`), modo `delegation` por padrão.
- `adapters/openviking/`: referência pinada ao commit `5b7c655…` (AGPL-3.0), credencial via `{env:OPENVIKING_API_KEY}`, template MCP `disabled: true`, **nenhum código vendorizado**.
- `scripts/verify_adapters.py`: verificação offline de pins, licenças, `disabled`, env, não-vendorização, CJK e padrões de execução; `--check-online` compara shasums no registry via urllib (sem shell).
- 3 skills core: `op-chrome-devtools-audit`, `op-open-code-review`, `op-openviking-context`. Cada uma detecta a necessidade pelo pedido, faz preflight e reporta `pendente` se o pré-requisito não estiver pronto. Nenhuma instala ou habilita sozinha.
- `tests/test_integrations.py`: 10 testes de contrato dos adapters e das skills. Total do pacote: **56 testes**.

### Alterado

- `generate_adapters.py`: `ler_mcp_template()` e `mesclar_config()` com merge de `mcp.servers` preservando chaves e servidores existentes; novas entradas nascem desabilitadas.
- `install.py`: passa o template MCP pra config, imprime os servers no plano e inclui `adapters/*/*.{json,md,py}` na fonte canônica. Manifesto: **817 arquivos**.
- `ci.yml` e `release.yml`: nova validação dos adapters.
- `VERSION` e constante do operador em `0.3.0`.

### Segurança

- Nenhum instalador externo foi executado: sem `npx skills add`, sem instalador remoto por pipe, sem `npm install`, sem subida de servidor.
- Credencial do OpenViking nunca gravada em arquivo; apenas referência a variável de ambiente.
- OpenViking não entra no tarball por ser AGPL-3.0.

### Não verificado

- Conexão real do Chrome DevTools MCP, instalação do `ocr` e review de um diff, servidor OpenViking/retrieval. Os três continuam `pendente` por design.

## [0.2.0] — 2026-11-19

Instalação isolada por cliente, portabilidade total e release verificável.

### Adicionado

- `scripts/install.py`: instalador com DRY-RUN por padrão, `--apply` como autorização explícita, `--scope project` (padrão, grava só no clone) e `--scope user` (global com backup). Verificação SHA256 fail-closed, backup timestampado, `--rollback`, idempotente, sem subprocesso via shell.
- `scripts/generate_manifest.py` + `install-manifest.json`: SHA256 de 801 arquivos da fonte canônica; a instalação aborta se houver drift.
- `tests/test_install.py`: 6 testes de integridade, dry-run sem escrita, isolamento project, idempotência, rollback, merge de config em user scope e bloqueio por manifesto divergente. Total do pacote: **37 testes**.
- `scripts/README.md`: catálogo dos scripts.
- Comando `status` no `scripts/godnaterra.py`: conta skills ativas na config efetiva, read-only — substitui a dependência do `skill_mode.py` externo.

### Alterado

- `scripts/generate_adapters.py`: artefatos derivados usam o token `__GODNATERRA_ROOT__` em vez de caminhos absolutos da máquina geradora; `os.path.relpath` para symlinks, `subprocess`/Python direto sem `os.system`, merge de `opencode.json` preservando chaves existentes.
- `README.md` e `docs/guides/INSTALL.md`: reescritos sem paths absolutos e sem `skill_mode.py`; fluxo "clone → dry-run → apply project → status".
- `.gitignore`: ignora `.opencode/` e `.claude/skills/` locais.
- `.github/workflows/ci.yml`: auditoria do operador, `status`, reproduzibilidade dos adaptadores, `generate_manifest.py --check`, `git diff --check` e actions pinadas por SHA obtido via `git ls-remote`.
- `.github/workflows/cd.yml` → `release.yml`: tag `v*` ou dispatch, tarball completo, `SHA256SUMS` e Release via `gh`; `contents: write` só no job de release. **Sem deploy.**
- Versão bumpada para `0.2.0`.

### Corrigido

- Caminhos absolutos da máquina geradora removidos dos artefatos `generated/` e da documentação.
- `godnaterra.py status`: typo no docstring e leitura dupla de SKILL.md corrigidos.

### Não verificado

- Execução dos workflows no GitHub Actions e criação da Release (sem `gh`/runner local).
- CARGA de skills pelo runtime do OpenCode na máquina cliente (CLI ausente).

## [0.2.1] — 2026-11-19

### Corrigido

- `.github/workflows/release.yml`: o tarball do Release passa a incluir `.github`, cobrindo os 2 workflows que o `install-manifest.json` exige. Sem isso, o instalador dentro do tarball abortava por drift.
- `VERSION` e a constante do operador alinhadas em `0.2.1` (antes a constante ainda estava em `0.1.0`).

## [Não publicado]

### Adicionado

- Loop de aprendizado com revisão: erro observado vira cenário de regressão; a correção só entra depois de revisão humana aprovada e testes verdes.
- `scripts/validate_incidents.py`: valida o contrato dos incidentes sem executar o campo `verificacao` (incidente é entrada não confiável).
- `evaluations/incidents/`: `TEMPLATE.example.json`, `README.md`, `INC-001.json` (fechado — README divergente no primeiro push) e `INC-002.json` (rascunho — gate read-only não verificado em provider externo por fallback de agente).
- `tests/test_incidents.py`: 7 testes do contrato e dos gates de revisão. Total do pacote: **14 testes**.
- `scripts/run_evals.py`: harness executável de eval, agnóstico de provider — `opencode` é o único registrado e o único com baseline medido; roda só com `--provider opencode` explícito, não é default. Novos runtimes entram como chave em `ARGV_PROVIDER`. `--provider`, `--model`, `--scenario`, `--dry-run`, `--no-record` e `--timeout`; argv fixo, sem `eval`/`exec`/`shell=True`.
- `tests/test_evals.py`: 17 testes do harness (extração de resposta final, sanitização, assertions, JSONL, troca de provider, registro de novo provider e regressões do parecer QA). Total do pacote: **31 testes**.
- `evaluations/RESULTS.jsonl`: baseline real com 4 registros — 01/02/04 via `opencode/deepseek-v4.1-flash-free`, 03 por verificação determinística local.
- `tests/test_release_workflow.py`: 9 testes do contrato do release (dispatch exige tag, checkout da tag, input fora do shell, guarda `VERSION`↔tag, tarball com `.github`, permissões e pins por SHA). Total do pacote: **46 testes**.

### Corrigido

- Extrator de evidência do harness: antes capturava `snapshot`/system prompt e gerou um falso positivo no cenário 01. Agora lê somente `part.type == "text"` dos eventos; sem texto final, marca `nao verificado`. Registro inválido removido e substituído por execução válida.
- Rótulo do cenário 02: saída com `UNVERIFIED` passa a ser rejeitada pelas assertions; presença de termo deixou de virar `testado` automático (parecer QA/Security).
- Honestidade do rótulo: qualquer provider registrado só vira `testado` com texto final e assertions válidas; erro de provider, saída vazia, cota (429) e `UNVERIFIED` viram `nao verificado` — nenhum runtime tem atalho.
- `.github/workflows/release.yml`: `workflow_dispatch` agora exige o input `tag` e faz checkout dela. Antes, dispatch em branch tentava `gh release create main --verify-tag` e falhava. Adicionada guarda `VERSION` ↔ tag (sem o `v`).

### Alterado

- `.github/workflows/ci.yml`: novo step de validação de incidentes e step do harness com `--provider none --no-record` (sem credencial de LLM).
- `scripts/godnaterra.py`: `audit` passou a validar incidentes além do catálogo.
- `evaluations/RESULTS.md` e `evaluations/README.md`: baseline medido, comando de reprodução e separação entre presença de termos e julgamento semântico.
- `--provider`: opções derivadas de `ARGV_PROVIDER` em vez de lista fixa; registrar runtime não exige mudar o parser.

### Não verificado

- Cenário 02 com prompt endurecido: rerun interrompida por `provider.free-limit` (HTTP 429, `retryAfterMs=38586000` e, em nova tentativa às 13:51 UTC, `retryAfterMs=36472000`). Registro corrente é `nao verificado` por cota, não por falha do gate; reexecutar quando a cota voltar.
- Providers adicionais além de `opencode`: registráveis em `ARGV_PROVIDER`, mas nenhum foi medido nesta rodada.

## [0.1.0] — 2026-11-18

Primeira versão publicada. Pacote canônico, vendor-free e portátil.

### Adicionado

- 764 skills canônicas em `skills/upstream/` e 5 em `skills/core/` — 769 no total.
- 70 variantes divergentes preservadas em `references/`; 45 duplicatas idênticas fundidas e rastreadas no `MANIFEST.csv`.
- 7 agentes Godnaterra: 1 router primário e 6 subagents read-only, um papel por tarefa.
- `scripts/generate_adapters.py`: gerador derivado para OpenCode e Claude Code.
- `scripts/validate_catalog.py` e 8 testes unitários (número da `0.1.0`; total atual em `[Não publicado]`).
- `scripts/godnaterra.py`: `version`, `audit`, `doctor`, `init`, `update`.
- Design system, contrato Qdrant (`contract-only`) e CI/CD sem deploy.
- 4 cenários de avaliação em `evaluations/`.
- `SECURITY_CLASSIFICATION.md` com triagem dos achados de análise estática.

### Alterado

- Visibilidade padrão `godnaterra`: 769 skills visíveis, `autoinvoke: true`.
- Modos `god`, `godnaterra`, `curated` e `status` preservados em `skill_mode.py`.

### Segurança

- Nenhuma skill externa foi executada; achados classificados por risco real.
- Nenhum deploy, reindexação, rotação de segredo ou mudança em produção.

[0.1.0]: https://github.com/hernestodf/godnaterra
