# Adaptador Claude Code

Fonte: `scripts/generate_adapters.py --target claude-code`. Artefato em `generated/install-skills.sh`; não editar à mão.

## Estado verificado

- **implementado:** script cria symlinks relativos para as 5 core + 764 upstream, sem sobrescrever destino existente.
- **testado:** `bash -n` passou; execução local criou 769 symlinks em `~/.claude/skills/`, 0 quebrados (5 `op-eia-*`).
- **não verificado:** Claude CLI está ausente nesta máquina. Formato de `SKILL.md` validado apenas por documentação oficial (`https://docs.claude.com/en/docs/claude-code/skills`) e pela estrutura de diretórios — não por execução.

Para verificar de verdade, rodar em ambiente com `claude` disponível e confirmar que as skills aparecem no seletor.
