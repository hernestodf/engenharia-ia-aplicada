# OpenViking — adaptador opcional (AGPL-3.0)

Banco de contexto para agentes: memória cross-sessão, recursos e skills.
**Não é uma skill**, é um serviço. O repositório tem ~433 MB e licença
AGPL-3.0 — por isso **nenhum código dele entra no tarball do Engenharia de IA Aplicada**.

Aqui existe só a referência pinada (`pin.json`, commit
`5b7c655610caef9017ed0540474dc7d49db4f2db`), um template MCP desabilitado e a
skill `op-openviking-context`, que orienta o uso sem automatizar a instalação.

## Por que não vendorizar

- AGPL-3.0 contaminaria a distribuição do pacote.
- O serviço exige servidor rodando, API key e modelo.
- A instalação oficial usa um instalador remoto por pipe — **nunca executado** pelo Engenharia de IA Aplicada.
- ~433 MB e deps pesadas (litellm, scrapy, fastapi, SDK da Volcengine).

## Pré-requisitos (se você decidir usar)

1. Servidor OpenViking acessível. A docs oficial indica healthcheck em
   `http://127.0.0.1:1933/health` e endpoint MCP em `/mcp`.
2. Uma **user key** (não root) desse servidor.
3. Habilitar a entrada `mcp.servers.openviking` (template em
   `mcp.opencode.json`), reiniciar o OpenCode e conferir `opencode mcp list`.

A credencial no template vem de `{env:OPENVIKING_API_KEY}` — nenhum segredo é
gravado em arquivo.

## Verificação

```bash
python3 scripts/verify_adapters.py
```

Não verificado aqui: upload/indexação real, latência de retrieval e os números
de benchmark publicados no README do projeto (tratados como marketing, não como
evidência).
