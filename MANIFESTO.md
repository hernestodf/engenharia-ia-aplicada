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
| Padrões incompatíveis remanescentes | 0 (`$ARGUMENTS`, `mcp__`, `~/`, `{{...}}`, `/Users/`) |
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
