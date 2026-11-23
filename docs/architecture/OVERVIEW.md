# Arquitetura — Visão Geral

O EngenhariaIaAplicada é organizado em **seis módulos lógicos**. São responsabilidades, não serviços separados obrigatórios — rodam como Markdown, scripts e config.versionáveis.

## Módulos

| Módulo | Nome | Onde vive | Responsabilidade |
|---|---|---|---|
| A | Project Registry | `project.yaml`, `docs/decisions/` | stack, restrições, convenções e decisões (ADRs) |
| B | Skill Factory | `skills/core/`, `skills/upstream/`, `evaluations/` | criar, portar, validar, auditar e testar skills |
| C | Agent Execution | `agents/`, `skills/core/agent-orchestration` | seleção de skills, delegação, limites e evidências |
| D | Knowledge Engine | `docs/`, `adapters/`, RAG opcional | contexto, proveniência, atualidade, deduplicação |
| E | Quality & Evaluation | `tests/`, `evaluations/`, `security-audit` | testes, revisão, segurança, regressão |
| F | Delivery Engine | `.github/workflows/`, `scripts/` | Git, CI, build, artefatos, deploy e rollback |

## Relação entre os módulos

```
        ┌──────────────────────────────────────────┐
        │        A · Project Registry              │
        │   project.yaml + ADRs = mapa do repo     │
        └────────────────────┬─────────────────────┘
                             │ informa
        ┌────────────────────▼─────────────────────┐
        │        C · Agent Execution               │
        │   roteia para core → upstream            │
        └───┬─────────────┬─────────────┬──────────┘
            │             │             │
   ┌────────▼──┐  ┌───────▼───┐  ┌──────▼────────┐
   │ B · Skill │  │ D · Knowledge│ │ E · Quality  │
   │  Factory  │  │   Engine     │ │ & Evaluation │
   └────────┬──┘  └───────┬───┘  └──────┬────────┘
            └──────────────┴─────────────┘
                           │
              ┌────────────▼─────────────┐
              │   F · Delivery Engine    │
              │   CI/CD + scripts        │
              └──────────────────────────┘
```

## Fluxo de dados

1. `project.yaml` e `AGENTS.md` definem **o que é verdade** sobre o projeto.
2. O agente lê o mapa e classifica a tarefa (domínio + risco).
3. Uma skill `core/` é o ponto de entrada; ela referencia `upstream/` por necessidade.
4. Skills externas passam por auditoria (Módulo E) antes de qualquer execução.
5. Resultado é validado, documentado e entregue via Módulo F.
6. ADRs registram decisões que mudam o estado desejado do sistema.

## Fontes de verdade

| Informação | Fonte única |
|---|---|
| Regras de comportamento | `AGENTS.md` |
| Stack e restrições | `project.yaml` |
| Decisões arquiteturais | `docs/decisions/` |
| Proveniência de skills | `MANIFESTO.md` |
| Contrato de instalação | `docs/guides/INSTALL.md` |

Regras duplicadas entre adaptadores são derivadas — nunca editadas diretamente.

## Estado de implementação (FASE 3)

- Módulos A, B, C, D, E e F: **estrutura criada**, conteúdo em expansão nas fases 4–10.
- Nenhum módulo marcado como testado nesta fase.
- Qdrant/MCP: **contrato apenas**, sem.indexação.
