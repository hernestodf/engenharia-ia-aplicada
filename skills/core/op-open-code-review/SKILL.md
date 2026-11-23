---
name: op-open-code-review
description: Revisa um diff com OpenCodeReview CLI em modo delegation, gerando comentarios de linha com regras deterministicas e validacao do agente. Use quando o usuario pede code review, revisao de PR ou auditoria de mudancas antes de commit. Nao use para escrever codigo nem para aprovar mudanca sem evidencia.
status: stable
category: engineering
subcategory: code-review
version: 1.0
tags: [review, diff, quality, security, ocr]
engenharia-ia-aplicada/layer: core
engenharia-ia-aplicada/source: canonical
---

# Revisao de codigo com OpenCodeReview

## Quando usar

- Revisao de diff antes de commit/merge.
- Verificacao de padroes deterministicos (XSS, SQL injection, NPE, thread safety)
  combinada com julgamento do agente.
- Segunda opiniao sobre mudanca em codigo de producao.

## Preflight

1. Confira se o binario `ocr` existe. Se nao existir, **pare** e reporte
   `pendente` com: `npm install -g @alibaba-group/open-code-review@1.14.2`.
2. **Nunca** instale o CLI, rode `npx skills add` ou configure provider sozinho.
3. Use **delegation** por padrao: o modelo da sessao faz a analise, sem second key.
   Modo native so mediante pedido explicito e provider configurado pelo operador.

## Regras

- Revise somente o diff informado; nao escaneie o repo inteiro sem pedido.
- Nunca envie segredo, token ou `.env` para o reviewer. Se o diff contiver
  segredo, pare antes de qualquer chamada e sinalize.
- Comentario do reviewer e **sugestao**, nao verdade. Confirme no codigo antes
  de aplicar.
- Diff muito grande, codigo de terceiro vendorizado ou binario: nao review —
  explique o motivo.

## Saida

Lista de achados com arquivo:linha, severidade e evidencia. Separe
`implementado` / `testado` / `pendente` / `nao verificado`. Sem binario, o
resultado e `pendente`.
