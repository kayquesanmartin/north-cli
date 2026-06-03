# -*- coding: utf-8 -*-
"""
discovery.py — auto-descoberta de projetos + montagem do modelo.

Um "projeto" = um diretorio que contem uma pasta `plan-build` (direta ou em
`docs/plan-build`) com pelo menos um Progress*.md e/ou Sprint*.md.

Para cada projeto, le os .md, normaliza via parsers e monta um dict completo
com sprints, tasks, bloqueios, debito, metadados e rollup de progresso.
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path

from . import parsers as P
from . import health as H
from . import gsd as G


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8") if path.exists() else ""
    except Exception:
        return ""


# ----------------------------------------------------------------------------
# Descoberta de diretorios de projeto
# ----------------------------------------------------------------------------
def discover_plan_dirs(scan_roots, max_depth=6):
    """Acha todas as pastas 'plan-build' sob os scan_roots (profundidade limitada)."""
    found = []
    seen = set()
    for root in scan_roots:
        root = Path(root)
        if not root.exists():
            continue
        for pb in root.rglob("plan-build"):
            if not pb.is_dir():
                continue
            try:
                rel_depth = len(pb.relative_to(root).parts)
            except ValueError:
                rel_depth = 0
            if rel_depth > max_depth:
                continue
            key = str(pb.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            found.append(pb)
    return found


def project_dir_for(plan_build: Path) -> Path:
    """Diretorio raiz do projeto a partir do plan-build.
    Se plan-build estiver dentro de 'docs', sobe mais um nivel."""
    parent = plan_build.parent
    if parent.name.lower() == "docs":
        return parent.parent
    return parent


def project_id_for(plan_build: Path, scan_roots) -> str:
    """Id estavel e legivel do projeto (nome do diretorio raiz)."""
    pdir = project_dir_for(plan_build)
    return pdir.name


def pick_progress_file(plan_build: Path) -> Path:
    """Escolhe o Progress principal: ignora 'Archive', prefere 'Progress.md'."""
    candidates = sorted(plan_build.glob("[Pp]rogress*.md"))
    candidates = [c for c in candidates if "archive" not in c.name.lower()]
    if not candidates:
        return None
    # prefere exatamente Progress*.md mais curto (menos sufixo)
    candidates.sort(key=lambda c: (len(c.name), c.name.lower()))
    return candidates[0]


# ----------------------------------------------------------------------------
# Git
# ----------------------------------------------------------------------------
def _git(args, cwd: Path):
    try:
        out = subprocess.run(
            ["git", "-C", str(cwd)] + args,
            capture_output=True, text=True, timeout=15,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return ""


def _gh_login():
    """Login do GitHub via gh CLI (se instalado/autenticado)."""
    try:
        out = subprocess.run(["gh", "api", "user", "--jq", ".login"],
                             capture_output=True, text=True, timeout=8)
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return ""


def current_identity(sample_dir: Path = None):
    """Identidade do dev nesta maquina: @github (gh) + nome/email do git."""
    cwd = sample_dir or Path.cwd()
    return {
        "github": _gh_login(),
        "name": _git(["config", "user.name"], cwd),
        "email": _git(["config", "user.email"], cwd),
    }


def file_author(cwd: Path, path):
    """Quem tocou por ultimo no arquivo (autoria auditavel via git log)."""
    out = _git(["log", "-1", "--format=%an%x1f%ae%x1f%cr", "--", str(path)], cwd)
    if not out:
        return None
    parts = out.split("\x1f")
    if len(parts) >= 3:
        return {"name": parts[0], "email": parts[1], "when": parts[2]}
    return None


def contributors(cwd: Path, plan_build: Path, limit=6):
    """Contribuidores do diretorio de planos, por nº de commits (desc)."""
    out = _git(["log", "--format=%an", "--", str(plan_build)], cwd)
    if not out:
        return []
    from collections import Counter
    c = Counter(l.strip() for l in out.splitlines() if l.strip())
    return [{"name": n, "count": k} for n, k in c.most_common(limit)]


def _git_sync(cwd: Path, branch: str):
    """Estado de sincronia (refs LOCAIS, sem fetch): ahead/behind do upstream e
    quanto a branch-base (origin/HEAD) avancou. Tudo degrada p/ 0/None offline."""
    s = {"upstream": None, "ahead": 0, "behind": 0, "base": None, "base_behind": 0}
    up = _git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd)
    if up and "{u}" not in up:
        s["upstream"] = up
        lr = _git(["rev-list", "--left-right", "--count", "@{u}...HEAD"], cwd)
        parts = lr.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            s["behind"], s["ahead"] = int(parts[0]), int(parts[1])
    base = _git(["rev-parse", "--abbrev-ref", "origin/HEAD"], cwd)  # ex.: origin/main
    if not (base and "/" in base):
        for cand in ("origin/main", "origin/master", "origin/dev", "origin/develop"):
            if _git(["rev-parse", "--verify", "--quiet", cand], cwd):
                base = cand
                break
    if base and "/" in base:
        s["base"] = base
        if base.rsplit("/", 1)[-1] != branch:
            bb = _git(["rev-list", "--count", "HEAD.." + base], cwd)
            if bb.isdigit():
                s["base_behind"] = int(bb)
    return s


def git_info(project_dir: Path):
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], project_dir)
    dirty = 0
    st = _git(["status", "--short"], project_dir)
    if st:
        dirty = len([l for l in st.splitlines() if l.strip()])
    commits = []
    log = _git(["log", "--since=midnight", "--pretty=format:%h\t%s"], project_dir)
    if log:
        for line in log.splitlines():
            if "\t" in line:
                h, s = line.split("\t", 1)
                commits.append((h.strip(), s.strip()))
    # idade do ultimo commit (dias) -> base do alerta "branch parada".
    # None quando nao ha commits/historico (projeto sem git ou recem-criado).
    idle_days = None
    ct = _git(["log", "-1", "--format=%ct"], project_dir)
    if ct.isdigit():
        idle_days = int((datetime.now().timestamp() - int(ct)) // 86400)
    return {"branch": branch, "dirty": dirty, "today_commits": commits,
            "idle_days": idle_days, "sync": _git_sync(project_dir, branch)}


# ----------------------------------------------------------------------------
# Metadados textuais
# ----------------------------------------------------------------------------
def parse_meta(progress_text: str):
    branch_m = re.search(r"\*\*Branch:\*\*\s*`([^`]+)`", progress_text)
    upd_m = re.search(r"[Aa]tualiza[çc][aã]o:?\*?\*?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",
                      progress_text)
    cur_m = re.search(r"\*\*Sprint Atual:\*\*\s*\*?\*?([^\n*]+)", progress_text)
    return {
        "branch_doc": branch_m.group(1) if branch_m else "",
        "updated": upd_m.group(1) if upd_m else "",
        "current_sprint": P.clean_desc(cur_m.group(1)) if cur_m else "",
    }


# ----------------------------------------------------------------------------
# Montagem do modelo de UM projeto
# ----------------------------------------------------------------------------
def build_project(plan_build: Path, scan_roots):
    pdir = project_dir_for(plan_build)
    pid = pdir.name
    progress_file = pick_progress_file(plan_build)
    progress_text = read(progress_file) if progress_file else ""

    meta = parse_meta(progress_text)
    git = git_info(pdir)

    # heuristica de "template": placeholders TODO-MAIUSCULAS <NOME DO PROJETO>,
    # <DESCRICAO>, <DATA>... — case-sensitive para NAO confundir com genericos C#
    # (Task<TResult>, List<CedenteDto>) que sao CamelCase.
    placeholders = len(re.findall(r"<[A-ZÀ-Ú][A-ZÀ-Ú0-9 _/-]{1,40}>", progress_text))
    is_template = placeholders >= 3

    # ---- nivel sprint (overview) ----
    sprints = {}
    _, status_rows = P.extract_table(
        progress_text, ["sprint", "status"])
    sp_order = 0
    for r in status_rows:
        cell = r.get("sprint", "")
        key = P.sprint_key(cell)
        if not key:
            continue
        status_raw = r.get("status", "")
        prog_cell = r.get("progresso", "") + " " + r.get("progress", "")
        done, total, pct = P.parse_progress(prog_cell + " " + status_raw)
        col, blocked = P.classify_status(status_raw)
        if pct is None:
            pct = 100 if col == P.COL_DONE else (0 if col == P.COL_PLANEJADO else None)
        sprints[key] = {
            "key": key,
            "name": P.sprint_name(cell),
            "status_raw": P.clean_desc(status_raw),
            "col": col,
            "blocked": blocked,
            "done": done,
            "total": total,
            "pct": pct,
            "order": sp_order,
        }
        sp_order += 1

    # ---- nivel task ----
    tasks = []
    sprint_author = {}   # key -> {name, email, when} (autoria via git, por arquivo de sprint)
    sprint_files = sorted(plan_build.glob("[Ss]print*.md"))
    for sp in sprint_files:
        if "archive" in sp.name.lower():
            continue
        key = P.sprint_key(sp.name) or sp.stem
        sprint_author[key] = file_author(pdir, sp)
        text = read(sp)
        t1 = P.tasks_from_tables(text, sprint_default=key)
        t2 = P.tasks_from_codeblocks(text, sprint_default=key) if not t1 else []
        for t in (t1 + t2):
            tasks.append(t)
    # tabelas de task no proprio Progress.md (formato C):
    # sprint_default vazio -> deriva o sprint pelo id da task (S3B-1 -> S3B)
    for t in P.tasks_from_tables(progress_text, sprint_default=""):
        tasks.append(t)
    # code-blocks do proprio Progress (formato B)
    if not tasks:
        for t in P.tasks_from_codeblocks(progress_text):
            tasks.append(t)

    # dedup por (id, sprint)
    seen = set()
    deduped = []
    for t in tasks:
        k = (t["id"], t["sprint"])
        if k in seen:
            continue
        seen.add(k)
        deduped.append(t)
    tasks = deduped

    # reconciliacao: se o sprint esta COMPLETO no overview, suas tasks viram Done
    for t in tasks:
        sp = sprints.get(t["sprint"])
        if sp and sp["col"] == P.COL_DONE and sp.get("pct") == 100:
            t["col"] = P.COL_DONE
            t["blocked"] = False

    # ---- bloqueios ----
    blockers = []
    _, blk_rows = P.extract_table(progress_text, ["bloqueio", "status"])
    for r in blk_rows:
        st = r.get("status", "")
        resolved = bool(re.search(r"\U0001F7E2|resolvid|sob controle|fechad", st, re.I))
        desc = r.get("bloqueio", "")
        if not P.clean_desc(desc):
            continue
        blockers.append({
            "id": P.clean_desc(r.get("#", r.get("id", ""))),
            "desc": P.clean_desc(desc),
            "impact": P.clean_desc(r.get("impacto", "")),
            "status": P.clean_desc(st),
            "resolved": resolved,
        })

    # ---- debito tecnico ----
    debt = []
    _, dt_rows = P.extract_table(progress_text, ["id", "prioridade"])
    for r in dt_rows:
        did = P.clean_desc(r.get("id", ""))
        if not re.match(r"DT[-_]", did, re.I):
            continue
        desc = r.get("descrição", r.get("descricao", ""))
        closed = "~~" in desc or "✅" in desc or "fechad" in desc.lower()
        debt.append({
            "id": did,
            "desc": P.clean_desc(desc),
            "sprint": P.clean_desc(r.get("sprint", "")),
            "prio": P.clean_desc(r.get("prioridade", "")).lower(),
            "closed": closed,
        })

    # ---- autoria (git, sem tocar nos .md) ----
    for s in sprints.values():
        s["author"] = sprint_author.get(s["key"])
    proj_author = file_author(pdir, progress_file) if progress_file else None
    proj_contributors = contributors(pdir, plan_build)

    # ---- rollup de progresso ----
    sprint_list = sorted(sprints.values(), key=lambda s: s["order"])
    if tasks:
        total = len(tasks)
        done = sum(1 for t in tasks if t["col"] == P.COL_DONE)
        pct = round(done / total * 100) if total else 0
        level = "task"
    else:
        # agrega do nivel sprint
        dones = [s for s in sprint_list if s["col"] == P.COL_DONE]
        total = len(sprint_list)
        done = len(dones)
        # media ponderada simples por pct quando houver
        pcts = [s["pct"] for s in sprint_list if isinstance(s.get("pct"), int)]
        pct = round(sum(pcts) / len(pcts)) if pcts else (
            round(done / total * 100) if total else 0)
        level = "sprint"

    open_blk = [b for b in blockers if not b["resolved"]]
    open_debt = [d for d in debt if not d["closed"]]

    return {
        "id": pid,
        "path": str(pdir),
        "plan_dir": str(plan_build),
        "progress_file": str(progress_file) if progress_file else "",
        "is_template": is_template,
        "has_docs": (pdir / "docs").is_dir(),
        "meta": meta,
        "git": git,
        "branch": git["branch"] or meta.get("branch_doc", ""),
        "current_sprint": meta.get("current_sprint", ""),
        "author": proj_author,
        "contributors": proj_contributors,
        "sprints": sprint_list,
        "tasks": tasks,
        "blockers": blockers,
        "debt": debt,
        "open_blockers": open_blk,
        "open_debt": open_debt,
        "rollup": {"done": done, "total": total, "pct": pct, "level": level},
    }


def scan_candidates(scan_roots):
    """Lista TODOS os projetos rastreaveis sob os scan_roots, com stats rapidas,
    sem aplicar filtros de config. Usado pelo menu interativo do instalador.
    Devolve lista de dicts: {id, path, plan_dir, sprints, tasks, is_template}."""
    out = []
    seen = set()
    for pb in discover_plan_dirs(scan_roots):
        pid = project_dir_for(pb).name
        if pid in seen:
            continue
        proj = build_project(pb, scan_roots)
        if not proj["sprints"] and not proj["tasks"]:
            continue
        seen.add(pid)
        out.append({
            "id": pid,
            "path": proj["path"],
            "plan_dir": proj["plan_dir"],
            "sprints": len(proj["sprints"]),
            "tasks": len(proj["tasks"]),
            "is_template": proj["is_template"],
        })
    out.sort(key=lambda c: c["id"].lower())
    return out


# ----------------------------------------------------------------------------
# Source adapters — cada estrutura de planejamento (plan-build, GSD, ...) e um
# adapter com contrato uniforme. Adicionar suporte a uma nova estrutura =
# registrar um adapter aqui; o core de discover_projects nao muda.
#   discover(scan_roots) -> [planning_root]
#   project_dir(root)    -> Path raiz do projeto (chave de agrupamento)
#   build(root, roots)   -> modelo do projeto (formato north)
#   mtime(root)          -> float (recencia: arquivo de plano mais novo)
# ----------------------------------------------------------------------------
def _newest_mtime(paths):
    best = 0.0
    for p in paths:
        try:
            best = max(best, p.stat().st_mtime)
        except Exception:
            pass
    return best


def _pb_mtime(pb: Path):
    return _newest_mtime(list(pb.glob("*.md")))


def _gsd_mtime(pl: Path):
    return _newest_mtime([pl / "STATE.md", pl / "ROADMAP.md", pl / "HANDOFF.json"])


ADAPTERS = [
    {"name": "plan-build", "label": "plan-build",
     "discover": discover_plan_dirs, "project_dir": project_dir_for,
     "build": lambda root, roots: build_project(root, roots), "mtime": _pb_mtime},
    {"name": "gsd", "label": "GSD",
     "discover": G.discover_planning_dirs, "project_dir": lambda pl: pl.parent,
     "build": lambda root, roots: G.build_gsd_project(root, git_info, file_author),
     "mtime": _gsd_mtime},
]


def discover_projects(config):
    """Descobre + monta todos os projetos habilitados. Devolve (lista, novos_ids).

    Reconciliacao por diretorio: cada projeto e UM card, mesmo que tenha varias
    estruturas de planejamento. A fonte primaria e a mais recentemente ativa
    (mtime), ou a fixada em config (projects.<id>.source); as demais viram
    secundarias (selo discreto)."""
    # 1. detecta todas as fontes, agrupadas por diretorio de projeto
    by_dir = {}   # Path resolvido -> [ {name,label,root,mtime,build} ]
    for ad in ADAPTERS:
        for root in ad["discover"](config.scan_roots):
            try:
                pdir = ad["project_dir"](root).resolve()
            except Exception:
                continue
            by_dir.setdefault(pdir, []).append({
                "name": ad["name"], "label": ad["label"], "root": root,
                "mtime": ad["mtime"](root), "build": ad["build"],
            })

    items = sorted(by_dir.items(), key=lambda kv: kv[0].name.lower())

    new_ids, projects = [], []
    for hint, (pdir, srcs) in enumerate(items):
        pid = pdir.name
        if config.register_discovered(pid, hint):
            new_ids.append(pid)
        if not config.is_enabled(pid):
            continue

        # ordem de tentativa: primaria fixada em config, depois por recencia (desc)
        pinned = config.project_cfg(pid).get("source")
        ordered = sorted(srcs, key=lambda s: (s["name"] != pinned, -s["mtime"]))

        # constroi a primeira fonte com conteudo (fallback se a primaria vier vazia)
        proj = primary = None
        for s in ordered:
            cand = s["build"](s["root"], config.scan_roots)
            if cand.get("sprints") or cand.get("tasks"):
                proj, primary = cand, s
                break
        if proj is None:
            continue
        if proj.get("is_template") and not config.project_cfg(pid).get("force_include"):
            continue

        order = config.order_for(pid, hint)
        proj["id"] = pid
        proj["order"] = order
        proj["name"] = config.alias_for(pid, pid)
        proj["color"] = config.color_for(pid, order)
        proj["source"] = primary["name"]
        proj["sources"] = [s["name"] for s in srcs]
        proj["secondary"] = [s["label"] for s in srcs if s["name"] != primary["name"]]
        proj["alerts"] = H.compute_alerts(proj, config.settings)
        projects.append(proj)

    projects.sort(key=lambda p: (p["order"], p["name"].lower()))
    return projects, new_ids
