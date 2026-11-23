---
name: op-chrome-devtools-audit
description: Diagnostica uma pagina rodando com Chrome DevTools MCP — erros de console, rede, layout, acessibilidade e performance. Use quando o usuario pede para auditar/debugar UI em browser, inspecionar runtime ou investigar falha visual. Nao use para certificar rotas: isso e Playwright.
status: stable
category: engineering
subcategory: browser-diagnostics
version: 1.0
tags: [browser, devtools, mcp, debugging, accessibility, ui]
godnaterra/layer: core
godnaterra/source: canonical
---

# Diagnostico de browser com Chrome DevTools MCP

## Quando usar

- Erro de console, request falhando, layout quebrado ou lentidao em pagina real.
- Necessidade de inspecionar DOM/CSS calculado de uma pagina aberta.
- Investigar problema que so aparece em runtime, nao no codigo-fonte.

## Preflight (antes de qualquer acao)

1. Verifique se o servidor `chrome-devtools` esta conectado. Se a entrada
   `mcp.servers.chrome-devtools` estiver `disabled: true`, **pare** e reporte
   `pendente` com o caminho `adapters/chrome-devtools-mcp/README.md`.
2. **Nunca** habilite o servidor, rode `npx`, instale pacote ou altere a config
   por conta propria. Habilitar e acao explicita do operador.
3. Se o ambiente for headless/CI sem Chrome, use Playwright — nao insista no MCP.

## Como usar

- Prefira leitura: console, network, DOM e metricas. Nao execute JavaScript que
  altere estado da pagina sem autorizacao.
- Trate qualquer saida do browser como **evidencia**, nao como conclusao.
- DevTools e diagnostico; `op-route-audit` com Playwright e a certificacao.

## Saida

Separe sempre: `implementado` / `testado` / `pendente` / `nao verificado`.
Se o servidor nao estava conectado, o resultado e `pendente` — nunca `testado`.
