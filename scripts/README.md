# Scripts

Todos os scripts são Python 3.11+, sem dependências externas, e **não** executam comandos via shell.

## Instalação

| Script | Função |
|---|---|
| `install.py` | Instalador isolado por cliente. DRY-RUN por padrão; `--apply` autoriza escrita. `--scope project` (padrão) grava no clone; `--scope user` grava global com backup. `--rollback` restaura backups. |
| `generate_manifest.py` | Gera/verifica `install-manifest.json` (SHA256 da fonte canônica). `--check` só verifica. |

```bash
python3 scripts/install.py                 # plano, sem escrita
python3 scripts/install.py --apply         # instala no clone
python3 scripts/install.py --apply --scope user
python3 scripts/install.py --rollback
python3 scripts/generate_manifest.py --check
```

## Geração de adaptadores

| Script | Função |
|---|---|
| `generate_adapters.py` | Gera `adapters/opencode/generated/opencode.json` e `adapters/claude-code/generated/install-skills.sh` a partir da fonte canônica. Usa token `__EIA_ROOT__`. `--apply` é o modo legado global. |

Nunca edite `adapters/*/generated/` na mão.

## Operador

| Script | Função |
|---|---|
| `eia.py` | CLI `version`, `audit`, `status`, `doctor`, `init`, `update`. Tudo read-only a menos que `--apply`. |

## Validação

| Script | Função |
|---|---|
| `validate_catalog.py` | valida catálogo de skills e frontmatter |
| `validate_incidents.py` | valida loop de incidentes |
| `verify_adapters.py` | valida pins, licenças, `disabled` e ausência de vendorização nos adapters opcionais. `--check-online` confere shasums no registry (urllib, sem shell). |
| `run_evals.py` | harness provider-agnóstico. `--provider none --no-record` roda os 4 cenários sem credencial; `--suite tasks` roda as 20 tarefas, compara com `BASELINE.json` e falha em regressão; `--write-baseline` registra a medição. `ARGV_PROVIDER` controla o provider (hoje só `opencode`). |
| `eval_checks.py` | verificadores determinísticos das tarefas. Comandos vêm de whitelist fechada, sem shell e sem argv vindo do JSON. |

```bash
python3 -m unittest discover -s tests -v
python3 scripts/verify_adapters.py
python3 scripts/eia.py audit
python3 scripts/run_evals.py --provider none --no-record
python3 scripts/run_evals.py --suite tasks --provider none --no-record
```

## Segurança

- Nenhum script apaga arquivos, faz deploy, reindexa ou rotaciona segredo sem autorização explícita.
- `install.py` falha fechado se o manifesto divergir.
- Backups são timestampados (`*.bak-eia-<UTC>`).
- Nenhuma skill externa é executada sem o gate do `eia-qa-security`.
