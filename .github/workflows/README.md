# CI/CD — workflows

| Workflow | Gatilho | Função |
|---|---|---|
| `ci.yml` | push e PR | valida catálogo/incidentes, roda testes + auditoria + harness, checa reproduzibilidade dos adaptadores, integridade do manifesto, whitespace e segredos |
| `release.yml` | tag `v*` ou `workflow_dispatch` (input `tag` obrigatório) | empacota o pacote completo + `SHA256SUMS` e cria Release no GitHub |

## Dispatch manual

O `workflow_dispatch` **exige** o input `tag` (ex.: `v0.2.1`) e faz checkout **dessa tag**, nunca do HEAD do branch. Guards:

- tag precisa casar `v*`, senão o job falha antes de empacotar;
- `VERSION` precisa ser igual à tag sem o `v` (ex.: `0.2.1` ↔ `v0.2.1`);
- `gh release create ... --verify-tag` recusa tag inexistente.

Isso evita o caso "dispatch em `main` tenta criar Release chamada `main`". O input é lido via `env`, nunca interpolado dentro do shell.

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

- **implementado:** YAMLs, validações no CI, Release por tag e por dispatch com input `tag`, pin por SHA, guards de versão/tag e este README.
- **testado:** run da tag `v0.2.1` (commit `7484c0c`) reportado como **completed successfully** na aba Actions pelo operador. Contrato do workflow coberto por `tests/test_release_workflow.py`.
- **não verificado:** conteúdo visual dos assets da Release (`godnaterra-0.2.1.tar.gz` + `SHA256SUMS`) e execução do dispatch corrigido no runner.
