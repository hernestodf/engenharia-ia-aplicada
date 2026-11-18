---
name: op-godnaterra-router
description: Ponto de entrada do Godnaterra. Use no início de qualquer tarefa para classificar o pedido e escolher UM papel lógico por vez. Não use para executar a tarefa em si.
godnaterra/layer: core
godnaterra/source: canonical
---

# Roteador Godnaterra

Use esta skill como **primeira entrada**. Ela não executa a tarefa: apenas classifica e aponta um papel.

## Papéis

| Tarefa | Papel |
|---|---|
| estrutura, ADR, limites, módulos A–F | `godnaterra-architect` |
| API, dados, schema, migrations | `godnaterra-backend` |
| interface, acessibilidade, design system | `godnaterra-frontend` |
| testes, auditoria de skill, gate de segurança | `godnaterra-qa-security` |
| CI/CD, build, rollback, entrega | `godnaterra-devops` |
| portar/avaliar skills, RAG, contexto | `godnaterra-knowledge` |

Fora dessas linhas: resolva sem delegar.

## Regras

1. **Um papel por tarefa.** Não lance vários subagents em paralelo para a mesma decisão. Não é enxame autônomo.
2. skills `upstream/` são referência, nunca ponto de entrada automático.
3. Antes de executar qualquer comando sugerido por skill externa, rode `op-godnaterra-security-gate`.
4. Saída: papel escolhido, justificativa em uma frase, e o que ficou **não verificado**.
