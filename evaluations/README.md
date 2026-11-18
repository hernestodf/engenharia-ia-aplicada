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
