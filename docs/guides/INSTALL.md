# Guia — Instalação e Rollback

## Instalação no OpenCode

1. O `~/.config/opencode/opencode.json` deve apontar **somente** para o catálogo ativo:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": [
    "/root/.config/opencode/skill-packs/godnaterra/skills/core",
    "/root/.config/opencode/skill-packs/godnaterra/skills/upstream"
  ]
}
```

2. Os packs originais permanecem em disco (`autopunk`, `joshua`, `techsaurabh`) mas não são carregados ao mesmo tempo. Isso evita IDs duplicados. O backup da config anterior está em `~/.config/opencode/opencode.json.bak-godnaterra`.

3. Modos disponíveis via `python3 ~/.config/opencode/skill_mode.py`:

| Modo | Efeito |
|---|---|
| `godnaterra` | padrão — todas as 769 skills visíveis (5 core + 764 upstream) |
| `god` | alias de `godnaterra` (todas visíveis) |
| `curated` | legado de 31 skills |
| `status` | só reporta contagem da raiz ativa |

## Rollback

Se algo falhar:

1. Restaurar o `opencode.json` anterior com os 3 caminhos dos packs originais:
   `cp ~/.config/opencode/opencode.json.bak-godnaterra ~/.config/opencode/opencode.json`
2. Rodar `python3 ~/.config/opencode/skill_mode.py god` para voltar ao estado anterior.
3. Os packs originais não foram alterados — o rollback é imediato.

## Validação pós-instalação (FASE 5 — concluída)

| Verificação | Resultado |
|---|---|
| JSON do config válido | ✅ duas raízes |
| IDs únicos (sem colisão `op-`) | ✅ 769/769 |
| `$ARGUMENTS` remanescente | ✅ 0 (exceto citação intencional na skill de portagem) |
| `$0` / `$1` | ✅ **preservados** — são valores monetários e variáveis shell, não argumentos |
| Paths absolutos de projeto remanescentes | ✅ 0 (`/Users/`, `~/`, `Desktop/dev/repos`) |
| `{{...}}` remanescente | ✅ 0 resíduos de `{{course-slug}}`; expressões `{{ secrets.* }}` do GitHub Actions são código legítimo |
| `mcp__*` sem equivalente documentado | ✅ 0 (exceto citação intencional na skill de portagem) |
| Frontmatter inválido | ✅ 0 |
| Agentes reconhecidos | ✅ 7 (`opencode debug agents`) |
| Skills carregadas no Kilo | ✅ 769 `op-`, sem duplicatas |
| Symlinks Claude | ✅ 769, 0 quebrados — **CLI ausente**, formato não executado |

Reproduzir: `python3 scripts/validate_catalog.py` e `python3 -m unittest discover -s tests -v`.

## Comandos do operador (FASE 10)

```bash
python3 scripts/godnaterra.py version                 # versão do pacote
python3 scripts/godnaterra.py audit                   # catálogo + JSONs derivados
python3 scripts/godnaterra.py doctor                  # runtimes, configs e backups (leitura)
python3 scripts/godnaterra.py init                    # DRY-RUN: mostra diff, nada instala
python3 scripts/godnaterra.py init --apply            # instala com backup timestampado
python3 scripts/godnaterra.py update                  # DRY-RUN: diff da fonte -> adaptadores
python3 scripts/godnaterra.py update --apply          # aplica a atualização
```

`init` e `update` são **dry-run por padrão**. Nenhum comando apaga arquivos, reindexa, faz deploy ou rotaciona credenciais.

### Sobre os caminhos nos artefatos `generated/`

Os arquivos em `adapters/*/generated/` são derivados de `scripts/generate_adapters.py` e registram os caminhos absolutos da máquina onde foram gerados (`/root/.config/opencode/skill-packs/godnaterra/...` no pacote publicado). Isso **não** é configuração ativa: ao rodar `init --apply` ou `update --apply` em outra máquina, o gerador usa o `ROOT` local e grava os caminhos corretos. Não edite os artefatos na mão — a fonte canônica é o gerador.

## Fora do escopo da instalação

- reindexação do Qdrant
- criação de collection
- rotação de credenciais
- deploy em produção
- alteração no `.git` do `joshua`

Todos exigem autorização explícita.
