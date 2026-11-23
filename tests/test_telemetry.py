#!/usr/bin/env python3
"""Testes de telemetria —Sem rede e sem gravação fora de um temp explícito."""

from __future__ import annotations

import io
import json
import os
import socket
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import telemetry as tel  # noqa: E402


class TelemetryTest(unittest.TestCase):
    def test_whitelist_de_eventos_e_resultados(self) -> None:
        with self.assertRaises(ValueError):
            tel.normalizar("evento_inventado", "ok")
        with self.assertRaises(ValueError):
            tel.normalizar("eval_concluido", "sucesso")

    def test_duracao_invalida(self) -> None:
        with self.assertRaises(ValueError):
            tel.normalizar("eval_concluido", "ok", -1)

    def test_registro_tem_apenas_campos_do_contrato(self) -> None:
        r = tel.normalizar("eval_concluido", "ok", 12, datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(
            set(r),
            {"schema", "evento", "resultado", "duracao_ms", "registrado_em", "versao_pacote"},
        )
        self.assertEqual(r["duracao_ms"], 12)
        self.assertTrue(r["registrado_em"].endswith("+00:00"))

    def test_redige_chaves_de_api(self) -> None:
        texto = "chave sk-abcdef123456 e ghp_abcdefghijklmnop"
        self.assertNotIn("sk-abcdef123456", tel.redigir(texto))
        self.assertNotIn("ghp_abcdefghijklmnop", tel.redigir(texto))

    def test_redige_aws_e_header_bearer(self) -> None:
        # Montado por partes para nao parecer credencial real em scan de segredos.
        aws = "AKIA" + "ABCDEFGHIJKLMNOP"
        bearer = "Bearer " + "abcdef123456"
        texto = f"{aws} e Authorization: {bearer}"
        limpo = tel.redigir(texto)
        self.assertNotIn(aws, limpo)
        self.assertNotIn(bearer, limpo)

    def test_redige_atributos_e_caminhos_de_usuario(self) -> None:
        texto = "api_key=segredo123 arquivo /home/alice/projeto/segredo.txt"
        limpo = tel.redigir(texto)
        self.assertNotIn("segredo123", limpo)
        self.assertNotIn("/home/alice", limpo)

    def test_desabilitado_por_padrao(self) -> None:
        with patch.dict(os.environ, {tel.VARIAVEL: "0"}, clear=False):
            self.assertFalse(tel.habilitado())
            saida = tel.registrar(tel.normalizar("eval_concluido", "ok"))
        self.assertFalse(saida["registrado"])
        self.assertEqual(saida["eventos"], 0)

    def test_grava_apenas_quando_habilitado_e_em_diretorio_permitido(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "events.jsonl"
            registro = tel.normalizar("rag_avaliado", "ok")
            with patch.dict(os.environ, {tel.VARIAVEL: "1"}, clear=False):
                with patch.object(tel, "DESTINO", alvo):
                    saida = tel.registrar(registro, alvo)
                    resumo = tel.resumo(alvo)
        self.assertTrue(saida["registrado"])
        self.assertEqual(resumo["total"], 1)
        self.assertIn("rag_avaliado/ok", resumo["por_evento_resultado"])

    def test_resumo_ignora_linhas_invalidas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "events.jsonl"
            alvo.write_text("{invalido}\n" + json.dumps({"evento": "gate_avaliado", "resultado": "erro"}) + "\n")
            self.assertEqual(tel.resumo(alvo)["total"], 1)

    def test_telemetria_nao_abre_socket(self) -> None:
        original = socket.socket

        def proibido(*args: object, **kwargs: object) -> object:
            raise AssertionError("telemetria tentou abrir socket")

        socket.socket = proibido  # type: ignore[assignment]
        try:
            tel.normalizar("eval_concluido", "ok")
            tel.resumo(Path(tempfile.gettempdir()) / "inexistente.jsonl")
        finally:
            socket.socket = original  # type: ignore[assignment]

    def test_cli_habilitado(self) -> None:
        with patch.dict(os.environ, {tel.VARIAVEL: "1"}, clear=False):
            with patch.object(sys, "argv", ["telemetry.py", "--habilitado"]):
                saida = io.StringIO()
                with redirect_stdout(saida):
                    codigo = tel.main()
        self.assertEqual(codigo, 0)
        self.assertIn("=1", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
