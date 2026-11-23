#!/usr/bin/env python3
"""Avaliação determinística de recuperação (RAG) sobre o catálogo local.

Não há embedding, vetor store, rede ou reindexação. Isto é um **baseline lexical**
(BM25) usado para medir recall/MRR com ground truth curado. Serve para detectar
regressão no retrieval; não prova qualidade de um pipeline vetorial.

Uso:
  python3 scripts/rag_eval.py
  python3 scripts/rag_eval.py --write-baseline
  python3 scripts/rag_eval.py --no-compare
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CORPUS = (ROOT / "skills" / "core", ROOT / "skills" / "upstream")
QUERIES = ROOT / "evaluations" / "rag" / "queries.jsonl"
BASELINE = ROOT / "evaluations" / "rag" / "BASELINE.json"
RESULTADOS = ROOT / "evaluations" / "rag" / "RESULTS.json"
VERSAO = 1
K = 5
K_MRR = 10
TOLERANCIA = 0.001

STOPWORDS = {
    "a", "as", "de", "da", "do", "em", "e", "para", "com", "um", "uma", "os",
    "no", "na", "que", "ou", "por", "como", "usar", "usando", "fazer", "the", "a", "an",
    "of", "to", "in", "and", "for", "with", "on", "is", "how", "use", "using",
}

TOKEN = re.compile(r"[^\W_]+", re.UNICODE)


def tokenizar(texto: str) -> list[str]:
    return [t for t in TOKEN.findall(texto.lower()) if t not in STOPWORDS and len(t) > 1]


def carregar_corpus() -> dict[str, str]:
    """Extrai id e descrição do frontmatter. Nenhum corpo é executado."""
    corpus: dict[str, str] = {}
    for raiz in CORPUS:
        for skill in sorted(raiz.glob("*/SKILL.md")):
            texto = skill.read_text(encoding="utf-8", errors="replace")
            if not texto.startswith("---"):
                continue
            fim = texto.find("\n---", 3)
            if fim < 0:
                continue
            cabecalho = texto[3:fim]
            nome = re.search(r"^name:\s*(\S+)", cabecalho, re.M)
            desc = re.search(r"^description:\s*(.+)$", cabecalho, re.M)
            if nome and desc and nome.group(1).startswith("op-"):
                # O ID é parte legítima do documento: nome e descrição são indexados.
                corpus[nome.group(1)] = f"{nome.group(1)} {desc.group(1)}"
    return corpus


def carregar_queries() -> list[dict[str, Any]]:
    itens: list[dict[str, Any]] = []
    with QUERIES.open(encoding="utf-8") as fh:
        for linha in fh:
            if linha.strip():
                item = json.loads(linha)
                if not isinstance(item, dict) or "consulta" not in item or "relevantes" not in item:
                    raise ValueError("query inválida")
                itens.append(item)
    return itens


class BM25:
    """BM25 puro, determinístico, sem dependências externas."""

    def __init__(self, docs: dict[str, str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.tokens = {doc: tokenizar(texto) for doc, texto in docs.items()}
        self.tf = {doc: Counter(ts) for doc, ts in self.tokens.items()}
        self.len = {doc: len(ts) for doc, ts in self.tokens.items()}
        n = len(docs)
        self.media = sum(self.len.values()) / n if n else 0.0
        self.df: Counter[str] = Counter()
        for ts in self.tokens.values():
            self.df.update(set(ts))
        self.idf = {
            termo: math.log(1 + (n - freq + 0.5) / (freq + 0.5)) for termo, freq in self.df.items()
        }

    def search(self, consulta: str, k: int = K) -> list[tuple[str, float]]:
        termos = tokenizar(consulta)
        pontos: list[tuple[str, float]] = []
        for doc, tf in self.tf.items():
            total = 0.0
            for termo in termos:
                freq = tf.get(termo, 0)
                if not freq or termo not in self.idf:
                    continue
                denom = freq + self.k1 * (1 - self.b + self.b * self.len[doc] / (self.media or 1))
                total += self.idf[termo] * freq * (self.k1 + 1) / denom
            if total > 0:
                pontos.append((doc, round(total, 6)))
        pontos.sort(key=lambda par: (-par[1], par[0]))
        return pontos[:k]


def avaliar(corpus: dict[str, str], queries: list[dict[str, Any]]) -> dict[str, Any]:
    bm25 = BM25(corpus)
    por_query: list[dict[str, Any]] = []
    for q in queries:
        esperados = set(q["relevantes"])
        top5 = [doc for doc, _ in bm25.search(q["consulta"], K)]
        top10 = [doc for doc, _ in bm25.search(q["consulta"], K_MRR)]
        acertos5 = len(esperados & set(top5))
        rank = next((i + 1 for i, doc in enumerate(top10) if doc in esperados), None)
        por_query.append(
            {
                "id": q["id"],
                "relevantes": sorted(esperados),
                "top5": top5,
                "recall_at_5": round(acertos5 / len(esperados), 6) if esperados else 0.0,
                "precision_at_5": round(acertos5 / K, 6),
                "mrr_at_10": round(1 / rank, 6) if rank else 0.0,
            }
        )
    macro = {
        chave: round(sum(item[chave] for item in por_query) / len(por_query), 6)
        for chave in ("recall_at_5", "precision_at_5", "mrr_at_10")
    }
    return {
        "descricao": "Baseline lexical BM25 sobre descrições de skills; ground truth curado.",
        "versao": VERSAO,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "corpus": len(corpus),
        "queries": len(queries),
        "k": K,
        "macro": macro,
        "por_query": por_query,
    }


def comparar(atual: dict[str, Any], base: dict[str, Any]) -> list[str]:
    """Falha quando uma métrica macro cai; nenhuma melhoria esconde a queda."""
    erros: list[str] = []
    if base.get("versao") != VERSAO:
        return ["baseline com versão incompatível"]
    for chave, valor in base.get("macro", {}).items():
        novo = atual.get("macro", {}).get(chave)
        if not isinstance(novo, (int, float)):
            erros.append(f"{chave}: métrica ausente")
        elif novo < valor - TOLERANCIA:
            erros.append(f"REGRESSAO: {chave}: {valor} -> {novo}")
    return erros


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-baseline", action="store_true", help="grava BASELINE.json com a execução atual")
    ap.add_argument("--no-compare", action="store_true", help="não compara com o baseline existente")
    args = ap.parse_args()

    corpus = carregar_corpus()
    queries = carregar_queries()
    if not corpus or not queries:
        print("Corpus ou consultas vazias.", file=sys.stderr)
        return 1
    atual = avaliar(corpus, queries)
    RESULTADOS.write_text(json.dumps(atual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    macro = atual["macro"]
    print(
        f"corpus {atual['corpus']} | {atual['queries']} consultas | "
        f"recall@5 {macro['recall_at_5']:.3f} | precision@5 {macro['precision_at_5']:.3f} | "
        f"MRR@10 {macro['mrr_at_10']:.3f}"
    )

    if args.write_baseline:
        BASELINE.write_text(json.dumps(atual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Baseline gravado: {BASELINE.name}")
        return 0
    if args.no_compare or not BASELINE.is_file():
        print("Sem comparação de baseline.")
        return 0

    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    erros = comparar(atual, base)
    if erros:
        for erro in erros:
            print(erro)
        return 1
    print("Baseline mantido (sem regressão).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
