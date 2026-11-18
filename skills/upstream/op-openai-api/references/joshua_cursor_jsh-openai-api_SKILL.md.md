# Variante divergente — openai-api

Origem: `joshua/cursor/jsh-openai-api/SKILL.md`

---


# OpenAI API (Cursor)

## Canonical source

**`.claude/skills/jsh-openai-api/SKILL.md`** lists **platform.openai.com** and **openai.github.io/openai-agents-python** references and implementation patterns.

## In Cursor

1. Read the canonical skill for the surface you need (`agents` vs `chat`).
2. Fetch current OpenAI docs (model list, API reference) before relying on model IDs or parameters.
3. OpenAI REST + Agents SDK entry: `src/lib/ai/clients/openai.ts` (`openaiClient`, `createAgent`, `createRunner`, re-exports `run`, `tool`, `fileSearchTool`).
