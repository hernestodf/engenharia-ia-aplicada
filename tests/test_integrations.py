#!/usr/bin/env python3
"""Contrato dos adapters opcionais e das skills de integracao.

Nao executa nenhum servidor, CLI externo ou comando de instalacao.
Executa com: python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from generate_adapters import ler_mcp_template, mesclar_config  # noqa: E402
from install import arquivos_canonicos  # noqa: E402
from verify_adapters import falhas  # noqa: E402

NOVAS = (
    "op-chrome-devtools-audit",
    "op-open-code-review",
    "op-openviking-context",
)


class AdaptersTest(unittest.TestCase):
    def test_verificador_sem_erros(self) -> None:
        self.assertEqual(falhas(), [], falhas())

    def test_tres_pins_presentes(self) -> None:
        for nome in ("chrome-devtools-mcp", "open-code-review", "openviking"):
            p = ROOT / "adapters" / nome / "pin.json"
            self.assertTrue(p.is_file(), p)
            dados = json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(dados["habilitado_por_padrao"], False)

    def test_openviking_nao_vendorizado(self) -> None:
        dados = json.loads((ROOT / "adapters/openviking/pin.json").read_text(encoding="utf-8"))
        self.assertEqual(dados["license"], "AGPL-3.0")
        self.assertFalse(dados["vendorizado"])
        self.assertIn("OPENVIKING_API_KEY", dados["credencial"])

    def test_template_mcp_desabilitado(self) -> None:
        mcp = ler_mcp_template()
        self.assertIsNotNone(mcp)
        assert mcp is not None
        servidores = mcp["servers"]
        self.assertEqual(set(servidores), {"chrome-devtools"})
        self.assertTrue(servidores["chrome-devtools"]["disabled"])
        self.assertIn("1.13.0", " ".join(servidores["chrome-devtools"]["command"]))

    def test_mesclar_preserva_chaves_e_nao_habilita(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "opencode.json"
            cfg.write_text(json.dumps({"model": "provider/model", "theme": "x"}), encoding="utf-8")
            saida = mesclar_config(cfg, ["/tmp/skills"], ler_mcp_template())
            dados = json.loads(saida)
            self.assertEqual(dados["model"], "provider/model")
            self.assertEqual(dados["theme"], "x")
            self.assertEqual(dados["skills"], ["/tmp/skills"])
            self.assertTrue(dados["mcp"]["servers"]["chrome-devtools"]["disabled"])

    def test_mesclar_respeita_servidor_existente(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "opencode.json"
            cfg.write_text(
                json.dumps({"mcp": {"servers": {"outro": {"type": "remote", "url": "https://x/mcp"}}}}),
                encoding="utf-8",
            )
            dados = json.loads(mesclar_config(cfg, [], ler_mcp_template()))
            self.assertIn("outro", dados["mcp"]["servers"])
            self.assertIn("chrome-devtools", dados["mcp"]["servers"])

    def test_manifesto_cobre_adapters(self) -> None:
        relativos = set(arquivos_canonicos(ROOT))
        for esperado in (
            "adapters/chrome-devtools-mcp/pin.json",
            "adapters/chrome-devtools-mcp/mcp.json",
            "adapters/chrome-devtools-mcp/README.md",
            "adapters/open-code-review/pin.json",
            "adapters/openviking/pin.json",
            "adapters/openviking/mcp.opencode.json",
            "scripts/verify_adapters.py",
        ):
            self.assertIn(esperado, relativos)


class SkillsIntegradasTest(unittest.TestCase):
    def test_skills_core_presentes_e_validas(self) -> None:
        for nome in NOVAS:
            md = ROOT / "skills/core" / nome / "SKILL.md"
            self.assertTrue(md.is_file(), md)
            texto = md.read_text(encoding="utf-8")
            self.assertIn(f"name: {nome}", texto)
            self.assertIn("engenharia-ia-aplicada/layer: core", texto)
            self.assertIn("pendente", texto)

    def test_preflight_nao_instala(self) -> None:
        padroes = ("npm install", "curl -fsSL", "npx skills add", "openviking-server init")
        for nome in NOVAS:
            texto = (ROOT / "skills/core" / nome / "SKILL.md").read_text(encoding="utf-8")
            # As skills podem NOMEAR o comando para orientar o operador, mas a
            # orientacao sempre vem acompanhada de "Nunca"/"pare".
            self.assertIn("Nunca", texto)
            for padrao in padroes:
                if padrao in texto:
                    self.assertIn("Nunca", texto)

    def test_sem_cjk_nas_novas_skills(self) -> None:
        import re

        cjk = re.compile(r"[\u3400-\u9FFF\uF900-\uFAFF\u3040-\u30FF]")
        for nome in NOVAS:
            texto = (ROOT / "skills/core" / nome / "SKILL.md").read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(texto), nome)


if __name__ == "__main__":
    unittest.main()
