# -*- coding: utf-8 -*-
"""
learnings.py — ledger de aprendizado por projeto (Pilar D do AI-SDLC).

north "aprende" enquanto você desenvolve — sem ML. É memória estruturada por
projeto: decisões, bugs+fix recorrentes, padrões e pegadinhas (gotchas), capturados
com triagem (o wrap-up propõe, você confirma; /north-note pode rotear) e DEVOLVIDOS
no bom-dia/foco pra não repetir erro.

Read-only sobre os planos/código do usuário; escreve só em
`~/.north/learnings/ledger/<project>.jsonl`. Stdlib: JSONL + filtro simples.

Memória BOUNDED (padrão Hermes — "teto + curadoria"): ao salvar, deduplica
near-duplicates (mesmo tipo + texto muito parecido), reaproveita o que volta
(refresca data + recência em vez de duplicar), e mantém um teto por projeto
(LEDGER_CAP) evictando os mais antigos — pra a memória não inchar e apodrecer.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from . import style as S

KINDS = {
    "decisao": "📌 decisão", "decisão": "📌 decisão",
    "bug": "🐛 bug/fix", "fix": "🐛 bug/fix",
    "padrao": "🧩 padrão", "padrão": "🧩 padrão",
    "gotcha": "⚠ pegadinha", "pegadinha": "⚠ pegadinha",
}
_CANON = {"decisao": "decisao", "decisão": "decisao", "bug": "bug", "fix": "bug",
          "padrao": "padrao", "padrão": "padrao", "gotcha": "gotcha", "pegadinha": "gotcha"}
_LABEL = {"decisao": "📌 decisão", "bug": "🐛 bug/fix", "padrao": "🧩 padrão", "gotcha": "⚠ pegadinha"}

# Teto por projeto (curadoria estilo Hermes): acima disso, os mais antigos saem.
LEDGER_CAP = 200
# Similaridade (Jaccard de tokens) a partir da qual dois aprendizados do mesmo
# tipo são tratados como o MESMO (near-duplicate).
_DUP_SIM = 0.85


def _safe(name):
    return re.sub(r"[^A-Za-z0-9_.+-]", "-", (name or "geral")) or "geral"


def _ledger_path(home: Path, project: str) -> Path:
    d = home / "learnings" / "ledger"
    d.mkdir(parents=True, exist_ok=True)
    return d / (_safe(project) + ".jsonl")


def _today():
    return datetime.now().strftime("%Y-%m-%d")


def _norm(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _tokens(text):
    return set(re.findall(r"[a-zà-ú0-9]{3,}", _norm(text)))


def _is_dup(a, b):
    """True se a e b são o MESMO aprendizado (mesmo tipo + texto igual ou muito
    parecido). Jaccard de tokens >= _DUP_SIM."""
    if a.get("kind") != b.get("kind"):
        return False
    na, nb = _norm(a.get("text")), _norm(b.get("text"))
    if not na or not nb:
        return False
    if na == nb:
        return True
    ta, tb = _tokens(na), _tokens(nb)
    if not ta or not tb:
        return False
    return (len(ta & tb) / len(ta | tb)) >= _DUP_SIM


def _write_all(home: Path, project: str, items):
    p = _ledger_path(home, project)
    body = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in items)
    p.write_text(body, encoding="utf-8")


def add(home: Path, project: str, kind: str, text: str, source="manual",
        dedup=True, cap=LEDGER_CAP):
    """Salva um aprendizado — BOUNDED. Deduplica (reaproveita o que volta,
    refrescando data + recência), e mantém o teto `cap` evictando os mais antigos.
    Devolve a entry salva; em duplicata, devolve a existente com `_dup=True`
    (nada foi adicionado, só refrescado)."""
    k = _CANON.get((kind or "").strip().lower(), "decisao")
    entry = {"date": _today(), "kind": k, "text": (text or "").strip(), "source": source}
    if not entry["text"]:
        return None
    items = load(home, project)
    if dedup:
        for i, e in enumerate(items):
            if _is_dup(entry, e):
                # reaproveita: move pro fim (mais recente) e refresca a data
                items.pop(i)
                refreshed = dict(e, date=_today())
                items.append(refreshed)
                if cap and len(items) > cap:
                    items = items[-cap:]
                _write_all(home, project, items)
                return dict(refreshed, _dup=True)
    items.append(entry)
    if cap and len(items) > cap:
        items = items[-cap:]
    _write_all(home, project, items)
    return entry


def prune(home: Path, project: str, cap=LEDGER_CAP):
    """Cura um ledger já existente: deduplica (mantém a ocorrência mais recente)
    e aplica o teto. Devolve (antes, depois)."""
    items = load(home, project)
    before = len(items)
    kept = []
    for e in items:
        # remove duplicata anterior (mantém a mais recente = esta)
        kept = [k for k in kept if not _is_dup(e, k)]
        kept.append(e)
    if cap and len(kept) > cap:
        kept = kept[-cap:]
    _write_all(home, project, kept)
    return before, len(kept)


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
       | prune <project>   ·   kinds: decisao | bug | padrao | gotcha.
       add é BOUNDED: deduplica + refresca o que volta + mantém o teto (LEDGER_CAP)."""
    sub = (args[0].lower() if args else "list")
    if sub == "add":
        if len(args) < 4:
            print("uso: learnings add <project> <decisao|bug|padrao|gotcha> <texto>")
            return 1
        e = add(home, args[1], args[2], " ".join(args[3:]), source="manual")
        if not e:
            print("nada a salvar (texto vazio).")
            return 1
        if e.get("_dup"):
            print("já conhecido em {} (não dupliquei; refresquei): {}".format(args[1], _fmt(e)))
            return 0
        print("aprendizado salvo em {}: {}".format(args[1], _fmt(e)))
        return 0
    if sub == "prune":
        if len(args) < 2:
            print("uso: learnings prune <project>")
            return 1
        before, after = prune(home, args[1])
        print("curado {}: {} -> {} registro(s) ({} removido[s]).".format(
            args[1], before, after, before - after))
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
    print(S.header("aprendizados", "{} · {} registro(s)".format(args[1], len(items))))
    print("")
    for e in items[:30]:
        print("  • " + _fmt(e))
    return 0
