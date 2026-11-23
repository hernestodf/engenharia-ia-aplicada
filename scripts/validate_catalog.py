#!/usr/bin/env python3
"""Valida o catálogo canônico EngenhariaIaAplicada (core/ + upstream/).

Uso: python3 scripts/validate_catalog.py
Saída: contadores + lista de problemas. Exit 1 se houver problema.

Regras verificadas:
  - name do frontmatter == nome do diretório;
  - prefixo op-;
  - ID lowercase;
  - sem $ARGUMENTS, mcp__, /Users/, caminho Desktop/dev/repos;
  - sem placeholder {{...}} residual (expressões legítimas do GitHub Actions são permitidas).
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAIZES = (ROOT / "skills" / "core", ROOT / "skills" / "upstream")

# Esta skill documenta os padrões proibidos; cita-los é obrigatório.
DOCUMENTA_PADROES = {"op-eia-portability"}

PROIBIDOS = {
    "ARGUMENTS": re.compile(r"\$ARGUMENTS\b"),
    "mcp": re.compile(r"\bmcp__[A-Za-z_]"),
    "users": re.compile(r"/Users/"),
    "desktop": re.compile(r"/Desktop/[Dd]ev/repos/"),
    # Expressões do GitHub Actions ({{ secrets.X }}, {{ github.ref }}) são código, não placeholder.
    "placeholder": re.compile(
        r"\{\{(?!\s*(?:secrets|github|inputs|vars|matrix|steps|needs|env)\.)"
        r"[A-Za-z_][\w.-]*\}\}"
    ),
}


def main() -> int:
    problemas: list[str] = []
    total = 0
    vistos: Counter[str] = Counter()

    for raiz in RAIZES:
        for md in sorted(raiz.glob("*/SKILL.md")):
            total += 1
            texto = md.read_text(encoding="utf-8")
            nome_dir = md.parent.name
            vistos[nome_dir] += 1

            match = re.search(r"^name:\s*(.+)$", texto, re.M)
            nome = match.group(1).strip() if match else ""
            if nome != nome_dir:
                problemas.append(f"{nome_dir}: name={nome!r} != diretório")
            if not nome.startswith("op-"):
                problemas.append(f"{nome_dir}: sem prefixo op-")
            if nome != nome.lower():
                problema = f"{nome_dir}: ID não lowercase"
                problemas.append(problema)

            if nome_dir in DOCUMENTA_PADROES:
                continue

            for rotulo, regex in PROIBIDOS.items():
                for encontrado in regex.finditer(texto):
                    linha = texto[: encontrado.start()].count("\n") + 1
                    problemas.append(
                        f"{nome_dir}:{linha}: padrão {rotulo} -> {encontrado.group(0)!r}"
                    )

    duplicatas = [nome for nome, qtd in vistos.items() if qtd > 1]
    for nome in duplicatas:
        problemas.append(f"{nome}: duplicado ({vistos[nome]})")

    print(f"Skills validadas: {total}")
    print(f"Problemas: {len(problemas)}")
    for p in problemas[:50]:
        print(f"  {p}")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
