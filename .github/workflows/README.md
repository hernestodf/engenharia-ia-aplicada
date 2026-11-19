# CI/CD — workflows

| Workflow | Gatilho | Função |
|---|---|---|
| `ci.yml` | push e PR | valida catálogo/incidentes, roda testes + auditoria + harness, checa reproduzibilidade dos adaptadores, integridade do manifesto, whitespace e segredos |
| `release.yml` | tag `v*` ou `workflow_dispatch` | empacota o pacote completo + `SHA256SUMS` e cria Release no GitHub |

## Permissões

- `ci.yml`: `contents: read`.
- `release.yml`: `contents: read` no workflow, `contents: write` **somente** no job `release`, com `environment: production` (exige aprovação).

## Actions pinadas

Todas as actions são pinadas por SHA, obtido via `git ls-remote` em 2026-11-19. O comentário ao lado registra a tag legível:

| Action | Tag | SHA |
|---|---|---|
| `actions/checkout` | v4 | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/setup-python` | v5 | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `gitleaks/gitleaks-action` | v2 | `dcedce43c6f43de0b836d1fe38946645c9c638dc` |
| `actions/upload-artifact` | v4 | `ea165f8d65b6e75b540449e92b4886f43607fa02` |

## Fora dos workflows

Deploy em produção, migration destrutiva, reindexação do Qdrant e rotação de credenciais exigem autorização explícita e mudança deliberada. `release.yml` **não** faz deploy — apenas publica um artefato versionado.

## Estado

- **implementado:** YAMLs, validações no CI, Release por tag, pin por SHA e este README.
- **não verificado:** execução em GitHub Actions (sem `gh`/runner local). Os YAMLs foram parseados localmente, mas o runner não foi observado. A criação da Release depende de `gh`/permissoes no runner.
