#!/usr/bin/env python3
"""Telemetria mínima e local da Engenharia de IA Aplicada.

Nada é enviado a lugar nenhum. Nenhum prompt, conteúdo de arquivo, caminho de
usuário ou segredo é registrado. O registro só acontece com EIA_TELEMETRY=1.

Eventos São de uma whitelist fechada; campos desconhecidos são descartados.
O destino é um JSONL dentro do diretório do pacote, com permissão 0600.

Uso:
  EIA_TELEMETRY=1 python3 scripts/telemetry.py --evento eval_concluido --resultado ok
  python3 scripts/telemetry.py --resumo
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DESTINO = ROOT / "evaluations" / "telemetry.jsonl"
VERSAO_SCHEMA = 1
VARIAVEL = "EIA_TELEMETRY"

EVENTOS = {
    "eval_concluido",
    "rag_avaliado",
    "gate_avaliado",
    "auditoria_concluida",
    "instalacao_concluida",
}
RESULTADOS = {"ok", "erro", "nao_verificado"}

PADROES_SECRETOS = (
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"ghp_[A-Za-z0-9]{8,}"),
    re.compile(r"AKIA[0-9A-Z]{12,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{8,}"),
)
PADRAO_CAMINHO_USUARIO = re.compile(r"(?:/home/|/Users/)[^\s\"']+")


def habilitado() -> bool:
    return os.environ.get(VARIAVEL, "").strip() == "1"


def redigir(texto: str) -> str:
    """Remove segredos e caminhos de usuário antes de qualquer persistência."""
    limpo = texto
    for padrao in PADROES_SECRETOS:
        limpo = padrao.sub("[REDACTED]", limpo)
    return PADRAO_CAMINHO_USUARIO.sub("[CAMINHO]", limpo)


def normalizar(
    evento: str,
    resultado: str,
    duracao_ms: int | None = None,
    agora: datetime | None = None,
) -> dict[str, Any]:
    """Constrói um registro canônico. Campos fora do contrato não entram."""
    if evento not in EVENTOS:
        raise ValueError(f"evento fora da whitelist: {evento}")
    if resultado not in RESULTADOS:
        raise ValueError(f"resultado inválido: {resultado}")
    if duracao_ms is not None and (not isinstance(duracao_ms, int) or duracao_ms < 0):
        raise ValueError("duracao_ms deve inteiro não negativo")
    momento = agora or datetime.now(timezone.utc)
    return {
        "schema": VERSAO_SCHEMA,
        "evento": redigir(evento),
        "resultado": redigir(resultado),
        "duracao_ms": duracao_ms,
        "registrado_em": momento.astimezone(timezone.utc).isoformat(),
        "versao_pacote": _versao(),
    }


def _versao() -> str:
    try:
        return (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "desconhecida"


def registrar(registro: dict[str, Any], destino: Path = DESTINO) -> dict[str, Any]:
    """Só grava quando habilitado. Nunca cria diretório fora do pacote."""
    if not habilitado():
        return {"registrado": False, "motivo": "telemetria desabilitada", "eventos": 0}
    if destino.parent != DESTINO.parent or not destino.parent.is_dir():
        return {"registrado": False, "motivo": "destino fora do pacote", "eventos": 0}
    linha = json.dumps(registro, ensure_ascii=False, sort_keys=True)
    with destino.open("a", encoding="utf-8") as arquivo:
        arquivo.write(linha + "\n")
    try:
        destino.chmod(0o600)
    except OSError:
        pass
    return {"registrado": True, "motivo": "ok", "eventos": 1}


def resumo(destino: Path = DESTINO) -> dict[str, Any]:
    """Lê o JSONL local e agrega por evento/resultado. Sem código de prompt."""
    contagem: Counter[str] = Counter()
    total = 0
    if destino.is_file():
        for linha in destino.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            try:
                dado = json.loads(linha)
            except ValueError:
                continue
            if not isinstance(dado, dict):
                continue
            total += 1
            contagem[f"{dado.get('evento', '?')}/{dado.get('resultado', '?')}"] += 1
    return {"total": total, "por_evento_resultado": dict(sorted(contagem.items()))}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evento", choices=sorted(EVENTOS))
    ap.add_argument("--resultado", choices=sorted(RESULTADOS), default="ok")
    ap.add_argument("--duracao-ms", type=int, default=None)
    ap.add_argument("--resumo", action="store_true", help="mostra o agregado local")
    ap.add_argument("--habilitado", action="store_true", help="mostra se a variável liga a telemetria")
    args = ap.parse_args()

    if args.resumo:
        print(json.dumps(resumo(), ensure_ascii=False))
        return 0
    if args.habilitado:
        print(f"{VARIAVEL}={'1' if habilitado() else '0'}")
        return 0
    if not args.evento:
        print("Informe --evento, --resumo ou --habilitado.", file=sys.stderr)
        return 1

    registro = normalizar(args.evento, args.resultado, args.duracao_ms)
    saida = registrar(registro)
    print(json.dumps({"registro": registro, "gravacao": saida}, ensure_ascii=False))
    return 0 if not saida["registrado"] or saida["motivo"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
