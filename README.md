# Godnaterra

Pacote de engenharia de software assistida por IA, **vendor-neutral e portátil**. Núcleo genérico; Profox Go e PHP legado entram como perfis opcionais.

Versão: `0.1.0`

## Estado atual

| Fase | Situação |
|---|---|
| 1 · Auditoria read-only | concluída |
| 2 · Inventário e plano | concluída |
| 3 · Repo, regras e estrutura canônica | concluída |
| 4 · Skills core + portagem integral das 879 | concluída (`2b0dde0`, `47bb750`) |
| 5 · Agentes e adapters | concluída (`b4d4e05`) |
| 6 · Design System e validação frontend | implementado; contraste/teclado/zoom não verificados sem UI de produto |
| 7 · Testes, segurança e avaliações | 15 testes automatizados OK; loop de incidentes com revisão ativo; cenários LLM não verificados |
| 8 · CI/CD | workflows implementados; execução no GitHub Actions não verificada |
| 9 · MCP e Qdrant | contrato-only; aguardando endpoint/collection/embedding/dimensões/métrica |
| 10 · Instalador e documentação | implementado; `version`/`audit`/`doctor`/`init` executados localmente |

Nada aqui é "testado" por padrão. O relatório final separa implementado, testado, pendente e não verificado.

## Uso no OpenCode

`~/.config/opencode/opencode.json` aponta somente para este diretório. Os packs originais (`autopunk`, `joshua`, `techsaurabh`) continuam em disco como rollback, mas não são carregados ao mesmo tempo.

Modos via `python3 ~/.config/opencode/skill_mode.py`:

- `godnaterra` — padrão, todas as skills visíveis
- `essencial` — core + melhores upstream
- `curado` — legado de 31 skills
- `status` — contagem atual

## Documentação

- `AGENTS.md` — fonte canônica de regras
- `docs/architecture/OVERVIEW.md` — mapa dos módulos A–F
- `docs/standards/ENGINEERING_WORKFLOW.md` — ciclo DISCOVER→DELIVER
- `docs/decisions/` — ADRs reais
- `MANIFESTO.md` — proveniência das skills portadas
- `docs/guides/INSTALL.md` — instalação e rollback
- `scripts/godnaterra.py` — operador (`version`, `audit`, `doctor`, `init`, `update`)

## Verificação rápida

```bash
python3 scripts/validate_catalog.py
python3 -m unittest discover -s tests -v
python3 scripts/godnaterra.py audit
python3 scripts/godnaterra.py doctor
```
