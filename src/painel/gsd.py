# -*- coding: utf-8 -*-
"""
gsd.py — adapter que le projetos GSD (.planning/) para o modelo do north.

O north e a camada de LARGURA (todos os projetos, foco, sinais vitais). O GSD e
a de PROFUNDIDADE (um projeto, ciclo spec->plan->execute->verify). Em vez de
reimplementar o GSD, o north INTEROPERA: le o estado estruturado do GSD e o
renderiza ao lado dos projetos plan-build, no mesmo painel/foco/vitais/statusline.

Mapa de conceitos GSD -> modelo north:
  Phase (ROADMAP.md)         -> sprint     (CONCLUIDA=Done, LIBERADA/em and.=Em Andamento,
                                            BLOQUEADA=Planejado+blocked)
  Plan dentro da phase       -> task       ([x]=Done; primeiro [ ] da phase ativa=Em Andamento)
  STATE.md "Progress: N of M"-> rollup      (nivel sprint)
  STATE.md Blockers/Concerns -> blockers
  HANDOFF.json next_action   -> dica da proxima acao (marca o plano ativo)

Tudo best-effort: campos ausentes degradam com elegancia (o GSD nem sempre
preenche frontmatter/handoff).
"""

import json
import re
from pathlib import Path

from . import parsers as P

STATUS_TO_COL = [
    (re.compile(r"conclu[ií]da|completo|done|archived", re.I), P.COL_DONE, False),
    (re.compile(r"bloquead", re.I), P.COL_PLANEJADO, True),
    (re.compile(r"em andamento|em progresso|executing|in.?progress|wip", re.I),
     P.COL_ANDAMENTO, False),
    (re.compile(r"liberada|ready|liberado|next|planning", re.I), P.COL_ANDAMENTO, False),
]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8") if path.exists() else ""
    except Exception:
        return ""


def discover_planning_dirs(scan_roots, max_depth=6):
    """Acha todas as pastas '.planning' (com STATE.md) sob os scan_roots.

    Poda VCS/deps/caches e os worktrees do Claude Code (`.claude/worktrees`),
    espelhos do mesmo repo que gerariam projetos-fantasma (ver fsutil)."""
    from . import fsutil
    found, seen = [], set()
    for pl in fsutil.find_dirs_named(scan_roots, ".planning", max_depth):
        if not pl.is_dir() or not (pl / "STATE.md").exists():
            continue
        key = str(pl.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        found.append(pl)
    return found


def _phase_col(status_tag):
    for rx, col, blocked in STATUS_TO_COL:
        if rx.search(status_tag or ""):
            return col, blocked
    return P.COL_PLANEJADO, False


def _parse_roadmap(text):
    """Extrai phases (checklist) e plans (NN-MM) do ROADMAP.md."""
    phases = []
    phase_rx = re.compile(
        r"^- \[([ xX])\]\s+\*\*Phase\s+(\d+)\s*:\s*([^*]+?)\*\*\s*-?\s*(.*)$", re.M)
    for m in phase_rx.finditer(text):
        checked, num, title, rest = m.groups()
        tag_m = re.search(r"`([^`]+)`", rest)
        status_tag = tag_m.group(1) if tag_m else ("CONCLUIDA" if checked.lower() == "x" else "")
        col, blocked = _phase_col(status_tag)
        if checked.lower() == "x":
            col, blocked = P.COL_DONE, False
        phases.append({"num": (num.lstrip("0") or "0"), "title": P.clean_desc(title).strip(),
                       "status": status_tag, "col": col, "blocked": blocked})
    # plans: "- [ ] 04-01: desc"  (NN-MM) — phase normalizado p/ casar com a fase
    plans = []
    plan_rx = re.compile(r"^[ \t]*- \[([ xX])\]\s+(\d+)-(\d+):\s*(.+)$", re.M)
    for m in plan_rx.finditer(text):
        checked, pnum, seq, desc = m.groups()
        plans.append({"phase": (pnum.lstrip("0") or "0"),
                      "id": "{}-{}".format(pnum, seq),
                      "desc": P.clean_desc(desc).strip(),
                      "done": checked.lower() == "x"})
    return phases, plans


def _parse_state(text):
    """Extrai foco atual, progresso (done/total/pct) e bloqueios do STATE.md."""
    out = {"focus": "", "done": None, "total": None, "pct": None,
           "blockers": [], "updated": ""}
    fm = re.search(r"\*\*Current focus:\*\*\s*(.+)", text)
    if fm:
        out["focus"] = P.clean_desc(fm.group(1)).strip()
    pm = re.search(r"Phase:\s*(\d+)\s+of\s+(\d+)(?:\s*\(([^)]+)\))?", text)
    if pm and not out["focus"]:
        out["focus"] = "Phase {} ({})".format(pm.group(1), pm.group(3) or "")
    prog = re.search(r"Progress:.*?(\d+)%\s*\((\d+)\s+of\s+(\d+)", text)
    if prog:
        out["pct"], out["done"], out["total"] = (
            int(prog.group(1)), int(prog.group(2)), int(prog.group(3)))
    la = re.search(r"Last activity:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
    if la:
        out["updated"] = la.group(1)
    # bloqueios: bloco "### Blockers/Concerns" ate o proximo header
    blk = re.search(r"###\s*Blockers/Concerns\s*\n(.*?)(?:\n#{2,3}\s|\Z)", text, re.S)
    if blk:
        for line in blk.group(1).splitlines():
            lm = re.match(r"\s*-\s+(.*)", line)
            if not lm:
                continue
            desc = P.clean_desc(lm.group(1)).strip()
            if desc and desc.lower() not in ("none", "none yet.", "nenhum"):
                out["blockers"].append(desc)
    return out


def _parse_handoff(planning_dir):
    """next_action + plano ativo do HANDOFF.json (se houver)."""
    try:
        h = json.loads(_read(planning_dir / "HANDOFF.json"))
    except Exception:
        return {}
    return {"next_action": h.get("next_action", ""),
            "phase": str(h.get("phase", "")).lstrip("0") or h.get("phase", ""),
            "status": h.get("status", "")}


def build_gsd_project(planning_dir: Path, git_info_fn, author_fn):
    """Monta o dict de projeto (formato north) a partir de um .planning/ do GSD.
    git_info_fn/author_fn vem do discovery (evita import circular)."""
    pdir = planning_dir.parent
    roadmap = _read(planning_dir / "ROADMAP.md")
    state = _parse_state(_read(planning_dir / "STATE.md"))
    phases, plans = _parse_roadmap(roadmap)
    handoff = _parse_handoff(planning_dir)

    # ---- sprints = phases ----
    sprints = []
    for i, ph in enumerate(phases):
        n_plans = [p for p in plans if p["phase"] == ph["num"]]
        done = sum(1 for p in n_plans if p["done"])
        total = len(n_plans)
        pct = (100 if ph["col"] == P.COL_DONE
               else (round(done / total * 100) if total else
                     (0 if ph["col"] == P.COL_PLANEJADO else None)))
        sprints.append({
            "key": "P{}".format(ph["num"]), "name": ph["title"],
            "status_raw": ph["status"], "col": ph["col"], "blocked": ph["blocked"],
            "done": done if total else None, "total": total or None,
            "pct": pct, "order": i, "author": None,
        })

    active_phase = next((ph["num"] for ph in phases if ph["col"] == P.COL_ANDAMENTO), None)
    blocked_phases = {ph["num"] for ph in phases if ph["blocked"]}

    # ---- tasks = plans ----
    tasks = []
    bumped = False
    for p in plans:
        blk = p["phase"] in blocked_phases
        col = P.COL_DONE if p["done"] else P.COL_PLANEJADO
        if (not p["done"] and not blk and not bumped and p["phase"] == active_phase):
            col = P.COL_ANDAMENTO   # primeiro plano aberto da fase ativa = proxima acao
            bumped = True
        tasks.append({
            "id": p["id"], "sprint": "P{}".format(p["phase"]),
            "desc": p["desc"], "owner": "", "col": col, "blocked": blk,
            "commit": "", "status_raw": "", "deps": "",
        })

    # ---- bloqueios ----
    blockers = [{"id": "", "desc": d, "impact": "", "status": "", "resolved": False}
                for d in state["blockers"]]

    # ---- rollup (nivel fase, via STATE) ----
    done = state["done"] if state["done"] is not None else sum(
        1 for s in sprints if s["col"] == P.COL_DONE)
    total = state["total"] if state["total"] is not None else (len(sprints) or 1)
    pct = state["pct"] if state["pct"] is not None else (
        round(done / total * 100) if total else 0)

    git = git_info_fn(pdir)
    meta = {"branch_doc": "", "updated": state["updated"], "current_sprint": state["focus"]}

    from .discovery import collect_living_docs  # deferido: evita import circular

    return {
        "id": pdir.name, "path": str(pdir), "plan_dir": str(planning_dir),
        "progress_file": str(planning_dir / "STATE.md"),
        "source": "gsd", "is_template": False, "has_docs": (pdir / "docs").is_dir(),
        "docs": collect_living_docs(pdir),
        "meta": meta, "git": git, "branch": git["branch"] or "",
        "current_sprint": state["focus"],
        "author": author_fn(pdir, planning_dir / "ROADMAP.md"),
        "contributors": [],
        "sprints": sprints, "tasks": tasks, "blockers": blockers, "debt": [],
        "open_blockers": [b for b in blockers if not b["resolved"]], "open_debt": [],
        "rollup": {"done": done, "total": total, "pct": pct, "level": "sprint"},
        "handoff": handoff,
    }
