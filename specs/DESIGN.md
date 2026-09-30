---
version: alpha
name: "Painel de Estoque — 愚公移山 Variedades"
description: "Sistema visual do painel da loja: jade de chá, papel quente e hierarquia funcional"
colors:
  primary: "#0F766E"
  primary-hover: "#115E59"
  primary-active: "#134E4A"
  on-primary: "#FFFFFF"
  accent: "#B45309"
  accent-soft: "#FEF3C7"
  accent-strong: "#92400E"
  paper: "#FAF9F6"
  surface: "#FFFFFF"
  ink: "#1C1917"
  ink-soft: "#57534E"
  border: "#E7E5E4"
  success: "#15803D"
  success-soft: "#DCFCE7"
  success-strong: "#166534"
  error: "#B91C1C"
  error-soft: "#FEE2E2"
  error-strong: "#991B1B"
typography:
  display:
    fontFamily: 'Georgia, "Times New Roman", serif'
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.2
  headline-lg:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 26px
    fontWeight: 600
    lineHeight: 1.25
  headline-md:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 20px
    fontWeight: 600
    lineHeight: 1.3
  headline-sm:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 17px
    fontWeight: 600
    lineHeight: 1.35
  body-lg:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.55
  body-sm:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
  label-lg:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.2
  label-md:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 12px
    fontWeight: 600
    lineHeight: 1.25
  label-sm:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1.25
  mono-md:
    fontFamily: 'ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace'
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.4
rounded:
  sm: 6px
  md: 10px
  lg: 16px
  full: 999px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  2xl: 32px
  3xl: 48px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    typography: "{typography.label-lg}"
    padding: 12px 20px
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-primary-active:
    backgroundColor: "{colors.primary-active}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    typography: "{typography.label-lg}"
    padding: 12px 20px
  button-danger:
    backgroundColor: "{colors.error}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    typography: "{typography.label-lg}"
    padding: 12px 20px
  button-ghost:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.md}"
    typography: "{typography.label-lg}"
    padding: 12px 20px
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    typography: "{typography.body-md}"
    padding: 10px 12px
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    typography: "{typography.body-md}"
    padding: 24px
  badge-entrada:
    backgroundColor: "{colors.success}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.full}"
    typography: "{typography.label-sm}"
    padding: 2px 10px
  badge-saida:
    backgroundColor: "{colors.error}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.full}"
    typography: "{typography.label-sm}"
    padding: 2px 10px
  badge-critico:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.full}"
    typography: "{typography.label-sm}"
    padding: 2px 10px
  alert-error:
    backgroundColor: "{colors.error-soft}"
    textColor: "{colors.error-strong}"
    rounded: "{rounded.sm}"
    typography: "{typography.body-sm}"
    padding: 12px 16px
  alert-success:
    backgroundColor: "{colors.success-soft}"
    textColor: "{colors.success-strong}"
    rounded: "{rounded.sm}"
    typography: "{typography.body-sm}"
    padding: 12px 16px
  alert-critico:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.accent-strong}"
    rounded: "{rounded.sm}"
    typography: "{typography.body-sm}"
    padding: 12px 16px
  divider:
    backgroundColor: "{colors.border}"
    height: 1px
  nav:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    typography: "{typography.body-md}"
    padding: 12px 24px
---

# Painel de Estoque — 愚公移山 Variedades

Sistema visual do front-end FastHTML que consome a API de Gerenciamento de
Estoque. Implementação: **Pico CSS** (vem embutido no FastHTML, sem build) com os
tokens abaixo mapeados para custom properties em `frontend/static/css/app.css`.
Tema **claro fixo** (`data-theme="light"` no shell): uma única tabela de contraste
para auditar; dark mode fica registrado como evolução futura.

## Overview

O painel é uma ferramenta de trabalho: o gestor e o funcionário passam o dia
cadastrando, conferindo saldo e registrando movimentações. Por isso a linguagem
visual é **calma e funcional** — leitura rápida de tabelas, ações inequívocas e
feedback imediato — com um toque de identidade: o jade do chá e o âmbar da
especiaria remetem ao nome da loja e ao seu catálogo.

Público: uma pessoa por vez, em desktop ou celular, muitas vezes em pé no balcão.
Densidade média, sem decoração que atrapalhe a leitura.

## Colors

O jade é a **única** cor de ação (botões primários, links, foco); o âmbar é
reservado para criticidade de estoque; vermelho e verde são exclusivamente
semânticos (saída/erro e entrada/sucesso). Nenhuma cor decorativa entra em cena.

- **Primary / jade (#0F766E):** ação principal, links e anel de foco.
- **Primary Hover/Active (#115E59 · #134E4A):** estados do botão primário.
- **Accent / âmbar-chá (#B45309):** criticidade — badge preenchido e `alert-critico`;
  o texto do alerta usa `accent-strong` (#92400E) sobre `accent-soft` (#FEF3C7),
  6,4:1.
- **Paper (#FAF9F6) e Surface (#FFFFFF):** fundo quente da página e cartões; o
  contraste tinta/papel passa de 15:1.
- **Ink (#1C1917) e Ink Soft (#57534E):** texto principal e metadados; o
  secundário mantém ~7:1 sobre branco.
- **Border (#E7E5E4):** separação de cartões e campos (`divider`).
- **Success / Error:** badges preenchidos (verde/vermelho com texto branco, acima
  de 5:1) e pares suaves para alertas (6,5:1 e 6,8:1).

## Typography

Pilha 100% de sistema — nada de webfont, nada de FOUT nem dependência de rede.

- **Display (Georgia/serif):** apenas o wordmark "愚公移山 Variedades" e os H1 de
  página; dá o tom de tradição da loja.
- **Sans (system-ui):** toda a interface.
- **Mono:** SKU, CNPJ, telefone, datas, quantidades e preços — dados que se
  confere dígito a dígito.
- Escala: 32/26/20/17/16/15/13 px com pesos 400/500/600/700. Nunca mais de dois
  pesos na mesma tela.

## Layout

- Conteúdo em coluna única com largura máxima de **1120px** e 24px de respiro
  lateral; nada de horizontal scroll em nenhuma viewport.
- Escala de espaçamento de 4px (`xs`–`3xl`); cartões com `xl` de padding interno.
- Filtros e formulários em **grade fluida** (`auto-fit`, mínimo 200px); em telas
  estreitas empilham em uma coluna, com labels acima dos campos.
- Listas usam "carregar mais" (a API não expõe contagem total): o botão fica ao
  fim da lista e refaz a consulta com +20 itens (`limit`), preservando os filtros;
  a lista cresce no lugar e para no teto de 100 da API.
- Tabelas/listas densas viram **cartões empilhados** abaixo de 720px, com o
  par rótulo/valor em linha; acima disso, grade em colunas.

## Elevation & Depth

Profundidade **tonal**, não dramática: o papel quente é o fundo, os cartões são
brancos com borda de 1px e uma sombra discreta
(`0 1px 2px rgba(28, 25, 23, .06)`). O painel não usa blur, vidro ou sombra
pesada; o que importa é a hierarquia de leitura, não o efeito.

## Shapes

Cantos suaves e consistentes: `sm` 6px em campos, `md` 10px em botões,
`lg` 16px em cartões, `full` em badges. Nada de misturar cantos retos com
arredondados na mesma tela; ícones são de traço, nunca preenchidos.

## Components

- **Botões:** primário preenchido (jade), secundário com borda, ghost para ações
  neutras (Sair), danger para excluir. Foco sempre visível: anel de 2px jade com
  2px de afastamento, inclusive no modo teclado.
- **Campos:** label acima, borda 1px, `body-md`; erro de validação 422 vira texto
  por campo (a partir de `loc`/`msg` do envelope) e o `detail` de 409/400 ocupa
  um `alert-error` no topo do formulário. Nunca há sucesso silencioso.
- **Listas:** cada item é um `row`; ações de escrita à direita. Para leitor, os
  controles de escrita **não existem** (não são desabilitados). Listas têm três
  estados explícitos: vazia (`empty-state`), carregando (`hx-indicator`, texto
  "Carregando…") e erro (`alert-error` com o `detail` da API).
- **Badges:** `entrada` (verde), `saida` (vermelha), `critico` (âmbar) —
  preenchidos, com texto branco, e sempre com a palavra, nunca só cor.
- **Navegação:** barra no topo com o wordmark, os cinco destinos e a conta;
  quebra em duas linhas quando falta largura, sem hambúrguer.
- **Feedback pós-mutação:** sucesso com `alert-success` curto e a lista
  recarregada; após registrar movimentação, o saldo exibido do produto é
  atualizado junto (swap OOB) — saldo velho é bug, não atraso.

## Do's and Don'ts

- **Do** usar jade em no máximo uma ação principal por bloco.
- **Do** mostrar a mensagem `detail` da API palavra por palavra — o usuário vê
  exatamente a razão da recusa.
- **Don't** esconder erro atrás de toast que some; alerta fica no fluxo, junto do
  que falhou.
- **Don't** usar cor como único sinal de estado (badges sempre com texto).
- **Don't** introduzir cantos retos, webfonts ou sombras fortes — fidelidade ao
  contrato importa mais que novidade visual.
