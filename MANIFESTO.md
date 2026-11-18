# MANIFESTO Godnaterra

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

**Implementado:** 7 agentes canônicos em `agents/` (6 `subagent` + `godnaterra-router` `primary`); 5 skills `core/` derivadas de `AGENTS.md`/`project.yaml` (`op-godnaterra-router`, `-security-gate`, `-evidence`, `-portability`, `-delivery`); gerador `scripts/generate_adapters.py`; artefatos derivados em `adapters/*/generated/`; `scripts/validate_catalog.py`.

**Testado:** `opencode debug agents` reconhece os 7; `kilo debug skill` lista 769 skills `op-` sem duplicatas; `kilo debug agent` confirma os papéis e a ordem das permissões; `kilo debug config` mostra as duas raízes; 769 symlinks em `~/.claude/skills/` sem quebrados; `skill_mode.py status` reporta 769 ativas/visíveis; `validate_catalog.py` retorna 0 problemas.

**Correção de evidência:** a checagem da FASE 4 usava regex frouxa para `{{...}}` e não detectou 13 ocorrências de `{{course-slug}}` em 9 skills. Todas foram substituídas por `<slug>` na FASE 5. Expressões legítimas do GitHub Actions (`{{ secrets.* }}`, `{{ github.ref }}`) permanecem — são código, não placeholder. A skill `op-godnaterra-portability` é exceção declarada no validador porque documenta os padrões proibidos.

**Não verificado:** execução de LLM (`opencode run` / `kilo run`), Claude CLI (ausente), e o motivo do flag `trusted: false` reportado pelo CLI do Kilo em skills de path externo.

