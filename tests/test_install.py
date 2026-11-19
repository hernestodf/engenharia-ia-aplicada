#!/usr/bin/env python3
"""Testes do instalador isolado por cliente. Sem dependências externas."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from install import ROOT as INSTALL_ROOT  # noqa: E402
from install import verificar_manifesto  # noqa: E402


def executar(root: Path, script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(root / "scripts" / script), *args],
        cwd=root,
        capture_output=True,
        text=True,
    )


def clonar_temp(td: str) -> tuple[Path, Path]:
    """Copia so o necessario para simular um clone em PC novo."""
    base = Path(td)
    clone = base / "clone"
    clone.mkdir()
    for nome in ("scripts", "skills", "agents"):
        shutil.copytree(
            ROOT / nome,
            clone / nome,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    shutil.copy2(ROOT / "VERSION", clone / "VERSION")
    return clone, base / "home"


class ManifestoTest(unittest.TestCase):
    def test_manifesto_integro(self) -> None:
        self.assertEqual(INSTALL_ROOT, ROOT)
        ok, motivo = verificar_manifesto(ROOT)
        self.assertTrue(ok, motivo)
        self.assertIn("arquivos íntegros", motivo)


class InstaladorTest(unittest.TestCase):
    def test_dry_run_nao_escreve(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            clone, home = clonar_temp(td)
            r = executar(clone, "install.py", "--no-verify", "--home", str(home))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("dry-run", r.stdout)
            self.assertIn("implementado: nada", r.stdout)
            self.assertFalse((clone / ".opencode").exists())
            self.assertFalse((clone / ".claude").exists())
            self.assertFalse(home.exists())

    def test_apply_project_isolado_e_idempotente(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            clone, home = clonar_temp(td)

            r1 = executar(clone, "install.py", "--apply", "--no-verify", "--home", str(home))
            self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
            self.assertIn("escopo: project", r1.stdout)

            cfg_path = clone / ".opencode" / "opencode.json"
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.assertEqual(
                cfg["skills"],
                [str(clone / "skills" / "core"), str(clone / "skills" / "upstream")],
            )
            self.assertNotIn("/root/", cfg_path.read_text(encoding="utf-8"))
            self.assertFalse((home / ".config").exists())
            self.assertFalse((home / ".claude").exists())

            links = list((clone / ".claude" / "skills").glob("op-*"))
            self.assertEqual(len(links), 769)
            self.assertTrue(all(l.is_symlink() for l in links))
            self.assertTrue(all(l.exists() for l in links), "symlink quebrado")

            r2 = executar(clone, "install.py", "--apply", "--no-verify", "--home", str(home))
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            self.assertIn("agentes: 0 copiados", r2.stdout)
            self.assertIn("symlinks: 0 criados", r2.stdout)
            self.assertEqual(len(list((clone / ".claude" / "skills").glob("op-*"))), 769)

            backups = list((clone / ".opencode").glob("opencode.json.bak-godnaterra-*"))
            self.assertEqual(len(backups), 1)

            r3 = executar(clone, "install.py", "--rollback", "--home", str(home))
            self.assertEqual(r3.returncode, 0, r3.stdout + r3.stderr)
            self.assertIn("Rollback: OK", r3.stdout)

    def test_apply_user_preserva_config_existente(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            clone, home = clonar_temp(td)
            cfg_path = home / ".config" / "opencode" / "opencode.json"
            cfg_path.parent.mkdir(parents=True)
            cfg_path.write_text(
                json.dumps({"minhaChave": "valor", "skills": ["/raiz/antiga"], "extra": [1, 2]}),
                encoding="utf-8",
            )

            r = executar(
                clone,
                "install.py",
                "--apply",
                "--no-verify",
                "--scope",
                "user",
                "--target",
                "opencode",
                "--home",
                str(home),
            )
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.assertEqual(cfg["minhaChave"], "valor")
            self.assertEqual(cfg["extra"], [1, 2])
            self.assertEqual(
                cfg["skills"],
                [str(clone / "skills" / "core"), str(clone / "skills" / "upstream")],
            )
            backups = list(cfg_path.parent.glob("opencode.json.bak-godnaterra-*"))
            self.assertEqual(len(backups), 1)
            self.assertFalse((clone / ".opencode").exists(), "user scope nao deve gravar no clone")

    def test_manifesto_divergente_bloqueia_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            clone, home = clonar_temp(td)
            shutil.copy2(ROOT / "install-manifest.json", clone / "install-manifest.json")
            (clone / "VERSION").write_text("9.9.9\n", encoding="utf-8")
            r = executar(clone, "install.py", "--apply", "--home", str(home))
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("Instalação abortada", r.stderr)
            self.assertFalse((clone / ".opencode").exists())


if __name__ == "__main__":
    unittest.main()
