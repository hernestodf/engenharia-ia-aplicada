# agents

Seis papéis lógicos, não processos simultâneos obrigatórios:

| Perfil | Responsabilidade |
|---|---|
| Architect | estrutura, ADRs, limites |
| Backend | API, dados, migrations |
| Frontend/UI | interface, acessibilidade, design system |
| QA/Security | testes, auditoria, regressão |
| DevOps | CI/CD, build, rollback |
| Knowledge/Skill | RAG, contexto, avaliação de skills |

Delegação via `agent-handoff` / `configure-handoff`. Subagents entram para leitura paralela; escrita fica centralizada e revisada.
