---
name: north-insight
description: north — Insights passivos (teach-on-write). Enquanto a IA CODA, ela te ensina por cima — micro-aulas curtas do que usou: conceitos de linguagem (LINQ, nullable, async…) E as bibliotecas/frameworks/ferramentas (MediatR, Gotenberg, Chakra UI, EF Core, React Query…) — o que é, pra que serve, como funciona, quando usar. Nunca repete o já ensinado (cooldown), ranqueando o mais difícil/importante. Ative para "/north-insight", "me ensina enquanto coda", "insights do código", "explica o que você usou", "que lib é essa".
allowed-tools: Bash, Read, Grep, Glob, WebSearch, WebFetch
argument-hint: "[on|off|status]"
---

# /north-insight — Insights passivos (teach-on-write)

Diferente do `/north-learn` (lá **você** coda e a IA orienta): aqui **a IA coda e te
ensina por cima** o que usou. O objetivo é você absorver conceitos no fluxo real do
seu código, **sem repetição** e focado no que importa. Vale para o resto da sessão,
até dizer "desliga os insights".

`on` (default ao ativar) liga o comportamento na sessão · `off` desliga · `status`
mostra o ledger (`north insight log <lang>`).

## O motor é a MEMÓRIA; VOCÊ (IA) é a inteligência
O north **não** detecta conceitos — quem identifica e ranqueia é você, que escreveu o
código. O north guarda o que já foi ensinado e diz o que está **devido** (novo, ou
cooldown vencido), para você **nunca repetir** dentro do período.

## O loop (após CADA bloco de código que você escrever na sessão)
1. **Liste o que você usou** naquele trecho — DOIS eixos:
   - **Conceitos de linguagem** (ex.: `nullable operators`, `LINQ`, `pattern matching`,
     `async/await`). Catálogo: `references/concepts/<lang>.md`.
   - **Bibliotecas / frameworks / ferramentas** (ex.: `MediatR`, `Gotenberg`, `EF Core`,
     `Chakra UI`, `React Query`) — tudo que veio de um `import`/`using`/dependência de
     pacote e **não é** linguagem pura. Catálogo: `references/concepts/<ecossistema>-libs.md`.
2. **Pergunte ao north o que está devido + ranqueado**, **separando por namespace** (o
   ledger é por namespace, então conceitos e libs não se misturam nem se repetem):

   ```bash
   # conceitos de linguagem -> namespace = a linguagem
   python3 ~/.north/run.py insight check <lang> "conceito1, conceito2"
   # libs/frameworks/tools -> namespace = o ecossistema (dotnet-libs | js-libs)
   python3 ~/.north/run.py insight check dotnet-libs "MediatR, Gotenberg"
   # Windows: python "%USERPROFILE%\.north\run.py" insight check <ns> "..."
   ```

   Mapa de namespace de libs: **.NET/C# → `dotnet-libs`** · **JS/TS/React → `js-libs`**.
   O north devolve só os **devidos** (novos ou com cooldown vencido), **ranqueados por
   dificuldade** (sr > pl > jr). Se vier "nada a ensinar", **não ensine** — siga o trabalho.
3. **Ensine o TOPO** (1 por mudança por padrão — `insight_max_per_change`): uma micro-aula
   de 2–4 linhas — **o que é, por que você usou ali, o trade-off**. **Ancore primeiro na
   biblioteca local** (`python3 ~/.north/run.py library find "<conceito>"`) e cite a
   referência se houver; senão use doc oficial (microsoft-docs p/ .NET; ou WebSearch e cite).
   Use o formato:

   > 💡 **Insight — `<conceito>` (`<dificuldade>`)**: <explicação curta e prática, no contexto do que você acabou de escrever>.

4. **Registre** o que ensinou (para não repetir) — **no mesmo namespace** do `check`
   (a linguagem para conceito; `dotnet-libs`/`js-libs` para lib):

   ```bash
   python3 ~/.north/run.py insight record <lang|libs-ns> "<conceito ou lib>"
   ```

## Ensinando uma biblioteca/framework/ferramenta
Quando o item devido é uma **lib** (não conceito de linguagem), a micro-aula tem uma forma
própria — porque a dor do dev é "apareceu `MediatR`/`Gotenberg`/`Chakra UI` no código e eu
não sei o que é". Cubra, em 2–4 linhas:
- **O que é** (em 1 frase) e **o problema que resolve** (por que existe).
- **Como funciona** (o modelo mental — ex.: MediatR = despacha um `IRequest` para 1 handler
  via um mediador, desacoplando quem chama de quem executa).
- **Quando usar / quando NÃO** + a **alternativa** óbvia (ex.: MediatR vs. chamar o serviço
  direto; Gotenberg vs. QuestPDF/Puppeteer).

**Ancore em doc oficial — não invente API:** para libs, prefira nesta ordem
(1) `north library find "<lib>"`, (2) **context7** (`resolve-library-id` → `query-docs`),
(3) **microsoft-docs** para .NET, (4) WebSearch citando a fonte. Se não achar, diga que não
sabe — nunca fabrique método/assinatura. Formato:

> 💡 **Insight — `<lib>` (`<dificuldade>`)**: <o que é + problema que resolve + modelo mental + quando usar>, no contexto do que você acabou de escrever.

## Regras de ouro
- **Nunca repita** um conceito já ensinado dentro do cooldown — o `check` já filtra isso.
  Só reensina quando o north marcar como devido (tempo passou) **e** o conceito reaparecer.
- **Foque no mais difícil/importante** do trecho (o `check` já ranqueia) — não ensine o trivial.
- **Conceito novo ou diferente apareceu?** Ensina por cima (o `check` traz como "novo").
- **Curto.** Insight não é aula longa; é um empurrão no contexto. Não interrompa demais:
  no máximo 1 por bloco (ajuste com `north config set insight_max_per_change N`).
- **Calibre por nível** com `--min`: `north insight check <lang> "..." --min pleno` não
  ensina abaixo de pleno (respeite `insight_min_level` se configurado).

## Saída
"desliga os insights" / "para de me ensinar": volte ao normal (não rode mais o loop).
