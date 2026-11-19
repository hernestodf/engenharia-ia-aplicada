# Changelog

Todas as mudanças relevantes do Godnaterra são registradas aqui.
Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [Não publicado]

### Adicionado

- Loop de aprendizado com revisão: erro observado vira cenário de regressão; a correção só entra depois de revisão humana aprovada e testes verdes.
- `scripts/validate_incidents.py`: valida o contrato dos incidentes sem executar o campo `verificacao` (incidente é entrada não confiável).
- `evaluations/incidents/`: `TEMPLATE.example.json`, `README.md`, `INC-001.json` (fechado — README divergente no primeiro push) e `INC-002.json` (rascunho — Kilo `trusted: false`).
- `tests/test_incidents.py`: 7 testes do contrato e dos gates de revisão. Total do pacote: **15 testes**.
- `scripts/run_evals.py`: harness executável de eval, agnóstico de provider — `opencode` é o padrão de fato do baseline e `kilo` é opcional; novos runtimes entram como chave em `ARGV_PROVIDER`. `--provider`, `--model`, `--scenario`, `--dry-run`, `--no-record` e `--timeout`; argv fixo, sem `eval`/`exec`/`shell=True`.
- `tests/test_evals.py`: 17 testes do harness (extração de resposta final, sanitização, assertions, JSONL, troca de provider, registro de novo provider e regressões do parecer QA). Total do pacote: **32 testes**.
- `evaluations/RESULTS.jsonl`: baseline real com 4 registros — 01/02/04 via `opencode/deepseek-v4.1-flash-free`, 03 por verificação determinística local.

### Corrigido

- Extrator de evidência do harness: antes capturava `snapshot`/system prompt e gerou um falso positivo no cenário 01. Agora lê somente `part.type == "text"` dos eventos; sem texto final, marca `nao verificado`. Registro inválido removido e substituído por execução válida.
- Rótulo do cenário 02: saída com `UNVERIFIED` passa a ser rejeitada pelas assertions; presença de termo deixou de virar `testado` automático (parecer QA/Security).
- `kilo`: harness nunca marca `testado`, porque o subagent `godnaterra-qa-security` sofre fallback para o agente default e as regras `deny` não são herdadas.

### Alterado

- `.github/workflows/ci.yml`: novo step de validação de incidentes e step do harness com `--provider none --no-record` (sem credencial de LLM).
- `scripts/godnaterra.py`: `audit` passou a validar incidentes além do catálogo.
- `evaluations/RESULTS.md` e `evaluations/README.md`: baseline medido, comando de reprodução e separação entre presença de termos e julgamento semântico.
- `--provider`: opções derivadas de `ARGV_PROVIDER` em vez de lista fixa; registrar runtime não exige mudar o parser.

### Não verificado

- Troca efetiva para `kilo` como provider de baseline: tentativa real retornou `nao verificado` por ID de modelo inválido e fallback de agente (`godnaterra-qa-security` é subagent no kilo). Gate read-only no kilo não verificado.
- Cenário 02 com prompt endurecido: rerun interrompida por `provider.free-limit` (HTTP 429, `retryAfterMs=38586000` e, em nova tentativa às 13:51 UTC, `retryAfterMs=36472000`). Registro corrente é `nao verificado` por cota, não por falha do gate; reexecutar quando a cota voltar.
- Providers adicionais além de `opencode` e `kilo`: registráveis, mas nenhum foi medido nesta rodada.
- Entrypoint primary do kilo com regras `deny` equivalentes ao subagent: não implementado.

## [0.1.0] — 2026-11-18

Primeira versão publicada. Pacote canônico, vendor-free e portátil.

### Adicionado

- 764 skills canônicas em `skills/upstream/` e 5 em `skills/core/` — 769 no total.
- 70 variantes divergentes preservadas em `references/`; 45 duplicatas idênticas fundidas e rastreadas no `MANIFEST.csv`.
- 7 agentes Godnaterra: 1 router primário e 6 subagents read-only, um papel por tarefa.
- `scripts/generate_adapters.py`: gerador derivado para OpenCode, Kilo e Claude Code.
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
