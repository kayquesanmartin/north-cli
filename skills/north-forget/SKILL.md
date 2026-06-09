---
name: north-forget
description: north — Des-pluga um projeto do tracking (modo enrolled). O inverso do /north-init. Read-only: só remove o caminho da lista em ~/.north. Ative para "/north-forget", "parar de rastrear este projeto", "remover projeto do north", "north untrack".
allowed-tools: Bash
argument-hint: "<projeto|caminho>"
---

# /north-forget — Parar de rastrear um projeto

Remove um projeto da lista de plugados (modo enrolled). Inverso do `/north-init`.
Read-only: só tira o caminho de `~/.north` — nada no projeto é tocado.

```bash
python3 ~/.north/run.py forget "<projeto|caminho>"
# Windows: python "$env:USERPROFILE\.north\run.py" forget "<projeto>"
```

- Aceita o **nome do projeto** (basename) ou o **caminho** que foi plugado.
- Veja o que está plugado com `north status`.
