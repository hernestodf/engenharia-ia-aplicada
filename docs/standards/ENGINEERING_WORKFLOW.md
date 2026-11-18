# Padrão — Ciclo de Engenharia

## Ciclo canônico

```
DISCOVER → AUDIT → SPECIFY → PLAN → IMPLEMENT → TEST → REVIEW → DOCUMENT → DELIVER
```

## Etapas

| Etapa | O que acontece | Saída |
|---|---|---|
| DISCOVER | ler `project.yaml`, `AGENTS.md`, ADRs e o estado real do repo | entendimento do escopo |
| AUDIT | inspecionar arquivos, dependências e riscos **antes de mudar** | achados com evidência |
| SPECIFY | escrever critério de aceite e comportamento esperado | especificação curta |
| PLAN | escolher skills e perfis envolvidos, definir limites | plano com pontos de parada |
| IMPLEMENT | menor mudança necessária | código/documento alterado |
| TEST | executar validações proporcionais ao risco | evidência de passagem ou falha |
| REVIEW | revisão de segurança, qualidade e regressão | achados ou aprovação |
| DOCUMENT | atualizar README, ADR e manifesto quando aplicável | rastro da mudança |
| DELIVER | commits, PR, artefato, rollback preparado | entrega rastreável |

## Regras do loop

- `AUDIT` vem antes de qualquer modificação, em toda iteração.
- `TEST` falhou → volta para `IMPLEMENT` com o erro anexado.
- `REVIEW` achou risco → volta para `PLAN` com o achado.
- Limite de iterações: **3 por ciclo**. Se exceder, para e pergunta ao operador.
- Critério de saída: **evidência**, não aparência de prontidão.
- Falta informação ou autorização? **Para e pergunta.** Nunca inventa.

## Exceções

Tarefas triviais (typos, uma linha, pergunta factual) podem usar o ciclo reduzido:

```
AUDIT → IMPLEMENT → DOCUMENT
```

A redução é explícita, não implícita.

## Proibições

- Pular `AUDIT` em mudança que toca arquivos existentes.
- Marcar algo como "testado" sem ter executado o teste.
- Transformar "parece pronto" em evidência.
- Executar skill externa sem auditoria prévia.
- Deploy, migration destrutiva, reindexação ou rotação de segredo sem autorização.
