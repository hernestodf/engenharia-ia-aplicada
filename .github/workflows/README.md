# CI/CD — workflows

| Workflow | Gatilho | Função |
|---|---|---|
| `ci.yml` | push e PR | valida catálogo e incidentes, roda testes do pacote, checa segredos com Gitleaks |
| `cd.yml` | `workflow_dispatch` | empacota a fonte canônica como artefato; **não faz deploy** |

Permissões mínimas: `contents: read` nos dois. `cd.yml` usa environment `production` para exigir aprovação antes mesmo de empacotar.

Deploy de produção, migration destrutiva, reindexação e rotação de credenciais ficam **fora** destes workflows e exigem autorização explícita.

## Estado (FASE 8)

- **implementado:** YAMLs, validação de incidentes no `ci.yml` e este README.
- **não verificado:** execução em GitHub Actions (sem `gh`/runner aqui). Os YAMLs foram parseados com PyYAML localmente, mas a execução do runner não foi observada.
