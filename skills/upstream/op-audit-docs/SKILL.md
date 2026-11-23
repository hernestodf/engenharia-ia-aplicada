---
name: op-audit-docs
description: Skill portada para EngenhariaIaAplicada.
---

# Type Safety Documentation Audit & Update

Audit every file in `<diretorio de documentacao de tipos>/` against the live codebase and fix any errors, gaps, or stale information so the docs are the authoritative single source of truth for the six-layer type safety chain.

## Before Starting

1. Read every file in `<diretorio de documentacao de tipos>/` (README.md, TYPE_SAFETY.md, all files in layers/, validation/, and any other files present).
2. Gather ground truth from the codebase for each layer — use the actual source files, generators, and validators as the authority.

## Ground Truth Collection

For each layer, collect the following from the **actual codebase** (not from existing docs):

### Layer 1 — Drizzle Schema
- Read `<caminho do schema>` (first ~100 lines for structure, then count pgTable exports)
- Read `<diretorio de scripts>/validate-db-alignment.ts` to understand what the validator actually checks
- Read `<diretorio de scripts>/generate-schema.ts` (if it exists) to understand schema generation
- Count: `grep -c "export const .* = pgTable(" <caminho do schema>`
- Note any tables with type annotations (e.g., `PgTableWithColumns<any>`)

### Layer 2 — Zod Schemas
- Read `<diretorio de schemas>/index.ts` (first ~80 lines for structure, imports, BaseFiltersSchema)
- List other files in `<diretorio de schemas>/` (custom schemas)
- Read `<diretorio de scripts>/generate-zod-schemas.ts` (first ~100 lines for pattern)
- Read `<diretorio de scripts>/validate-semantic-alignment.ts` to understand validation logic
- Note the four-schema pattern and type exports

### Layer 3 — Services
- Read `<services dir>/base.service.ts` for the Result<T> pattern, class signature, and methods
- Sample one entity service file for the actual pattern
- List `src/lib/services/custom/` contents
- Read `<diretorio de scripts>/generate-services.ts` (first ~80 lines)
- Read `<diretorio de scripts>/validate-services-alignment.ts`

### Layer 4 — API Routes
- Sample one route file from `<api dir>/` for the actual handler pattern
- List `src/app/api/custom/` directories
- Read `<diretorio de scripts>/generate-routes.ts` (first ~80 lines)
- Read `<diretorio de scripts>/validate-routes-alignment.ts`

### Layer 5 — React Hooks
- Sample one hook file from `<hooks dir>/` for the actual pattern (keys, hooks, fetchApi, buildQueryString)
- List `<hooks dir>/custom/` contents
- Read `<diretorio de scripts>/generate-hooks.ts` (first ~80 lines)
- Read `<diretorio de scripts>/validate-hooks-alignment.ts`
- Check `src/app/providers.tsx` for QueryClientProvider

### Layer 6 — UI Components
- Sample one component from `<components dir>/simplified/` for the actual pattern
- Read `<diretorio de scripts>/generate-ui-components.ts` (first ~80 lines)
- Read `<diretorio de scripts>/validate-ui-alignment.ts`

### Cross-Cutting
- Read `<caminho da configuracao>` (first ~30 lines) for tenant scoping context
- Read `src/lib/tenant.ts` for getTenantOrgId
- Count entities at each layer to verify consistency

## Audit Checklist

Compare every claim in the docs against ground truth. Flag and fix:

1. **Incorrect counts** — table counts, entity counts, file counts
2. **Wrong patterns** — code examples that don't match actual generated code
3. **Missing information** — layers, patterns, or conventions not documented
4. **Stale references** — files, paths, or commands that no longer exist
5. **Naming convention errors** — incorrect camelCase/PascalCase/kebab-case mappings
6. **Validator behavior** — what each validator actually checks vs. what docs claim
7. **Generator behavior** — what each generator does (overwrites vs. skips existing) vs. what docs claim
8. **Custom code gaps** — custom services, hooks, routes not mentioned or incorrectly described
9. **contentCategories discrepancy** — verify the 148 vs 147 explanation is still accurate
10. **Lock-Before-Proceed protocol** — ensure the protocol description matches actual validator exit codes and workflow
11. **Commands** — ensure all pnpm commands listed match package.json
12. **Cross-references** — ensure layer docs reference each other correctly

## Update Rules

- Fix errors in place — do not create new files unless a section genuinely needs its own file
- Use actual code snippets from the codebase, not invented examples
- Keep the same document structure and voice — just make it accurate
- Update counts, paths, patterns, and examples to match reality
- If a doc file covers something that no longer exists, remove that section
- If the codebase has something undocumented, add it to the appropriate doc
- Update `<diretorio de documentacao de tipos>/validation/VALIDATION_STATUS.md` with current actual status (run validators if possible)
- Update the README.md index if any files were added or removed

## After Updating

1. Review each updated file for internal consistency
2. Ensure no doc references a pattern that contradicts another doc
3. Verify all code examples are syntactically correct
4. Confirm the README.md index accurately lists all files in `<diretorio de documentacao de tipos>/`
