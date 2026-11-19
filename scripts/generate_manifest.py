#!/usr/bin/env python3
"""Gera/verifica install-manifest.json (SHA256 da fonte canônica).

Uso:
  python3 scripts/generate_manifest.py            # grava o manifesto
  python3 scripts/generate_manifest.py --check    # só verifica; exit 1 se houver drift

O manifesto é a base da verificação fail-closed feita por scripts/install.py.
Nunca inclui a si mesmo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from install import MANIFESTO, ROOT, calcular_manifesto, verificar_manifesto  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="apenas verifica, não grava")
    args = ap.parse_args()

    if args.check:
        ok, motivo = verificar_manifesto(ROOT)
        print(f"Manifesto: {motivo}")
        return 0 if ok else 1

    dados = calcular_manifesto(ROOT)
    MANIFESTO.write_text(
        json.dumps(dados, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Manifesto gravado: {MANIFESTO.relative_to(ROOT)} ({len(dados['arquivos'])} arquivos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
