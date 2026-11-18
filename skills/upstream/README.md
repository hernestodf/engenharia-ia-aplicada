# skills/upstream

As 879 skills dos packs originais portadas para OpenCode-native, com prefixo `op-`.

Origem → destino, duplicatas e descartes: ver `../../MANIFESTO.md`.

Regras de limpeza aplicadas na portagem (FASE 4):

- `$ARGUMENTS`, `$0`, `$1` → dados informados pelo usuário na mensagem
- `/comando` → `skill:<id>`
- `mcp__*` → ferramenta externa equivalente (documentada)
- paths absolutos → `<repo atual>`
- `{{...}}` → `<...>`
