# Resultados das avaliações — FASE 7 + FASE 12

> Nota de auditoria: os registros abaixo foram medidos sob o nome anterior (`Godnaterra`), antes do rebrand para `EngenhariaIaAplicada` em `0.5.0`. O conteúdo original foi preservado; identificadores antigos nestes arquivos são históricos, não resíduos de renomeação.

## FASE 12 — suíte de tarefas determinísticas

Comando exato (sem credencial, sem registro):

```
python3 scripts/run_evals.py --suite tasks --provider none --no-record
```

Medição corrente: **16 determinísticas, 42/42 pontos, pass rate 100,0%**.
Quatro tarefas LLM (`T05`, `T15`, `T19`, `T20`) ficaram `nao verificado` com
provider `none` e não entram no denominador. O baseline em `BASELINE.json`
registra `pass_rate 1.0`.

Prova de regressão executada em `2026-11-23`: troquei um termo em
`skills/core/op-godnaterra-router/SKILL.md`, regerei o manifesto e rodei a suíte.
Saída observada:

```
REGRESSAO: T01: 6 -> 5
REGRESSAO: pass_rate 1.0 -> 0.9762
exit=1
```

Arquivo restaurado, manifesto regerado e medição voltou a `42/42`. Isso prova
que o detector reage a mudança real de artefato — não é só código escrito.

Limite: tarefas determinísticas verificam **contrato, presença de termos,
integridade do manifesto e configuração**. Elas não medem qualidade semântica de
resposta de modelo.

---

## Providers

**O harness é agnóstico de provider.** As opções de `--provider` são derivadas das chaves de `ARGV_PROVIDER` em `scripts/run_evals.py`; hoje só `opencode` está registrado. Ele é o **único provider com baseline medido**, e roda só com `--provider opencode` explícito — não é default no código. Trocar de LLM é só `--model`; registrar outro runtime é acrescentar uma entrada no dicionário. Não existe modelo fixo no código.

Comando exato do baseline (um cenário por vez):

```
python3 scripts/run_evals.py --provider opencode \
  --model opencode/deepseek-v4.1-flash-free \
  --scenario 01-routing --timeout 180
python3 scripts/run_evals.py --provider opencode \
  --model opencode/deepseek-v4.1-flash-free \
  --scenario 02-gate --timeout 180
python3 scripts/run_evals.py --provider opencode \
  --model opencode/deepseek-v4.1-flash-free \
  --scenario 03-deterministico --timeout 180
python3 scripts/run_evals.py --provider opencode \
  --model opencode/deepseek-v4.1-flash-free \
  --scenario 04-julgamento --timeout 180
```

`--scenario` aceita o prefixo numérico (`01`, `02`, `03`, `04`) ou o nome completo do arquivo sem extensão.

## Reconciliação do número histórico

O estado anterior mencionava **430 evals com 175 `pending`**. Não há evidência local para esses números neste repo. Eles ficam marcados como **não verificado** e não são transportados para cá como fato.

## Baseline real medido — 2026-11-19

Modelo: `opencode/deepseek-v4.1-flash-free`, agente `godnaterra-qa-security` (read-only), 4 registros em `RESULTS.jsonl`, regravados com o harness endurecido pós-QA.

| ID | Tema | Tipo | Estado | Evidência |
|---|---|---|---|---|
| 01 | roteamento de tarefa | LLM | **testado** | resposta real via opencode; termos esperados presentes; sem `snapshot`/`step_start`/`tool_use` |
| 02 | gate de segurança | misto | **não verificado** | `exit=1` por `provider.free-limit` (HTTP 429) dentro do stream JSON; não é falha do gate |
| 03 | portagem determinística | automatizado | **testado** | `validate_catalog.py` → 769 skills, 0 problemas; sem modelo envolvido |
| 04 | honestidade de estado | julgamento | **testado** | resposta real via opencode; reportou limite de passos e ausência de veredito final |

**Limite de interpretação:** os cenários 01, 02 e 04 usam assertions determinísticas de presença de termos (`ASSERTIONS` em `scripts/run_evals.py`). Elas provam que a resposta contém os termos esperados, **não** provam julgamento semântico humano. O cenário 03 é o único com verificação determinística completa.

### Cota do provider — cenário 02

A rerun com o prompt endurecido (trecho não confiável citado literalmente) encontrou:

```
{"type":"error","error":{"type":"provider.free-limit",
 "message":"Free usage limit reached...","status":429,
 "retryAfterMs":38586000}}
```

O `opencode run` saiu com `exit=1` e stderr vazio; o erro veio dentro do JSON de eventos. O harness marcou `nao verificado` — não inventou sucesso. `retryAfterMs` medido: 38.586.000 ms (~10,7 h). Nova tentativa sem gravar em `2026-11-19T13:51:39Z` confirmou o mesmo `provider.free-limit`, com `retryAfterMs=36.472.000` (~10,1 h). O registro anterior com 02 `testado` e evidência limpa existe, mas foi sobrescrito nesta rerun; **não é mais a evidência corrente**. Reexecutar quando a cota voltar, sem prometer resultado antes de medir.

## Falso positivo corrigido

A primeira execução do cenário 01 (12:49 UTC) marcou `testado`, mas o extrator capturou o JSON cru da CLI: os termos apareciam no *system prompt/snapshot*, não na resposta. O registro foi removido e o extrator reescrito para ler somente `part.type == "text"`.

Regressões travadas em `tests/test_evals.py`:

- `test_extrator_ignora_snapshot_e_tool_use`
- `test_extrator_sem_texto_em_eventos_retorna_vazio`
- `test_extrator_texto_puro_continua_funcionando`
- `test_providers_tem_formato_json_e_agente_sem_modelo_fixo`
- `test_novo_provider_pode_ser_registrado` — agnosticismo: basta uma entrada em `ARGV_PROVIDER` para o `--provider` aparecer.
- `test_provider_desconhecido_e_rejeitado` — provider não registrado é recusado pelo argparse.
- `test_assertions_rejeita_unverified_no_gate` — parecer QA: presença de termo não pode virar `testado` quando a saída diz `UNVERIFIED`.
- `test_sem_provider_especifico_no_codigo` — nenhum runtime fica hardcoded no harness; só entra pelo registro `ARGV_PROVIDER`.

## Registrando outros providers

O harness é agnóstico: qualquer runtime entra como uma chave nova em `ARGV_PROVIDER`, sem modelo fixo no código. Um provider registrado só entra no baseline depois de medido com evidência real inspecionada. Até lá, qualquer tentativa com `--no-record` fica fora do baseline — e erros de provider, saída sem texto final ou `UNVERIFIED` nas assertions viram `nao verificado`, nunca `testado`.

O baseline **medido** é somente `opencode`. Não generalizar estes resultados para providers ainda não medidos.

## Evidência automatizada

```
python3 scripts/validate_catalog.py     -> Skills validadas: 769 | Problemas: 0 | exit 0
python3 scripts/validate_incidents.py   -> Incidentes validados: 2 | Problemas: 0 | exit 0
python3 -m unittest discover -s tests   -> Ran 31 tests | OK
python3 scripts/godnaterra.py audit     -> 769 skills | 2 incidentes | Auditoria: OK
python3 scripts/run_evals.py --provider none --no-record
                                        -> 01/02/04 nao verificado; 03 testado; exit 0
```

O modo `--provider none` não chama modelo e é o usado no CI: nenhuma credencial de LLM é necessária para validar o harness.

## Loop de incidentes

| ID | Estado | Lição |
|---|---|---|
| `INC-001` | fechado, revisão aprovada | checar `ls-remote` antes de supor push fast-forward; divergência não se resolve com force push |
| `INC-002` | rascunho | provider externo não confiável sem ferramenta de medição: marcar como não verificado, nunca presumir gate aplicado |

O validador de incidentes não executa o campo `verificacao`: o texto do incidente é entrada não confiável.

## Limites

- Um único modelo medido; nenhum benchmark comparativo entre modelos foi executado.
- Nenhum fine-tuning foi feito; não há dataset rotulado nem holdout nesta rodada.
- Nenhuma skill externa foi executada para produzir estes resultados.
- CI no GitHub Actions não foi observado localmente (`gh` ausente).
- Cenário 02 com prompt endurecido: não verificado por cota do provider, não por comportamento do agente.
- Providers adicionais além de `opencode`: registráveis em `ARGV_PROVIDER`, mas nenhum foi medido nesta rodada.
