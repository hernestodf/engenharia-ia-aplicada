#!/usr/bin/env python3
"""Valida o contrato dos incidentes do loop de aprendizado EngenhariaIaAplicada.

Entrada: evaluations/incidents/INC-*.json

SEGURANÇA: este validador NUNCA executa comandos descritos nos incidentes.
Arquivos de incidente são entrada não confiável. O campo "verificacao" é
texto para o revisor e para o CI, não uma instrução a executar daqui.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR_INCIDENTES = ROOT / "evaluations" / "incidents"
DIR_CENARIOS = ROOT / "evaluations" / "scenarios"
RAIZES_SKILLS = (ROOT / "skills" / "core", ROOT / "skills" / "upstream")

STATUS_VALIDOS = {"rascunho", "em_revisao", "aprovado", "rejeitado", "fechado"}
STATUS_COM_REVISAO = {"aprovado", "rejeitado", "fechado"}
CAMPOS_CONHECIDOS = {
    "id", "titulo", "data", "status", "origem", "sintoma", "evidencia",
    "cenario", "skill_afetada", "correcao", "verificacao", "testes_verdes",
    "licao_aprendida", "revisao",
}
CAMPOS_TEXTO = (
    "titulo", "origem", "sintoma", "evidencia", "correcao", "verificacao", "licao_aprendida",
)
RE_ID = re.compile(r"^INC-\d{3,}$")
RE_CENARIO = re.compile(r"^\d{2}-[a-z0-9-]+\.md$")
RE_SKILL = re.compile(r"^op-[a-z0-9-]+$")


def data_valida(valor: object) -> bool:
    if not isinstance(valor, str):
        return False
    try:
        date.fromisoformat(valor)
    except ValueError:
        return False
    return True


def validar_incidente(inc: object, nome: str) -> list[str]:
    """Valida um incidente já carregado. Não toca disco nem executa nada."""
    problemas: list[str] = []
    if not isinstance(inc, dict):
        return [f"{nome}: JSON raiz deve ser objeto"]

    desconhecidas = sorted(set(inc) - CAMPOS_CONHECIDOS)
    if desconhecidas:
        problemas.append(f"{nome}: campos desconhecidos: {', '.join(desconhecidas)}")

    if not isinstance(inc.get("id"), str) or not RE_ID.match(inc["id"]):
        problemas.append(f"{nome}: id inválido (esperado INC-NNN)")
    if not data_valida(inc.get("data")):
        problemas.append(f"{nome}: data inválida (esperado YYYY-MM-DD)")

    status = inc.get("status")
    if status not in STATUS_VALIDOS:
        problemas.append(f"{nome}: status inválido: {status!r}")

    for campo in CAMPOS_TEXTO:
        valor = inc.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            problemas.append(f"{nome}: {campo} vazio ou ausente")

    if not isinstance(inc.get("testes_verdes"), bool):
        problemas.append(f"{nome}: testes_verdes deve ser booleano")

    cenario = inc.get("cenario")
    if cenario is not None:
        if not isinstance(cenario, str) or not RE_CENARIO.match(cenario):
            problemas.append(f"{nome}: cenario com formato inválido: {cenario!r}")
        elif not (DIR_CENARIOS / cenario).is_file():
            problemas.append(f"{nome}: cenario não existe: {cenario}")

    skill = inc.get("skill_afetada")
    if skill is not None:
        if not isinstance(skill, str) or not RE_SKILL.match(skill):
            problemas.append(f"{nome}: skill_afetada inválida: {skill!r}")
        elif not any((raiz / skill).is_dir() for raiz in RAIZES_SKILLS):
            problemas.append(f"{nome}: skill não existe: {skill}")

    rev = inc.get("revisao")
    if not isinstance(rev, dict):
        problemas.append(f"{nome}: revisao deve ser objeto")
    else:
        por = rev.get("revisado_por")
        data_rev = rev.get("data")
        decisao = rev.get("decisao")
        if status in STATUS_COM_REVISAO:
            if not isinstance(por, str) or not por.strip():
                problemas.append(f"{nome}: revisao.revisado_por obrigatório para status {status}")
            if not data_valida(data_rev):
                problemas.append(f"{nome}: revisao.data inválida para status {status}")
            if decisao not in {"aprovado", "rejeitado"}:
                problemas.append(f"{nome}: revisao.decisao inválida para status {status}")
            if status in {"aprovado", "fechado"} and inc.get("testes_verdes") is not True:
                problemas.append(f"{nome}: testes_verdes deve ser true para status {status}")
            if status == "fechado" and decisao != "aprovado":
                problemas.append(f"{nome}: status fechado exige decisao aprovado")
        elif status == "rascunho":
            if (isinstance(por, str) and por.strip()) or decisao not in (None, ""):
                problemas.append(f"{nome}: rascunho não pode ter revisao preenchida")

    return problemas


def main() -> int:
    arquivos = sorted(DIR_INCIDENTES.glob("INC-*.json"))
    problemas: list[str] = []
    ids: set[str] = set()

    for arquivo in arquivos:
        try:
            inc = json.loads(arquivo.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            problemas.append(f"{arquivo.name}: JSON inválido: {exc}")
            continue
        problemas.extend(validar_incidente(inc, arquivo.name))
        ident = inc.get("id") if isinstance(inc, dict) else None
        if isinstance(ident, str):
            if ident in ids:
                problemas.append(f"{arquivo.name}: id duplicado: {ident}")
            ids.add(ident)

    for p in problemas:
        print(f"  problema: {p}")
    print(f"Incidentes validados: {len(arquivos)} | Problemas: {len(problemas)}")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
