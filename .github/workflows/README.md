# CI/CD — workflows

Templates previstos:

| Workflow | Função |
|---|---|
| `ci.yml` | lint, validação de IDs, checagem de padrões proibidos, Gitleaks |
| `cd.yml` | build/artefato, ambiente protegido, aprovação manual |

Permissões mínimas: `contents: read` no CI. Deploy de produção **nunca** automático — exige aprovação.
