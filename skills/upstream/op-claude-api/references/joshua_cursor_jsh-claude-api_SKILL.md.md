# Variante divergente — claude-api

Origem: `joshua/cursor/jsh-claude-api/SKILL.md`

---


# Claude API (Cursor)

## Canonical source

**`.claude/skills/jsh-claude-api/SKILL.md`** contains model IDs, message format notes, tool-use loops, caching, and a table of **authoritative docs.anthropic.com URLs**.

## In Cursor

1. Read the canonical skill section for your task (tool use, streaming, caching, etc.).
2. Use **WebFetch** or **WebSearch** on the listed Anthropic URLs when model names or API fields may have changed.
3. Keep client access through `anthropicClient` from `src/lib/ai/clients/anthropic.ts` and `env` from `@/lib/env`.
