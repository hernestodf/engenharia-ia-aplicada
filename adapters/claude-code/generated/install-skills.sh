#!/usr/bin/env bash
# DERIVADO — gere novamente com scripts/generate_adapters.py --target claude-code
# Cria symlinks relativos; nunca sobrescreve destino existente.
set -euo pipefail
RAIZES=("/root/.config/opencode/skill-packs/godnaterra/skills/core" "/root/.config/opencode/skill-packs/godnaterra/skills/upstream")
DEST="${HOME}/.claude/skills"
mkdir -p "$DEST"
criados=0; ignorados=0
for raiz in "${RAIZES[@]}"; do
for md in "$raiz"/*/SKILL.md; do
  nome="$(basename "$(dirname "$md")")"
  alvo="$DEST/$nome"
  if [ -e "$alvo" ] || [ -L "$alvo" ]; then
    ignorados=$((ignorados+1))
    continue
  fi
  ln -s "$(realpath --relative-to="$DEST" "$(dirname "$md")")" "$alvo"
  criados=$((criados+1))
done
done
echo "symlinks criados: $criados | ignorados: $ignorados"
