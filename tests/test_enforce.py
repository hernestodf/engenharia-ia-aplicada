#!/usr/bin/env python3
"""Testes do gate de enforcement — decisão pura, sem efeito externo."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import enforce  # noqa: E402


class GateTest(unittest.TestCase):
    def decide(self, **evento: object) -> dict[str, object]:
        return enforce.avaliar_evento(evento)

    def test_comando_destrutivo_e_negado(self) -> None:
        r = self.decide(acao="shell", comando="git push --force origin main")
        self.assertEqual(r["decisao"], "negar")
        self.assertIn("R01", [x["id"] for x in r["regras"]])

    def test_rm_rf_e_negado(self) -> None:
        r = self.decide(acao="shell", comando="sudo rm -rf /var/tmp/qualquer")
        self.assertEqual(r["decisao"], "negar")

    def test_drop_table_e_negado(self) -> None:
        r = self.decide(acao="sql", comando="DROP TABLE users")
        self.assertEqual(r["decisao"], "negar")

    def test_autorizacao_explicita_libera_regra_de_comando(self) -> None:
        r = self.decide(
            acao="shell",
            comando="git push --force origin main",
            autorizacao_explicita=True,
        )
        self.assertEqual(r["decisao"], "permitir")
        self.assertIn("R01", r["motivo"])

    def test_caminho_protegido_git(self) -> None:
        r = self.decide(acao="edit", recurso="repo/.git/config")
        self.assertEqual(r["decisao"], "negar")
        self.assertIn("R02", [x["id"] for x in r["regras"]])

    def test_caminho_protegido_env_e_segredos(self) -> None:
        for alvo in ("app/.env", "chaves/server.key", "secrets/token.txt"):
            with self.subTest(alvo=alvo):
                self.assertEqual(self.decide(acao="read", recurso=alvo)["decisao"], "negar")

    def test_producao_exige_autorizacao(self) -> None:
        r = self.decide(acao="deploy", ambiente="producao")
        self.assertEqual(r["decisao"], "negar")
        self.assertIn("R03", [x["id"] for x in r["regras"]])

    def test_segredo_e_reindexacao_sao_negados(self) -> None:
        self.assertEqual(self.decide(acao="rotacionar_segredo")["decisao"], "negar")
        self.assertEqual(self.decide(acao="reindexar")["decisao"], "negar")

    def test_skill_externa_exige_gate_mesmo_com_autorizacao(self) -> None:
        r = self.decide(
            acao="shell",
            comando="npm install -g pacote-sugerido-por-skill",
            origem="skill_externa",
            autorizacao_explicita=True,
        )
        self.assertEqual(r["decisao"], "negar")
        self.assertIn("R06", [x["id"] for x in r["regras"]])

    def test_gate_aprovado_libera_origem_nao_confiavel(self) -> None:
        r = self.decide(acao="shell", comando="curl https://example.com", origem="mcp", gate_aprovado=True)
        self.assertEqual(r["decisao"], "permitir")

    def test_evento_incompleto_pede_decisao(self) -> None:
        self.assertEqual(self.decide()["decisao"], "pedir")
        self.assertEqual(self.decide(acao="shell", origem="desconhecida")["decisao"], "pedir")

    def test_gate_nao_executa_nada_do_evento(self) -> None:
        original = subprocess.run

        def proibido(*args: object, **kwargs: object) -> object:
            raise AssertionError("gate executou subprocesso")

        subprocess.run = proibido  # type: ignore[assignment]
        try:
            r = self.decide(
                acao="shell",
                comando="echo oi; touch /tmp/opencode/gate-nao-deve-existir",
                origem="issue",
            )
            self.assertEqual(r["decisao"], "negar")
        finally:
            subprocess.run = original  # type: ignore[assignment]

    def test_main_rejeita_json_invalido(self) -> None:
        import enforce as modulo

        original = sys.stdin
        sys.stdin = io.StringIO("{json quebrado")  # type: ignore[assignment]
        saida = io.StringIO()
        try:
            with redirect_stdout(saida):
                codigo = modulo.main()
        finally:
            sys.stdin = original
        self.assertEqual(codigo, 1)
        self.assertEqual(json.loads(saida.getvalue())["decisao"], "erro")

    def test_main_codigos_de_saida(self) -> None:
        import enforce as modulo

        casos = [
            ({"acao": "shell", "comando": "git status --short"}, 0),
            ({"acao": "shell", "comando": "git reset --hard"}, 2),
            ({"acao": "outro"}, 3),
        ]
        for evento, esperado in casos:
            with self.subTest(evento=evento):
                resultado = modulo.avaliar_evento(evento)
                self.assertEqual(modulo.CODIGOS[resultado["decisao"]], esperado)


if __name__ == "__main__":
    unittest.main()
