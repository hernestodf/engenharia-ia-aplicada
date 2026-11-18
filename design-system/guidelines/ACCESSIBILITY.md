# Acessibilidade — regras não negociáveis

Perfis podem trocar cores, fontes e densidade. Não podem trocar estas regras.

## Checklist

- [ ] Contraste mínimo 4.5:1 para texto normal e 3:1 para texto grande e controles.
- [ ] Foco visível em todo elemento interativo (`--gt-focus-width`, `--gt-focus-offset`).
- [ ] Alvo de toque com pelo menos 24×24 px (44×44 px recomendado).
- [ ] Semântica HTML antes de ARIA: `<button>`, `<a>`, `<label>`, `<table>`.
- [ ] Toda imagem informativa tem texto alternativo; decorativa tem `alt=""`.
- [ ] Erros de formulário associados ao campo e anunciados, não só por cor.
- [ ] Navegação por teclado completa, sem armadilha de foco.
- [ ] `prefers-reduced-motion` respeitado (`--gt-motion-duration`).
- [ ] Zoom até 200% sem perda de conteúdo ou funcionalidade.
- [ ] Texto nunca fixo em imagem quando pode ser HTML.

## Verificação mínima antes de entregar UI

1. Tab pela tela inteira.
2. Desligar CSS e ler a estrutura.
3. Checar contraste com ferramenta.
4. Testar largura de 320 px.

Sem evidência desses quatro passos, marque como **não verificado**.
