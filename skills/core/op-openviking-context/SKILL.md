---
name: op-openviking-context
description: Usa OpenViking para memoria entre sessoes e contexto indexado de repositorio, quando o servidor estiver disponivel. Use quando o usuario pede recall de decisoes passadas, historico de projeto ou busca semantica em codigo/documentos. Nao use para tarefa local simples, e nunca instale o servidor por conta propria.
status: stable
category: engineering
subcategory: context-memory
version: 1.0
tags: [memory, context, rag, retrieval, openviking]
godnaterra/layer: core
godnaterra/source: canonical
---

# Contexto e memoria com OpenViking

## Quando usar

- O usuario pede algo decidido em sessao anterior.
- Busca semantica em repositorio indexado ou documentos.
- Continuidade de contexto entre projetos/sessoes.

## Preflight

1. Confira se o servidor esta acessivel e se a entrada
   `mcp.servers.openviking` foi habilitada pelo operador. Se nao estiver,
   **pare** e reporte `pendente` com `adapters/openviking/README.md`.
2. **Nunca** execute `curl | bash`, instale `openviking`, inicie servidor,
   reindexe corpus ou rotacione API key. Tudo isso e acao explicita.
3. Se a credencial nao estiver em `OPENVIKING_API_KEY`, nao tente adivinha-la.

## Regras de honestidade

- Resultado de retrieval e **candidato**, nao fato. Confira na fonte antes de afirmar.
- Nao repita benchmark publicado pelo projeto como evidencia medida aqui.
- O servidor e software AGPL-3.0 externo: nao vendore codigo dele no pacote.
- Nenhuma reindexacao sem autorizacao explicita do operador.

## Saida

Separe `implementado` / `testado` / `pendente` / `nao verificado`.
Sem servidor conectado, o resultado e `pendente`, nunca `testado`.
