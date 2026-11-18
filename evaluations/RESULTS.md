# Resultados das avaliações — FASE 7

## Reconciliação do número histórico

O estado anterior mencionava **430 evals com 175 `pending`**. Não há evidência local para esses números neste repo. Eles ficam marcados como **não verificado** e não são transportados para cá como fato.

## Cenários locais

| ID | Tema | Tipo | Estado |
|---|---|---|---|
| 01 | roteamento de tarefa | LLM | não verificado |
| 02 | gate de segurança | misto | implementado; LLM não verificado |
| 03 | portagem determinística | automatizado | testado |
| 04 | honestidade de estado | julgamento | implementado na doc; LLM não verificado |

## Evidência automatizada

```
python3 scripts/validate_catalog.py    -> Skills validadas: 769 | Problemas: 0 | exit 0
python3 scripts/validate_incidents.py  -> Incidentes validados: 2 | Problemas: 0 | exit 0
python3 -m unittest discover -s tests  -> Ran 15 tests | OK
python3 scripts/godnaterra.py audit    -> 769 skills | 2 incidentes | Auditoria: OK
```

## Loop de incidentes

| ID | Estado | Lição |
|---|---|---|
| `INC-001` | fechado, revisão aprovada | checar `ls-remote` antes de supor push fast-forward; divergência não se resolve com force push |
| `INC-002` | rascunho | sem ferramenta de medição do estado de confiança do Kilo, marcar como não verificado |

O validador de incidentes não executa o campo `verificacao`: o texto do incidente é entrada não confiável.

## Limites

Nenhum cenário foi executado com modelo real. Não afirmar que roteamento ou gate de segurança funcionam em inferência — apenas que estão especificados e que as verificações estáticas passaram.
