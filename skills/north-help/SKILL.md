---
name: north-help
description: north — Guia da ferramenta. Explica TUDO que o north oferece (foco, rituais, painel, captura, mentor, insights, config) e ensina a usar — no terminal e dentro da IA. Ative para "/north-help", "north help", "o que o north faz", "como uso o north", "ajuda do north", "quais comandos do north", "me explica a ferramenta".
allowed-tools: Bash
argument-hint: "[comando opcional para detalhar]"
---

# /north-help — Guia do north

Apresente, de forma clara e didática, **tudo que o north oferece e como usar**.

## Passos

1. Rode o guia do motor (fonte única dos comandos):

   ```bash
   # macOS / Linux
   python3 ~/.north/run.py help
   # Windows (PowerShell)
   python "$env:USERPROFILE\.north\run.py" help
   ```

   (Instalou via npm / habilitou o PATH? `north help` funciona em qualquer SO.)

2. **Mostre a saída** e complemente em linguagem natural, agrupando por intenção:
   - **"Por onde começo?"** → `morning` (foco do dia + painel) e `focus` (a próxima ação).
   - **"Quero acompanhar os projetos"** → `panel` (dashboard), `status`.
   - **"Tive uma ideia no meio do trabalho"** → `note`, depois `inbox` pra triar.
   - **"Quero aprender, não só copiar"** → trilhas mentor: `learn`, `review`, `test`,
     `codebase`, `standup` (a IA orienta, **você** implementa).
   - **"Me ensina enquanto você coda"** → `insight` (a IA ensina por cima o que usou,
     sem repetir, focando no mais difícil).
   - **"Configurar / sistema"** → `config`, `status`, `uninstall`.

3. **Ensine os dois caminhos** (são equivalentes): no **terminal** `north <cmd>`; **dentro
   da IA** `/north-<cmd>` (no Gemini, `/north:<cmd>`). Diga que o terminal é opcional e
   exige ter habilitado o PATH na instalação (`python install.py --add-to-path`).

4. **Se o usuário citou um comando específico** (argumento), foque nele: o que faz, quando
   usar, 1 exemplo real, e o que costuma vir antes/depois no fluxo.

5. Reforce o princípio: **north é READ-ONLY sobre os planos** — só lê e orienta, nunca
   edita seus arquivos de projeto. Termine sugerindo **um** próximo passo concreto pro
   contexto do usuário (ex.: "rode `/north-morning` pra ver seu foco de hoje").

## Regras
- Seja conciso e prático; não despeje a doc inteira — guie pela intenção do usuário.
- Não invente comandos: use os que aparecem na saída do `run.py help`.
- Não execute outras ações além de mostrar o guia e explicar.
