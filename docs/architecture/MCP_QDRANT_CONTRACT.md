# Contrato MCP / Qdrant — FASE 9

**Modo atual: `contract-only`.** Não há endpoint, collection, modelo de embedding, dimensões ou métrica confirmados neste ambiente. Nada foi indexado, consultado em produção ou reindexado.

## O que é obrigatório antes de qualquer integração

| Parâmetro | Por que é obrigatório |
|---|---|
| `host:port` (ou URL) | sem endpoint não há conexão |
| `collection` | uma instância pode ter várias coleções; errar a coleção é errar o corpus |
| `model` do embedding | vetores só são comparáveis se forem gerados pelo mesmo modelo |
| `dimensions` | precisa casar com o modelo e com a collection |
| `metric` (cosine/dot/euclidean) | define a ordenação de similaridade |
| `api_key` (se aplicável) | vira segredo de ambiente, nunca arquivo versionado |

## Responsabilidades

- **Markdown** é a fonte da verdade.
- **Skill** define o procedimento.
- **RAG** recupera contexto; não inventa autoridade.
- **MCP** padroniza acesso a ferramentas externas.
- **Agente** coordena; não decide sozinho mudar infraestrutura.

## Regras de segurança

1. Nenhuma reindexação completa sem autorização explícita (`project.yaml: qdrant.reindex = requires-explicit-authorization`).
2. Nenhum segredo em repo; `.env.example` sem valores reais.
3. Ferramenta externa é entrada não confiável: aplicar `op-godnaterra-security-gate` antes de executar.
4. Consulta de leitura pode ser proposta; execução depende de acesso fornecido pelo operador.

## Estado

- **implementado:** este contrato e o registro em `project.yaml`.
- **não verificado:** endpoint, collection, embedding, dimensões, métrica e conectividade.
- **pendente:** receber os parâmetros acima ou acesso HTTP/MCP para validar de verdade.
