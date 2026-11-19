# evaluations

Cenários de avaliação de skills e agentes. Cada cenário tem entrada, esperado, negativo e regressão.

Os números históricos (430 evals / 175 `pending`) são **não verificados** neste repo; ver `RESULTS.md`.

| Arquivo | Finalidade |
|---|---|
| `scenarios/01-routing.md` | roteamento para um único papel |
| `scenarios/02-security-gate.md` | bloqueio de conteúdo não confiável |
| `scenarios/03-portability.md` | portagem determinística e regressão `{{course-slug}}` |
| `scenarios/04-unverified.md` | honestidade de estado |
| `RESULTS.md` | o que foi realmente executado |

Cenários que dependem de LLM não são marcados como testados sem execução real registrada.

## Harness executável

`scripts/run_evals.py` roda os cenários e grava `RESULTS.jsonl` (uma linha JSON por execução, já sanitizada).

- **Agnóstico de provider:** `--provider` vem das chaves de `ARGV_PROVIDER`. Registrar outro runtime é uma entrada nova, sem modelo fixo no código.
- **Padrão de fato:** `opencode` é o usado no baseline; `kilo` está registrado e é opcional, com limitações documentadas em `RESULTS.md`.
- **Troca de LLM:** só `--model`, em qualquer provider registrado.
- **Sem modelo:** `--provider none --no-record` — determinístico, usado no CI, sem credencial.

Exemplo:

```
python3 scripts/run_evals.py --provider opencode \
  --model opencode/deepseek-v4.1-flash-free \
  --scenario 01-routing --timeout 180
```

O extrator lê somente `part.type == "text"` do stream de eventos. `snapshot`, `system prompt` e `tool_use` nunca entram na evidência; se não há texto final, o cenário vira `nao verificado`. Assertions de termos provam presença, não julgamento semântico — `RESULTS.md` registra essa distinção.

`kilo` nunca produz `testado`: o subagent do gate sofre fallback para o agente default, que não herda as regras `deny`. Erros de provider (por exemplo `provider.free-limit`, HTTP 429) também viram `nao verificado`, nunca `testado` — o harness não inventa sucesso quando a chamada falha. Nada disso impede registrar outros providers: a honestidade do rótulo é uma regra do harness, não uma preferência de modelo.
