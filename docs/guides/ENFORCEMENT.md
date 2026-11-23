# Enforcement — gate determinístico

O gate não substitui o gate de segurança do skill `op-eia-security-gate`. Ele é a camada **mecânica**: decide, sem inferência e sem execução, se uma intenção pode seguir.

Nada aqui é ativado automaticamente. O adapter de permissões é opt-in e o comando `eia enforce` só roda quando você chama.

## 1. Gate semântico (`scripts/enforce.py`)

Lê um objeto JSON em stdin, devolve um JSON com `decisao`, `motivo`, `regras` e `versao`.

```bash
echo '{"acao":"shell","comando":"git status --short"}' \
  | python3 scripts/enforce.py
```

```json
{"decisao": "permitir", "motivo": "ação benigna de origem local", "regras": [], "versao": "0.1.0"}
```

Saída também é sinalizada por código: `0` permitir, `2` negar, `3` pedir, `1` erro de contrato.

Ou pelo operador:

```bash
echo '{"acao":"deploy","ambiente":"producao"}' | python3 scripts/eia.py enforce
```

### Contrato de entrada

| Campo | Tipo | Uso |
|---|---|---|
| `acao` | string | obrigatório; ex.: `shell`, `edit`, `deploy`, `rotacionar_segredo` |
| `recurso` | string | caminho ou alvo inspecionado |
| `comando` | string | texto de shell inspecionado, **nunca executado** |
| `origem` | string | `operador`, `ferramenta`, `skill_externa`, `mcp`, `documento`, `issue` |
| `ambiente` | string | `local`, `stage`, `producao` |
| `autorizacao_explicita` | bool | autorização direta do operador |
| `gate_aprovado` | bool | aprovação do QA/Security para conteúdo não confiável |

### Regras

| ID | Bloqueia | Liberação |
|---|---|---|
| `R01` | comandos destrutivos (`rm -r`, `reset --hard`, `clean -fd`, `push --force`, `--force-with-lease`, `mkfs`, `dd if=`, `DROP/TRUNCATE/DELETE`) | `autorizacao_explicita` |
| `R02` | `.git/`, `secrets/`, `*.env`, `*.key`, `*.pem`, `*.p12` | `autorizacao_explicita` |
| `R03` | `ambiente: producao` | `autorizacao_explicita` |
| `R04` | segredos (rotacionar, exportar, ler, publicar) | `autorizacao_explicita` |
| `R05` | reindexação | `autorizacao_explicita` |
| `R06` | origem não confiável (skill externa, MCP, documento, issue) | **somente** `gate_aprovado` |

`R06` de propósito **não** é liberada por autorização explícita: o gate do QA/Security continua obrigatório mesmo quando o operador autoriza a ação.

Ações benignas de origem local (`shell`, `read`, `edit`, `write`, `glob`, `grep`, `status`, `version`, `audit`, `doctor`) seguem automaticamente se nenhuma regra incidir. Qualquer coisa fora da whitelist cai em `pedir`.

### Limites

- Não há execução de comando, subprocesso, rede ou escrita em disco.
- Valores do evento nunca viram argv, caminho de import ou expressão avaliada.
- É uma decisão sobre intenção declarada, não uma inspeção do sistema. Não detecta comando ofuscado, `eval`, script baixado e executado depois, nem efeito colateral indireto.

## 2. Permissões nativas do OpenCode (opt-in)

O arquivo `adapters/opencode/generated/permissions.json` contém regras V2 somente de bloqueio — nenhuma `allow` ampla. Ele é derivado da fonte canônica por `generate_adapters.py` e verificado por `verify_adapters.py`.

Para usar, mescle o array `permissions` no `opencode.json` da máquina. Não faça isso sem querer; o merge altera o comportamento do runtime. Regras locais e de agente são aplicadas depois das globais, e a última regra que casa vence.

As regras estáticas cobrem padrões de texto (`rm -rf *`, `git push --force *`, edição em `.git/` e `secrets/`).Decisões que dependem de contexto — autorização explícita e gate de skill externa — pertencem ao `eia enforce`, não à config.

## Testado

`tests/test_enforce.py`: 14 testes cobrindo regras `R01`–`R06`, autorização, whitelist, contrato inválido, códigos de saída e a garantia de que nenhum subprocesso é chamado.
