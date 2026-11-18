---
name: op-godnaterra-portability
description: Aplica as regras de portagem de skills para o formato Godnaterra e decide quando gerar adaptador derivado. Use ao portar, renomear ou adaptar skills entre OpenCode, Claude Code e Kilo.
godnaterra/layer: core
godnaterra/source: canonical
---

# Portabilidade Godnaterra

## Regras de portagem

| Entrada | Saída |
|---|---|
| `$ARGUMENTS` | `dados informados pelo usuario na mensagem` |
| `$0`, `$1`, `$3` | preservar (valores monetários e variáveis shell) |
| `/comando` | `skill:<id>` **só** se bater com skill existente |
| `mcp__servico__ferramenta` | `ferramenta externa: servico/ferramenta` |
| path absoluto de máquina | `<repo atual>` |
| `{{...}}` | `<...>` |

Atenção à ordem das regex: paths mais específicos primeiro, senão sobra fragmento (`<repo atual>/Desktop/dev/repos/...`).

## Critérios

- Uma skill canônica por domínio. Duplicata idêntica → 1 canônica + manifesto. Variante divergente → `references/`. Stub/ponteiro morto → nota de descarte. Nada é apagado dos packs originais.
- Prefixo `op-`. `name` casa com o diretório. IDs únicos em lowercase.
- Núcleo genérico. `profox-go` e `legacy-php` são profiles opcionais.
- Adaptadores são **derivados** da fonte canônica (`AGENTS.md`, `project.yaml`, `skills/`, `agents/`), nunca editados à mão. Gerar com `scripts/generate_adapters.py`.
- Config global só com `--apply`, backup timestampado, merge sem apagar conteúdo do usuário.
