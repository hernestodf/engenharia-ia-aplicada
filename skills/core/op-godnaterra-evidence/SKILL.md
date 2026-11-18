---
name: op-godnaterra-evidence
description: Padroniza o ciclo DISCOVER→DELIVER e a saída em implementado/testado/pendente/não verificado. Use ao reportar qualquer trabalho no Godnaterra. Não use para esconder falha sob linguagem de conclusão.
godnaterra/layer: core
godnaterra/source: canonical
---

# Evidência e ciclo Godnaterra

## Ciclo

`DISCOVER → AUDIT → SPECIFY → PLAN → IMPLEMENT → TEST → REVIEW → DOCUMENT → DELIVER`

`AUDIT` vem antes de qualquer mudança, em toda iteração. `TEST`/`REVIEW` podem devolver a `IMPLEMENT` com a evidência do problema. Limite de **3 iterações**; se a terceira não fechar, pare e reporte o que falta. Critério de saída é evidência, não "parece pronto". Se faltar informação ou autorização, o fluxo para e pergunta.

Não transformar isso em burocracia para tarefa trivial.

## Formato de saída

| Estado | Significado |
|---|---|
| **implementado** | arquivo/commit existe e foi inspecionado |
| **testado** | houve comando real, com resultado observado |
| **pendente** | planejado, ainda não feito |
| **não verificado** | ferramenta ausente, ambiente sem acesso, ou não executado |

Nunca escreva "passou" onde cabe "não verificado". Sempre separe as quatro classes.
