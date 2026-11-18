#!/usr/bin/env python3
"""Gera adaptadores DERIVADOS da fonte canônica Godnaterra.

Fonte canônica: AGENTS.md, project.yaml, skills/core/, skills/upstream/, agents/.
Nunca edite adapters/*/generated/ na mão — são artefatos.

Uso:
  python3 scripts/generate_adapters.py                 # dry-run: gera artefatos no repo, não instala
  python3 scripts/generate_adapters.py --apply         # instala globalmente com backup
  python3 scripts/generate_adapters.py --target kilo --apply

Segurança:
  - não apaga nada;
  - backup com timestamp antes de sobrescrever config global;
  - recusa mesclar JSONC com comentários (avoid perder conteúdo);
  - symlinks do Claude são relativos e nunca sobrescrevem destino existente.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COREL = ROOT / "skills" / "core"
CATALOG = ROOT / "skills" / "upstream"
RAIZES = (COREL, CATALOG)
AGENTES = ROOT / "agents"

KILO_CONFIG = Path.home() / ".config" / "kilo" / "kilo.jsonc"
OPENCODE_CONFIG = Path.home() / ".config" / "opencode" / "opencode.json"
CLAUDE_SKILLS = Path.home() / ".claude" / "skills"
KILO_AGENTS = Path.home() / ".config" / "kilo" / "agent"
OPENCODE_AGENTS = Path.home() / ".config" / "opencode" / "agents"


def stamp() -> str:
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


def escrever_artefato(path: Path, conteudo: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(conteudo, encoding="utf-8")
    print(f"  gerado: {path.relative_to(ROOT)}")


def configuracao_opencode() -> str:
    cfg = {
        "$schema": "https://opencode.ai/config.json",
        "skills": [str(r) for r in RAIZES],
    }
    return json.dumps(cfg, ensure_ascii=False, indent=2) + "\n"


def configuracao_kilo(path_atual: Path) -> str:
    cfg: dict = {}
    if path_atual.exists():
        cru = path_atual.read_text(encoding="utf-8")
        # JSONC pode ter comentários; não vamos achatar comentários do usuário.
        sem_strings = re.sub(r'"(?:\\.|[^"\\])*"', '""', cru)
        if "//" in sem_strings or "/*" in sem_strings:
            raise SystemExit(
                f"Recusado mesclar {path_atual}: comentários presentes. "
                "Remova manualmente ou ajuste o gerador."
            )
        cfg = json.loads(cru)
    paths = list(cfg.get("skills", {}).get("paths", []))
    for raiz in RAIZES:
        alvo = str(raiz)
        if alvo not in paths:
            paths.append(alvo)
    cfg.setdefault("skills", {})["paths"] = paths
    cfg.setdefault("$schema", "https://app.kilo.ai/config.json")
    return json.dumps(cfg, ensure_ascii=False, indent=2) + "\n"


def script_claude() -> str:
    return f"""#!/usr/bin/env bash
# DERIVADO — gere novamente com scripts/generate_adapters.py --target claude-code
# Cria symlinks relativos; nunca sobrescreve destino existente.
set -euo pipefail
RAIZES=("{COREL}" "{CATALOG}")
DEST="${{HOME}}/.claude/skills"
mkdir -p "$DEST"
criados=0; ignorados=0
for raiz in "${{RAIZES[@]}}"; do
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
"""


def agente_kilo(path: Path) -> str:
    """Converte frontmatter OpenCode → formato de agente Kilo."""
    texto = path.read_text(encoding="utf-8")
    partes = texto.split("---", 2)
    if len(partes) < 3:
        raise SystemExit(f"Frontmatter inválido: {path}")
    head, corpo = partes[1].strip(), partes[2].strip()

    descricao = re.search(r"^description:\s*(.+)$", head, re.M).group(1).strip()
    modo = re.search(r"^mode:\s*(.+)$", head, re.M).group(1).strip()
    steps = re.search(r"^steps:\s*(\d+)", head, re.M)
    if modo not in {"primary", "subagent"}:
        raise SystemExit(f"Modo não mapeado em {path}: {modo}")

    permission: dict = {}
    if modo == "subagent":
        permission = {"bash": {"*": "deny"}, "edit": {"*": "deny"}, "task": {"*": "deny"}}
    else:
        # Router: bloqueio amplo vem primeiro; overrides específicos depois.
        allow = re.findall(r"resource:\s*godnaterra-([\w-]+)", head)
        permission = {
            "bash": {"*": "ask"},
            "edit": {"*": "ask"},
            "task": {"*": "deny", **{f"godnaterra-{a}": "allow" for a in allow}},
        }

    novo = ["---", f"description: {descricao}", f"mode: {modo}"]
    if steps:
        novo.append(f"steps: {steps.group(1)}")
    novo.append("permission:")
    for ferramenta, regras in permission.items():
        novo.append(f"  {ferramenta}:")
        for padrao, efeito in regras.items():
            novo.append(f'    "{padrao}": {efeito}')
    novo += ["---", "", corpo, ""]
    return "\n".join(novo)


def backup(path: Path) -> None:
    if path.exists():
        dest = path.with_name(f"{path.name}.bak-godnaterra-{stamp()}")
        shutil.copy2(path, dest)
        print(f"  backup: {dest}")


def apply_config(path: Path, conteudo: str) -> None:
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(conteudo, encoding="utf-8")
    print(f"  instalado: {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", choices=["opencode", "claude-code", "kilo", "all"], default="all")
    ap.add_argument("--apply", action="store_true", help="instalar configs globais com backup")
    args = ap.parse_args()

    skills = ler_skills()
    print(f"Fonte canônica: {len(skills)} skills válidas em skills/core/ + skills/upstream/")

    alvos = ["opencode", "claude-code", "kilo"] if args.target == "all" else [args.target]

    if "opencode" in alvos:
        print("[opencode]")
        escrever_artefato(
            ROOT / "adapters" / "opencode" / "generated" / "opencode.json",
            configuracao_opencode(),
        )
        if args.apply:
            apply_config(OPENCODE_CONFIG, configuracao_opencode())
            OPENCODE_AGENTS.mkdir(parents=True, exist_ok=True)
            for ag in sorted(AGENTES.glob("godnaterra-*.md")):
                shutil.copy2(ag, OPENCODE_AGENTS / ag.name)
            print(f"  agentes sincronizados: {len(list(AGENTES.glob('godnaterra-*.md')))}")

    if "kilo" in alvos:
        print("[kilo]")
        escrever_artefato(
            ROOT / "adapters" / "kilo" / "generated" / "kilo.jsonc",
            configuracao_kilo(KILO_CONFIG),
        )
        for ag in sorted(AGENTES.glob("godnaterra-*.md")):
            escrever_artefato(
                ROOT / "adapters" / "kilo" / "generated" / "agents" / ag.name,
                agente_kilo(ag),
            )
        if args.apply:
            apply_config(KILO_CONFIG, configuracao_kilo(KILO_CONFIG))
            KILO_AGENTS.mkdir(parents=True, exist_ok=True)
            for ag in sorted((ROOT / "adapters" / "kilo" / "generated" / "agents").glob("*.md")):
                shutil.copy2(ag, KILO_AGENTS / ag.name)
            print(f"  agentes sincronizados: {len(list(AGENTES.glob('godnaterra-*.md')))}")

    if "claude-code" in alvos:
        print("[claude-code]")
        escrever_artefato(
            ROOT / "adapters" / "claude-code" / "generated" / "install-skills.sh",
            script_claude(),
        )
        if args.apply:
            script = ROOT / "adapters" / "claude-code" / "generated" / "install-skills.sh"
            os.chmod(script, 0o755)
            print("  Instalação local de symlinks:")
            os.system(f"bash {script}")

    if not args.apply:
        print("\nDRY-RUN: nada foi instalado globalmente. Use --apply para instalar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
