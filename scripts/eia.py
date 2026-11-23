#!/usr/bin/env python3
"""Instalador/operador do pacote Engenharia de IA Aplicada.

Comandos:
  version              imprime a versão do pacote
  audit                valida catálogo e artefatos derivados
  doctor               inspeciona runtimes, configs e backups (somente leitura)
  status               conta skills ativas na config efetiva (somente leitura)
  init   [--apply]     gera adaptadores; --apply instala com backup
  update [--apply]     regenera adaptadores da fonte canônica; --apply instala

Por padrão tudo é dry-run. Nenhum comando apaga arquivos, reindexa, faz deploy
ou rotaciona segredos.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = "0.5.0"

OP_CONFIG = Path.home() / ".config/opencode/opencode.json"
CLAUDE_SKILLS = Path.home() / ".claude/skills"


def executar(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(ROOT / "scripts" / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def cmd_version(_: argparse.Namespace) -> int:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"Versão:\s*`?([0-9.]+)", readme)
    print(f"Engenharia de IA Aplicada {m.group(1) if m else VERSION}")
    return 0


def cmd_audit(_: argparse.Namespace) -> int:
    r = executar("validate_catalog.py")
    print(r.stdout.rstrip())
    if r.returncode:
        print(r.stderr.rstrip(), file=sys.stderr)
        return r.returncode

    r_inc = executar("validate_incidents.py")
    print(r_inc.stdout.rstrip())
    if r_inc.returncode:
        print(r_inc.stderr.rstrip(), file=sys.stderr)
        return r_inc.returncode

    problemas: list[str] = []
    for rel in [
        "adapters/opencode/generated/opencode.json",
        "design-system/tokens/tokens.json",
    ]:
        p = ROOT / rel
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            problemas.append(f"{rel}: {exc}")

    for p in problemas:
        print(f"  problema: {p}")
    print(f"Auditoria: {'FALHOU' if problemas else 'OK'} ({len(problemas)} problemas)")
    return 1 if problemas else 0


def cmd_status(_: argparse.Namespace) -> int:
    """Conta skills ativas na config efetiva, sem alterar arquivos."""
    projeto = ROOT / ".opencode" / "opencode.json"
    cfg_path = projeto if projeto.exists() else OP_CONFIG
    print(f"config: {cfg_path} ({'presente' if cfg_path.exists() else 'AUSENTE'})")
    if not cfg_path.exists():
        print("Skills ativas: 0 | instale com scripts/install.py --apply")
        return 0
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        raizes = [Path(p) for p in cfg.get("skills", [])]
    except (OSError, ValueError, TypeError) as exc:
        print(f"Config ilegível: {exc}")
        return 1
    total = visiveis = 0
    for raiz in raizes:
        if not raiz.is_dir():
            continue
        for md in raiz.rglob("SKILL.md"):
            total += 1
            texto = md.read_text(encoding="utf-8")
            head = texto.split("---", 2)[1] if texto.startswith("---") else ""
            if "opencode/autoinvoke: false" not in head and "disable-model-invocation: true" not in head:
                visiveis += 1
    print(f"Raízes ativas: {', '.join(str(r) for r in raizes) or '(nenhuma)'}")
    print(f"Skills ativas: {total} | visíveis: {visiveis} | sob demanda: {total - visiveis}")
    print("Modo: GOD" if visiveis > 100 else "Modo: CURADO")
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    print("=== runtimes ===")
    for nome in ("opencode", "claude"):
        caminho = shutil.which(nome)
        print(f"  {nome}: {caminho or 'AUSENTE'}")

    print("=== configs ===")
    for nome, p in (("opencode", OP_CONFIG),):
        estado = "presente" if p.exists() else "AUSENTE"
        print(f"  {nome}: {p} ({estado})")

    print("=== backups ===")
    for nome, padrao in (
        ("opencode", "opencode.json.bak-eia-*"),
    ):
        pasta = OP_CONFIG.parent
        print(f"  {nome}: {len(list(pasta.glob(padrao)))}")

    print("=== symlinks Claude ===")
    links = list(CLAUDE_SKILLS.glob("op-*")) if CLAUDE_SKILLS.exists() else []
    quebrados = [l for l in links if not l.exists()]
    print(f"  total: {len(links)} | quebrados: {len(quebrados)}")
    return 0


def mostrar_diff(gerado: Path, instalado: Path, rotulo: str) -> None:
    novo = gerado.read_text(encoding="utf-8").splitlines(keepends=True)
    antigo = (
        instalado.read_text(encoding="utf-8").splitlines(keepends=True)
        if instalado.exists()
        else []
    )
    diff = list(difflib.unified_diff(antigo, novo, fromfile=str(instalado), tofile=str(gerado)))
    print(f"--- diff {rotulo} ({len(diff)} linhas) ---")
    if diff:
        sys.stdout.writelines(diff)
    else:
        print("  (sem alterações)")


def cmd_sync(args: argparse.Namespace) -> int:
    acao = "init" if args.command == "init" else "update"
    print(f"[{acao}] fonte canônica -> adaptadores derivados")
    flags = ["--apply"] if args.apply else []
    r = executar("generate_adapters.py", *flags)
    print(r.stdout.rstrip())
    if r.returncode:
        print(r.stderr.rstrip(), file=sys.stderr)
        return r.returncode

    print()
    mostrar_diff(ROOT / "adapters/opencode/generated/opencode.json", OP_CONFIG, "opencode.json")

    if not args.apply:
        print("\nDRY-RUN: nada instalado. Use --apply para instalar com backup.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("version", help=cmd_version.__doc__)
    sub.add_parser("audit", help=cmd_audit.__doc__)
    sub.add_parser("status", help=cmd_status.__doc__)
    sub.add_parser("doctor", help=cmd_doctor.__doc__)
    for nome in ("init", "update"):
        p = sub.add_parser(nome)
        p.add_argument("--apply", action="store_true", help="instalar configs globais com backup")
    args = ap.parse_args()

    return {
        "version": cmd_version,
        "audit": cmd_audit,
        "status": cmd_status,
        "doctor": cmd_doctor,
        "init": cmd_sync,
        "update": cmd_sync,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
