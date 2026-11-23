# MANIFESTO Engenharia de IA Aplicada

Registro de proveniência e rastreabilidade do pacote. Nenhuma skill é portada, fundida ou descartada sem rastro aqui.

## Regras aplicadas

1. **Preservação:** os packs originais `autopunk`, `joshua` e `techsaurabh` permanecem intactos em disco.
2. **Portagem:** cada `SKILL.md` é lido integralmente e reescrito como OpenCode-native em `skills/upstream/`, com ID prefixado `op-`.
3. **Limpeza:** `$ARGUMENTS` vira "dados informados pelo usuario na mensagem"; `/comando` vira `skill:<id>` quando o ID existe; `mcp__*` vira `ferramenta externa: servico/ferramenta`; paths absolutos (inclusive `/Users/<usuario>/Desktop/Dev/repos/`) viram `<repo atual>`; `{{...}}` vira `<...>`. **`$0`/`$1` são preservados**: evidência mostrou que são valores monetários (`$2.4M`) e variáveis posicionais de shell (`awk $3`), não argumentos.
4. **Duplicatas idênticas:** uma canônica; as demais viram entrada aqui apontando para ela. Conteúdo idêntico não é perda.
5. **Variantes divergentes:** todas preservadas como `references/` da skill canônica do domínio.
6. **Stubs e ponteiros mortos:** viram nota de descarte com motivo. Nada é apagado silenciosamente.
7. **Segurança:** nenhuma skill externa é executada antes da auditoria de prompt injection, comandos destrutivos, exfiltração e execução arbitrária.

## Estado do mapeamento

FASE 4 concluída. Portagem aplicada e validada:

| Métrica | Valor |
|---|---|
| Skills lidas dos 3 packs | 879 |
| Skills canônicas gravadas | 764 |
| Variantes divergentes em `references/` | 70 |
| Duplicatas idênticas fundidas | 45 |
| IDs finais únicos | 764 / 764 |
| Frontmatter inválido | 0 |
| Padrões incompatíveis remanescentes | 0 na FASE 4 (medição refinada na FASE 5 corrigiu 13 resíduos de `{{course-slug}}` — ver abaixo) |
| Skills carregadas com sucesso via ferramenta `skill` | 3 (PDF, agentes/RAG, SEO/GEO) |

O mapeamento individual origem → destino está em `skills/upstream/MANIFEST.csv`.
O relatório bruto de risco está em `skills/upstream/SECURITY_AUDIT.md`.
A classificação manual dos achados está em `SECURITY_CLASSIFICATION.md`.

## Origem dos packs

| Pacote | Origem | Skills |
|---|---|---|
| `autopunk` | github.com/ur-grue/autopunk-media-skills (MIT) | 408 |
| `joshua` | github.com/JoshuaShepherd/my-skills | 468 |
| `techsaurabh` | github.com/techsaurabh-394/claude-skills (MIT) | 3 |

O número "394" vem do Skills Directory, não de um repositório único.

## FASE 5 — agentes, adapters e nucleus core

**Implementado:** 7 agentes canônicos em `agents/` (6 `subagent` + `eia-router` `primary`); 5 skills `core/` derivadas de `AGENTS.md`/`project.yaml` (`op-eia-router`, `-security-gate`, `-evidence`, `-portability`, `-delivery`); gerador `scripts/generate_adapters.py`; artefatos derivados em `adapters/*/generated/`; `scripts/validate_catalog.py`.

**Testado:** `opencode debug agents` reconhece os 7; 769 symlinks em `~/.claude/skills/` sem quebrados; `skill_mode.py status` reporta 769 ativas/visíveis; `validate_catalog.py` retorna 0 problemas.

**Correção de evidência:** a checagem da FASE 4 usava regex frouxa para `{{...}}` e não detectou 13 ocorrências de `{{course-slug}}` em 9 skills. Todas foram substituídas por `<slug>` na FASE 5. Expressões legítimas do GitHub Actions (`{{ secrets.* }}`, `{{ github.ref }}`) permanecem — são código, não placeholder. A skill `op-eia-portability` é exceção declarada no validador porque documenta os padrões proibidos.

**Não verificado:** execução de LLM (`opencode run`) e Claude CLI (ausente).

## FASE 6–10 — pacote de engenharia

**Implementado:** tokens neutros (`tokens.json`, `tokens.css`), contrato de primitivas e checklist de acessibilidade (FASE 6); 14 testes automatizados (sendo 7 do loop de incidentes) e 4 cenários de avaliação com registro honesto do número histórico não verificado de 430 evals/175 `pending` (FASE 7); loop de aprendizado com revisão humana em `evaluations/incidents/`, 1 incidente fechado e 1 em rascunho; `ci.yml` com `contents: read` e `cd.yml` que só empacota artefato, sem deploy (FASE 8); contrato MCP/Qdrant em modo `contract-only` (FASE 9); operador `scripts/eia.py` com `version`, `audit`, `doctor`, `init`, `update`, dry-run por padrão e diff antes de aplicar (FASE 10).

**Testado localmente:** `validate_catalog.py` → 769 skills, 0 problemas; `unittest` → 14/14 OK; `validate_incidents.py` → 2 incidentes, 0 problemas; ambos os YAMLs parseados com PyYAML; `eia.py version` → `0.1.0`; `audit` → OK; `doctor` → 2 runtimes presentes, Claude ausente, 769 symlinks sem quebrados; `init` em dry-run → diffs vazios contra as configs ativas, nenhuma instalação global.

**Não verificado:** execução real dos workflows no GitHub Actions; contraste, navegação por teclado e zoom em UI concreta; inferência com modelo nos cenários de roteamento e gate de segurança; CLI do Claude; endpoint/collection/embedding/dimensões/métrica do Qdrant.

**Fora de escopo, sem autorização explícita:** deploy, reindexação, alteração de segredos, escrita nos packs originais e no `.git` do `joshua`.

## FASE 11 — integrações opcionais (0.3.0)

**Implementado:** três integrações externas como **referências pinadas**, nenhuma
habilitada e nenhuma com código copiado para o pacote. Auditoria estática dos
pins e das licenças feita por `scripts/verify_adapters.py`; nenhum instalador
externo, servidor ou CLI foi executado.

| Integração | Origem | Licença | Pin | Motivo do formato |
|---|---|---|---|---|
| Chrome DevTools MCP | `ChromeDevTools/chrome-devtools-mcp` | Apache-2.0 | npm `1.13.0`, shasum `e76ecc…` | servidor MCP; template `disabled: true`, sem código vendorizado |
| OpenCodeReview | `alibaba/open-code-review` | Apache-2.0 | npm `1.14.2`, shasum `4459a7…` | CLI externo; modo `delegation` por padrão, sem instalação automática |
| OpenViking | `volcengine/OpenViking` | **AGPL-3.0** | commit `5b7c655…` | licença AGPL e serviço de ~433 MB → adapter, nunca vendorizado |

Skills core derivadas dessa decisão: `op-chrome-devtools-audit`,
`op-open-code-review` e `op-openviking-context`. Todas fazem preflight e param
com `pendente` quando o pré-requisito não está pronto; nenhuma instala, habilita
servidor, reindexa ou rotaciona credencial por conta própria.

**Testado:** `verify_adapters.py` → 3 pinados, 0 problemas; catálogo → 772
skills, 0 problemas; 58/58 testes; manifesto íntegro; zero CJK e zero
`/root/` nos artefatos novos. As três skills foram descobertas pelo runtime em
tempo real, sem restart.

**Não verificado:** conexão efetiva do Chrome DevTools MCP, instalação do `ocr`
e execução de review real, servidor OpenViking/retrieval. Os números de
benchmark publicados pelo OpenViking não são tratados como evidência medida aqui.

**Fora de escopo:** img2threejs (Apache-2.0, 371 arquivos) ficou de fora até
existir caso de uso concreto — vendorizá-lo exigiria manifesto multi-arquivo e
aumentaria a superfície executável em ~46%.

## FASE 12 — avaliação determinística

**Implementado:** 20 tarefas de eval, 16 determinísticas e 4 LLM, com critérios
pontuados de 0 a 2. `scripts/eval_checks.py` só usa verificadores registrados,
comandos de whitelist e caminhos relativos contidos no repo — tarefa é entrada
não confiável e nunca é interpretada como código. Harness grava
`RESULTS_TASKS.jsonl`, suporta `--write-baseline` e falha em regressão.

**Testado:** baseline medido em **42/42 pontos, pass rate 100,0%** nas 16
determinísticas; as 4 LLM ficaram `nao verificado` com provider `none`, fora do
denominador. Regressão provocada de propósito gerou `REGRESSAO: T01: 6 -> 5` e
`pass_rate 1.0 -> 0.9762`, com exit 1; restauração voltou a 1.0. Suite de testes:
**66/66**.

**Não verificado:** julgamento semântico das quatro tarefas LLM; o novo step do
CI no runner. Nenhum benchmark comparativo entre modelos, nenhum fine-tuning e
nenhum dataset rotulado com holdout — isso continua fora do que foi medido.

## FASE 13 — enforcement em código

**Implementado:** `scripts/enforce.py` decide sobre um evento de intenção sem
executar comando, sem rede e sem escrita. Seis regras cobrem destrutivos, alvos
protegidos, produção, segredos, reindexação e origem não confiável. A regra de
origem não confiável exige gate do QA/Security e não é burlada por autorização
explícita. `eia enforce` expõe o gate; `permissions.json` traz bloqueios V2
opt-in, gerados e verificados como artefato derivado.

**Testado:** 14 testes novos, total **80/80 OK**. Execução real do gate com seis
eventos: permitir/0, negar/2 e autorização explícita liberando apenas `R01`–`R05`.
Manifesto regerado com **820 arquivos** integrados.

**Não verificado:** o adapter de permissões não foi mesclado na config global;
nenhum hook de plugin foi ativado; o gate não inspeciona o sistema, apenas a
intenção declarada — comando ofuscado, `eval` e efeito indireto ficam fora.

## FASE 14 — RAG medido

**Implementado:** `scripts/rag_eval.py` mede recuperação lexical BM25 sobre nome e
descrição das 772 skills, com 18 consultas de ground truth verificado. Não há
embedding, rede, vetor store nem reindexação: o contrato Qdrant permanece
`contract-only`. `eia rag-eval` expõe a medição, que falha em regressão.

**Testado:** recall@5 **0,759**, precision@5 0,189 e MRR@10 **0,694** após
corrigir o índice para incluir o ID da skill (medição anterior: 0,704 / 0,178 /
0,637, registrada no guia). Regressão provocada gerou exit 1 e a restauração
voltou a 0. Suite de testes: **90/90**.

**Não verificado:** quatro consultas seguem com recall zero, provável efeito do
desbalanceamento de idioma nas descrições. Ground truth é curado, sem holdout;
nenhum pipeline vetorial foi avaliado.

## FASE 15 — telemetria mínima

**Implementado:** `scripts/telemetry.py` registra eventos locais somente com
`EIA_TELEMETRY=1`. Whitelist fechada de eventos e resultados, campos fixos sem
texto livre, redação de chaves de API e caminhos de usuário, JSONL `0600` com
destino restrito ao pacote. Nenhum socket é aberto e nenhum dado sai da máquina.
`eia telemetry` mostra o estado e o agregado.

**Testado:** 11 testes novos, total **101/101 OK**. Comando real com telemetria
desabilitada reportou `EIA_TELEMETRY=0` e resumo vazio; `eia rag-eval` seguiu com
baseline mantido após as edições no operador.

**Não verificado:** nenhum evento foi gravado de fato, porque a variável não foi
ligada. Telemetria não é avaliação: não substitui os 101 testes, as 20 tarefas
nem o baseline de RAG.
