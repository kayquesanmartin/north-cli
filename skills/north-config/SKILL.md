---
name: north-config
description: north — Ajusta a configuração sem reinstalar: pastas varridas (scan_roots), preferências (tema, limite de WIP, abrir browser) e ajustes por projeto (ligar/desligar, apelido, fonte primária). Ative para "/north-config", "configurar o north", "adicionar pasta de projetos", "desligar um projeto", "mudar o tema", "mudar o limite de WIP".
allowed-tools: Bash
argument-hint: "[show | add-root <pasta> | set <chave> <valor> | project <id> <enable|disable|...>]"
---

# /north-config — Configuração do north

CRUD leve da config (`projects.json`) — **não reinstala** nada.

1. Por padrão, mostre o estado atual:

   ```bash
   python3 ~/.north/run.py config show
   # Windows: python "$env:USERPROFILE\.north\run.py" config show
   ```

2. Subcomandos disponíveis:
   - `add-root "<pasta>"` / `remove-root "<pasta>"` — pastas que o north varre.
   - `set <chave> <valor>` — ex.: `set theme light`, `set wip_limit 4`, `set open_browser false`.
   - `project <id> <enable|disable|alias "<v>"|source <v>|order <n>|clear-source>`.

   ```bash
   python3 ~/.north/run.py config add-root "/caminho/dos/projetos"
   ```

   (Instalou via npm? `north config ...` funciona em qualquer SO.)

3. Pergunte o que o usuário quer ajustar, rode o subcomando certo e confirme a
   mudança. Mudanças valem na próxima execução de qualquer comando (sem reinstalar).
