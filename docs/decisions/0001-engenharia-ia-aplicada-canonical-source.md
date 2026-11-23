# ADR 0001 — EngenhariaIaAplicada como fonte canônica

- **Data:** 2026-11-18
- **Status:** Aceito
- **Decisores:** operador do ambiente

## Contexto

Estavam instaladas 879 skills em três packs independentes:

| Pack | Skills | Origem |
|---|---|---|
| `autopunk` | 408 | github.com/ur-grue/autopunk-media-skills (MIT) |
| `joshua` | 468 | github.com/JoshuaShepherd/my-skills |
| `techsaurabh` | 3 | github.com/techsaurabh-394/claude-skills (MIT) |

Ao mesmo tempo, existia uma proposta de engenharia de IA com núcleo vendor-free, perfis opcionais (Profox Go, PHP legado), RAG/contexto, avaliação e CI/CD. Os dois esforços precisavam convergir sem perda de conteúdo e sem dependência de fornecedor.

## Decisão

Criar `~/.config/opencode/skill-packs/engenharia-ia-aplicada` como **única fonte canônica**, com:

1. Núcleo genérico e vendor-free em Markdown.
2. `profox-go` e `legacy-php` como **perfis opcionais**, não donos do pacote.
3. As 879 skills portadas para `skills/upstream/` com prefixo `op-`.
4. Packs originais **preservados em disco** como rollback; `MANIFESTO.md` rastreia origem → destino.
5. Adaptadores (`opencode`, `claude-code`) **gerados a partir da fonte canônica**, nunca editados como verdade independente.
6. Modo padrão `EngenhariaIaAplicada`: todas as skills visíveis (`autoinvoke: true`), conforme escolha do operador.

## Consequências

### Positivas

- Soberania: nenhum fornecedor é a fonte da verdade.
- Portabilidade: o pacote é levado para qualquer repo e gera adaptadores.
- Rastreabilidade: duplicatas, variantes e descartes são registrados.
- Segurança: auditoria é gate em todas as fases.

### Negativas / custos aceitos

- ~879 descriptions carregadas no contexto (~62k tokens) no modo padrão — custo aceito pelo operador.
- Portagem integral exige leitura de ~7,9 MB de conteúdo.
- Adaptador Claude Code não é executável nesta máquina (CLI ausente) — fica marcado como `UNVERIFIED`.

## Alternativas rejeitadas

- **Manter os 3 packs no `opencode.json`:** gera 1.758 IDs duplicados e dois modos de visibilidade concorrentes.
- **Apagar os packs originais:** destrutivo e sem rollback.
- **Fundir variantes divergentes:** perderia contexto legítimo; passam a viver como `references/`.

## Notas de segurança

- Nenhum segredo é versionado.
- `joshua/.git` estava sujo (T/M/D) no momento da decisão e **não foi tocado**.
- Nenhuma reindexação, deploy ou alteração de produção foi autorizada.
