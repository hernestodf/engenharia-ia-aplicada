#!/usr/bin/env python3
"""Testes do loop de incidentes: contrato, gates de revisão e não-execução."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate_incidents as vi  # noqa: E402


class IncidentsTest(unittest.TestCase):
    def test_validador_da_estado_limpo(self) -> None:
        r = subprocess.run(
            ["python3", str(ROOT / "scripts" / "validate_incidents.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Incidentes validados: 2 | Problemas: 0", r.stdout)

    def test_incidentes_reais_estao_presentes(self) -> None:
        arquivos = sorted((ROOT / "evaluations" / "incidents").glob("INC-*.json"))
        self.assertGreaterEqual(len(arquivos), 2)
        estados = {}
        for arquivo in arquivos:
            inc = json.loads(arquivo.read_text(encoding="utf-8"))
            estados[inc["id"]] = inc["status"]
        self.assertEqual(estados.get("INC-001"), "fechado")
        self.assertEqual(estados.get("INC-002"), "rascunho")

    def test_fechado_sem_revisao_e_recusado(self) -> None:
        inc = json.loads((ROOT / "evaluations/incidents/INC-001.json").read_text())
        inc["revisao"] = {"revisado_por": "", "data": "", "decisao": ""}
        problemas = vi.validar_incidente(inc, "INC-001.json")
        self.assertTrue(any("revisao.revisado_por" in p for p in problemas), problemas)

    def test_fechado_sem_testes_verdes_e_recusado(self) -> None:
        inc = json.loads((ROOT / "evaluations/incidents/INC-001.json").read_text())
        inc["testes_verdes"] = False
        problemas = vi.validar_incidente(inc, "INC-001.json")
        self.assertTrue(any("testes_verdes deve ser true" in p for p in problemas), problemas)

    def test_id_fora_do_padrao_e_recusado(self) -> None:
        inc = json.loads((ROOT / "evaluations/incidents/INC-001.json").read_text())
        inc["id"] = "INC-abc"
        problemas = vi.validar_incidente(inc, "INC-001.json")
        self.assertTrue(any("id inválido" in p for p in problemas), problemas)

    def test_rascunho_com_revisao_preenchida_e_recusado(self) -> None:
        inc = json.loads((ROOT / "evaluations/incidents/INC-002.json").read_text())
        inc["revisao"]["revisado_por"] = "alguém"
        problemas = vi.validar_incidente(inc, "INC-002.json")
        self.assertTrue(any("rascunho não pode ter revisao" in p for p in problemas), problemas)

    def test_validador_nao_contem_execucao_de_comandos(self) -> None:
        fonte = (ROOT / "scripts" / "validate_incidents.py").read_text()
        for proibido in ("subprocess", "os.system", "eval(", "Popen"):
            self.assertNotIn(proibido, fonte, f"validador não deve usar {proibido}")


if __name__ == "__main__":
    unittest.main()
