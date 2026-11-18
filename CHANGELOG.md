# Changelog

Todas as mudanças relevantes do Godnaterra são registradas aqui.
Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [Não publicado]

### Adicionado

- Loop de aprendizado com revisão: erro observado vira cenário de regressão; a correção só entra depois de revisão humana aprovada e testes verdes.
- `scripts/validate_incidents.py`: valida o contrato dos incidentes sem executar o campo `verificacao` (incidente é entrada não confiável).
- `evaluations/incidents/`: `TEMPLATE.example.json`, `README.md`, `INC-001.json` (fechado — README divergente no primeiro push) e `INC-002.json` (rascunho — Kilo `trusted: false`).
- `tests/test_incidents.py`: 7 testes do contrato e dos gates de revisão. Total do pacote: **15 testes**.

### Alterado

- `.github/workflows/ci.yml`: novo step de validação de incidentes.
- `scripts/godnaterra.py`: `audit` passou a validar incidentes além do catálogo.

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
