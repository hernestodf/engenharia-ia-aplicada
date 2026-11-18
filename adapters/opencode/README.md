# Adaptador OpenCode

Fonte: `scripts/generate_adapters.py --target opencode`. Artefato em `generated/opencode.json`; não editar à mão.

## Estado verificado

- **implementado:** `generated/opencode.json` com `skills/core` e `skills/upstream`; 7 agentes sincronizados em `~/.config/opencode/agents/`.
- **testado:** `opencode debug agents` reconhece 7 agentes Godnaterra (6 `subagent`, 1 `primary`); `skill_mode.py status` reporta 769 ativas/visíveis; as 5 core skills apareceram na lista ativa da sessão.
- **não verificado:** execução de LLM via `opencode run` (flag `--print` inexistente; tentativa com timeout devolveu `exit=124`).

Config ativa: `~/.config/opencode/opencode.json`. Backup timestampado antes de cada `--apply`.
