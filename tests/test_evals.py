#!/usr/bin/env python3
"""Testes do harness de eval — sem chamada de modelo, sem efeito externo."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import run_evals as reval  # noqa: E402


class HarnessTest(unittest.TestCase):
    def test_carrega_quatro_cenarios(self) -> None:
        cenarios = reval.carregar_cenarios()
        self.assertEqual(len(cenarios), 4)
        self.assertEqual([c.id for c in cenarios], ["01", "02", "03", "04"])
        for c in cenarios:
            self.assertTrue(c.entrada, f"entrada vazia em {c.arquivo}")
            self.assertTrue(c.esperado, f"esperado vazio em {c.arquivo}")

    def test_tipos_derivados_do_campo_automatico(self) -> None:
        tipos = {c.id: c.tipo for c in reval.carregar_cenarios()}
        self.assertEqual(tipos["01"], "llm")
        self.assertEqual(tipos["02"], "misto")
        self.assertEqual(tipos["03"], "deterministico")
        self.assertEqual(tipos["04"], "llm")

    def test_modo_none_nao_chama_provider(self) -> None:
        original = reval.subprocess.run
        chamadas: list[list[str]] = []

        def vigia(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            chamadas.append(argv)
            if "validate_catalog.py" in " ".join(argv):
                return original(argv, **kwargs)  # type: ignore[arg-type]
            raise AssertionError(f"provider chamado indevidamente: {argv}")

        reval.subprocess.run = vigia  # type: ignore[assignment]
        try:
            codigo = reval.main(["--provider", "none", "--no-record"])
        finally:
            reval.subprocess.run = original  # type: ignore[assignment]

        self.assertEqual(codigo, 0)
        self.assertFalse(any(c and c[0] != "python3" for c in chamadas), chamadas)

    def test_sanitizacao_redige_segredos_antes_de_sair(self) -> None:
        # Montado por partes para nao parecer credencial real em scan de segredos.
        chave = "sk-" + "abcdef123456"
        gh = "ghp_" + "abcdefghijklmnopqrst"
        texto = f"api_key={chave} {gh} token: " + "ABC123XYZ"
        limpo = reval.sanitizar(texto)
        self.assertNotIn(chave, limpo)
        self.assertNotIn(gh, limpo)
        self.assertNotIn("ABC123XYZ", limpo)
        self.assertIn("<redigido>", limpo)

    def test_registro_jsonl_e_valido_e_sanitizado(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "RESULTS.jsonl"
            reval.registrar(caminho, {"status": "testado", "evidencia": "chave sk-1234567890abc"})
            linha = caminho.read_text(encoding="utf-8").strip()
            dados = json.loads(linha)
            self.assertEqual(dados["status"], "testado")
            self.assertNotIn("sk-1234567890abc", linha)

    def test_assertions_presenca_e_ausencia(self) -> None:
        ok, _ = reval.checar_assertions(
            "01-routing", "Escolho eia-backend. Fica não verificado o restante."
        )
        self.assertTrue(ok)
        ok, motivo = reval.checar_assertions("01-routing", "sem conteúdo")
        self.assertFalse(ok)
        self.assertIn("ausentes", motivo)

    def test_assertions_rejeita_unverified_no_gate(self) -> None:
        """Regressão do parecer QA: presença de termo não pode virar 'testado'."""
        texto = "bloqueado rm -rf autorizacao UNVERIFIED"
        ok, motivo = reval.checar_assertions("02-security-gate", texto)
        self.assertFalse(ok)
        self.assertIn("proibidos", motivo)

    def test_extrai_texto_de_json_do_provider(self) -> None:
        bruto = '{"tipo":"text","content":"eia-backend e nao verificado"}'
        self.assertIn("eia-backend", reval.extrair_texto_saida(bruto))

    def test_extrator_ignora_snapshot_e_tool_use(self) -> None:
        """Regressão do falso positivo: snapshot/tool_use não são resposta."""
        bruto = "\n".join(
            [
                '{"type":"step_start","part":{"type":"step-start","snapshot":"ABC123"}}',
                '{"type":"tool_use","part":{"type":"tool","tool":"glob","text":"rm -rf"}}',
                '{"type":"text","part":{"type":"text","text":"resposta real do modelo"}}',
                '{"type":"step_finish","part":{"type":"step-finish","reason":"stop"}}',
            ]
        )
        extraido = reval.extrair_texto_saida(bruto)
        self.assertEqual(extraido, "resposta real do modelo")
        self.assertNotIn("ABC123", extraido)
        self.assertNotIn("rm -rf", extraido)

    def test_extrator_sem_texto_em_eventos_retorna_vazio(self) -> None:
        bruto = '{"type":"step_start","part":{"type":"step-start","snapshot":"ABC123"}}'
        self.assertEqual(reval.extrair_texto_saida(bruto), "")

    def test_extrator_texto_puro_continua_funcionando(self) -> None:
        self.assertEqual(reval.extrair_texto_saida("resposta sem json"), "resposta sem json")

    def test_providers_tem_formato_json_e_agente_sem_modelo_fixo(self) -> None:
        """Trocar de LLM é só --provider/--model; nada de modelo hardcoded."""
        self.assertEqual(set(reval.ARGV_PROVIDER), {"opencode"})
        for argv in reval.ARGV_PROVIDER.values():
            self.assertIn("--format", argv)
            self.assertIn("json", argv)
            self.assertIn("eia-qa-security", argv)
            self.assertNotIn("--model", argv)

    def test_novo_provider_pode_ser_registrado(self) -> None:
        """Agnóstico de provider: basta registrar em ARGV_PROVIDER."""
        original = dict(reval.ARGV_PROVIDER)
        reval.ARGV_PROVIDER["demo"] = ["demo", "run", "--format", "json"]
        try:
            with redirect_stdout(io.StringIO()):
                codigo = reval.main(
                    ["--provider", "demo", "--dry-run", "--scenario", "01", "--no-record"]
                )
        finally:
            reval.ARGV_PROVIDER.clear()
            reval.ARGV_PROVIDER.update(original)
        self.assertEqual(codigo, 0)

    def test_provider_desconhecido_e_rejeitado(self) -> None:
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                reval.main(["--provider", "inexistente", "--no-record"])
        self.assertEqual(ctx.exception.code, 2)

    def test_sem_provider_especifico_no_codigo(self) -> None:
        """Nenhum runtime fica hardcoded no harness; só entra pelo registro."""
        fonte = (ROOT / "scripts" / "run_evals.py").read_text(encoding="utf-8")
        self.assertNotIn("ki" + "lo", fonte.lower())

    def test_sem_exec_sem_shell_true(self) -> None:
        fonte = (ROOT / "scripts" / "run_evals.py").read_text(encoding="utf-8")
        for proibido in ("eval(", "exec(", "shell=True", "os.system"):
            self.assertNotIn(proibido, fonte, f"harness não deve conter {proibido}")

    def test_carrega_vinte_tarefas(self) -> None:
        tarefas = reval.carregar_tarefas()
        self.assertEqual(len(tarefas), 20)
        self.assertEqual([t["id"] for t in tarefas[:3]], ["T01", "T02", "T03"])
        self.assertEqual([t["id"] for t in tarefas[-2:]], ["T19", "T20"])
        det = [t for t in tarefas if t["tipo"] == "deterministico"]
        llm = [t for t in tarefas if t["tipo"] == "llm"]
        self.assertEqual((len(det), len(llm)), (16, 4))

    def test_tarefa_llm_sem_provider_e_nao_verificado(self) -> None:
        tarefas = {t["id"]: t for t in reval.carregar_tarefas()}
        status, nota, maxima, ev = reval.avaliar_tarefa(tarefas["T05"], "none", None, 10)
        self.assertEqual((status, nota, maxima), ("nao verificado", 0, 2))
        self.assertIn("sem inferencia", ev)

    def test_tarefa_deterministica_pontua_criterios(self) -> None:
        tarefas = {t["id"]: t for t in reval.carregar_tarefas()}
        status, nota, maxima, _ = reval.avaliar_tarefa(tarefas["T01"], "none", None, 10)
        self.assertEqual((status, nota, maxima), ("testado", 6, 6))

    def test_verificador_desconhecido_falha_fechada(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "ruim.json"
            p.write_text(
                json.dumps([{
                    "id": "T99", "tipo": "deterministico", "prompt": "x",
                    "criterios": [{"id": "C1", "verificador": "inexistente", "params": {}}],
                }]),
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit):
                reval.carregar_tarefas(Path(tmp))

    def test_comando_fora_da_whitelist_e_rejeitado(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import eval_checks

        with self.assertRaises(ValueError):
            eval_checks.comando_saida({"comando": "rm", "contem": "ok"})
        with self.assertRaises(ValueError):
            eval_checks.arquivo_termos({"arquivo": "/etc/passwd", "termos": ["root"]})

    def test_comparar_baseline_detecta_queda_de_nota(self) -> None:
        base = {
            "versao": reval.VERSAO_BASELINE,
            "pass_rate": 1.0,
            "por_tarefa": {"T01": {"nota": 6, "maxima": 6, "status": "testado"}},
        }
        registros = [
            {"tarefa": "T01", "tipo": "deterministico", "nota": 5, "maxima": 6, "status": "falhou"},
            {"tarefa": "T05", "tipo": "llm", "nota": 0, "maxima": 2, "status": "nao verificado"},
        ]
        problemas = reval.comparar_baseline(base, registros)
        self.assertTrue(any("T01: 6 -> 5" in p for p in problemas), problemas)
        self.assertTrue(any("pass_rate" in p for p in problemas), problemas)

    def test_baseline_gravado_e_legivel(self) -> None:
        import tempfile

        original = reval.ARQUIVO_BASELINE
        with tempfile.TemporaryDirectory() as tmp:
            reval.ARQUIVO_BASELINE = Path(tmp) / "BASELINE.json"
            try:
                registros = [
                    {"tarefa": "T01", "tipo": "deterministico", "nota": 6, "maxima": 6,
                     "status": "testado"},
                    {"tarefa": "T05", "tipo": "llm", "nota": 0, "maxima": 2,
                     "status": "nao verificado"},
                ]
                base = reval.escrever_baseline(registros)
                self.assertEqual(base["pass_rate"], 1.0)
                self.assertEqual(base["deterministicas"], 1)
                self.assertEqual(reval.ler_baseline()["versao"], reval.VERSAO_BASELINE)
            finally:
                reval.ARQUIVO_BASELINE = original

    def test_suite_tasks_sem_provider_nao_chama_modelo(self) -> None:
        original = reval.subprocess.run
        chamadas: list[list[str]] = []

        def vigia(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            chamadas.append(argv)
            return original(argv, **kwargs)  # type: ignore[arg-type]

        reval.subprocess.run = vigia  # type: ignore[assignment]
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                codigo = reval.main([
                    "--suite", "tasks", "--provider", "none",
                    "--no-record", "--no-compare",
                ])
        finally:
            reval.subprocess.run = original  # type: ignore[assignment]
        self.assertEqual(codigo, 0)
        self.assertFalse(
            any(c and any(c[0] == argv[0] for argv in reval.ARGV_PROVIDER.values()) for c in chamadas), chamadas
        )
        self.assertTrue(any("verify_adapters.py" in " ".join(c) for c in chamadas))
        self.assertIn("pass rate", buf.getvalue())

    def test_dry_run_nao_registra(self) -> None:
        original = reval.subprocess.run

        def vigia(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            raise AssertionError(f"dry-run chamou processo: {argv}")

        reval.subprocess.run = vigia  # type: ignore[assignment]
        try:
            codigo = reval.main(["--dry-run", "--scenario", "01-routing", "--no-record"])
        finally:
            reval.subprocess.run = original  # type: ignore[assignment]
        self.assertEqual(codigo, 0)


if __name__ == "__main__":
    unittest.main()
