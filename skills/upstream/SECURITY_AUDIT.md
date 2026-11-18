# Auditoria de Seguranca — Skills Portadas

Padroes detectados por `scripts/port_skills.py`. Nenhum trecho foi executado.

## comando_destrutivo (3)

- `joshua/claude/infrastructure/migrations-workflow/SKILL.md` — `gration files so changes are tracked - NEVER`DROP COLUMN`or`DROP TABLE`without a deprecation period in production - NEVER commit s`
- `joshua/claude/infrastructure/tenant-migration/SKILL.md` — ` history — start fresh cd ~/Desktop/dev/repos/<leader-slug> rm -rf .git # 3. Initialize new repo git init git checkout -b main`
- `joshua/cursor/git-land-main/SKILL.md` — `git stash push -u -m "wip <branch>"`before switching. Never`git reset --hard`/`git clean -fd`| | Untracked files that belong | Include i`

## exfiltracao (27)

- `joshua/claude/agents/data-scraper-agent/SKILL.md` — `prompt}]}], "generationConfig": { "responseMimeType": "application/json", "temperature": 0.3, "maxOutputTokens": 2048, }, } try: resp = requests.post(url, json=`
- `joshua/claude/agents/openai-vector-store/SKILL.md` — `+$/i) || f.filename.includes('temp')); // 4. Check for duplicates const nameCounts = {}; for (const f of details) nameCounts[f.filename] = (nameCounts[f.filenam`
- `joshua/claude/assets/image-optimize/SKILL.md` — `EY .env.local```3. Identify the scope — which tenant and/or category to process 4. Inventory source files: count, formats, sizes ## Optimization Pipeline ### St`
- `joshua/claude/infrastructure/analytics-audit/SKILL.md` — `mponent is missing from root layout. ### 1c. Check for duplicate provider initialization Grep for`posthog.init\|Sentry.init\|gtag\('config'`— each should appear`
- `joshua/claude/infrastructure/analytics-setup/SKILL.md` — `-setup/SKILL.md]. Covers: install, provider, person identification, group analytics (org + tenant), session replay, feature flags. --- ## Step 3 — Google Analyt`
- `joshua/claude/infrastructure/auth-setup/SKILL.md` — `e: Never install`@supabase/auth-helpers-nextjs`— it is deprecated.`@supabase/ssr`is the correct package. --- ## Step 2 — Environment Variables Add to`.env.local`
- `joshua/claude/infrastructure/deploy-to-vercel/SKILL.md` — `cally linked to a Vercel project (either file means linked) cat .vercel/project.json 2>/dev/null || cat .vercel/repo.json 2>/dev/null # 3. Check if the Vercel C`
- `joshua/claude/infrastructure/email-setup/SKILL.md` — `attern templates/ WelcomeEmail.tsx MagicLinkEmail.tsx NotificationEmail.tsx _Base.tsx ← Shared layout (logo, footer, brand colors) src/app/api/email/ preview/ro`
- `joshua/claude/infrastructure/env-setup/SKILL.md` — `.env\." src/ --include="*.ts" --include="*.tsx" | sort -u```Catalog every var found — this drives what goes in the schema. --- ## Step 2 — Zod Env Schema (Next.`
- `joshua/claude/infrastructure/ga4-setup/SKILL.md` — `ronment: process.env.NODE_ENV, ...e.params, }, })), }), } ).catch(() => { // Never let analytics failures surface to users }) }```Usage in a Stripe webhook rout`
- `joshua/claude/infrastructure/posthog-setup/SKILL.md` — `ildren} </PostHogProvider>```--- ## Step 6 — Person Identification (Tie Events to Users) Create`src/lib/analytics/posthog-identify.tsx`:```tsx 'use client' impo`
- `joshua/claude/infrastructure/project-setup/SKILL.md` — `work:** [Next.js 15 App Router | Vite + React Router] - **Location:** [path] ### Installed Libraries | Category | Packages | |----------|---------| | UI | tailw`
- `joshua/claude/infrastructure/repo-cleanup/SKILL.md` — `version suffixes:`-v2`,`-v3`,`-new`,`-old`,`-backup`,`-deprecated`,`-temp`,`-wip`,`-draft`,`-copy`,`-legacy`,`-experimental`- Files matching`*.bak.ts`,`*.old.ts`
- `joshua/claude/infrastructure/security-setup/SKILL.md` — `Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=(self)", }, // Content Security Policy // Start in report-only mode, then switch `
- `joshua/claude/infrastructure/sentry-setup/SKILL.md` — `RY_DSN= # Server DSN (same DSN or separate project): same location SENTRY_DSN= # Source map upload (CI/CD only, not needed locally): # SENTRY_ORG= # SENTRY_PROJ`
- `joshua/claude/infrastructure/supabase-analytics/SKILL.md` — `production', }) return { success: true, data: undefined } } catch (error) { // Never let analytics failures bubble up console.error('[analytics] Failed to track`
- `joshua/claude/infrastructure/supabase-security-audit/SKILL.md` — `er: 1. Disable email signup in Supabase Dashboard → Authentication → Providers 2. Add an invite-code gate in the signup form 3. Use Supabase's "Restrict email d`
- `joshua/claude/infrastructure/tenant-migration/SKILL.md` — `### PHASE 5: ENVIRONMENT VARIABLES #### 5A. Env Var Classification **Shared across all tenants** (same value, from`~/.env.shared`): -`DATABASE_URL`/`DIRECT_DATA`
- `joshua/claude/infrastructure/testing-setup/SKILL.md` — ` "only-on-failure", }, projects: [ // Setup: create authenticated session { name: "setup", testMatch: /.*\.setup\.ts/ }, { name: "chromium", use: { ...devices["`
- `joshua/claude/integrations/ai-lab-notebook-gemini/SKILL.md` — `ment-notebook-model-messages.ts#L29)). Claude only sees the catalog titles in the system prompt + user-pasted sources. **Sources discovery is Gemini-only, alway`
- `joshua/claude/integrations/gemini-api/SKILL.md` — `empt <= maxRetries; attempt++) { try { return await fn(); } catch (error) { if (error instanceof GoogleGenerativeAIError) { // Check for rate limit (429) or ser`
- `joshua/claude/integrations/grok-api/SKILL.md` — `gent** → orchestrator role in multi-agent systems (only dedicated multi-agent model on market) 5. Determine reasoning mode: -`reasoning`→ better accuracy, slowe`
- `joshua/claude/movemental/movemental-leader-corpus-upload/SKILL.md` — `Title`+`\| Published \| YYYY \|`+`**Description**:`(or wide catalog table) | |`articles`/`audio`/`videos`|`content/{articles,audio,videos}.md`| pipe table with `
- `joshua/claude/movemental/movemental-site-template-publish/SKILL.md` — `ell the operator you're updating, not adding. ### 2. Derive catalog metadata from the HTML - **subtitle**: one short phrase (e.g. "Cream paper, Newsreader headl`
- `joshua/claude/stitch/integrate-stitch-template/SKILL.md` — `the persona. Available local assets (see`images/README.md`,`catalog/images.json`,`catalog/stock-images.json`): | Folder | Use | Path form | |--------|-----|----`
- `joshua/cursor/jsh-movemental-leader-corpus-upload/SKILL.md` — `Title`+`\| Published \| YYYY \|`+`**Description**:`(or wide catalog table) | |`articles`/`audio`/`videos`|`content/{articles,audio,videos}.md`| pipe table with `
- `joshua/repo-specific/movemental-content-studio/jsh-supabase-security-audit/SKILL.md` — `No overly permissive policies (`USING (true)`without justification) - Auth context is properly used (`auth.uid()`,`auth.role()`) ### 3. API Route Security Audit`

