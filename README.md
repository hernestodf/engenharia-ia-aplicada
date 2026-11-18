# Godnaterra

Pacote de engenharia de software assistida por IA, **vendor-neutral e portátil**. Núcleo genérico; Profox Go e PHP legado entram como perfis opcionais.

Versão: `0.1.0`

## Estado atual

| Fase | Situação |
|---|---|
| 1 · Auditoria read-only | concluída |
| 2 · Inventário e plano | concluída |
| 3 · Repo, regras e estrutura canônica | concluída |
| 4 · Skills core + portagem integral das 879 | pendente |
| 5 · Agentes e adapters | parcial (perfis lógicos descritos) |
| 6 · Design System e validação frontend | pendente |
| 7 · Testes, segurança e avaliações | pendente |
| 8 · CI/CD | pendente |
| 9 · MCP e Qdrant | pendente (contrato apenas) |
| 10 · Instalador e documentação | pendente |

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
