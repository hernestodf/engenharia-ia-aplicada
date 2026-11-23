#!/usr/bin/env python3
"""Verificadores determinísticos das tarefas de eval.

SEGURANCA: tarefas sao ENTRADA NAO CONFIAVEL. Este modulo nao interpreta texto
como codigo: so usa tabela fechada de verificadores, caminhos relativos contidos
no repo e comandos de uma whitelist. Nenhum argv vem do JSON da tarefa.

Cada verificador devolve (nota 0..2, evidencia curta). Nunca executa filtro
externo, nunca usa shell e nunca escreve arquivo.
"""

from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

SEGREDOS = (
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password|authorization)\b\s*[:=]\s*\S+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)

# unica fonte de comandos permitidos. A tarefa escolhe pela CHAVE, nunca por argv.
COMANDOS: dict[str, list[str]] = {
    "validate_catalog": ["python3", str(ROOT / "scripts" / "validate_catalog.py")],
    "verify_adapters": ["python3", str(ROOT / "scripts" / "verify_adapters.py")],
    "manifesto_check": ["python3", str(ROOT / "scripts" / "generate_manifest.py"), "--check"],
}


def normalizar(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return " ".join(sem_acento.lower().split())


def _arquivo(params: dict[str, Any]) -> Path:
    rel = params.get("arquivo")
    if not isinstance(rel, str) or not rel:
        raise ValueError("parametro 'arquivo' obrigatorio")
    caminho = Path(rel)
    if caminho.is_absolute() or ".." in caminho.parts:
        raise ValueError("caminho de tarefa deve ser relativo e contido no repo")
    return ROOT / caminho


def _termos(params: dict[str, Any], chave: str) -> list[str]:
    valores = params.get(chave)
    if not isinstance(valores, list) or not valores or not all(isinstance(v, str) for v in valores):
        raise ValueError(f"parametro '{chave}' deve ser lista de strings")
    return valores


def arquivo_termos(params: dict[str, Any]) -> tuple[int, str]:
    """2 = todos os termos; 1 = arquivo existe e tem parte; 0 = ausente/vazio."""
    alvo = _arquivo(params)
    termos = _termos(params, "termos")
    if not alvo.is_file():
        return 0, "arquivo ausente"
    corpo = normalizar(alvo.read_text(encoding="utf-8", errors="replace"))
    faltando = [t for t in termos if normalizar(t) not in corpo]
    if not faltando:
        return 2, "termos presentes"
    if len(faltando) < len(termos):
        return 1, "parcial; faltam: " + ", ".join(faltando[:3])
    return 0, "nenhum termo encontrado"


def arquivo_ausencia(params: dict[str, Any]) -> tuple[int, str]:
    """2 = nenhum termo proibido; 0 = pelo menos um presente."""
    alvo = _arquivo(params)
    proibidos = _termos(params, "proibidos")
    if not alvo.is_file():
        return 0, "arquivo ausente"
    corpo = normalizar(alvo.read_text(encoding="utf-8", errors="replace"))
    achados = [t for t in proibidos if normalizar(t) in corpo]
    if achados:
        return 0, "proibidos presentes: " + ", ".join(achados[:3])
    return 2, "nenhum termo proibido"


def _campo(dados: Any, caminho: str) -> Any:
    atual = dados
    for parte in caminho.split("."):
        if not isinstance(atual, dict) or parte not in atual:
            return None
        atual = atual[parte]
    return atual


def json_campo(params: dict[str, Any]) -> tuple[int, str]:
    alvo = _arquivo(params)
    campo = params.get("campo")
    esperado = params.get("valor")
    if not isinstance(campo, str):
        raise ValueError("parametro 'campo' obrigatorio")
    if not alvo.is_file():
        return 0, "arquivo ausente"
    try:
        dados = json.loads(alvo.read_text(encoding="utf-8"))
    except ValueError:
        return 0, "JSON invalido"
    obtido = _campo(dados, campo)
    if obtido == esperado:
        return 2, f"{campo}={obtido!r}"
    return 0, f"{campo}={obtido!r} (esperado {esperado!r})"


def json_linha_filtrada(params: dict[str, Any]) -> tuple[int, str]:
    """Ultima linha JSONL que casa com o filtro; confere um campo."""
    alvo = _arquivo(params)
    filtro = params.get("filtro")
    campo = params.get("campo")
    esperado = params.get("valor")
    if not isinstance(filtro, dict) or not isinstance(campo, str):
        raise ValueError("filtro e campo obrigatorios")
    if not alvo.is_file():
        return 0, "arquivo ausente"
    encontrado: dict[str, Any] | None = None
    for linha in alvo.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        try:
            obj = json.loads(linha)
        except ValueError:
            continue
        if isinstance(obj, dict) and all(obj.get(k) == v for k, v in filtro.items()):
            encontrado = obj
    if encontrado is None:
        return 0, "nenhuma linha casa com o filtro"
    obtido = encontrado.get(campo)
    if obtido == esperado:
        return 2, f"{campo}={obtido!r}"
    return 0, f"{campo}={obtido!r} (esperado {esperado!r})"


def comando_saida(params: dict[str, Any]) -> tuple[int, str]:
    """Executa so comando da whitelist, com argv fixo e sem shell."""
    chave = params.get("comando")
    contem = params.get("contem")
    if chave not in COMANDOS or not isinstance(contem, str):
        raise ValueError("comando ou contem invalido")
    try:
        r = subprocess.run(
            COMANDOS[chave], cwd=ROOT, capture_output=True, text=True,
            timeout=180, shell=False, check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return 0, f"comando indisponivel: {type(exc).__name__}"
    corpo = normalizar(r.stdout + "\n" + r.stderr)
    if r.returncode == 0 and normalizar(contem) in corpo:
        return 2, "exit=0 e trecho esperado presente"
    return 0, f"exit={r.returncode}; trecho esperado ausente"


def core_frontmatter_valido(_: dict[str, Any]) -> tuple[int, str]:
    arquivos = sorted((ROOT / "skills" / "core").glob("*/SKILL.md"))
    if not arquivos:
        return 0, "nenhuma skill core"
    bons = 0
    ruins: list[str] = []
    for md in arquivos:
        texto = md.read_text(encoding="utf-8", errors="replace")
        cab = texto.split("---", 2)
        if len(cab) < 3:
            ruins.append(md.parent.name)
            continue
        bloco = cab[1]
        esperado = f"name: {md.parent.name}"
        if (esperado in bloco and "godnaterra/layer: core" in bloco
                and re.search(r"(?m)^description: \S", bloco)):
            bons += 1
        else:
            ruins.append(md.parent.name)
    if bons == len(arquivos):
        return 2, f"{bons}/{len(arquivos)} skills core validas"
    if bons:
        return 1, f"{bons}/{len(arquivos)} validas; ruins: {','.join(ruins[:3])}"
    return 0, "nenhuma skill core valida"


def sem_secretos(params: dict[str, Any]) -> tuple[int, str]:
    alvo = _arquivo(params)
    if not alvo.is_file():
        return 0, "arquivo ausente"
    corpo = alvo.read_text(encoding="utf-8", errors="replace")
    achados = [p.pattern[:24] for p in SEGREDOS if p.search(corpo)]
    if achados:
        return 0, f"{len(achados)} padrao(oes) de segredo"
    return 2, "nenhum padrao de segredo"


VERIFICADORES = {
    "arquivo_termos": arquivo_termos,
    "arquivo_ausencia": arquivo_ausencia,
    "json_campo": json_campo,
    "json_linha_filtrada": json_linha_filtrada,
    "comando_saida": comando_saida,
    "core_frontmatter_valido": core_frontmatter_valido,
    "sem_secretos": sem_secretos,
}
