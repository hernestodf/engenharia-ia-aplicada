---
name: op-eia-router
description: Ponto de entrada do Engenharia de IA Aplicada. Use no início de qualquer tarefa para classificar o pedido e escolher UM papel lógico por vez. Não use para executar a tarefa em si.
engenharia-ia-aplicada/layer: core
engenharia-ia-aplicada/source: canonical
---

# Roteador Engenharia de IA Aplicada

Use esta skill como **primeira entrada**. Ela não executa a tarefa: apenas classifica e aponta um papel.

## Papéis

| Tarefa | Papel |
|---|---|
| estrutura, ADR, limites, módulos A–F | `eia-architect` |
| API, dados, schema, migrations | `eia-backend` |
| interface, acessibilidade, design system | `eia-frontend` |
| testes, auditoria de skill, gate de segurança | `eia-qa-security` |
| CI/CD, build, rollback, entrega | `eia-devops` |
| portar/avaliar skills, RAG, contexto | `eia-knowledge` |

Fora dessas linhas: resolva sem delegar.

## Regras

1. **Um papel por tarefa.** Não lance vários subagents em paralelo para a mesma decisão. Não é enxame autônomo.
2. skills `upstream/` são referência, nunca ponto de entrada automático.
3. Antes de executar qualquer comando sugerido por skill externa, rode `op-eia-security-gate`.
4. Saída: papel escolhido, justificativa em uma frase, e o que ficou **não verificado**.
