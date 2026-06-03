---
name: north-status
description: north — Mostra o que está instalado, as pastas varridas (scan_roots) e os projetos rastreados. Ative para "/north-status", "north status", "o que o north está vendo", "quais projetos rastreados", "o que está configurado".
allowed-tools: Bash
argument-hint: ""
---

# /north-status — Estado do north

Visão rápida do que o north enxerga: motor instalado, scan_roots e projetos rastreados.

1. Rode:

   ```bash
   # macOS / Linux
   python3 ~/.north/run.py status
   # Windows (PowerShell)
   python "$env:USERPROFILE\.north\run.py" status
   ```

   (Instalou via npm? `north status` funciona em qualquer SO.)

2. Apresente a saída formatada. Se não houver scan_roots ou projetos, oriente o
   usuário a adicionar uma pasta com `/north-config add-root "<pasta>"`.

Comando de leitura — não altera nada.
