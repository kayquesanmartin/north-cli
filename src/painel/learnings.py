# -*- coding: utf-8 -*-
"""
learnings.py — ledger de aprendizado por projeto (Pilar D do AI-SDLC).

north "aprende" enquanto você desenvolve — sem ML. É memória estruturada por
projeto: decisões, bugs+fix recorrentes, padrões e pegadinhas (gotchas), capturados
com triagem (o wrap-up propõe, você confirma; /north-note pode rotear) e DEVOLVIDOS
no bom-dia/foco pra não repetir erro.

Read-only sobre os planos/código do usuário; escreve só em
`~/.north/learnings/ledger/<project>.jsonl`. Stdlib: JSONL + filtro simples.
"""

import json
import re
from datetime import datetime
from pathlib import Path

KINDS = {
    "decisao": "📌 decisão", "decisão": "📌 decisão",
    "bug": "🐛 bug/fix", "fix": "🐛 bug/fix",
    "padrao": "🧩 padrão", "padrão": "🧩 padrão",
    "gotcha": "⚠ pegadinha", "pegadinha": "⚠ pegadinha",
}
_CANON = {"decisao": "decisao", "decisão": "decisao", "bug": "bug", "fix": "bug",
          "padrao": "padrao", "padrão": "padrao", "gotcha": "gotcha", "pegadinha": "gotcha"}
_LABEL = {"decisao": "📌 decisão", "bug": "🐛 bug/fix", "padrao": "🧩 padrão", "gotcha": "⚠ pegadinha"}


def _safe(name):
    return re.sub(r"[^A-Za-z0-9_.+-]", "-", (name or "geral")) or "geral"


def _ledger_path(home: Path, project: str) -> Path:
    d = home / "learnings" / "ledger"
    d.mkdir(parents=True, exist_ok=True)
    return d / (_safe(project) + ".jsonl")


def _today():
    return datetime.now().strftime("%Y-%m-%d")


def add(home: Path, project: str, kind: str, text: str, source="manual"):
    k = _CANON.get((kind or "").strip().lower(), "decisao")
    entry = {"date": _today(), "kind": k, "text": (text or "").strip(), "source": source}
    if not entry["text"]:
        return None
    with _ledger_path(home, project).open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def load(home: Path, project: str):
    p = _ledger_path(home, project)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def recent(home: Path, project: str, limit=3):
    return list(reversed(load(home, project)))[:limit]


def find(home: Path, project: str, query: str, limit=8):
    q = [w for w in re.findall(r"[a-zà-ú0-9]{2,}", (query or "").lower())]
    items = list(reversed(load(home, project)))
    if not q:
        return items[:limit]
    scored = []
    for e in items:
        text = (e.get("text", "") + " " + e.get("kind", "")).lower()
        score = sum(1 for w in q if w in text)
        if score:
            scored.append((score, e))
    scored.sort(key=lambda x: -x[0])
    return [e for _s, e in scored[:limit]]


def _fmt(e):
    return "[{}] {}: {}".format(e.get("date", ""), _LABEL.get(e.get("kind", ""), e.get("kind", "")),
                                e.get("text", ""))


def cmd_learnings(home: Path, args):
    """CLI: learnings add <project> <kind> <texto> | list <project> | find <project> <q>
       kinds: decisao | bug | padrao | gotcha."""
    sub = (args[0].lower() if args else "list")
    if sub == "add":
        if len(args) < 4:
            print("uso: learnings add <project> <decisao|bug|padrao|gotcha> <texto>")
            return 1
        e = add(home, args[1], args[2], " ".join(args[3:]), source="manual")
        if not e:
            print("nada a salvar (texto vazio).")
            return 1
        print("aprendizado salvo em {}: {}".format(args[1], _fmt(e)))
        return 0
    if sub in ("find", "search"):
        if len(args) < 2:
            print("uso: learnings find <project> <termo>")
            return 1
        res = find(home, args[1], " ".join(args[2:]))
        if not res:
            print("nenhum aprendizado para isso em {}.".format(args[1]))
            return 0
        print("APRENDIZADOS ({}):".format(args[1]))
        for e in res:
            print("  • " + _fmt(e))
        return 0
    # list
    if len(args) < 2:
        print("uso: learnings list <project>")
        return 1
    items = list(reversed(load(home, args[1])))
    if not items:
        print("sem aprendizados em {} ainda. (capture com: learnings add ...)".format(args[1]))
        return 0
    print("📚 Aprendizados — {} ({}):".format(args[1], len(items)))
    for e in items[:30]:
        print("  • " + _fmt(e))
    return 0
