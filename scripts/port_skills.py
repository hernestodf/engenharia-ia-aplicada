#!/usr/bin/env python3
"""Porta os 879 SKILL.md dos packs originais para o Engenharia de IA Aplicada (OpenCode-native).

SEGURANCA: executa apenas leitura + transformacao deterministica de texto.
Nenhuma skill externa e executada. Padrao e --dry-run; use --apply para gravar.

Uso:
    python3 scripts/port_skills.py            # dry-run (sem gravar)
    python3 scripts/port_skills.py --apply    # grava em skills/upstream/
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import hashlib
import re

ROOT = Path.home() / ".config/opencode/skill-packs"
GOD = ROOT / "engenharia-ia-aplicada"
DEST = GOD / "skills" / "upstream"
PACKS = ("autopunk", "joshua", "techsaurabh")

# Campos de frontmatter especificos de outros agentes, removidos na portagem.
CLAUDE_ONLY = {
    "disable-model-invocation", "opencode/autoinvoke", "allowed-tools",
    "context", "agent", "argument-hint", "user-invocable",
}

# Placeholders conhecidos -> texto legivel em portugues.
PLACEHOLDERS = {
    "AGENTS_DIR": "diretorio de agentes",
    "PROJECT_ROOT": "raiz do projeto",
    "SCRIPTS_DIR": "diretorio de scripts",
    "AUTHOR_NAME": "nome do autor",
    "REFERENCE_REPO": "repositorio de referencia",
    "COURSE_COMPONENTS_DIR": "diretorio de componentes do curso",
    "IMAGES_DIR": "diretorio de imagens",
    "DOCS_DIR": "diretorio de documentacao",
    "SCHEMAS_DIR": "diretorio de schemas",
    "SCHEMA_PATH": "caminho do schema",
    "CONFIG_PATH": "caminho da configuracao",
    "OUTPUT_DIR": "diretorio de saida",
    "VOICE_GUIDE": "guia de voz",
    "RUN_CMD": "comando de execucao",
    "DOCS_ROOT": "raiz da documentacao",
    "TENANT_ORG_ID": "id da organizacao do tenant",
    "INDEX_ROOT": "raiz do indice",
    "COURSE_SECTIONS_DIR": "diretorio de secoes do curso",
    "ASSET_DOCS_DIR": "diretorio de documentacao de assets",
    "TYPE_DOCS_DIR": "diretorio de documentacao de tipos",
    "TABLE_NAME": "nome da tabela",
    "SKILLS_DIR": "diretorio de skills",
    "CONTENT_DIR": "diretorio de conteudo",
    "DESIGN_THEME": "tema de design",
}

# Padroes de risco -- apenas reportados, nunca executados.
RISK_PATTERNS = {
    "comando_destrutivo": re.compile(
        r"(rm\s+-rf|DROP\s+TABLE|DROP\s+DATABASE|TRUNCATE\s+TABLE|"
        r"git\s+reset\s+--hard|git\s+push\s+--force|git\s+clean\s+-fd|kubectl\s+delete)",
        re.I,
    ),
    "exfiltracao": re.compile(
        r"(curl[^\n]*\|\s*(sh|bash)|wget[^\n]*\|\s*(sh|bash)|"
        r"cat[^\n]*(\.env|\.ssh/|id_rsa)|\.aws/credentials)",
        re.I,
    ),
    "instrucao_oculta": re.compile(r"<!--[\s\S]{0,400}?(ignore|ignore previous|system:|instru[cç][aã]o)", re.I),
    "caracter_invisivel": re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff]"),
}


def split_fm(text):
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in ("---", "...")), None)
    if end is None:
        return None, text
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1:])


def fm_value(fm, key):
    m = re.search(r"^" + re.escape(key) + r":\s*(.*)$", fm, re.M)
    if not m:
        return None
    return m.group(1).strip().strip("\"'")


def collect():
    rows = []
    for pack in PACKS:
        for md in sorted((ROOT / pack).rglob("SKILL.md")):
            text = md.read_text(encoding="utf-8", errors="replace")
            fm, body = split_fm(text)
            name = fm_value(fm or "", "name") or md.parent.name
            rows.append({
                "pack": pack,
                "path": str(md.relative_to(ROOT)),
                "name": name,
                "fm": fm,
                "body": body,
                "text": text,
            })
    return rows


def final_id_for(name):
    """ID canonico: lowercase, sem prefixo jsh-, sem duplas hifenizacoes."""
    n = re.sub(r"^jsh-", "", name.lower())
    return "op-" + re.sub(r"[^a-z0-9]+", "-", n).strip("-")


def known_names(rows):
    """Nomes que podem virar referencia skill:<id> no corpo."""
    nomes = set()
    for r in rows:
        nomes.add(final_id_for(r["name"]))
        # tambem o nome no frontmatter e o diretorio de origem
        nomes.add(r["name"])
        nomes.add(r["path"].split("/")[-2])
        nomes.add("op-" + re.sub(r"[^a-z0-9]+", "-", r["name"].lower()).strip("-"))
    return nomes


def clean_frontmatter(fm, final_id, row):
    if not fm:
        return f"name: {final_id}\ndescription: Skill portada para Engenharia de IA Aplicada."
    # descriptions tambem precisam de limpeza de paths e placeholders.
    fm = re.sub(r"~/Desktop/[Dd]ev/repos/?", "<repo atual>/", fm)
    fm = re.sub(r"~/", "<casa do usuario>/", fm)
    fm = re.sub(
        r"\{\{([A-Za-z0-9_]+)\}\}",
        lambda m: "<" + PLACEHOLDERS.get(m.group(1).upper(), m.group(1).replace("_", " ").lower()) + ">",
        fm,
    )
    if not fm:
        return f"name: {final_id}\ndescription: Skill portada para Engenharia de IA Aplicada."
    out = []
    skip = False
    for line in fm.split("\n"):
        stripped = line.strip()
        key = stripped.split(":", 1)[0].strip() if ":" in stripped else ""
        if key in CLAUDE_ONLY:
            skip = False
            continue
        if key == "name":
            out.append(f"name: {final_id}")
            continue
        if key == "engenharia-ia-aplicada/source" or key == "engenharia-ia-aplicada/original-name" or key == "metadata":
            skip = True
            continue
        if skip and (line.startswith(" ") or line.startswith("\t") or not line.strip()):
            continue
        skip = False
        out.append(line)
    out += [
        f"engenharia-ia-aplicada/source: {row['path']}",
        f"engenharia-ia-aplicada/original-name: {row['name']}",
    ]
    return "\n".join(out)


def clean_body(body, names, stats):
    t = body

    def sub_count(pattern, repl, label, flags=0):
        nonlocal t
        t, n = re.subn(pattern, repl, t, flags=flags)
        if n:
            stats[label] += n
        return n

    # $ARGUMENTS -> dado informado pelo usuario.
    # $0/$1/... NAO sao convertidos: nas skills reais sao valores monetarios
    # ($2.4M, $0.006/min) e variaveis posicionais de shell (awk $3).
    sub_count(r"\$ARGUMENTS\b", "dados informados pelo usuario na mensagem", "argumentos")

    # mcp__servico__ferramenta -> ferramenta externa: servico/ferramenta
    def mcp_repl(m):
        return f"ferramenta externa: {m.group(1)}/{m.group(2)}"

    sub_count(r"mcp__([A-Za-z0-9_-]+)__([A-Za-z0-9_]+)", mcp_repl, "mcp")
    sub_count(r"\bmcp__([A-Za-z0-9_-]+)\b", r"ferramenta externa: \1", "mcp_servico")

    # Referencias a skills: /nome ou $nome, somente se o nome existir de fato.
    if names:
        skill_alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
        sub_count(r"(?<![\w/`])/(" + skill_alt + r")(?![\w/-])", r"skill:\1", "slash_skill")
        sub_count(r"\$(" + skill_alt + r")(?![\w-])", r"skill:\1", "dollar_skill")

    # Paths absolutos conhecidos -> <repo atual>
    # IMPORTANTE: repos vem PRIMEIRO. Se ~/ virar <casa do usuario> antes,
    # sobra "<repo atual>/Desktop/dev/repos/..." no output (bug ja visto).
    # Caminho real nos packs: /Users/<usuario>/Desktop/<Dev|dev>/repos/<projeto>/...
    # Casar o pacote TODO antes de path_usuario, senao sobra Desktop/dev/repos.
    sub_count(r"/Users/[A-Za-z0-9._-]+/Desktop/[Dd]ev/repos/", "<repo atual>/", "path_repos")
    sub_count(r"~/Desktop/[Dd]ev/repos/", "<repo atual>/", "path_repos")
    sub_count(r"/Users/[A-Za-z0-9._-]+", "<repo atual>", "path_usuario")
    sub_count(r"/home/[A-Za-z0-9._-]+(?:/|$)", "<repo atual>/", "path_home")
    sub_count(r"~/.claude/skills/", "<config do agente>/skills/", "path_claude")
    sub_count(r"~/.claude/", "<config do agente>/", "path_claude")
    sub_count(r"~/.config/opencode/", "<config do opencode>/", "path_opencode")
    sub_count(r"~/.env\.shared", "<arquivo de ambiente compartilhado>", "path_env")
    sub_count(r"~/", "<casa do usuario>/", "path_tilde")

    # {{PLACEHOLDER}} -> <descricao legivel>
    def ph_repl(m):
        key = m.group(1).upper()
        return "<" + PLACEHOLDERS.get(key, key.replace("_", " ").lower()) + ">"

    sub_count(r"\{\{([A-Za-z0-9_]+)\}\}", ph_repl, "placeholders")
    return t


def risk_report(rows):
    achados = defaultdict(list)
    for r in rows:
        for label, pat in RISK_PATTERNS.items():
            m = pat.search(r["text"])
            if m:
                trecho = r["text"][max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
                achados[label].append((r["path"], trecho[:160]))
    return achados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="grava os arquivos (padrao: dry-run)")
    args = ap.parse_args()

    rows = collect()
    names = known_names(rows)
    stats = Counter()

    # Agrupa pelo ID FINAL normalizado (lowercase, sem prefixo jsh-) para
    # resolver colisoes. Agrupar pelo nome bruto deixaria 85 colisoes de ID.
    grupos = defaultdict(list)
    for r in rows:
        grupos[final_id_for(r["name"])].append(r)

    plan = []
    for final_id, members in sorted(grupos.items()):
        # Hash do corpo apos limpeza define identidade real.
        Limpa = [(clean_body(r["body"], names, stats), r) for r in members]
        hashes = defaultdict(list)
        for corpo, r in Limpa:
            h = hashlib.sha256(corpo.encode("utf-8")).hexdigest()[:12]
            hashes[h].append((corpo, r))
        canon_hash = max(hashes, key=lambda h: len(hashes[h]))
        canon_corpo, canon_row = hashes[canon_hash][0]
        # Dentro do hash canonico: duplicatas identicas (fundidas).
        # Em outros hashes: variantes divergentes (preservadas em references/).
        identical = [x for x in hashes[canon_hash] if x[1] is not canon_row]
        variants = [x for h, arr in hashes.items() if h != canon_hash for x in arr]
        plan.append({
            "name": canon_row["name"],
            "id": final_id,
            "canonical": canon_row,
            "body": canon_corpo,
            "identical": identical,
            "variants": variants,
            "members": members,
            "identical_groups": len(hashes) == 1,
        })

    riscos = risk_report(rows)

    print(f"Skills lidas: {len(rows)}")
    print(f"Grupos por nome: {len(grupos)}")
    print(f"Canonicalicas: {len(plan)}")
    print(f"Variantes divergentes preservadas: {sum(len(p['variants']) for p in plan)}")
    print(f"Duplicatas identicas fundidas: {sum(len(p['identical']) for p in plan)}")
    print("\nTransformacoes:")
    for k, v in sorted(stats.items()):
        print(f"  {k:22} {v}")
    print("\nAuditoria de risco (achados, nao executados):")
    for k, v in sorted(riscos.items()):
        print(f"  {k:22} {len(v)} arquivos")

    if not args.apply:
        print("\n[DRY-RUN] Nenhum arquivo foi gravado. Use --apply para gravar.")
        amostra = plan[0]
        print(f"\nAmostra de frontmatter limpo ({amostra['id']}):")
        print(clean_frontmatter(amostra["canonical"]["fm"], amostra["id"], amostra["canonical"]))
        return

    DEST.mkdir(parents=True, exist_ok=True)
    manifest_lines = [
        "# Manifesto de Portagem — Engenharia de IA Aplicada",
        "",
        "Gerado por `scripts/port_skills.py`. Origem -> destino de cada SKILL.md.",
        "",
        "| Origem | Destino | Tipo | Hash |",
        "|---|---|---|---|",
    ]
    for p in plan:
        target = DEST / p["id"]
        target.mkdir(parents=True, exist_ok=True)
        fm = clean_frontmatter(p["canonical"]["fm"], p["id"], p["canonical"])
        (target / "SKILL.md").write_text(f"---\n{fm}\n---\n{p['body']}", encoding="utf-8")
        manifest_lines.append(
            f"| {p['canonical']['path']} | {p['id']}/SKILL.md | canonica | {hashlib.sha256(p['body'].encode()).hexdigest()[:12]} |"
        )
        for corpo, r in p["variants"]:
            refdir = target / "references"
            refdir.mkdir(parents=True, exist_ok=True)
            refname = re.sub(r"[^A-Za-z0-9._-]+", "_", r["path"]) + ".md"
            (refdir / refname).write_text(
                f"# Variante divergente — {r['name']}\n\nOrigem: `{r['path']}`\n\n---\n\n{corpo}",
                encoding="utf-8",
            )
            manifest_lines.append(
                f"| {r['path']} | {p['id']}/references/{refname} | variante | {hashlib.sha256(corpo.encode()).hexdigest()[:12]} |"
            )
        for corpo, r in p["identical"]:
            manifest_lines.append(f"| {r['path']} | {p['id']}/SKILL.md | duplicata-identica | - |")

    (DEST / "MANIFEST.csv").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    audit = ["# Auditoria de Seguranca — Skills Portadas", "",
             "Padroes detectados por `scripts/port_skills.py`. Nenhum trecho foi executado.", ""]
    for label, itens in sorted(riscos.items()):
        audit += [f"## {label} ({len(itens)})", ""]
        for path, trecho in itens[:40]:
            audit.append(f"- `{path}` — `{trecho}`")
        if len(itens) > 40:
            audit.append(f"- ... e mais {len(itens) - 40} arquivos")
        audit.append("")
    (DEST / "SECURITY_AUDIT.md").write_text("\n".join(audit) + "\n", encoding="utf-8")

    print(f"\n[APPLY] Gravado em {DEST}")
    print(f"  {len(plan)} diretorios de skill canonica")
    print("  MANIFEST.csv + SECURITY_AUDIT.md gerados")


if __name__ == "__main__":
    main()
