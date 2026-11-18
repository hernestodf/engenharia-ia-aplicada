# tests

Testes do próprio pacote (não das skills upstream).

Prioridade de validação nesta máquina:

1. JSON válido do `opencode.json`
2. IDs únicos após prefixação `op-`
3. zero padrões incompatíveis remanescentes
4. carregamento real de 3 skills de áreas diferentes

Ferramentas ausentes aqui (Go, Playwright CLI, Claude CLI) geram itens `UNVERIFIED`, não "passou".
