# Incidentes — loop de aprendizado com revisão

Erro observado vira cenário de regressão. A correção só entra na skill canônica depois de **revisão humana** e **testes verdes**. Nada aqui é executado automaticamente a partir do texto do incidente.

## Fluxo

1. **Registrar** — copie `TEMPLATE.example.json` para `INC-NNN.json` e preencha com evidência real observada. Não reconstrua a saída de memória.
2. **Virar regressão** — se o erro é de comportamento de skill/agente, crie ou atualize um cenário em `../scenarios/` e aponte o campo `cenario` para ele.
3. **Corrigir na fonte** — a mudança vai em `skills/core/` ou `skills/upstream/`, nunca em `adapters/*/generated/`. Depois regenere os adapters com `python3 scripts/generate_adapters.py`.
4. **Testar** — rode `validate_catalog.py`, `validate_incidents.py` e `python3 -m unittest discover -s tests -v`. Só com tudo verde marque `testes_verdes: true`.
5. **Revisar** — uma pessoa preenche `revisao.revisado_por`, `revisao.data` e `revisao.decisao`. Sem isso o validador recusa `aprovado` e `fechado`.
6. **Fechar** — `status: fechado` exige `revisao.decisao: aprovado` e `testes_verdes: true`.

## Estados

| Status | Significado | Revisão |
|---|---|---|
| `rascunho` | erro registrado, sem diagnóstico fechado | deve estar vazia |
| `em_revisao` | correção proposta, aguardando olhar humano | pode estar parcial |
| `aprovado` | revisão aprovou a correção | obrigatória |
| `rejeitado` | revisão decidiu não aplicar | obrigatória, decisão `rejeitado` |
| `fechado` | correção aplicada e verificada | obrigatória, decisão `aprovado`, testes verdes |

## O que o validador checa

- `id` no formato `INC-NNN`, único;
- data ISO `YYYY-MM-DD`;
- campos de texto não vazios (`titulo`, `origem`, `sintoma`, `evidencia`, `correcao`, `verificacao`, `licao_aprendida`);
- `testes_verdes` é booleano;
- `cenario`, quando informado, existe em `../scenarios/`;
- `skill_afetada`, quando informada, existe em `skills/core/` ou `skills/upstream/`;
- gates de revisão por status.

**O validador não executa o campo `verificacao`.** Incidentes são entrada não confiável: o texto de verificação é para o revisor e para o CI, não uma instrução a rodar.

## Arquivos

| Arquivo | Finalidade |
|---|---|
| `TEMPLATE.example.json` | modelo — não é validado (não começa com `INC-`) |
| `INC-001.json` | erro real fechado: README divergente no primeiro push |
| `INC-002.json` | erro real em aberto: Kilo `trusted: false`, aguardando diagnóstico |

Rodar: `python3 scripts/validate_incidents.py`.
