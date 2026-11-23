#!/usr/bin/env python3
"""Testes do avaliador de recuperação — corpus em memória, sem rede."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import rag_eval as rag  # noqa: E402


CORPUS = {
    "op-pdf": "Converte arquivos e documentos em PDF e gera PDFs a partir de markdown.",
    "op-xlsx": "Abre, edita e cria planilhas Excel com formulas e formatacao.",
    "op-pptx": "Cria slide decks e apresentacoes em PowerPoint.",
}


class RagEvalTest(unittest.TestCase):
    def test_tokenizar_remove_stopwords(self) -> None:
        tokens = rag.tokenizar("Como converter Markdown em PDF usando a ferramenta")
        self.assertIn("converter", tokens)
        self.assertIn("markdown", tokens)
        self.assertIn("pdf", tokens)
        self.assertNotIn("como", tokens)
        self.assertNotIn("usando", tokens)

    def test_bm25_ranking(self) -> None:
        bm = rag.BM25(CORPUS)
        resultados = [doc for doc, _ in bm.search("criar apresentacao slide pptx")]
        self.assertEqual(resultados[0], "op-pptx")

    def test_bm25_ignora_termos_fora_do_corpus(self) -> None:
        bm = rag.BM25(CORPUS)
        self.assertEqual(bm.search("zzzz inexistente"), [])

    def test_bm25_e_deterministico(self) -> None:
        bm = rag.BM25(CORPUS)
        self.assertEqual(bm.search("pdf markdown"), bm.search("pdf markdown"))

    def test_metricas_recall_precision_mrr(self) -> None:
        consultas = [{"id": "Q1", "consulta": "converter markdown pdf", "relevantes": ["op-pdf"]}]
        medido = rag.avaliar(CORPUS, consultas)
        item = medido["por_query"][0]
        self.assertEqual(item["top5"][0], "op-pdf")
        self.assertEqual(item["recall_at_5"], 1.0)
        self.assertEqual(item["mrr_at_10"], 1.0)
        self.assertEqual(item["precision_at_5"], 0.2)

    def test_relevante_fora_do_corpus_conta_como_erro(self) -> None:
        consultas = [{"id": "Q1", "consulta": "pdf", "relevantes": ["op-inexistente"]}]
        medido = rag.avaliar(CORPUS, consultas)
        self.assertEqual(medido["por_query"][0]["recall_at_5"], 0.0)
        self.assertEqual(medido["por_query"][0]["mrr_at_10"], 0.0)

    def test_comparar_detecta_regressao(self) -> None:
        base = {"versao": rag.VERSAO, "macro": {"recall_at_5": 0.8, "mrr_at_10": 0.6}}
        atual = {"versao": rag.VERSAO, "macro": {"recall_at_5": 0.7, "mrr_at_10": 0.6}}
        erros = rag.comparar(atual, base)
        self.assertTrue(any("REGRESSAO" in e for e in erros))

    def test_comparar_aceita_estabilidade_e_melhoria(self) -> None:
        base = {"versao": rag.VERSAO, "macro": {"recall_at_5": 0.5}}
        self.assertEqual(rag.comparar({"macro": {"recall_at_5": 0.5}}, base), [])
        self.assertEqual(rag.comparar({"macro": {"recall_at_5": 0.9}}, base), [])

    def test_comparar_rejeita_versao_incompativel(self) -> None:
        erros = rag.comparar({"macro": {}}, {"versao": 999, "macro": {}})
        self.assertTrue(erros)

    def test_ground_truth_e_valido_para_o_corpus_real(self) -> None:
        corpus = rag.carregar_corpus()
        consultas = rag.carregar_queries()
        self.assertGreater(len(corpus), 700)
        self.assertGreaterEqual(len(consultas), 16)
        for q in consultas:
            self.assertTrue(q["relevantes"], q["id"])
            for alvo in q["relevantes"]:
                self.assertIn(alvo, corpus, f"{q['id']}: {alvo} ausente")


if __name__ == "__main__":
    unittest.main()
