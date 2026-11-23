#!/usr/bin/env python3
"""Verifica integridade estrutural dos adapters opcionais.

Modo padrao: offline, somente leitura, sem rede e sem subprocesso de servico.
--check-online: confere o shasum dos pacotes npm contra o registry (urllib, sem shell).

Uso: python3 scripts/verify_adapters.py [--check-online]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTERS = ROOT / "adapters"
MCP_TEMPLATE = ADAPTERS / "chrome-devtools-mcp" / "mcp.json"
CJK = re.compile(r"[\u3400-\u9FFF\uF900-\uFAFF\u3040-\u30FF]")
HEX40 = re.compile(r"^[0-9a-f]{40}$")

REGRAS: dict[str, dict[str, object]] = {
    "chrome-devtools-mcp": {
        "license": "Apache-2.0",
        "campos": ("adaptador", "tipo", "license", "pacote", "versao",
                   "integrity_shasum", "registro", "fonte", "comando"),
        "sem_latest": True,
    },
    "open-code-review": {
        "license": "Apache-2.0",
        "campos": ("adaptador", "tipo", "license", "pacote", "versao",
                   "integrity_shasum", "registro", "fonte", "binario"),
        "sem_latest": True,
    },
    "openviking": {
        "license": "AGPL-3.0",
        "campos": ("adaptador", "tipo", "license", "fonte", "commit",
                   "endpoint_padrao", "credencial"),
        "sem_latest": False,
    },
}


def falhas() -> list[str]:
    erros: list[str] = []

    for nome, regra in REGRAS.items():
        p = ADAPTERS / nome / "pin.json"
        if not p.is_file():
            erros.append(f"{nome}: pin.json ausente")
            continue
        try:
            dados = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            erros.append(f"{nome}: pin.json invalido ({exc})")
            continue
        if not isinstance(dados, dict):
            erros.append(f"{nome}: pin.json nao e objeto")
            continue
        for campo in regra["campos"]:
            if not dados.get(campo):
                erros.append(f"{nome}: campo obrigatorio ausente: {campo}")
        if dados.get("license") != regra["license"]:
            erros.append(f"{nome}: licenca divergente: {dados.get('license')!r}")
        if dados.get("habilitado_por_padrao") is not False:
            erros.append(f"{nome}: deve estar habilitado_por_padrao=false")
        if regra["sem_latest"]:
            if not HEX40.match(str(dados.get("integrity_shasum", ""))):
                erros.append(f"{nome}: integrity_shasum nao e SHA1 de 40 hex")
            if "latest" in str(dados.get("registro", "")):
                erros.append(f"{nome}: registro usa @latest")
        if nome == "openviking":
            if dados.get("vendorizado") is not False:
                erros.append("openviking: nao pode ser vendorizado (AGPL)")
            if "OPENVIKING_API_KEY" not in str(dados.get("credencial", "")):
                erros.append("openviking: credencial deve vir de env")
        if CJK.search(p.read_text(encoding="utf-8")):
            erros.append(f"{nome}: CJK em pin.json")

    try:
        t = json.loads(MCP_TEMPLATE.read_text(encoding="utf-8"))
        servidores = t["mcp"]["servers"]
        cdm = servidores["chrome-devtools"]
        if cdm.get("disabled") is not True:
            erros.append("mcp.json: chrome-devtools deve nascer disabled")
        if not any("chrome-devtools-mcp@1.13.0" in str(a) for a in cdm.get("command", [])):
            erros.append("mcp.json: comando nao esta pinado em 1.13.0")
        if cdm.get("type") != "local":
            erros.append("mcp.json: type deve ser local")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        erros.append(f"mcp.json: template invalido ({exc})")

    ov = ADAPTERS / "openviking" / "mcp.opencode.json"
    try:
        d = json.loads(ov.read_text(encoding="utf-8"))
        s = d["mcp"]["servers"]["openviking"]
        if s.get("disabled") is not True:
            erros.append("mcp.opencode.json: openviking deve nascer disabled")
        if s.get("type") != "remote":
            erros.append("mcp.opencode.json: type deve ser remote")
        hdr = json.dumps(s.get("headers", {}))
        if "OPENVIKING_API_KEY" not in hdr:
            erros.append("mcp.opencode.json: credencial deve vir de env")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        erros.append(f"mcp.opencode.json: template invalido ({exc})")

    for p in ADAPTERS.rglob("*"):
        if not p.is_file() or p.suffix not in {".json", ".md", ".py"}:
            continue
        texto = p.read_text(encoding="utf-8", errors="replace")
        if CJK.search(texto):
            erros.append(f"{p.relative_to(ROOT)}: CJK detectado")
        if "curl -fsSL" in texto or "shell=True" in texto:
            erros.append(f"{p.relative_to(ROOT)}: padrao de execucao externa")
    return erros


def conferir_online() -> list[str]:
    erros: list[str] = []
    for nome in ("chrome-devtools-mcp", "open-code-review"):
        dados = json.loads((ADAPTERS / nome / "pin.json").read_text(encoding="utf-8"))
        url = f"https://registry.npmjs.org/{dados['pacote']}/{dados['versao']}"
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                remoto = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            erros.append(f"{nome}: registry inalcancavel ({exc})")
            continue
        atual = remoto.get("dist", {}).get("shasum")
        if atual != dados.get("integrity_shasum"):
            erros.append(
                f"{nome}: shasum divergente (pin={dados.get('integrity_shasum')} registry={atual})"
            )
    return erros


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-online", action="store_true", help="confere shasum no registry npm")
    args = ap.parse_args()

    erros = falhas()
    if args.check_online:
        erros += conferir_online()
    if erros:
        print(f"Adapters: {len(erros)} problema(s)")
        for e in erros:
            print(f"  {e}")
        return 1
    print("Adapters: 3 pinados, 0 problemas (disabled por padrao)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
