---
name: op-add-section-type
description: Create a new course section component and register it in the section router. Use when adding a new section type to the course learn experience (e.g., "add a quiz section type" or "add a new section component").
engenharia-ia-aplicada/source: joshua/claude/design/add-section-type/SKILL.md
engenharia-ia-aplicada/original-name: add-section-type
---

Create a new course section component for the section type: $0

## Process

1. Read 2-3 existing sections in `<diretorio de secoes do curso>/` to understand the pattern (e.g., `ReadingSection.tsx`, `VideoSection.tsx`, `ReflectionSection.tsx`)
2. Read `<diretorio de secoes do curso>/SectionContent.tsx` to understand the section registry and how sections are rendered
3. Create the new section at `<diretorio de secoes do curso>/$0Section.tsx` following the exact same pattern as existing sections
4. Register it in `SectionContent.tsx` by adding the import and mapping entry

## Rules

- Follow the exact component signature and prop types of existing sections
- Use shadcn/ui components and semantic CSS classes
- Never hardcode tenant-specific text
- Keep the component focused on rendering its content type
