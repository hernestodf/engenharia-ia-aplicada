# Contrato das primitivas

O pacote não fixa framework. Uma primitiva é definida pelo comportamento, não pela biblioteca.

| Primitiva | Obrigatório | Proibido |
|---|---|---|
| `Button` | `type`, estado `disabled`, foco visível, rótulo textual ou `aria-label` | usar `<div>` clicável; esconder foco |
| `Input` | `<label>` associado, `id` único, erro ligado por `aria-describedby` | placeholder como único rótulo |
| `Card` | hierarquia de título, padding por `--gt-space-*`, sem cor hardcoded | sombra como única separação visual |
| `Badge` | texto curto, contraste igual ao texto normal | conveyar estado só por cor |
| `Table` | `<caption>` ou heading, `<th scope>`, scroll horizontal em telas estreitas | layout com `<div>` para dados tabulares |

## Regra de dependência

`tokens → primitivas → componentes de domínio → páginas`. Um componente de nível superior não define cor, fonte ou espaçamento diretamente — consome token.

Perfis (`profox-go`, `legacy-php`) sobrescrevem `tokens/tokens.css`. Não criam guideline paralela.
