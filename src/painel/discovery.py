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
from . import fsutil


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8") if path.exists() else ""
    except Exception:
        return ""


# ----------------------------------------------------------------------------
# Descoberta de diretorios de projeto
# ----------------------------------------------------------------------------
def discover_plan_dirs(scan_roots, max_depth=6):
    """Acha todas as pastas 'plan-build' sob os scan_roots (profundidade limitada).

    Poda VCS/deps/caches e os worktrees do Claude Code (`.claude/worktrees`),
    que sao espelhos do mesmo repo e gerariam projetos-fantasma duplicados
    (ver fsutil)."""
    found, seen = [], set()
    for pb in fsutil.find_dirs_named(scan_roots, "plan-build", max_depth):
        if not pb.is_dir():
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


def group_md_by_feature(plan_build: Path):
    """Agrupa TODOS os .md sob o plan-build por feature, descendo a arvore inteira.

    feature = subpasta de 1o nivel sob o plan-build:
      plan-build/Progress.md          -> feature ""        (raiz / "Principal")
      plan-build/calculo/Sprint-1.md  -> feature "calculo"
      plan-build/calculo/sub/x.md     -> feature "calculo" (1o nivel agrupa o resto)

    Devolve lista ordenada de (feature, {"progress": Path|None, "sprints": [Path]}),
    com a raiz primeiro e as features em ordem alfabetica. Arquivos/pastas que
    contenham 'archive' no caminho sao ignorados (mesmo criterio do legado)."""
    groups = {}
    for md in sorted(plan_build.rglob("*.md")):
        try:
            rel = md.relative_to(plan_build).parts
        except ValueError:
            continue
        if any("archive" in part.lower() for part in rel):
            continue
        feature = rel[0] if len(rel) > 1 else ""
        g = groups.setdefault(feature, {"progress": None, "sprints": []})
        name = md.name.lower()
        if name.startswith("progress"):
            # progress "principal" da feature = nome mais curto (menos sufixo)
            cur = g["progress"]
            if cur is None or len(md.name) < len(cur.name):
                g["progress"] = md
        elif name.startswith("sprint"):
            g["sprints"].append(md)
    return sorted(groups.items(), key=lambda kv: (kv[0] != "", kv[0].lower()))


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


# Branches "compartilhadas" — estar nelas NAO indica trabalho pessoal ativo.
DEFAULT_BRANCHES = {"main", "master", "develop", "dev", "trunk", "head", ""}


def _my_today_count(project_dir: Path, identity):
    """Quantos commits de HOJE sao seus (filtra o log pela sua identidade git).
    Usa o nome (mais estavel que o e-mail entre maquinas); 0 se sem identidade."""
    who = (identity or {}).get("name") or (identity or {}).get("email") or ""
    if not who:
        return 0
    out = _git(["log", "--since=midnight", "--author=" + who, "--pretty=format:%h"],
               project_dir)
    return len([l for l in out.splitlines() if l.strip()]) if out else 0


def _is_me(author, identity):
    """True se a autoria (name/email) bate com a sua identidade."""
    if not author or not identity:
        return False
    ae, an = (author.get("email") or "").lower(), (author.get("name") or "").lower()
    ie, iname = (identity.get("email") or "").lower(), (identity.get("name") or "").lower()
    return bool((ie and ae and ie == ae) or (iname and an and iname == an))


def personal_signal(proj, identity):
    """Sinal de PERTENCIMENTO: o quanto ESTE projeto e o que VOCE esta tocando
    agora, derivado do git (zero input extra). working tree sujo e o sinal mais
    forte (e a sua copia, por definicao). Devolve {score, signals[], active}."""
    git = proj.get("git", {}) or {}
    dirty = git.get("dirty", 0) or 0
    my_today = git.get("my_today", 0) or 0
    branch = (proj.get("branch") or "").strip()
    score, signals = 0, []
    if dirty:
        score += 50
        signals.append("{} arquivo(s) nao commitado(s)".format(dirty))
    if my_today:
        score += 40
        signals.append("{} commit(s) seu(s) hoje".format(my_today))
    if branch and branch.lower() not in DEFAULT_BRANCHES:
        score += 20
        signals.append("branch {}".format(branch))
    if _is_me(proj.get("author"), identity):
        score += 15
        signals.append("ultima edicao sua")
    return {"score": score, "signals": signals, "active": score > 0}


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
def _build_feature_blockers(ftext):
    """Bloqueios de um texto de progress (tabela Bloqueio|Status)."""
    out = []
    _, blk_rows = P.extract_table(ftext, ["bloqueio", "status"])
    for r in blk_rows:
        st = r.get("status", "")
        resolved = bool(re.search(r"\U0001F7E2|resolvid|sob controle|fechad", st, re.I))
        desc = r.get("bloqueio", "")
        if not P.clean_desc(desc):
            continue
        out.append({
            "id": P.clean_desc(r.get("#", r.get("id", ""))),
            "desc": P.clean_desc(desc),
            "impact": P.clean_desc(r.get("impacto", "")),
            "status": P.clean_desc(st),
            "resolved": resolved,
        })
    return out


def _build_feature_debt(ftext):
    """Debito tecnico de um texto de progress (tabela id|prioridade, ids DT-*)."""
    out = []
    _, dt_rows = P.extract_table(ftext, ["id", "prioridade"])
    for r in dt_rows:
        did = P.clean_desc(r.get("id", ""))
        if not re.match(r"DT[-_]", did, re.I):
            continue
        desc = r.get("descrição", r.get("descricao", ""))
        closed = "~~" in desc or "✅" in desc or "fechad" in desc.lower()
        out.append({
            "id": did,
            "desc": P.clean_desc(desc),
            "sprint": P.clean_desc(r.get("sprint", "")),
            "prio": P.clean_desc(r.get("prioridade", "")).lower(),
            "closed": closed,
        })
    return out


# ----------------------------------------------------------------------------
# Documentos de SDLC dentro do plan-build (PRD/SDD/TDD/SPEC/SECURITY/UML/ADR).
# Read-only: o painel apenas DETECTA e LINKA — nunca edita. (Fase 1 do AI-SDLC.)
# ----------------------------------------------------------------------------
# "Vivos" (CONTEXT/DECISIONS) primeiro: são o ponto de entrada — briefing e o porquê.
DOC_TYPES = [
    ("CONTEXT", re.compile(r"\bCONTEXT\b|contexto", re.I)),
    ("DECISIONS", re.compile(r"\bDECISIONS?\b|decis[õo]es", re.I)),
    ("PRD", re.compile(r"\bPRD\b|product[-_ ]?requirement", re.I)),
    ("SDD", re.compile(r"\bSDD\b|software[-_ ]?design|design[-_ ]?doc", re.I)),
    ("TDD", re.compile(r"\bTDD\b|test[-_ ]?design|test[-_ ]?plan", re.I)),
    ("SPEC", re.compile(r"\bspec(?:ification)?\b", re.I)),
    ("SECURITY", re.compile(r"\bsecurity\b|seguran[cç]a|threat[-_ ]?model|owasp", re.I)),
    ("ADR", re.compile(r"\bADR\b|architecture[-_ ]?decision", re.I)),
    ("UML", re.compile(r"\bUML\b|\bC4\b|diagram|sequence[-_ ]?diagram", re.I)),
]

# Docs "vivos" projetados na RAIZ do projeto (e em docs/) — DECISIONS.md / CONTEXT.md.
LIVING_DOC_TYPES = ("CONTEXT", "DECISIONS")


def classify_doc(stem: str):
    """Tipo de doc a partir do nome do arquivo (sem extensão). None se não é doc."""
    if re.match(r"^(progress|sprint)", stem, re.I):
        return None          # tracking, não documento
    for typ, rx in DOC_TYPES:
        if rx.search(stem):
            return typ
    return None


def collect_docs(plan_build: Path, extra_pbs=None):
    """Lista os documentos de SDLC sob o plan-build (e plan-builds aninhados),
    tipados. Read-only. Devolve [{type, name, path, feature}] ordenado por tipo."""
    seen, out = set(), []
    roots = [("", plan_build)] + [(pre, npb) for pre, npb in (extra_pbs or [])]
    for prefix, root in roots:
        for md in sorted(root.rglob("*.md")):
            try:
                rel = md.relative_to(root).parts
            except ValueError:
                continue
            if any("archive" in p.lower() for p in rel):
                continue
            typ = classify_doc(md.stem)
            if not typ:
                continue
            key = str(md.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            feature = prefix or (rel[0] if len(rel) > 1 else "")
            out.append({"type": typ, "name": md.name, "path": str(md), "feature": feature})
    order = {t: i for i, (t, _) in enumerate(DOC_TYPES)}
    out.sort(key=lambda d: (order.get(d["type"], 99), d["name"].lower()))
    return out


def collect_living_docs(project_dir: Path):
    """Docs 'vivos' (DECISIONS.md / CONTEXT.md) na RAIZ do projeto e em docs/.
    Read-only; não desce a árvore (só topo + docs/) p/ não capturar ruído.
    Devolve [{type, name, path, feature:""}]."""
    out, seen = [], set()
    locations = [project_dir, project_dir / "docs"]
    for loc in locations:
        try:
            if not loc.is_dir():
                continue
            for md in sorted(loc.glob("*.md")):
                typ = classify_doc(md.stem)
                if typ not in LIVING_DOC_TYPES:
                    continue
                key = str(md.resolve()).lower()
                if key in seen:
                    continue
                seen.add(key)
                out.append({"type": typ, "name": md.name, "path": str(md), "feature": ""})
        except OSError:
            continue
    return out


def _merge_docs(*lists):
    """Funde listas de docs, dedup por caminho, reordena pela ordem de DOC_TYPES."""
    seen, merged = set(), []
    for lst in lists:
        for d in lst:
            key = str(Path(d["path"]).resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(d)
    order = {t: i for i, (t, _) in enumerate(DOC_TYPES)}
    merged.sort(key=lambda d: (order.get(d["type"], 99), d["name"].lower()))
    return merged


def build_project(plan_build: Path, scan_roots, extra_pbs=None):
    """Monta o modelo de UM projeto a partir do seu plan-build.

    extra_pbs: lista opcional de (feature_prefix, plan_build_aninhado) — usada
    para FUNDIR plan-builds aninhados (projeto/feature-x/plan-build) como grupos
    de feature deste mesmo projeto, em vez de cards separados."""
    pdir = project_dir_for(plan_build)
    pid = pdir.name

    # agrupa os .md por feature (subpasta de 1o nivel; raiz = ""), descendo a
    # arvore inteira — resolve o caso "plan-build segregado por feature". Os
    # plan-builds aninhados (extra_pbs) entram com a feature prefixada pelo
    # caminho relativo (feature-x, feature-x/sub, ...).
    groups_map = {}

    def _merge(feat, g):
        slot = groups_map.setdefault(feat, {"progress": None, "sprints": []})
        gp = g["progress"]
        if gp is not None and (slot["progress"] is None
                               or len(gp.name) < len(slot["progress"].name)):
            slot["progress"] = gp
        slot["sprints"].extend(g["sprints"])

    for feat, g in group_md_by_feature(plan_build):
        _merge(feat, g)
    for prefix, npb in (extra_pbs or []):
        for feat, g in group_md_by_feature(npb):
            _merge(prefix if not feat else prefix + "/" + feat, g)

    groups = sorted(groups_map.items(), key=lambda kv: (kv[0] != "", kv[0].lower()))

    # progress "principal" do projeto = o da raiz (meta/branch/sprint atual);
    # se nao houver raiz, usa o da primeira feature com progress (degrada).
    root_progress = groups_map.get("", {}).get("progress")
    if root_progress is None:
        for _f, g in groups:
            if g["progress"] is not None:
                root_progress = g["progress"]
                break
    progress_text = read(root_progress) if root_progress else ""

    meta = parse_meta(progress_text)
    git = git_info(pdir)

    # heuristica de "template": placeholders TODO-MAIUSCULAS <NOME DO PROJETO>,
    # <DESCRICAO>, <DATA>... — case-sensitive para NAO confundir com genericos C#
    # (Task<TResult>, List<CedenteDto>) que sao CamelCase.
    placeholders = len(re.findall(r"<[A-ZÀ-Ú][A-ZÀ-Ú0-9 _/-]{1,40}>", progress_text))
    is_template = placeholders >= 3

    # ---- por feature: sprints (overview) + tasks + bloqueios + debito ----
    sprints = {}             # (feature, key) -> sprint dict
    sprint_author = {}       # (feature, key) -> autoria via git
    sprint_brief_map = {}    # (feature, key) -> resumo narrativo (Sprint*.md)
    tasks = []
    blockers = []
    debt = []
    feature_order = []       # ordem das features que contribuiram com algo
    sp_order = 0

    for feature, g in groups:
        ftext = read(g["progress"]) if g["progress"] else ""

        # sprints da feature (tabela Status Geral)
        _, status_rows = P.extract_table(ftext, ["sprint", "status"])
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
            sprints[(feature, key)] = {
                "key": key, "feature": feature,
                "name": P.sprint_name(cell),
                "status_raw": P.clean_desc(status_raw),
                "col": col, "blocked": blocked,
                "done": done, "total": total, "pct": pct, "order": sp_order,
            }
            sp_order += 1

        # tasks da feature: cada Sprint*.md + tabelas/code-blocks do progress
        feat_tasks = []
        for sp in g["sprints"]:
            key = P.sprint_key(sp.name) or sp.stem
            sprint_author[(feature, key)] = file_author(pdir, sp)
            text = read(sp)
            br = P.sprint_brief(text)
            if any(br.values()):
                sprint_brief_map[(feature, key)] = br
            t1 = P.tasks_from_tables(text, sprint_default=key)
            t2 = P.tasks_from_codeblocks(text, sprint_default=key) if not t1 else []
            for t in (t1 + t2):
                detail = P.task_brief(text, t["id"])   # contrato: entrega + aceite
                if detail:
                    t.update(detail)
            feat_tasks.extend(t1 + t2)
        # tabelas de task no proprio progress (formato C): sprint_default vazio
        # -> deriva o sprint pelo id da task (S3B-1 -> S3B)
        feat_tasks.extend(P.tasks_from_tables(ftext, sprint_default=""))
        # code-blocks do progress (formato B) so se a feature nao gerou nada
        if not feat_tasks:
            feat_tasks.extend(P.tasks_from_codeblocks(ftext))
        for t in feat_tasks:
            t["feature"] = feature
            tasks.append(t)

        # bloqueios / debito desta feature (agregados no nivel projeto)
        for b in _build_feature_blockers(ftext):
            b["feature"] = feature
            blockers.append(b)
        for d in _build_feature_debt(ftext):
            d["feature"] = feature
            debt.append(d)

        if feat_tasks or any(k[0] == feature for k in sprints):
            if feature not in feature_order:
                feature_order.append(feature)

    # dedup por (feature, id, sprint)
    seen = set()
    deduped = []
    for t in tasks:
        k = (t.get("feature", ""), t["id"], t["sprint"])
        if k in seen:
            continue
        seen.add(k)
        deduped.append(t)
    tasks = deduped

    # reconciliacao: se o sprint esta COMPLETO no overview, suas tasks viram Done
    # (casado por feature, para nao misturar sprints homonimos de features distintas)
    for t in tasks:
        sp = sprints.get((t.get("feature", ""), t["sprint"]))
        if sp and sp["col"] == P.COL_DONE and sp.get("pct") == 100:
            t["col"] = P.COL_DONE
            t["blocked"] = False

    # ---- autoria (git, sem tocar nos .md) ----
    for (feature, key), s in sprints.items():
        s["author"] = sprint_author.get((feature, key))
        s["brief"] = sprint_brief_map.get((feature, key))
    proj_author = file_author(pdir, root_progress) if root_progress else None
    proj_contributors = contributors(pdir, plan_build)

    # ---- rollup de progresso ----
    sprint_list = sorted(sprints.values(), key=lambda s: s["order"])

    # ---- indice de features (ordenado) para o render agrupar ----
    features = []
    for fk in feature_order:
        f_sprints = [s for s in sprint_list if s["feature"] == fk]
        f_tasks = [t for t in tasks if t.get("feature", "") == fk]
        if f_tasks:
            f_done = sum(1 for t in f_tasks if t["col"] == P.COL_DONE)
            f_total = len(f_tasks)
            f_level = "task"
        else:
            f_done = sum(1 for s in f_sprints if s["col"] == P.COL_DONE)
            f_total = len(f_sprints)
            f_level = "sprint"
        features.append({
            "key": fk, "label": fk or "Principal",
            "sprint_keys": [s["key"] for s in f_sprints],
            "done": f_done, "total": f_total,
            "pct": round(f_done / f_total * 100) if f_total else 0,
            "level": f_level,
        })
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
        "progress_file": str(root_progress) if root_progress else "",
        "is_template": is_template,
        "has_docs": (pdir / "docs").is_dir(),
        "docs": _merge_docs(collect_docs(plan_build, extra_pbs), collect_living_docs(pdir)),
        "meta": meta,
        "git": git,
        "branch": git["branch"] or meta.get("branch_doc", ""),
        "current_sprint": meta.get("current_sprint", ""),
        "author": proj_author,
        "contributors": proj_contributors,
        "features": features,
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
    # rglob: a recencia precisa enxergar edicoes em subpastas segregadas
    # (plan-build/calculo/Sprint-1.md), nao so os .md na raiz do plan-build.
    return _newest_mtime(list(pb.rglob("*.md")))


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


def _nested_planbuilds(by_dir):
    """Reparenta plan-builds aninhados sob outro projeto plan-build.

    Um plan-build em projeto/feature-x/plan-build vira FEATURE do projeto-pai
    (ancestral mais ALTO com plan-build), em vez de um card separado. Devolve:
      extra_by_root: pdir_raiz -> [(feature_prefix, plan_build_aninhado)]
      absorbed:      set de pdirs aninhados que NAO viram card proprio
    So absorve quando o pdir aninhado tem APENAS fonte plan-build (se tiver um
    .planning GSD, permanece como card para nao engolir um projeto legitimo)."""
    pb_root = {}   # pdir -> plan_build root (fonte plan-build)
    for pdir, srcs in by_dir.items():
        s = next((x for x in srcs if x["name"] == "plan-build"), None)
        if s is not None:
            pb_root[pdir] = s["root"]

    extra_by_root, absorbed = {}, set()
    for pdir in pb_root:
        ancestors = [c for c in pdir.parents if c in pb_root]
        if not ancestors:
            continue   # e uma raiz de projeto — nao aninhado
        if not all(x["name"] == "plan-build" for x in by_dir[pdir]):
            continue   # tem outra fonte (ex.: GSD) — mantem como card proprio
        root_parent = ancestors[-1]   # ancestral mais alto = raiz da arvore
        try:
            prefix = pdir.relative_to(root_parent).as_posix()
        except ValueError:
            prefix = pdir.name
        extra_by_root.setdefault(root_parent, []).append((prefix, pb_root[pdir]))
        absorbed.add(pdir)
    return extra_by_root, absorbed


def discover_projects(config):
    """Descobre + monta projetos habilitados. Devolve (lista, novos_ids, removidos).

    Reconciliacao por diretorio: cada projeto e UM card, mesmo que tenha varias
    estruturas de planejamento. A fonte primaria e a mais recentemente ativa
    (mtime), ou a fixada em config (projects.<id>.source); as demais viram
    secundarias (selo discreto). Plan-builds aninhados sob outro projeto sao
    fundidos como features do projeto-pai (ver _nested_planbuilds)."""
    # 1. detecta todas as fontes, agrupadas por diretorio de projeto.
    #    discovery_roots(): projetos plugados (modo enrolled) ou scan_roots (legado).
    roots = config.discovery_roots()
    by_dir = {}   # Path resolvido -> [ {name,label,root,mtime,build} ]
    for ad in ADAPTERS:
        for root in ad["discover"](roots):
            try:
                pdir = ad["project_dir"](root).resolve()
            except Exception:
                continue
            by_dir.setdefault(pdir, []).append({
                "name": ad["name"], "label": ad["label"], "root": root,
                "mtime": ad["mtime"](root), "build": ad["build"],
            })

    extra_by_root, absorbed = _nested_planbuilds(by_dir)

    # auto-cura: poda da config os projetos que sumiram do disco (re-map). Um id
    # so e considerado vivo se apareceu na varredura (by_dir = tudo que existe,
    # inclusive desabilitados/templates/aninhados). Guarda: NAO poda se a
    # varredura nao achou nada (scan_roots vazio/quebrado -> nao zera a config).
    discovered_ids = {pdir.name for pdir in by_dir}
    removed_ids = []
    if discovered_ids:
        for pid in list(config.projects.keys()):
            if pid not in discovered_ids:
                config.projects.pop(pid, None)
                removed_ids.append(pid)
        st = config.data.get("settings", {}) or {}
        if st.get("focused_project") in removed_ids:
            st.pop("focused_project", None)

    items = sorted(by_dir.items(), key=lambda kv: kv[0].name.lower())

    identity = config.settings.get("identity") or {}
    new_ids, projects = [], []
    for hint, (pdir, srcs) in enumerate(items):
        if pdir in absorbed:
            continue   # plan-build aninhado: ja entra como feature do projeto-pai
        pid = pdir.name
        if config.register_discovered(pid, hint):
            new_ids.append(pid)
        if not config.is_enabled(pid):
            continue

        # ordem de tentativa: primaria fixada em config, depois por recencia (desc)
        pinned = config.project_cfg(pid).get("source")
        ordered = sorted(srcs, key=lambda s: (s["name"] != pinned, -s["mtime"]))
        extra = extra_by_root.get(pdir)

        # constroi a primeira fonte com conteudo (fallback se a primaria vier vazia)
        proj = primary = None
        for s in ordered:
            if s["name"] == "plan-build":
                cand = build_project(s["root"], roots, extra)
            else:
                cand = s["build"](s["root"], roots)
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
        proj["git"]["my_today"] = _my_today_count(pdir, identity)
        proj["mine"] = personal_signal(proj, identity)
        projects.append(proj)

    projects.sort(key=lambda p: (p["order"], p["name"].lower()))
    return projects, new_ids, removed_ids
