# Telemetria mínima (local, opt-in)

Nada é enviado. Não há endpoint, token, socket, serviço externo nem rede. O registro fica em um JSONL dentro do próprio pacote, com permissão `0600`, e só acontece quando `EIA_TELEMETRY=1`.

## Estado e resumo

```bash
python3 scripts/eia.py telemetry
python3 scripts/eia.py telemetry --resumo
python3 scripts/telemetry.py --habilitado
```

Sem a variável, a gravação é um no-op: nenhum arquivo é criado e o resultado diz `telemetria desabilitada`.

## Gravar um evento

```bash
EIA_TELEMETRY=1 python3 scripts/telemetry.py \
  --evento eval_concluido --resultado ok --duracao-ms 1200
```

Eventos aceitos (whitelist fechada): `eval_concluido`, `rag_avaliado`, `gate_avaliado`, `auditoria_concluida`, `instalacao_concluida`.

Resultados aceitos: `ok`, `erro`, `nao_verificado`.

## Contrato do registro

| Campo | Conteúdo |
|---|---|
| `schema` | versão do contrato (atualmente 1) |
| `evento` | nome da whitelist |
| `resultado` | `ok`, `erro` ou `nao_verificado` |
| `duracao_ms` | inteiro não negativo ou nulo |
| `registrado_em` | ISO-8601 em UTC |
| `versao_pacote` | lido de `VERSION` |

Não existe campo livre. Não há prompt, texto de arquivo, comando, ID de sessão, usuário, e-mail ou caminho de máquina.

## Redação

Antes de qualquer persistência, `redigir()` remove:

- chaves `sk-…`, `ghp_…`, `AKIA…`;
- atribuições `api_key=…`, `token: …`, `secret: …`;
- headers `Bearer …`;
- caminhos absolutos de usuário (`/home/…`, `/Users/…`).

Testes cobrem cada uma dessas famílias e também garantem que nenhum socket é aberto.

## Limites

- O resumo agrega `evento/resultado`, não mede latência agregada nem tendência — isso exigiria mais volume do que o pacote tem.
- O arquivo é local e pode ser apagado pelo operador; não é fonte de verdade para nada.
- Telemetria não é avaliação. Não troca os 90 testes, a suíte de 20 tarefas nem o baseline de RAG.

## Testado

`tests/test_telemetry.py`: 11 testes, incluindo desabilitação padrão, redação de segredos e caminhos, restrição de destino, agregação de JSONL e prova de que nenhum socket é aberto.
