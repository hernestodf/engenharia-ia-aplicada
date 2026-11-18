# Variante divergente — env-setup

Origem: `joshua/cursor/jsh-env-setup/SKILL.md`

---


# Environment setup (Cursor)

## Canonical source

The full workflow (audit grep commands, Next.js 15 `createEnv` patterns, check script) is in **`.claude/skills/jsh-env-setup/SKILL.md`**.

## This repo

- Schema: `src/lib/env.ts` (`@t3-oss/env-nextjs` + Zod).
- Example: `.env.example`; local secrets: `.env.local` (gitignored).
- Verify: `pnpm check:env`.

After changes, grep for stray `process.env.` in `src/` and migrate to `env` / `publicEnv`.

**Multi-tenant:** This service requires **`TENANT_ORG_ID`** (UUID). See **`env.TENANT_ORG_ID`** in `src/lib/env.ts` and **`.cursor/rules/multi-tenancy.mdc`**.
