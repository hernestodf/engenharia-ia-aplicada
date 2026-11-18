# Cenário 01 — roteamento de tarefa

- **entrada:** "preciso de uma migration no schema e um contrato de API"
- **esperado:** classificar como domínio backend; escolher `godnaterra-backend`; `godnaterra-router` não executa a tarefa; saída declara o que ficou não verificado.
- **negativo:** lançar vários subagents em paralelo; entrar direto por skill `upstream/`.
- **regressão:** nenhuma.
- **automático:** não (requer execução de LLM). Estado: **não verificado**.
