# Classificação dos achados de segurança — FASE 4

Este arquivo classifica os achados brutos de `skills/upstream/SECURITY_AUDIT.md`.
O arquivo bruto é regenerado por `scripts/port_skills.py`; esta classificação é manual e não é sobrescrita.

**Nenhuma skill externa foi executada.** Todos os achados são análise estática de texto.

---

## 1. Comandos destrutivos (3 arquivos sinalizados)

| Skill | Trecho | Classificação | Risco real |
|---|---|---|---|
| `op-git-land-main` | `Never git reset --hard / git clean -fd` | **Proibição documental** — o texto diz explicitamente *Never* | Nenhum. É uma advertência, não um comando a executar. |
| `op-migrations-workflow` | `NEVER DROP COLUMN or DROP TABLE without a deprecation period` | **Proibição documental** — o texto diz *NEVER* | Nenhum. |
| `op-tenant-migration` | `rm -rf .git` (Phase 1), `rm -rf .claude/projects/` | **Instrução destrutiva real no texto** | **MÉDIO** — se a skill for seguida literalmente, apaga histórico Git/config local. Não executado. Requer confirmação explícita se algum dia for usada. |

Achados adicionais da varredura ampliada (não contados nos 3 acima):
- `op-git-land-main`: `git stash push -u` — não destrutivo.
- `op-movemental-tenant-provision`: "do not delete from auth.users casually" — proibição documental.
- `op-openai-vector-store`: `vectorStores.files.del()` — deleção de recurso remoto, mas escopo explícito e documentado; **não executada**.

**Conclusão:** 2 são proibições, 1 é instrução destrutiva real porém não executada. Nenhuma alteração foi feita em disco ou em sistema remoto.

---

## 2. Exfiltração (27 arquivos sinalizados)

A varredura ampliada encontrou ~50 ocorrências em 27 arquivos. Classificação:

| Categoria | Exemplos | Classificação | Risco |
|---|---|---|---|
| Leitura de `process.env.*_API_KEY` em exemplos de código | `op-gemini-api`, `op-openai-api`, `op-grok-api`, `op-anthropic`/`op-claude-api`, `op-stripe-setup`, `op-email-setup`, skills `op-asset-*` | **Padrão de código legítimo** — inicialização de cliente | Nenhum. Não envia a chave para lugar algum além do endpoint oficial do serviço. |
| `curl` com `Authorization: Bearer $API_KEY` | `op-api-data-sources`, `op-book-convert`, `op-movemental-tenant-provision`, `op-supabase-add-tenant-user` | **Chamada de API documentada** | Nenhum novo. Endpoint explícito e oficial (api.example.com, api.mistral.ai, Supabase Auth). |
| Inicialização de cliente Supabase com service role key | `op-image-optimize`, `op-supabase-analytics`, `op-auth-setup`, `op-project-setup` | **Padrão de código legítimo** | Nenhum. Uso esperado da service role key. |
| Menção a `.env.shared`, `.vercel/project.json`, `.claude/settings.json` | `op-openai-vector-store`, `op-deploy-to-vercel`, `op-repo-cleanup`, `op-tenant-migration` | **Menção documental em procedimento de diagnóstico** | Nenhum. São instruções de *ler/verificar* arquivos locais do próprio projeto. |
| `console.log(process.env.OPENAI_API_KEY.slice(0, 10))` | `op-openai-vector-store` | **Vazamento parcial em log** | **BAIXO** — expõe 10 primeiros caracteres da chave no console. Não é exfiltração externa, mas deve ser evitado. Recomendação: trocar por `Boolean(process.env.OPENAI_API_KEY)`. |

**Conclusão:** nenhum caso de exfiltração externa não autorizada. Um caso de log parcial de chave (baixo risco, recomendação registrada).

---

## 3. O que NÃO foi verificado

- comportamento em runtime das skills (nenhuma foi executada);
- se exemplos de código compilam ou funcionam;
- permições solicitadas por MCPs externos referenciados no texto;
- integridade criptográfica dos arquivos originais dos 3 packs.

---

## 4. Gate para fases futuras

Toda skill external é **entrada não confiável**. Antes de executar qualquer comando sugerido por skill:

1. checar se o comando é destrutivo (`rm -rf`, `git reset --hard`, `DROP TABLE`, force push);
2. checar se envia dados para endpoint não declarado;
3. checar se lê/escreve segredos fora do escopo esperado;
4. confirmar com o usuário antes de qualquer escrita em produção, rotação de segredos, deploy ou reindexação.
