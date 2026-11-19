#!/usr/bin/env python3
"""Gera adaptadores DERIVADOS da fonte canônica Godnaterra.

Fonte canônica: AGENTS.md, project.yaml, skills/core/, skills/upstream/, agents/.
Nunca edite adapters/*/generated/ na mão — são artefatos.

Uso:
  python3 scripts/generate_adapters.py                 # dry-run: gera artefatos no repo, não instala
  python3 scripts/generate_adapters.py --apply         # instala globalmente com backup (modo legado)
  python3 scripts/generate_adapters.py --target opencode --apply

Para instalação isolada por cliente, use scripts/install.py (padrão --scope project).

Segurança:
  - não apaga nada;
  - backup com timestamp antes de sobrescrever config global;
  - recusa configuracao existente que nao seja JSON valido (JSONC com comentarios);
  - symlinks relativos e nunca sobrescrevem destino existente;
  - nenhum subprocesso via shell (shell=False / chamada Python direta).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COREL = ROOT / "skills" / "core"
CATALOG = ROOT / "skills" / "upstream"
RAIZES = (COREL, CATALOG)
AGENTES = ROOT / "agents"

# Os artefatos versionados NAO podem conter caminhos da maquina que os gerou.
# O token abaixo e resolvido para o ROOT local no momento da instalacao.
ROOT_TOKEN = "__GODNATERRA_ROOT__"

OPENCODE_CONFIG = Path.home() / ".config" / "opencode" / "opencode.json"
CLAUDE_SKILLS = Path.home() / ".claude" / "skills"
OPENCODE_AGENTS = Path.home() / ".config" / "opencode" / "agents"


def stamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ler_skills() -> list[Path]:
    """Retorna SKILL.md canônicos de core/ e upstream/, validando nome == diretório."""
    erros: list[str] = []
    skills: list[Path] = []
    for raiz in RAIZES:
        for skill_md in sorted(raiz.glob("*/SKILL.md")):
            texto = skill_md.read_text(encoding="utf-8")
            match = re.search(r"^name:\s*(.+)$", texto, re.M)
            nome = match.group(1).strip() if match else ""
            if nome != skill_md.parent.name:
                erros.append(f"{skill_md.parent.name}: name={nome!r}")
            if not nome.startswith("op-"):
                erros.append(f"{skill_md.parent.name}: sem prefixo op-")
            skills.append(skill_md)
    if erros:
        raise SystemExit("Fonte canônica inconsistente:\n  " + "\n  ".join(erros[:20]))
    return skills


def caminhos_skills(root: Path | None = None) -> list[str]:
    """Caminhos das duas raízes; token quando nao ha root explicito."""
    prefixo = str(root) if root is not None else ROOT_TOKEN
    return [f"{prefixo}/skills/core", f"{prefixo}/skills/upstream"]


def resolver_caminhos(caminhos: list[str], root: Path | None = None) -> list[str]:
    """Resolve o token para um root informado, sem alterar caminhos ja absolutos."""
    base = root if root is not None else ROOT
    return [c.replace(ROOT_TOKEN, str(base)) for c in caminhos]


def escrever_artefato(path: Path, conteudo: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(conteudo, encoding="utf-8")
    print(f"  gerado: {path.relative_to(ROOT)}")


def configuracao_opencode(root: Path | None = None) -> str:
    cfg = {
        "$schema": "https://opencode.ai/config.json",
        "skills": caminhos_skills(root),
    }
    return json.dumps(cfg, ensure_ascii=False, indent=2) + "\n"


def script_claude(root: Path | None = None) -> str:
    """Script derivado de conveniencia. Instalador prefere criar symlinks em Python."""
    if root is None:
        raiz = 'RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"'
    else:
        raiz = f"RAIZ={shlex.quote(str(root))}"
    return f"""#!/usr/bin/env bash
# DERIVADO — gere novamente com scripts/generate_adapters.py
# Cria symlinks absolutos; nunca sobrescreve destino existente.
# Para symlinks relativos e isolados por cliente, use scripts/install.py.
set -euo pipefail
{raiz}
RAIZES=("$RAIZ/skills/core" "$RAIZ/skills/upstream")
DEST="${{HOME}}/.claude/skills"
mkdir -p "$DEST"
criados=0; ignorados=0
for raiz in "${{RAIZES[@]}}"; do
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
"""


def criar_symlinks(raizes: tuple[Path, ...], destino: Path) -> tuple[int, int]:
    """Cria symlinks RELATIVOS em destino. Idempotente; nunca sobrescreve."""
    destino.mkdir(parents=True, exist_ok=True)
    criados = ignorados = 0
    for raiz in raizes:
        for md in sorted(raiz.glob("*/SKILL.md")):
            alvo = destino / md.parent.name
            if alvo.exists() or alvo.is_symlink():
                ignorados += 1
                continue
            os.symlink(os.path.relpath(md.parent, destino), alvo)
            criados += 1
    return criados, ignorados


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    dest = path.with_name(f"{path.name}.bak-godnaterra-{stamp()}")
    shutil.copy2(path, dest)
    print(f"  backup: {dest}")
    return dest


def restaurar(path: Path) -> bool:
    """Restaura o backup mais recente de um arquivo gerenciado."""
    candidatos = sorted(path.parent.glob(f"{path.name}.bak-godnaterra-*"))
    if not candidatos:
        print(f"  sem backup para: {path}")
        return False
    ultimo = candidatos[-1]
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ultimo, path)
    print(f"  restaurado: {path} <- {ultimo.name}")
    return True


def mesclar_config(path: Path, skills: list[str]) -> str:
    """Preserva chaves existentes; substitui apenas $schema e skills."""
    atual: dict[str, object] = {}
    if path.exists():
        try:
            carregado = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise SystemExit(
                f"Config existente nao e JSON valido (JSONC com comentarios?): {path}\n"
                f"  {exc}\n"
                "  Nada foi alterado. Converta para JSON antes de instalar."
            ) from exc
        if not isinstance(carregado, dict):
            raise SystemExit(f"Config existente nao e objeto JSON: {path}")
        atual = carregado
    atual["$schema"] = "https://opencode.ai/config.json"
    atual["skills"] = skills
    return json.dumps(atual, ensure_ascii=False, indent=2) + "\n"


def sincronizar_agentes(destino: Path) -> tuple[int, int]:
    destino.mkdir(parents=True, exist_ok=True)
    copiados = ignorados = 0
    for ag in sorted(AGENTES.glob("godnaterra-*.md")):
        alvo = destino / ag.name
        if alvo.exists() and alvo.read_bytes() == ag.read_bytes():
            ignorados += 1
            continue
        if alvo.exists():
            backup(alvo)
        shutil.copy2(ag, alvo)
        copiados += 1
    return copiados, ignorados


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", choices=["opencode", "claude-code", "all"], default="all")
    ap.add_argument("--apply", action="store_true", help="instala globalmente com backup (legado)")
    args = ap.parse_args()

    skills = ler_skills()
    print(f"Fonte canônica: {len(skills)} skills válidas em skills/core/ + skills/upstream/")

    alvos = ["opencode", "claude-code"] if args.target == "all" else [args.target]

    if "opencode" in alvos:
        print("[opencode]")
        escrever_artefato(
            ROOT / "adapters" / "opencode" / "generated" / "opencode.json",
            configuracao_opencode(),
        )
        if args.apply:
            conteudo = mesclar_config(OPENCODE_CONFIG, caminhos_skills(ROOT))
            backup(OPENCODE_CONFIG)
            OPENCODE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
            OPENCODE_CONFIG.write_text(conteudo, encoding="utf-8")
            print(f"  instalado: {OPENCODE_CONFIG}")
            copiados, ignorados = sincronizar_agentes(OPENCODE_AGENTS)
            print(f"  agentes: {copiados} copiados | {ignorados} ja equivalentes")

    if "claude-code" in alvos:
        print("[claude-code]")
        escrever_artefato(
            ROOT / "adapters" / "claude-code" / "generated" / "install-skills.sh",
            script_claude(),
        )
        if args.apply:
            criados, ignorados = criar_symlinks(RAIZES, CLAUDE_SKILLS)
            print(f"  symlinks criados: {criados} | ignorados: {ignorados}")

    if not args.apply:
        print("\nDRY-RUN: nada foi instalado globalmente. Use --apply para instalar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
