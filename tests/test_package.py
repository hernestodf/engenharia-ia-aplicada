#!/usr/bin/env python3
"""Testes do pacote Engenharia de IA Aplicada (não das skills upstream).

Executa com: python3 -m unittest discover -s tests -v
Sem dependências externas.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def executar(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(ROOT / "scripts" / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class CatalogoTest(unittest.TestCase):
    def test_catalogo_valido(self) -> None:
        r = executar("validate_catalog.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Skills validadas: 772", r.stdout)
        self.assertIn("Problemas: 0", r.stdout)

    def test_core_e_upstream_presentes(self) -> None:
        core = list((ROOT / "skills/core").glob("*/SKILL.md"))
        upstream = list((ROOT / "skills/upstream").glob("*/SKILL.md"))
        self.assertEqual(len(core), 8)
        self.assertEqual(len(upstream), 764)

    def test_agentes_e_papeis(self) -> None:
        agentes = sorted(p.name for p in (ROOT / "agents").glob("eia-*.md"))
        self.assertEqual(len(agentes), 7)
        self.assertIn("eia-router.md", agentes)
        self.assertIn("eia-qa-security.md", agentes)


class AdaptadoresTest(unittest.TestCase):
    def test_opencode_json_valido_e_raizes_existem(self) -> None:
        cfg = json.loads((ROOT / "adapters/opencode/generated/opencode.json").read_text())
        self.assertEqual(len(cfg["skills"]), 2)
        for raiz in cfg["skills"]:
            resolvida = raiz.replace("__EIA_ROOT__", str(ROOT))
            self.assertTrue(Path(resolvida).is_dir(), resolvida)

    def test_artefatos_derivados_sem_caminho_da_maquina_geradora(self) -> None:
        for rel in (
            "adapters/opencode/generated/opencode.json",
            "adapters/claude-code/generated/install-skills.sh",
        ):
            texto = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("/root/", texto, rel)
            self.assertNotIn(str(ROOT), texto, rel)

    def test_script_claude_sintaticamente_valido(self) -> None:
        r = subprocess.run(
            ["bash", "-n", str(ROOT / "adapters/claude-code/generated/install-skills.sh")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)


class DesignSystemTest(unittest.TestCase):
    def test_tokens_json_valido(self) -> None:
        tokens = json.loads((ROOT / "design-system/tokens/tokens.json").read_text())
        self.assertIn("color", tokens)
        self.assertIn("focus", tokens)

    def test_tokens_css_sem_hex_arbitrario_fora_da_raiz(self) -> None:
        css = (ROOT / "design-system/tokens/tokens.css").read_text()
        self.assertIn("--gt-color-bg:", css)
        self.assertIn("--gt-focus-width:", css)
        self.assertIn("prefers-reduced-motion", css)


if __name__ == "__main__":
    unittest.main()
