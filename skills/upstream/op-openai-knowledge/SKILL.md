---
name: op-openai-knowledge
description: Use when working with the OpenAI API (Responses API) or OpenAI platform features (tools, streaming, Realtime API, auth, models, rate limits, MCP) and you need authoritative, up-to-date documentation (schemas, examples, limits, edge cases). Prefer the OpenAI Developer Documentation MCP server tools when available; otherwise guide the user to enable `openaiDeveloperDocs`.
godnaterra/source: joshua/vendor/skills-openai/openai-knowledge/SKILL.md
godnaterra/original-name: openai-knowledge
---

# OpenAI Knowledge

## Overview

Use the OpenAI Developer Documentation MCP server to search and fetch exact docs (markdown), then base your answer on that text instead of guessing.

## Workflow

### 1) Check whether the Docs MCP server is available

If the `ferramenta externa: openaiDeveloperDocs__*` tools are available, use them.

If you are unsure, run `codex mcp list` and check for `openaiDeveloperDocs`.

### 2) Use MCP tools to pull exact docs

- Search first, then fetch the specific page(s).
  - `ferramenta externa: openaiDeveloperDocs/search_openai_docs` → pick the best URL.
  - `ferramenta externa: openaiDeveloperDocs/fetch_openai_doc` → retrieve the exact markdown (optionally with an `anchor`).
- When you need endpoint schemas or parameters, use:
  - `ferramenta externa: openaiDeveloperDocs/get_openapi_spec`
  - `ferramenta externa: openaiDeveloperDocs/list_api_endpoints`

Base your answer on the fetched text and quote or paraphrase it precisely. Do not invent flags, field names, defaults, or limits.

### 3) If MCP is not configured, guide setup (do not change config unless asked)

Provide one of these setup options, then ask the user to restart the Codex session so the tools load:

- CLI:
  - `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp`
- Config file (`<casa do usuario>/.codex/config.toml`):
  - Add:
    ```toml [mcp_servers.openaiDeveloperDocs] url = "https://developers.openai.com/mcp"```

Also point to: https://developers.openai.com/resources/docs-mcp#quickstart
