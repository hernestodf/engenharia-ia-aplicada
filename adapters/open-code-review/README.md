# OpenCodeReview — adaptador opcional

CLI de revisão de código da Alibaba (`alibaba/open-code-review`, Apache-2.0),
pinada em `@alibaba-group/open-code-review@1.14.2` (`shasum` em `pin.json`).

**Não vem instalado.** Aqui só existe a referência pinada, a skill
`op-open-code-review` e a verificação de integridade. O instalador Godnaterra
não roda `npm install`.

## Dois modos

| Modo | Quem chama o modelo | Custo |
|---|---|---|
| **delegation** (padrão) | o agente hospedeiro | usa a sessão atual, sem key extra |
| **native** | o `ocr`, via `ocr config provider` | provider próprio, custo separado |

O wrapper do Godnaterra recomenda **delegation**. Native só quando você quiser
a pipeline completa do `ocr` e aceitar configurar provider/modelo.

## Habilitar (ação explícita)

```bash
npm install -g @alibaba-group/open-code-review@1.14.2
ocr --version
```

Depois disso a skill `op-open-code-review` sabe quando acionar. Sem o binário,
ela reporta `pendente` — nunca finge que rodou.

## Verificação

```bash
python3 scripts/verify_adapters.py
python3 scripts/verify_adapters.py --check-online
```

## Segurança

- Versão e integridade pinadas; nunca `@latest`.
- Não rodamos `npx skills add alibaba/open-code-review` (instalador remoto).
- A skill wrapper foi escrita aqui, com proveniência — não é código copiado.
- Sem segredo no arquivo, sem execução via shell, sem auto-instalação.

Não verificado aqui: review real de um diff e a pipeline determinística do `ocr`.
