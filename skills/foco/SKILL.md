---
name: foco
description: north — Direção do dia. Mostra A próxima ação de maior valor entre todos os projetos (sprint atual > caminho crítico > desbloqueada), respeita o limite de WIP e sugere o squad para atacar. Ative para "/foco", "/agora", "o que faço agora", "qual a próxima", "tô perdido", "por onde começo".
allowed-tools: Bash
argument-hint: ""
---

# /foco — Direção (north)

Tira a fadiga de decisão. Em vez de uma lista, aponta **A próxima ação** que mais
vale a pena fazer agora, considerando todos os projetos ativos.

**Passos:**

1. Rode:

   ```bash
   python "%USERPROFILE%\.claude\painel\run.py" foco
   ```

   (Fallback: `C:\Users\<seu-usuario>\.claude\painel\run.py`.)

2. Mostre a saída completa: a **próxima ação** (task + projeto + sprint), o
   **porquê** (em andamento / sprint atual / desbloqueada), o **squad sugerido**,
   eventuais **alertas de WIP** ("termine antes de começar") e as **alternativas**
   caso ele trave na principal. O script também regenera o painel silenciosamente.

3. **Ofereça acionar o squad sugerido** para começar a task agora (ex.: "quer que
   eu chame o `/squad backend` para a `S_CC4-3`?"). **Não acione sem confirmação.**

4. Se a ação de maior valor estiver **bloqueada**, destaque isso e sugira resolver
   o bloqueio ou pegar a primeira alternativa desbloqueada.

**Princípio:** dar direção, não executar. A decisão de começar é do dev.
