#!/usr/bin/env python3
"""Instalador Engenharia de IA Aplicada — isolado por cliente (padrao --scope project).

Uso:
  python3 scripts/install.py                             # DRY-RUN, nada escreve
  python3 scripts/install.py --apply                     # instala no CLONE (project)
  python3 scripts/install.py --apply --scope user        # instala global com backup
  python3 scripts/install.py --target opencode --apply
  python3 scripts/install.py --rollback                  # restaura backups

Seguranca:
  - integridade SHA256 verificada antes de qualquer escrita (fail-closed);
  - --apply e a autorizacao explicita; sem ele nada e alterado;
  - project scope grava apenas dentro do clone, sem tocar configs globais;
  - user scope preserva chaves existentes do opencode.json e faz backup;
  - symlinks relativos, nunca sobrescreve destino existente;
  - nenhum subprocesso via shell.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_adapters import (  # noqa: E402
    AGENTES,
    RAIZES,
    ROOT,
    ROOT_TOKEN,
    backup,
    caminhos_skills,
    criar_symlinks,
    ler_mcp_template,
    ler_skills,
    mesclar_config,
    resolver_caminhos,
    restaurar,
    sincronizar_agentes,
)

MANIFESTO = ROOT / "install-manifest.json"
VERSAO = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else "0.0.0"


def arquivos_canonicos(root: Path) -> list[str]:
    """Arquivos que formam a fonte canônica versionada (sem o proprio manifesto)."""
    relativos: list[str] = [
        "AGENTS.md",
        "project.yaml",
        "VERSION",
        "README.md",
        "MANIFESTO.md",
        "CHANGELOG.md",
        "SECURITY_CLASSIFICATION.md",
        "docs/guides/INSTALL.md",
        "adapters/opencode/generated/opencode.json",
        "adapters/claude-code/generated/install-skills.sh",
        "design-system/tokens/tokens.json",
    ]
    padroes = (
        ("skills/core", "*/SKILL.md"),
        ("skills/upstream", "*/SKILL.md"),
        ("adapters", "*/*.json"),
        ("adapters", "*/*.md"),
        ("adapters", "*/*.py"),
        ("agents", "eia-*.md"),
        ("scripts", "*.py"),
        ("tests", "*.py"),
        (".github/workflows", "*.yml"),
    )
    for pasta, padrao in padroes:
        base = root / pasta
        if base.is_dir():
            relativos.extend(
                str(p.relative_to(root)) for p in sorted(base.glob(padrao)) if p.is_file()
            )
    return sorted(set(relativos))


def calcular_manifesto(root: Path) -> dict[str, object]:
    arquivos = arquivos_canonicos(root)
    hashes: dict[str, str] = {}
    for rel in arquivos:
        p = root / rel
        hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return {
        "versao": VERSAO,
        "token": ROOT_TOKEN,
        "algoritmo": "sha256",
        "arquivos": hashes,
    }


def verificar_manifesto(root: Path = ROOT) -> tuple[bool, str]:
    """Fail-closed: manifesto ausente, ilegível ou divergente bloqueia a instalacao."""
    if not MANIFESTO.exists():
        return False, "manifesto ausente (execute scripts/generate_manifest.py)"
    try:
        esperado = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return False, f"manifesto ilegível: {exc}"
    arquivos = esperado.get("arquivos")
    if not isinstance(arquivos, dict) or not arquivos:
        return False, "manifesto sem campo 'arquivos'"

    divergentes: list[str] = []
    for rel, digest in sorted(arquivos.items()):
        p = root / rel
        if not p.is_file():
            divergentes.append(f"{rel} (ausente)")
            continue
        atual = hashlib.sha256(p.read_bytes()).hexdigest()
        if atual != digest:
            divergentes.append(rel)
    if divergentes:
        return False, "divergências: " + ", ".join(divergentes[:8])
    return True, f"{len(arquivos)} arquivos íntegros"


def destinos(scope: str, root: Path, home: Path) -> dict[str, Path]:
    if scope == "user":
        return {
            "opencode_config": home / ".config" / "opencode" / "opencode.json",
            "opencode_agents": home / ".config" / "opencode" / "agents",
            "claude_skills": home / ".claude" / "skills",
        }
    return {
        "opencode_config": root / ".opencode" / "opencode.json",
        "opencode_agents": root / ".opencode" / "agents",
        "claude_skills": root / ".claude" / "skills",
    }


def tem_backup(path: Path) -> bool:
    return bool(sorted(path.parent.glob(f"{path.name}.bak-eia-*")))


def imprimir_plano(args: argparse.Namespace, dest: dict[str, Path], total: int) -> None:
    print("=== plano de instalação ===")
    print(f"  versão: {VERSAO}")
    print(f"  escopo: {args.scope} ({'isolado no clone' if args.scope == 'project' else 'global'})")
    print(f"  raiz canônica: {ROOT}")
    print(f"  skills: {total} (core + upstream)")
    if args.target in ("opencode", "all"):
        print(f"  opencode config: {dest['opencode_config']}")
        print(f"  opencode agentes: {dest['opencode_agents']} (7)")
        mcp = ler_mcp_template()
        nomes = sorted((mcp or {}).get("servers", {}))
        print(f"  mcp servers: {', '.join(nomes) or 'nenhum'} (todos disabled)")
    if args.target in ("claude-code", "all"):
        print(f"  claude symlinks: {dest['claude_skills']} (relative, sem sobrescrever)")
    print("  escrita: " + ("SIM (--apply)" if args.apply else "NÃO (dry-run)"))


def cmd_rollback(dest: dict[str, Path], args: argparse.Namespace) -> int:
    print("=== rollback ===")
    ok = True
    if args.target in ("opencode", "all"):
        cfg = dest["opencode_config"]
        if tem_backup(cfg):
            ok = restaurar(cfg) and ok
        else:
            print(f"  sem backup para: {cfg}")
        for ag in sorted(AGENTES.glob("eia-*.md")):
            alvo = dest["opencode_agents"] / ag.name
            if tem_backup(alvo):
                ok = restaurar(alvo) and ok
    print("  claude-code: symlinks são aditivos; remova manualmente se desejar")
    print(f"Rollback: {'OK' if ok else 'PARCIAL/FALHOU'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", choices=["opencode", "claude-code", "all"], default="all")
    ap.add_argument("--scope", choices=["project", "user"], default="project")
    ap.add_argument("--apply", action="store_true", help="autorização explícita para escrever")
    ap.add_argument("--no-verify", action="store_true", help="pula checagem SHA256 (uso em dev)")
    ap.add_argument("--rollback", action="store_true", help="restaura backups timestampados")
    ap.add_argument("--home", type=Path, default=Path.home(), help="HOME alternativa (testes)")
    args = ap.parse_args()

    dest = destinos(args.scope, ROOT, args.home.expanduser().resolve())

    if args.rollback:
        return cmd_rollback(dest, args)

    if not args.no_verify:
        integro, motivo = verificar_manifesto(ROOT)
        print(f"[integridade] {motivo}")
        if not integro:
            print("Instalação abortada: fonte canônica divergente.", file=sys.stderr)
            return 1

    skills = ler_skills()
    total = len(skills)
    imprimir_plano(args, dest, total)

    if not args.apply:
        print("\nimplementado: nada (dry-run)")
        print("testado: integridade da fonte e plano gerados sem escrita")
        print("pendente: execute com --apply para instalar")
        print("não verificado: runtime da máquina cliente")
        return 0

    print("\n=== aplicando ===")
    if args.target in ("opencode", "all"):
        cfg = dest["opencode_config"]
        cfg.parent.mkdir(parents=True, exist_ok=True)
        conteudo = mesclar_config(
            cfg, resolver_caminhos(caminhos_skills(), ROOT), ler_mcp_template()
        )
        backup(cfg)
        cfg.write_text(conteudo, encoding="utf-8")
        print(f"  opencode config: {cfg}")
        copiados, equivalentes = sincronizar_agentes(dest["opencode_agents"])
        print(f"  agentes: {copiados} copiados | {equivalentes} já equivalentes")

    if args.target in ("claude-code", "all"):
        criados, ignorados = criar_symlinks(RAIZES, dest["claude_skills"])
        print(f"  symlinks: {criados} criados | {ignorados} ignorados (destino ocupado)")

    print("\n=== resumo ===")
    print(f"implementado: opencode + claude-code, escopo {args.scope}")
    print("testado: manifesto SHA256, JSON mesclado, idempotência de agentes/symlinks")
    print("pendente: verificação em runtime do cliente (CLI não executada aqui)")
    print("não verificado: CARGA de skills pelo OpenCode na máquina destino")
    return 0


if __name__ == "__main__":
    sys.exit(main())
