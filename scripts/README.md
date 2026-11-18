# scripts

Scripts de manutenção do pacote: instalação, auditoria, portagem, geração de adaptadores e checagem de integridade.

Regras:

- todo script com efeito colateral deve aceitar `--dry-run`
- diff antes de aplicar
- registrar versão e permitir rollback
- nenhum segredo em argumentos ou arquivos versionados
