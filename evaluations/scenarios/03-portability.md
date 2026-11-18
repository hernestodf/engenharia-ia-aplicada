# Cenário 03 — portagem determinística

- **entrada:** skill com `$ARGUMENTS`, `mcp__supabase__execute_sql`, `/Users/x/Desktop/Dev/repos/y`, `{{course-slug}}` e `$2.4M`.
- **esperado:** viram respectivamente "dados informados pelo usuario na mensagem", "ferramenta externa: supabase/execute_sql", `<repo atual>`, `<slug>`; `$2.4M` preservado.
- **negativo:** apagar `$0`/`$1`; aplicar regex genérico de `/Users/` antes do path completo.
- **regressão:** FASE 5 encontrou 13 `{{course-slug}}` não detectados pela checagem da FASE 4; corrigidos e cobertos por `scripts/validate_catalog.py`.
- **automático:** sim. Estado: **testado** (`python3 scripts/validate_catalog.py` → 0 problemas).
