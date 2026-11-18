# Guia — Instalação e Rollback

## Instalação no OpenCode

1. O `~/.config/opencode/opencode.json` deve apontar **somente** para:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": [
    "/root/.config/opencode/skill-packs/godnaterra"
  ]
}
```

2. Os packs originais permanecem em disco (`autopunk`, `joshua`, `techsaurabh`) mas não são carregados ao mesmo tempo. Isso evita IDs duplicados.

3. Modos disponíveis via `python3 ~/.config/opencode/skill_mode.py`:

| Modo | Efeito |
|---|---|
| `godnaterra` | padrão — todas as skills visíveis |
| `essencial` | core + melhores upstream |
| `curado` | legado de 31 skills |
| `status` | só reporta contagem |

## Rollback

Se algo falhar:

1. Restaurar o `opencode.json` anterior com os 3 caminhos dos packs originais.
2. Rodar `python3 ~/.config/opencode/skill_mode.py god` para voltar ao estado anterior.
3. Os packs originais não foram alterados — o rollback é imediato.

## Validação pós-instalação (FASE 4)

- [ ] JSON do config válido
- [ ] IDs únicos (sem colisão `op-`)
- [ ] nenhum `$ARGUMENTS`, `$0`, `$1` remanescente
- [ ] nenhum path absoluto de projeto remanescente
- [ ] nenhum `mcp__*` sem equivalente documentado
- [ ] 3 skills de áreas diferentes carregadas com sucesso

## Fora do escopo da instalação

- reindexação do Qdrant
- criação de collection
- rotação de credenciais
- deploy em produção
- alteração no `.git` do `joshua`

Todos exigem autorização explícita.
