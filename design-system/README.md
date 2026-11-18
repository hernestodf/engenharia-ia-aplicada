# Design System

Base vendor-neutral para qualquer interface gerada pelo pacote. Não é um design system de produto — é um contrato mínimo para que perfis diferentes não produzam UI incoerente.

| Pasta | Conteúdo |
|---|---|
| `tokens/` | `tokens.json` (fonte legível por máquina) e `tokens.css` (variáveis `--gt-*`) |
| `components/` | contrato comportamental das primitivas, sem framework |
| `guidelines/` | regras de acessibilidade não negociáveis |

Perfis (Profox, legado) podem sobrescrever **valores** de token, nunca nomes semânticos ou regras de acessibilidade.

## FASE 6 — estado

- **implementado:** tokens, contrato de primitivas, checklist de acessibilidade.
- **testado:** `tokens.json` é JSON válido e `tokens.css` foi inspecionado quanto ao uso exclusivo de variáveis `--gt-*` (ver `tests/test_package.py`).
- **não verificado:** contraste real, navegação por teclado e zoom em interface concreta — não há UI de produto neste repo.
