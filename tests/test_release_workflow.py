#!/usr/bin/env python3
"""Contrato do workflow de release.

Garante que o dispatch publica uma tag existente (checkout da tag, nao do
branch), que o input nao e interpolado dentro do shell, que a versao bate
com a tag e que o tarball cobre os arquivos exigidos pelo manifesto.

Executa com: python3 -m unittest discover -s tests -v
Sem dependencias obrigatorias (PyYAML e opcional).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASE = ROOT / ".github/workflows/release.yml"


class ReleaseWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.texto = RELEASE.read_text(encoding="utf-8")

    def test_dispatch_exige_input_tag(self) -> None:
        self.assertIsNotNone(
            re.search(r"workflow_dispatch:\s*\n\s*inputs:\s*\n\s*tag:", self.texto),
            "workflow_dispatch deve declarar inputs.tag",
        )
        self.assertRegex(
            self.texto, r"tag:\s*\n\s*description:[^\n]*\n\s*required:\s*true"
        )

    def test_checkout_usa_tag_resolvida(self) -> None:
        self.assertIn("ref: ${{ steps.rel.outputs.tag }}", self.texto)

    def test_release_usa_release_tag_e_verify_tag(self) -> None:
        self.assertIn("RELEASE_TAG: ${{ steps.rel.outputs.tag }}", self.texto)
        self.assertIn('gh release create "${RELEASE_TAG}"', self.texto)
        self.assertIn("--verify-tag", self.texto)
        self.assertNotIn('gh release create "${GITHUB_REF_NAME}"', self.texto)

    def test_input_nao_interpolado_no_shell(self) -> None:
        for bloco in re.findall(r"run: \|\n((?:[ \t]+.*\n?)+)", self.texto):
            self.assertNotIn("${{ inputs.", bloco)
            self.assertNotIn("${{ github.event.inputs.", bloco)

    def test_guarda_versao_vs_tag(self) -> None:
        self.assertIn("${RELEASE_TAG#v}", self.texto)

    def test_tarball_inclui_github(self) -> None:
        self.assertIn("install-manifest.json .github \\", self.texto)

    def test_release_publica_tres_assets(self) -> None:
        # O SHA256SUMS referencia o tarball E o manifesto, entao os tres
        # precisam estar disponiveis para `sha256sum -c SHA256SUMS`.
        self.assertIn(
            '"${ASSET}" install-manifest.json SHA256SUMS', self.texto
        )
        self.assertIn("Baixe os 3 assets", self.texto)
        self.assertIn(
            "            install-manifest.json\n            SHA256SUMS", self.texto
        )

    def test_dispatch_idempotente(self) -> None:
        self.assertIn('gh release view "${RELEASE_TAG}"', self.texto)
        self.assertIn("ja existe. Nada a publicar.", self.texto)

    def test_permissions_write_so_no_job(self) -> None:
        self.assertIn("permissions:\n  contents: read", self.texto)
        self.assertIn("permissions:\n      contents: write", self.texto)
        self.assertIn("environment: production", self.texto)

    def test_actions_pinadas_por_sha(self) -> None:
        usos = re.findall(r"uses:\s*([^\s#]+)", self.texto)
        self.assertTrue(usos)
        for u in usos:
            self.assertRegex(u, r"@[0-9a-f]{40}$", u)


class ReleaseWorkflowYamlTest(unittest.TestCase):
    def setUp(self) -> None:
        try:
            import yaml  # type: ignore
        except ImportError:
            self.skipTest("PyYAML ausente — checagem estrutural pulada")
        self.doc = yaml.safe_load(RELEASE.read_text(encoding="utf-8"))

    def test_estrutura(self) -> None:
        on = self.doc.get(True, self.doc.get("on"))
        self.assertIn("workflow_dispatch", on)
        self.assertTrue(on["workflow_dispatch"]["inputs"]["tag"]["required"])
        job = self.doc["jobs"]["release"]
        self.assertEqual(job["permissions"]["contents"], "write")
        passos = job["steps"]
        self.assertEqual(passos[0]["id"], "rel")
        checkout = next(
            p for p in passos if str(p.get("uses", "")).startswith("actions/checkout@")
        )
        self.assertEqual(checkout["with"]["ref"], "${{ steps.rel.outputs.tag }}")


if __name__ == "__main__":
    unittest.main()
