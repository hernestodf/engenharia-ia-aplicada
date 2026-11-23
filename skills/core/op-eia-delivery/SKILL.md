---
name: op-eia-delivery
description: Orienta instalação, modos, rollback e limites de entrega do pacote EngenhariaIaAplicada. Use antes de instalar adaptadores, trocar modo ou mexer em config global.
engenharia-ia-aplicada/layer: core
engenharia-ia-aplicada/source: canonical
---

# Entrega EngenhariaIaAplicada

## Modos

`god` / `EngenhariaIaAplicada` = todas as skills visíveis. `curated` = subconjunto. `status` = relatório. Ver `skill_mode.py` e `docs/guides/INSTALL.md`.

## Instalação segura

1. `python3 scripts/generate_adapters.py` (dry-run) — inspecionar artefatos em `adapters/*/generated/`.
2. `--apply` com backup timestampado; merge de config, nunca sobrescrita cega.
3. Validar com comando real de cada runtime disponível (`opencode debug agents`).
4. Runtime ausente fica `UNVERIFIED` — não "passou".

## Rollback

- OpenCode: `opencode.json.bak-eia-*`.
- Claude: remover symlinks `~/.claude/skills/op-*`; fonte canônica intacta.
- Packs originais (`autopunk`, `joshua`, `techsaurabh`) preservados como trilha de retorno.

## Limites

Sem deploy, reindexação, reset de banco, rotação de segredos ou produção sem autorização explícita. Qdrant é `contract-only` até receber endpoint/collection/embedding/dimensões/métrica.
