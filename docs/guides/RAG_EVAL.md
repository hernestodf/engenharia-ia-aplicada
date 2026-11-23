# RAG medido — baseline lexical

Este guia descreve **o que foi medido**, não o que se espera medir. Não há embedding, vetor store, rede ou reindexação. O contrato do Qdrant permanece `contract-only`.

## O que é

Um avaliador BM25 determinístico sobre **nome + descrição** das 772 skills do catálogo local. Ground truth: 18 consultas em `evaluations/rag/queries.jsonl`, com IDs relevantes verificados contra o corpus real.

Não é um teste de modelo, não mede LLM e não substitui avaliação de um pipeline vetorial. É uma régua de retrieval lexical para detectar regressão quando o catálogo muda.

## Como rodar

```bash
python3 scripts/rag_eval.py
python3 scripts/eia.py rag-eval
python3 scripts/rag_eval.py --write-baseline
python3 scripts/rag_eval.py --no-compare
```

Saída: `evaluations/rag/RESULTS.json` (sempre) e `evaluations/rag/BASELINE.json` (só com `--write-baseline`). Código de saída `1` quando alguma métrica macro cai mais que `0.001` — a diferença é reportada como `REGRESSAO: ...`.

## Número medido

Execução em 2026-11-23, corpus de 772 skills, 18 consultas, `k=5` e MRR em `k=10`:

| Métrica | Valor |
|---|---|
| recall@5 | **0,759** |
| precision@5 | **0,189** |
| MRR@10 | **0,694** |

Primeira medição, **antes** de indexar o ID da skill (somente descrição): recall@5 0,704, precision@5 0,178, MRR@10 0,637. O índice foi corrigido para incluir nome + descrição e as duas medições estão registradas aqui — a melhora não é disfarçada.

Regressão provocada de propósito (trocar o ground truth de `Q01` por um ID inexistente): `REGRESSAO: recall_at_5: 0.759259 -> 0.722222`, exit **1**. Restauração: baseline mantido, exit **0**.

## Limitações (declaração honesta)

- 4 das 18 consultas ainda falham em recall@5: Q02 (Excel), Q08 (currículo), Q15 (design system) e Q18 (rotas/Playwright). Causa provável: descrições majoritariamente em inglês e consultas em português, além de vocabulário específico de domínio.
- precision@5 de 0,189 é baixa porque a maioria das consultas tem 1 documento relevante num catálogo de 772 — esperado para recall-oriented retrieval.
- O ground truth é **curado por humanos**, não amostrado de produção. Não há holdout, não há inferência de modelo e não há comparação entre providers.
- BM25 não entende sinônimos, tradução ou intenção. Um número maior aqui não provaria que um pipeline vetorial é bom; um número menor não provaria que ele é ruim.
- Nenhum índice foi construído em Qdrant, nenhuma collection foi tocada, nenhuma reindexação foi feita.

## Arquivos

| Arquivo | Papel |
|---|---|
| `evaluations/rag/queries.jsonl` | 18 consultas com ground truth |
| `evaluations/rag/BASELINE.json` | baseline versionado |
| `evaluations/rag/RESULTS.json` | última execução |
| `scripts/rag_eval.py` | avaliador determinístico |
| `tests/test_rag_eval.py` | 10 testes, corpus em memória |
