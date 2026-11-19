#!/usr/bin/env bash
# DERIVADO — gere novamente com scripts/generate_adapters.py
# Cria symlinks absolutos; nunca sobrescreve destino existente.
# Para symlinks relativos e isolados por cliente, use scripts/install.py.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
RAIZES=("$RAIZ/skills/core" "$RAIZ/skills/upstream")
DEST="${HOME}/.claude/skills"
mkdir -p "$DEST"
criados=0; ignorados=0
for raiz in "${RAIZES[@]}"; do
for md in "$raiz"/*/SKILL.md; do
  [ -e "$md" ] || continue
  nome="$(basename "$(dirname "$md")")"
  alvo="$DEST/$nome"
  if [ -e "$alvo" ] || [ -L "$alvo" ]; then
    ignorados=$((ignorados+1))
    continue
  fi
  ln -s "$(dirname "$md")" "$alvo"
  criados=$((criados+1))
done
done
echo "symlinks criados: $criados | ignorados: $ignorados"
