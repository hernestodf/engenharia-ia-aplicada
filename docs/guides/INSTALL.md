# Guia — Instalação e Rollback

## Instalação no OpenCode

1. O `~/.config/opencode/opencode.json` deve apontar **somente** para o catálogo ativo:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": [
    "/root/.config/opencode/skill-packs/godnaterra/skills/upstream"
  ]
}
```

2. Os packs originais permanecem em disco (`autopunk`, `joshua`, `techsaurabh`) mas não são carregados ao mesmo tempo. Isso evita IDs duplicados. O backup da config anterior está em `~/.config/opencode/opencode.json.bak-godnaterra`.

3. Modos disponíveis via `python3 ~/.config/opencode/skill_mode.py`:

| Modo | Efeito |
|---|---|
| `godnaterra` | padrão — todas as 764 skills visíveis |
| `god` | alias de `godnaterra` (todas visíveis) |
| `curated` | legado de 31 skills |
| `status` | só reporta contagem da raiz ativa |

## Rollback

Se algo falhar:

1. Restaurar o `opencode.json` anterior com os 3 caminhos dos packs originais:
   `cp ~/.config/opencode/opencode.json.bak-godnaterra ~/.config/opencode/opencode.json`
2. Rodar `python3 ~/.config/opencode/skill_mode.py god` para voltar ao estado anterior.
3. Os packs originais não foram alterados — o rollback é imediato.

## Validação pós-instalação (FASE 4 — concluída)

| Verificação | Resultado |
|---|---|
| JSON do config válido | ✅ |
| IDs únicos (sem colisão `op-`) | ✅ 764/764 |
| `$ARGUMENTS` remanescente | ✅ 0 |
| `$0` / `$1` | ✅ **preservados** — são valores monetários e variáveis shell, não argumentos |
| Paths absolutos de projeto remanescentes | ✅ 0 (`/Users/`, `~/`, `Desktop/dev/repos`) |
| `{{...}}` remanescente | ✅ 0 |
| `mcp__*` sem equivalente documentado | ✅ 0 |
| Frontmatter inválido | ✅ 0 |
| 3 skills de áreas diferentes carregadas | ✅ PDF, agentes/RAG, SEO/GEO |

## Fora do escopo da instalação

- reindexação do Qdrant
- criação de collection
- rotação de credenciais
- deploy em produção
- alteração no `.git` do `joshua`

Todos exigem autorização explícita.
