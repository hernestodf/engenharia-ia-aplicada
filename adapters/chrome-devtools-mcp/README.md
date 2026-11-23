# Chrome DevTools MCP — adaptador opcional

Servidor MCP do Chrome DevTools, pinado em `chrome-devtools-mcp@1.13.0`
(Apache-2.0, `shasum` em `pin.json`).

**Não vem habilitado.** O template `mcp.json` entra na config com
`"disabled": true`. O instalador nunca conecta, nunca baixa e nunca executa o
servidor — ele só grava a entrada.

## Por que existe

Dá suporte real à skill `op-chrome-devtools-audit` e ao `op-route-audit`, que
hoje citam DevTools MCP como diagnóstico mas não tinham servidor configurado.
Playwright continua sendo a certificação; DevTools é diagnóstico.

## Habilitar (ação explícita)

1. Confira os requisitos: Node `^20.19 || ^22.12 || >=23` e Chrome instalado.
2. Edite a config do projeto (`opencode.json`): mude `"disabled": true` para
   `false` na entrada `mcp.servers.chrome-devtools`.
3. Reinicie o OpenCode. `opencode mcp list` deve mostrar o servidor conectado.
4. Na primeira conexão o `npx` baixa o pacote pinado — isso é rede, e é consentimento seu.

## Verificação local

```bash
python3 scripts/verify_adapters.py              # estrutura e pins (offline)
python3 scripts/verify_adapters.py --check-online  # confere shasum no registry
```

## Segurança

- Versão pinada; nunca `@latest`.
- Sem segredo no arquivo.
- Sem execução via shell, sem instalador remoto por pipe, sem auto-instalação.
- O código do servidor **não** é vendorizado — só a referência e o checksum.

Não verificado aqui: conexão efetiva do servidor e lista de tools no runtime.
Node 22.23.1 e Chrome estão presentes na máquina de validação, mas o servidor
não foi executado.
