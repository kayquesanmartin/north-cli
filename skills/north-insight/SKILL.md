---
name: north-insight
description: north — Insights passivos (teach-on-write). Enquanto a IA CODA, ela te ensina por cima — micro-aulas curtas do que usou (nullable operators, LINQ, if/else…), nunca repetindo o que já ensinou (só após um tempo e se reusado), ranqueando o conceito mais difícil/importante. Ative para "/north-insight", "me ensina enquanto coda", "insights do código", "explica o que você usou".
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
1. **Liste os conceitos** que você usou naquele trecho (ex.: `nullable operators`,
   `LINQ`, `pattern matching`, `async/await`, `if/else`, `arrays`). Use os nomes do
   catálogo quando possível (`references/concepts/<lang>.md`).
2. **Pergunte ao north o que está devido + ranqueado** (passe a linguagem do código):

   ```bash
   python3 ~/.north/run.py insight check <lang> "conceito1, conceito2, conceito3"
   # Windows: python "%USERPROFILE%\.north\run.py" insight check <lang> "..."
   ```

   O north devolve só os **devidos** (novos ou com cooldown vencido), **ranqueados por
   dificuldade** (sr > pl > jr). Se vier "nada a ensinar", **não ensine** — siga o trabalho.
3. **Ensine o TOPO** (1 por mudança por padrão — `insight_max_per_change`): uma micro-aula
   de 2–4 linhas — **o que é, por que você usou ali, o trade-off**. Ancore em doc oficial
   quando útil (plugin microsoft-docs p/ .NET; senão WebSearch e cite). Use o formato:

   > 💡 **Insight — `<conceito>` (`<dificuldade>`)**: <explicação curta e prática, no contexto do que você acabou de escrever>.

4. **Registre** o que ensinou (para não repetir):

   ```bash
   python3 ~/.north/run.py insight record <lang> "<conceito>"
   ```

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
