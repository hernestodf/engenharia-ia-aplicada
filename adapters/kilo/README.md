# Adaptador Kilo

Fonte: `scripts/generate_adapters.py --target kilo`. Artefatos em `generated/`; não editar à mão.

## Estado verificado

- **implementado:** merge de `skills.paths` em `~/.config/kilo/kilo.jsonc` (sem apagar `permission`), 7 agentes derivados em `~/.config/kilo/agent/`. Backup timestampado em cada aplicação.
- **testado:** `kilo debug skill` lista 769 skills `op-` (764 upstream + 5 core), sem duplicatas; `kilo debug agent godnaterra-router` e `godnaterra-qa-security` mostram `primary`/`subagent` e regras na ordem correta; `kilo debug config` confirma as duas raízes. Segunda execução não duplicou paths.
- **não verificado:** execução de LLM/sessão real, e por que o CLI reporta `trusted: false` nas skills `op-` apesar de a doc dizer que paths absolutos em config global são trusted. Não assumir que comandos embutidos (`!`...) rodam no Kilo.

CLI: `/usr/local/sbin/kilo`, versão `7.8.27`. Formato consultado em `https://kilo.ai/docs/customize/skills`.
