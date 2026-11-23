# adapters

Adaptadores **derivados** da fonte canônica (`AGENTS.md`, `project.yaml`, `skills/`). Nunca edite um adaptador como verdade independente.

| Adaptador | Situação nesta máquina |
|---|---|
| `opencode` | testável aqui (OpenCode v2.3.2 presente) |
| `claude-code` | gerável, não executável (CLI ausente) |

Regenerar sempre que a fonte canônica mudar.

## Integrações opcionais (FASE 11)

Diferente dos adaptadores derivados acima, estes são **referências pinadas** a
projetos externos. Nenhum código deles é vendorizado, nenhum servidor é
habilitado e nenhum CLI é instalado pelo `install.py`.

| Diretório | Origem | Licença | Pin | Estado |
|---|---|---|---|---|
| `chrome-devtools-mcp/` | `ChromeDevTools/chrome-devtools-mcp` | Apache-2.0 | npm `1.13.0`, shasum `e76ecc…` | MCP `disabled: true` |
| `open-code-review/` | `alibaba/open-code-review` | Apache-2.0 | npm `1.14.2`, shasum `4459a7…` | CLI não instalado |
| `openviking/` | `volcengine/OpenViking` | **AGPL-3.0** | commit `5b7c655…` | MCP `disabled: true`, não vendorizado |

Verificação: `python3 scripts/verify_adapters.py` (use `--check-online` para
conferir os shasums contra o registry). Regras e pré-requisitos em cada README.

A licença AGPL do OpenViking é o motivo pelo qual ele é adapter e não código
no tarball. Nenhum comando de instalação externa é executado automaticamente.
