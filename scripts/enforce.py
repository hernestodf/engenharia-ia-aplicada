#!/usr/bin/env python3
"""Gate determinístico de enforcement da Engenharia de IA Aplicada.

Avalia UM evento de intenção e devolve uma decisão. Não executa comando,
não abre arquivo, não faz rede e não aceita argv vindo do evento. A única
entrada é um objeto JSON em stdin.

Contrato de entrada (campos desconhecidos são ignorados):
  acao                    string obrigatória
  recurso                 string (caminho, alvo ou id)
  comando                 string (texto de shell a inspecionar)
  origem                  operador | ferramenta | skill_externa | mcp | documento | issue
  ambiente               local | stage | producao
  autorizacao_explicita  booleano
  gate_aprovado          booleano

Saída: JSON com decisao (permitir | negar | pedir), motivo, regras e versao.
Código de saída: 0 permitir, 2 negar, 3 pedir, 1 erro de contrato.

Uso:
  echo '{"acao":"shell","comando":"git push --force"}' | python3 scripts/enforce.py
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

VERSAO_GATE = "0.1.0"

ORIGENS = {"operador", "ferramenta", "skill_externa", "mcp", "documento", "issue"}
ORIGENS_NAO_CONFIAVEIS = {"skill_externa", "mcp", "documento", "issue"}
ACOES_SEGREDOS = {
    "rotacionar_segredo",
    "exportar_segredo",
    "ler_segredo",
    "publicar_segredo",
}
ACOES_REINDEXACAO = {"reindexar", "reindexacao", "reindex"}

# Whitelist fechada: só estas ações, vindas de origem local, podem seguir
# automaticamente quando nenhuma regra de bloqueio incide.
ACOES_BENIGNAS = {
    "shell",
    "read",
    "edit",
    "write",
    "glob",
    "grep",
    "status",
    "version",
    "audit",
    "doctor",
}
ORIGENS_LOCAIS = {"operador", "ferramenta"}

# Padrões são exclusivamente para INSPEÇÃO de texto. Nada daqui é executado.
PADROES_DESTRUTIVOS = (
    re.compile(r"(?:^|\s)rm\s+-[a-zA-Z]*[rR]"),
    re.compile(r"(?:^|\s)git\s+reset\s+--hard\b"),
    re.compile(r"(?:^|\s)git\s+clean\s+-fd\b"),
    re.compile(r"(?:^|\s)git\s+push\b[^|;&]*--force\b"),
    re.compile(r"--force-with-lease\b"),
    re.compile(r"(?:^|\s)mkfs\b"),
    re.compile(r"(?:^|\s)dd\s+if="),
    re.compile(r"\b(?:DROP\s+TABLE|TRUNCATE\s+TABLE|DELETE\s+FROM)\b", re.IGNORECASE),
)

SUFIXOS_PROTEGIDOS = (".env", ".key", ".pem", ".p12")


def _texto(evento: dict[str, Any], chave: str) -> str:
    valor = evento.get(chave, "")
    return valor if isinstance(valor, str) else ""


def _booleano(evento: dict[str, Any], chave: str) -> bool:
    return evento.get(chave) is True


def caminho_protegido(recurso: str) -> bool:
    """Detecta alvos sensíveis sem glob, shell ou normalização de sistema."""
    partes = [p for p in recurso.replace("\\", "/").split("/") if p]
    if ".git" in partes or "secrets" in partes:
        return True
    return any(parte.endswith(SUFIXOS_PROTEGIDOS) for parte in partes)


def comando_destrutivo(comando: str) -> bool:
    return any(padrao.search(comando) for padrao in PADROES_DESTRUTIVOS)


def avaliar_evento(evento: dict[str, Any]) -> dict[str, Any]:
    """Devolve a decisão. Nunca executa nada do conteúdo recebido."""
    acao = _texto(evento, "acao")
    recurso = _texto(evento, "recurso")
    comando = _texto(evento, "comando")
    origem = _texto(evento, "origem") or "ferramenta"
    ambiente = _texto(evento, "ambiente") or "local"
    autorizado = _booleano(evento, "autorizacao_explicita")
    gate = _booleano(evento, "gate_aprovado")

    encontradas: list[dict[str, str]] = []
    autorizadas: list[str] = []

    def aplicar(rule_id: str, motivo: str, condicao: bool, *, via_gate: bool = False) -> None:
        if not condicao:
            return
        if via_gate and gate:
            autorizadas.append(rule_id)
            return
        if not via_gate and autorizado:
            autorizadas.append(rule_id)
            return
        encontradas.append({"id": rule_id, "motivo": motivo})

    aplicar("R01", "comando destrutivo detectado", comando_destrutivo(comando))
    aplicar("R02", "alvo protegido detectado", caminho_protegido(recurso))
    aplicar("R03", "operação em produção", ambiente == "producao")
    aplicar("R04", "operação sobre segredo", acao in ACOES_SEGREDOS)
    aplicar("R05", "reindexação solicitada", acao in ACOES_REINDEXACAO)
    aplicar(
        "R06",
        "conteúdo não confiável exige gate do QA/Security",
        origem in ORIGENS_NAO_CONFIAVEIS,
        via_gate=True,
    )

    if encontradas:
        return {
            "decisao": "negar",
            "motivo": "; ".join(r["motivo"] for r in encontradas),
            "regras": encontradas,
            "versao": VERSAO_GATE,
        }
    if autorizadas:
        return {
            "decisao": "permitir",
            "motivo": "autorização explícita registrada para: " + ", ".join(autorizadas),
            "regras": [],
            "versao": VERSAO_GATE,
        }
    if not acao or origem not in ORIGENS:
        return {
            "decisao": "pedir",
            "motivo": "evento incompleto ou origem desconhecida",
            "regras": [],
            "versao": VERSAO_GATE,
        }
    if acao in ACOES_BENIGNAS and origem in ORIGENS_LOCAIS:
        return {
            "decisao": "permitir",
            "motivo": "ação benigna de origem local",
            "regras": [],
            "versao": VERSAO_GATE,
        }
    return {
        "decisao": "pedir",
        "motivo": "nenhuma regra cobre o evento; decisão com operador",
        "regras": [],
        "versao": VERSAO_GATE,
    }


CODIGOS = {"permitir": 0, "negar": 2, "pedir": 3}


def main() -> int:
    try:
        bruto = sys.stdin.read()
        dados = json.loads(bruto) if bruto.strip() else {}
    except (ValueError, OSError):
        print(json.dumps({"decisao": "erro", "motivo": "JSON inválido", "regras": []}))
        return 1
    if not isinstance(dados, dict):
        print(json.dumps({"decisao": "erro", "motivo": "evento deve ser objeto", "regras": []}))
        return 1
    resultado = avaliar_evento(dados)
    print(json.dumps(resultado, ensure_ascii=False))
    return CODIGOS.get(resultado["decisao"], 1)


if __name__ == "__main__":
    raise SystemExit(main())
