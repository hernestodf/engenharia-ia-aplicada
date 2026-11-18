# MANIFESTO Godnaterra

Registro de proveniência e rastreabilidade do pacote. Nenhuma skill é portada, fundida ou descartada sem rastro aqui.

## Regras aplicadas

1. **Preservação:** os packs originais `autopunk`, `joshua` e `techsaurabh` permanecem intactos em disco.
2. **Portagem:** cada `SKILL.md` é lido integralmente e reescrito como OpenCode-native em `skills/upstream/`, com ID prefixado `op-`.
3. **Limpeza:** `$ARGUMENTS`, `$0`, `$1` viram "dados informados pelo usuário na mensagem"; `/comando` vira `skill:<id>`; `mcp__*` vira ferramenta externa equivalente; paths absolutos viram `<repo atual>`; `{{...}}` vira `<...>`.
4. **Duplicatas idênticas:** uma canônica; as demais viram entrada aqui apontando para ela. Conteúdo idêntico não é perda.
5. **Variantes divergentes:** todas preservadas como `references/` da skill canônica do domínio.
6. **Stubs e ponteiros mortos:** viram nota de descarte com motivo. Nada é apagado silenciosamente.
7. **Segurança:** nenhuma skill externa é executada antes da auditoria de prompt injection, comandos destrutivos, exfiltração e execução arbitrária.

## Estado do mapeamento

FASE 3 concluída: estrutura canônica criada.

O mapeamento completo origem → destino das 879 skills será anexado a este arquivo na FASE 4, junto com:
- contagem de portadas, fundidas e descartadas;
- motivos individuais de cada descarte;
- lista de variantes divergentes preservadas;
- resultado da validação (IDs únicos, JSON válido, zero padrões incompatíveis).

## Origem dos packs

| Pacote | Origem | Skills |
|---|---|---|
| `autopunk` | github.com/ur-grue/autopunk-media-skills (MIT) | 408 |
| `joshua` | github.com/JoshuaShepherd/my-skills | 468 |
| `techsaurabh` | github.com/techsaurabh-394/claude-skills (MIT) | 3 |

O número "394" vem do Skills Directory, não de um repositório único.
