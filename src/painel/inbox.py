# -*- coding: utf-8 -*-
"""
inbox.py — captura rápida ("/btw") + memória de ideias/notas/reuniões.

Coluna "Memória & Comunicação" do north. Uma inbox central append-only guarda
o que o dev capturou no meio do fluxo, para o north RELEMBRAR depois (fim-do-dia
e bom-dia do dia seguinte) — nada se perde.

Armazenamento: <home>/inbox/inbox.jsonl — uma entrada JSON por linha:
  {id, ts, date, text, project, tag, status}   status: open | done | dismissed

Nunca apaga linhas: resolver = reescrever a linha com novo status (historico vivo).
"""

import json
import re
from datetime import datetime
from pathlib import Path


TAGS = ("idea", "meeting", "todo", "question")

_MEETING_RX = re.compile(r"reuni|meeting|daily|call\b|aliny|alinhament|1:1|one ?on ?one", re.I)
_TODO_RX = re.compile(r"\btodo\b|a fazer|fazer depois|lembrar de|preciso (de )?fazer|implementar depois", re.I)


def auto_tag(text: str) -> str:
    t = (text or "").strip()
    if _MEETING_RX.search(t):
        return "meeting"
    if t.endswith("?") or re.match(r"^(será|sera|como|por que|porque|e se)\b", t, re.I):
        return "question"
    if _TODO_RX.search(t):
        return "todo"
    return "idea"


def _inbox_file(home: Path) -> Path:
    return home / "inbox" / "inbox.jsonl"


def _read_all(home: Path):
    f = _inbox_file(home)
    if not f.exists():
        return []
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _write_all(home: Path, entries):
    f = _inbox_file(home)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n",
                 encoding="utf-8")


def _next_id(entries) -> str:
    mx = 0
    for e in entries:
        m = re.match(r"BTW-(\d+)", e.get("id", ""))
        if m:
            mx = max(mx, int(m.group(1)))
    return "BTW-{:04d}".format(mx + 1)


def add(home: Path, text: str, project: str = "", tag: str = "", now: datetime = None):
    """Adiciona uma captura. Devolve a entrada criada."""
    now = now or datetime.now()
    entries = _read_all(home)
    entry = {
        "id": _next_id(entries),
        "ts": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "text": (text or "").strip(),
        "project": project or "",
        "tag": tag or auto_tag(text),
        "status": "open",
    }
    entries.append(entry)
    _write_all(home, entries)
    return entry


def open_items(home: Path):
    return [e for e in _read_all(home) if e.get("status", "open") == "open"]


def resolve(home: Path, item_id: str, status: str) -> bool:
    """Marca um item como done|dismissed. Aceita id completo (BTW-0003) ou numero (3)."""
    entries = _read_all(home)
    target = item_id.strip().upper()
    if target.isdigit():
        target = "BTW-{:04d}".format(int(target))
    found = False
    for e in entries:
        if e.get("id", "").upper() == target:
            e["status"] = status
            found = True
            break
    if found:
        _write_all(home, entries)
    return found


def age_days(entry, now: datetime = None) -> int:
    now = now or datetime.now()
    try:
        d = datetime.strptime(entry.get("date", ""), "%Y-%m-%d")
        return (now.date() - d.date()).days
    except Exception:
        return 0


TAG_EMOJI = {"idea": "💡", "meeting": "🗣️", "todo": "✅", "question": "❓"}


def format_list(items, now: datetime = None):
    """Linhas legiveis para terminal (bom-dia / fim-do-dia / inbox)."""
    now = now or datetime.now()
    L = []
    for e in items:
        age = age_days(e, now)
        when = "hoje" if age == 0 else ("ontem" if age == 1 else "{}d atrás".format(age))
        emoji = TAG_EMOJI.get(e.get("tag", "idea"), "•")
        proj = " ({})".format(e["project"]) if e.get("project") else ""
        L.append("    {} [{}] {}{}  · {}".format(
            emoji, e["id"], e["text"][:80], proj, when))
    return "\n".join(L)
