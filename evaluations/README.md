# evaluations

Cenários e tarefas de avaliação de skills e agentes. Entrada de tarefa é **entrada não confiável**: nunca é interpretada como código nem vira argv de comando externo.

Os números históricos (430 evals / 175 `pending`) são **não verificados** neste repo; ver `RESULTS.md`.

## Dois conjuntos

| Conjunto | Arquivos | Finalidade |
|---|---|---|
| Cenários | `scenarios/01`–`04` | baseline histórico de 4 cenários, com assertions de termos |
| Tarefas | `tasks/01`–`04` | 20 tarefas pontuadas, 16 determinísticas e 4 LLM |

| Arquivo | Finalidade |
|---|---|
| `scenarios/01-routing.md` | roteamento para um único papel |
| `scenarios/02-security-gate.md` | bloqueio de conteúdo não confiável |
| `scenarios/03-portability.md` | portagem determinística e regressão `{{course-slug}}` |
| `scenarios/04-unverified.md` | honestidade de estado |
| `tasks/01-roteamento.json` | roteamento, frontmatter e regras do AGENTS.md |
| `tasks/02-seguranca.json` | gate, ações destrutivas, adapters e OpenViking |
| `tasks/03-evidencia.json` | quatro estados, cota do provider, sanitização |
| `tasks/04-entrega.json` | manifesto, release, instalação isolada, revisão e recusa |
| `BASELINE.json` | medição de referência das determinísticas |
| `RESULTS.jsonl` | registros dos 4 cenários |
| `RESULTS_TASKS.jsonl` | registros das 20 tarefas |
| `RESULTS.md` | o que foi realmente executado |

Cada critério determinístico vale 0–2. A nota é soma dos critérios; a tarefa passa se tirar o máximo. Quatro tarefas LLM exigem provider: sem ele ficam `nao verificado` e **fora do denominador**.

## Harness executável

`scripts/run_evals.py` roda os dois conjuntos e grava JSONL já sanitizado.

- **Agnóstico de provider:** `--provider` vem das chaves de `ARGV_PROVIDER`. Registrar outro runtime é uma entrada nova, sem modelo fixo.
- **Sem modelo:** `--provider none` — determinístico, usado no CI, sem credencial.
- **Cenários (padrão):** `python3 scripts/run_evals.py --provider none --no-record`
- **Tarefas:** `python3 scripts/run_evals.py --suite tasks --provider none --no-record`
- **Registrar baseline:** `python3 scripts/run_evals.py --suite tasks --provider none --write-baseline`
- **Comparar:** sem `--no-compare`, o comando falha se alguma determinística cair de nota ou se o pass rate cair.

Exemplo com inferência real:

```
python3 scripts/run_evals.py --provider opencode \
  --model opencode/deepseek-v4.1-flash-free \
  --scenario 01-routing --timeout 180
```

`scripts/eval_checks.py` é a única ponte entre o JSON da tarefa e o filesystem. Comandos executáveis estão numa whitelist fechada (`validate_catalog`, `verify_adapters`, `manifesto_check`), sempre com `shell=False` e argv fixo. Caminhos absolutos e `..` são rejeitados.

## Resultado medido (provider `none`)

16 determinísticas, **42/42 pontos, pass rate 100,0%**, 4 tarefas LLM `nao verificado`. Regressão provocada em `T01` gerou `REGRESSAO: T01: 6 -> 5` e `pass_rate 1.0 -> 0.9762`, exit 1. Isso é verificação de contrato e regressão de artefato, **não** julgamento semântico de modelo.

Cenários com LLM não são marcados como testados sem execução real registrada. Assertions de termos provam presença, não entendimento. Erros de provider e saída sem texto final viram `nao verificado`, nunca `testado`.
