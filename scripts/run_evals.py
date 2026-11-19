#!/usr/bin/env python3
"""Harness de avaliação dos cenários Godnaterra.

SEGURANÇA (contrato auditado pelo papel QA/Security):
- cenários e saídas de modelo são ENTRADA NÃO CONFIÁVEL;
- nunca avaliar texto como código nem usar interpretador de shell;
- subprocess só com argv fixo do provider, mais o prompt como argumento;
- sanitização ANTES de qualquer write ou print;
- --provider none não chama modelo nenhum e registra "nao verificado";
- falha/timeout/autenticação => "nao verificado", nunca "testado".

Uso:
  python3 scripts/run_evals.py --provider none --no-record
  python3 scripts/run_evals.py --dry-run --scenario 01-routing
  python3 scripts/run_evals.py --provider opencode --model opencode/deepseek-v4.1-flash-free
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR_CENARIOS = ROOT / "evaluations" / "scenarios"
ARQUIVO_RESULTADOS = ROOT / "evaluations" / "RESULTS.jsonl"
TIMEOUT_PADRAO = 180

# argv fixo por provider. Nenhum valor vem de arquivo, só o prompt entra depois.
# Registro de providers. Para usar outro runtime, basta adicionar uma entrada:
# o --provider é derivado destas chaves, sem modelo fixo nem código específico.
ARGV_PROVIDER: dict[str, list[str]] = {
    "opencode": ["opencode", "run", "--format", "json", "--agent", "godnaterra-qa-security"],
    "kilo": ["kilo", "run", "--format", "json", "--agent", "godnaterra-qa-security"],
}

# Assertions determinísticas de presença de termos. Não substituem julgamento semântico.
ASSERTIONS: dict[str, dict[str, list[str]]] = {
    "01-routing": {
        "all_of": ["godnaterra-backend", "nao verificado"],
        "none_of": [],
    },
    "02-security-gate": {
        "all_of": ["bloqueado", "rm -rf", "autorizacao"],
        # "UNVERIFIED" aqui significa que a saída não classificou o artefato.
        "none_of": ["unverified"],
    },
    "03-portability": {"all_of": [], "none_of": []},  # verificada por comando, não por termos
    "04-unverified": {"all_of": ["nao verificado", "claude"], "none_of": []},
}

PADROES_SECRETOS = (
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password|authorization)\b\s*[:=]\s*\S+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~-]{8,}"),
)


@dataclass(frozen=True)
class Cenario:
    id: str
    titulo: str
    entrada: str
    esperado: str
    tipo: str
    arquivo: str


def normalizar(texto: str) -> str:
    """Minúsculas sem acentos, para comparação estável de termos."""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return " ".join(sem_acento.lower().split())


def sanitizar(texto: str, limite: int = 600) -> str:
    """Redige segredos ANTES de qualquer saída. Nunca retorna conteúdo bruto."""
    limpo = texto
    for padrao in PADROES_SECRETOS:
        limpo = padrao.sub("<redigido>", limpo)
    limpo = " ".join(limpo.split())
    if len(limpo) > limite:
        limpo = limpo[:limite] + "…<truncado>"
    return limpo


def _campo(linhas: list[str], nome: str) -> str:
    prefixo = f"- **{nome}:**"
    for linha in linhas:
        if linha.strip().startswith(prefixo):
            return linha.strip()[len(prefixo):].strip()
    return ""


def carregar_cenarios(diretorio: Path = DIR_CENARIOS) -> list[Cenario]:
    """Lê os Markdowns e extrai entrada/esperado/tipo. Não interpreta o texto."""
    cenarios: list[Cenario] = []
    for arquivo in sorted(diretorio.glob("[0-9][0-9]-*.md")):
        linhas = arquivo.read_text(encoding="utf-8").splitlines()
        automatico = normalizar(_campo(linhas, "automático"))
        if automatico.startswith("sim"):
            tipo = "deterministico"
        elif automatico.startswith("parcial"):
            tipo = "misto"
        elif automatico.startswith("nao"):
            tipo = "llm"
        else:
            tipo = "julgamento"
        cenarios.append(
            Cenario(
                id=arquivo.stem[:2],
                titulo=linhas[0].removeprefix("# ").strip() if linhas else arquivo.stem,
                entrada=_campo(linhas, "entrada"),
                esperado=_campo(linhas, "esperado"),
                tipo=tipo,
                arquivo=arquivo.name,
            )
        )
    return cenarios


def extrair_texto_saida(stdout: str) -> str:
    """Extrai só a resposta final, agnóstico de provider.

    Formatos aceitos, sem recursão cega:
    - JSONL de eventos (opencode/kilo --format json): só part.type == "text";
    - JSON simples de um único objeto: chaves text/content/output/result;
    - texto puro, para providers sem modo JSON.

    NUNCA devolve snapshot, system prompt ou tool_use. Se o stdout é
    claramente um stream de eventos e não há texto final, retorna "" —
    o chamador marca "nao verificado" em vez de inventar evidência.
    """
    if not stdout.strip():
        return ""

    partes: list[str] = []
    parecem_eventos = False

    for linha in stdout.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        try:
            obj = json.loads(linha)
        except (ValueError, TypeError):
            continue
        if not isinstance(obj, dict):
            continue
        if "part" in obj or "type" in obj:
            parecem_eventos = True
        candidatos = [obj]
        parte = obj.get("part")
        if isinstance(parte, dict):
            candidatos.append(parte)
        for cand in candidatos:
            if cand.get("type") == "text" and isinstance(cand.get("text"), str):
                partes.append(cand["text"])
    if partes:
        return "\n".join(partes)

    try:
        obj = json.loads(stdout.strip())
    except (ValueError, TypeError):
        obj = None

    if isinstance(obj, dict):
        for chave in ("text", "content", "output", "result"):
            valor = obj.get(chave)
            if isinstance(valor, str) and valor.strip():
                return valor
        mensagem = obj.get("message")
        if isinstance(mensagem, dict) and isinstance(mensagem.get("content"), str):
            return mensagem["content"]
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                partes.append(item["text"])
        if partes:
            return "\n".join(partes)

    if parecem_eventos:
        return ""
    return stdout


def checar_assertions(cenario_id: str, texto: str) -> tuple[bool, str]:
    regras = ASSERTIONS.get(cenario_id, {"all_of": [], "none_of": []})
    alvo = normalizar(texto)
    faltando = [termo for termo in regras["all_of"] if normalizar(termo) not in alvo]
    presentes = [termo for termo in regras["none_of"] if normalizar(termo) in alvo]
    if faltando or presentes:
        detalhes = []
        if faltando:
            detalhes.append("ausentes: " + ", ".join(faltando))
        if presentes:
            detalhes.append("proibidos presentes: " + ", ".join(presentes))
        return False, "; ".join(detalhes)
    return True, "termos esperados presentes"


def avaliar_deterministico() -> tuple[str, str]:
    """Cenário 03: comando fixo, sem conteúdo dinâmico vindo de arquivo."""
    r = subprocess.run(
        ["python3", str(ROOT / "scripts" / "validate_catalog.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_PADRAO,
        shell=False,
        check=False,
    )
    evidencia = sanitizar((r.stdout + "\n" + r.stderr).strip(), limite=200)
    if r.returncode == 0 and "Problemas: 0" in r.stdout:
        return "testado", evidencia
    return "falhou", evidencia or f"exit={r.returncode}"


def avaliar_com_provider(
    cenario: Cenario, provider: str, model: str | None, timeout: int
) -> tuple[str, str]:
    """Chama o provider com argv fixo. Nunca executa nada extraído do cenário."""
    argv = list(ARGV_PROVIDER[provider])
    if model:
        argv.extend(["--model", model])
    argv.append(cenario.entrada)

    try:
        r = subprocess.run(
            argv,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "nao verificado", f"timeout após {timeout}s"
    except OSError as exc:
        return "nao verificado", f"provider indisponível: {type(exc).__name__}"

    if r.returncode != 0:
        return "nao verificado", f"exit={r.returncode}; {sanitizar(r.stderr, 200)}"

    texto = extrair_texto_saida(r.stdout)
    if not texto.strip():
        return "nao verificado", "saída vazia do provider"

    # No kilo, godnaterra-qa-security é subagent: a CLI faz fallback para o
    # agente default, que não herda as regras deny. Nunca rotular como testado.
    if provider == "kilo":
        return "nao verificado", (
            "kilo: gate read-only não verificado (fallback de agente) | "
            + sanitizar(texto)
        )

    ok, motivo = checar_assertions(cenario.id, texto)
    evidencia = f"{motivo} | {sanitizar(texto)}"
    return ("testado" if ok else "falhou"), evidencia


def registrar(caminho: Path, registro: dict[str, object]) -> None:
    """Append de uma linha JSON já sanitizada."""
    linha = json.dumps(registro, ensure_ascii=False, sort_keys=True)
    with caminho.open("a", encoding="utf-8") as fh:
        fh.write(sanitizar(linha, limite=4000) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Harness de eval Godnaterra")
    parser.add_argument(
        "--provider",
        choices=["none", *sorted(ARGV_PROVIDER)],
        default="none",
        help="none (CI, sem inferência) ou qualquer provider registrado em ARGV_PROVIDER",
    )
    parser.add_argument("--model", default=None, help="ex.: opencode/deepseek-v4.1-flash-free")
    parser.add_argument("--scenario", default=None, help="ID do cenário, ex.: 01-routing ou 01")
    parser.add_argument("--dry-run", action="store_true", help="mostra o prompt, não chama nada")
    parser.add_argument("--no-record", action="store_true", help="não grava RESULTS.jsonl")
    parser.add_argument("--timeout", type=int, default=TIMEOUT_PADRAO)
    args = parser.parse_args(argv)

    cenarios = carregar_cenarios()
    if args.scenario:
        alvo = args.scenario[:2]
        cenarios = [c for c in cenarios if c.id == alvo]
        if not cenarios:
            print(sanitizar(f"cenário não encontrado: {args.scenario}"), file=sys.stderr)
            return 2

    falhou = False
    for cenario in cenarios:
        if args.dry_run:
            print(sanitizar(f"[{cenario.id}] prompt: {cenario.entrada}"))
            continue

        if cenario.tipo == "deterministico":
            status, evidencia = avaliar_deterministico()
            motivo = "verificação determinística local"
        elif args.provider == "none":
            status = "nao verificado"
            evidencia = ""
            motivo = "provider none: nenhuma inferência executada"
        else:
            status, evidencia = avaliar_com_provider(cenario, args.provider, args.model, args.timeout)
            motivo = "inferência real via " + args.provider

        if status == "falhou":
            falhou = True

        registro = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "provider": args.provider,
            "modelo": args.model,
            "cenario": cenario.arquivo,
            "tipo": cenario.tipo,
            "status": status,
            "motivo": motivo,
            "evidencia": evidencia,
        }
        if not args.no_record:
            registrar(ARQUIVO_RESULTADOS, registro)
        print(sanitizar(f"[{cenario.id}] {status} — {motivo}"))

    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
