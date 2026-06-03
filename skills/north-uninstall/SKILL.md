---
name: north-uninstall
description: north — Desinstala o north. Remove as skills/comandos dos runtimes (Claude/Codex/Gemini) e o motor (~/.north), preservando seus dados por padrão. Ative para "/north-uninstall", "desinstalar north", "remover north", "tirar o north".
allowed-tools: Bash
argument-hint: ""
---

# /north-uninstall — Desinstalar o north

Remove o north da máquina. Por padrão **preserva seus dados** (config, inbox,
resumos); só apaga o programa (skills/comandos + motor).

**Passos:**

1. **Pergunte ao usuário** (você é o "menu" — não rode nada ainda):
   - De quais runtimes remover? (todos · Claude · Codex · Gemini)
   - Apagar também os **dados** (config/inbox/resumos)? (padrão: **não**, preserva)

2. Com a resposta, rode o comando **não-interativo** correspondente:

   ```bash
   # remover de todos os runtimes, preservando dados (padrão):
   north uninstall --all --yes
   # apenas um runtime:
   north uninstall --runtimes claude --yes
   # remover tudo, INCLUSIVE os dados (irreversível):
   north uninstall --all --purge --yes
   ```

   (Instalou via npx e o `north` não está no PATH? Use `npx north-cli uninstall ...`.)

3. Mostre o resumo do que foi removido (o comando lista cada item) e confirme.

**Cuidado:** `--purge` é **irreversível** — só use se o usuário pedir explicitamente
para apagar os dados. Sem `--purge`, os dados ficam preservados em `~/.north`.
