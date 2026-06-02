# -*- coding: utf-8 -*-
"""
render.py — gera o dashboard.html profissional (multi-projeto, CSS/JS puro).

Sem Tailwind, sem framework. Os dados de todos os projetos sao embutidos como
JSON e renderizados client-side por um pequeno app vanilla JS, o que permite:
  - troca instantanea entre projetos (sidebar)
  - visao "Todos os Projetos" (portfolio) com cards + donuts
  - filtros por status e busca por TASK
  - tema claro/escuro
"""

import json
from datetime import datetime

from . import parsers as P
from . import focus as F


def build_data(projects, settings, inbox_items=None):
    totals_done = sum(p["rollup"]["done"] for p in projects)
    totals_total = sum(p["rollup"]["total"] for p in projects)
    totals_blk = sum(len(p["open_blockers"]) for p in projects)
    totals_debt = sum(len(p["open_debt"]) for p in projects)
    today_commits = sum(len(p["git"]["today_commits"]) for p in projects)
    overall_pct = round(totals_done / totals_total * 100) if totals_total else 0

    def author_json(a):
        return {"name": a["name"], "when": a["when"]} if a else None

    def proj_json(p):
        return {
            "id": p["id"],
            "name": p["name"],
            "color": p["color"],
            "branch": p["branch"] or "—",
            "currentSprint": p["current_sprint"] or "—",
            "dirty": p["git"]["dirty"],
            "todayCommits": [{"h": h, "s": s} for h, s in p["git"]["today_commits"]],
            "author": author_json(p.get("author")),
            "contributors": [c["name"] for c in p.get("contributors", [])],
            "rollup": p["rollup"],
            "sprints": [
                {"key": s["key"], "name": s["name"], "pct": s["pct"] if s["pct"] is not None else 0,
                 "col": s["col"], "blocked": s["blocked"],
                 "done": s["done"], "total": s["total"],
                 "author": author_json(s.get("author"))}
                for s in p["sprints"]
            ],
            "tasks": [
                {"id": t["id"], "sprint": t["sprint"], "desc": t["desc"],
                 "owner": (t["owner"] or "").replace("squad-", ""),
                 "col": t["col"], "blocked": t["blocked"], "commit": t["commit"][:7],
                 "statusRaw": t["status_raw"]}
                for t in p["tasks"]
            ],
            "blockers": [
                {"id": b["id"], "desc": b["desc"], "impact": b["impact"], "status": b["status"]}
                for b in p["open_blockers"]
            ],
            "debt": [
                {"id": d["id"], "desc": d["desc"], "sprint": d["sprint"], "prio": d["prio"]}
                for d in sorted(p["open_debt"],
                                key=lambda d: {"alta": 0, "média": 1, "media": 1,
                                               "baixa": 2}.get(d["prio"], 3))
            ],
        }

    # ---- foco (direcao): proxima acao + WIP ----
    fc = F.compute_focus(projects, settings.get("wip_limit", F.WIP_LIMIT))
    focus_json = None
    if fc["pick"]:
        pk = fc["pick"]
        focus_json = {
            "project": pk["project"], "projectId": pk["project_id"], "color": pk["color"],
            "id": pk["task"]["id"], "sprint": pk["task"]["sprint"] or "—",
            "desc": P.clean_desc(pk["task"]["desc"])[:120] or pk["task"].get("status_raw", "")[:120],
            "reasons": pk["reasons"], "squad": pk["squad"], "actionable": pk["actionable"],
            "wip": [{"project": w["project"], "count": w["count"], "limit": w["limit"]}
                    for w in fc["wip_alerts"]],
            "alts": [{"project": s["project"], "id": s["task"]["id"],
                      "sprint": s["task"]["sprint"] or "—",
                      "desc": P.clean_desc(s["task"]["desc"])[:60]} for s in fc["alts"]],
        }

    inbox_json = [
        {"id": e["id"], "text": e["text"], "tag": e.get("tag", "idea"),
         "project": e.get("project", ""), "date": e.get("date", "")}
        for e in (inbox_items or [])
    ]

    return {
        "focus": focus_json,
        "inbox": inbox_json,
        "meta": {
            "title": settings.get("title", "north"),
            "owner": settings.get("owner_name", ""),
            "generated": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "theme": settings.get("theme", "dark"),
            "identity": settings.get("identity", {}),
        },
        "totals": {
            "projects": len(projects),
            "pct": overall_pct,
            "done": totals_done,
            "total": totals_total,
            "blockers": totals_blk,
            "debt": totals_debt,
            "commits": today_commits,
        },
        "columns": [
            {"key": c, "emoji": P.COLUMN_META[c]["emoji"], "color": P.COLUMN_META[c]["color"]}
            for c in P.COLUMN_ORDER
        ],
        "projects": [proj_json(p) for p in projects],
    }


def render(projects, settings, inbox_items=None):
    data = build_data(projects, settings, inbox_items)
    blob = json.dumps(data, ensure_ascii=False)
    theme = data["meta"]["theme"]
    html = _SHELL.replace("/*__THEME__*/", theme)
    html = html.replace("/*__DATA__*/", blob)
    return html


# ============================================================================
# Shell HTML (CSS + JS vanilla). Sem f-string: dados injetados por replace().
# ============================================================================
_SHELL = r"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="/*__THEME__*/">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Central de Produtividade</title>
<style>
  :root{
    --bg:#0b1120; --bg2:#0f172a; --panel:#111c30; --panel2:#16233c;
    --card:#1e293b; --line:#243349; --line2:#1e293b;
    --text:#e8eef7; --muted:#93a4bd; --dim:#5b6b85;
    --accent:#f97316; --accent2:#fb923c;
    --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444; --info:#38bdf8;
    --radius:14px; --shadow:0 10px 30px -12px rgba(0,0,0,.55);
    --mono:ui-monospace,"Cascadia Code","SF Mono",Consolas,monospace;
    --sans:"Segoe UI",-apple-system,Roboto,Helvetica,Arial,sans-serif;
  }
  html[data-theme="light"]{
    --bg:#eef2f7; --bg2:#e7edf5; --panel:#ffffff; --panel2:#f5f8fc;
    --card:#ffffff; --line:#dbe3ee; --line2:#e8eef6;
    --text:#16233c; --muted:#5b6b85; --dim:#94a3b8;
    --shadow:0 10px 28px -16px rgba(15,23,42,.35);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:var(--sans);background:
    radial-gradient(1200px 600px at 80% -10%, rgba(249,115,22,.10), transparent 60%),
    var(--bg);color:var(--text);min-height:100vh;font-size:14px;line-height:1.5}
  ::-webkit-scrollbar{width:9px;height:9px}
  ::-webkit-scrollbar-thumb{background:var(--line);border-radius:6px}
  ::-webkit-scrollbar-track{background:transparent}
  a{color:var(--accent);text-decoration:none}
  .mono{font-family:var(--mono)}

  /* ---- layout ---- */
  .app{display:grid;grid-template-columns:288px 1fr;min-height:100vh}
  .side{background:linear-gradient(180deg,var(--bg2),var(--bg));
    border-right:1px solid var(--line);padding:20px 16px;position:sticky;top:0;
    height:100vh;overflow-y:auto}
  .main{padding:24px 30px 60px;max-width:1640px}

  /* ---- brand ---- */
  .brand{display:flex;align-items:center;gap:11px;margin-bottom:22px}
  .brand .logo{width:38px;height:38px;border-radius:11px;flex:0 0 auto;
    background:linear-gradient(135deg,var(--accent),#c2410c);
    display:grid;place-items:center;font-weight:800;color:#fff;font-size:18px;
    box-shadow:0 6px 16px -6px rgba(249,115,22,.7)}
  .brand .bt{font-weight:700;font-size:15px;letter-spacing:.2px;line-height:1.15}
  .brand .bs{font-size:11px;color:var(--muted)}

  /* ---- nav projetos ---- */
  .nav-h{font-size:10.5px;text-transform:uppercase;letter-spacing:1.4px;
    color:var(--dim);margin:18px 6px 10px;font-weight:700}
  .nav-item{display:block;width:100%;text-align:left;border:1px solid transparent;
    background:transparent;color:var(--text);padding:11px 12px;border-radius:11px;
    cursor:pointer;margin-bottom:6px;transition:.15s;font-family:inherit;font-size:13px}
  .nav-item:hover{background:var(--panel);border-color:var(--line)}
  .nav-item.active{background:var(--panel);border-color:var(--line);
    box-shadow:inset 3px 0 0 var(--ni,—)}
  .nav-top{display:flex;align-items:center;gap:9px;margin-bottom:7px}
  .dot{width:9px;height:9px;border-radius:50%;flex:0 0 auto}
  .nav-name{font-weight:600;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .nav-pct{font-size:12px;font-weight:700;color:var(--muted)}
  .nav-bar{height:5px;border-radius:4px;background:var(--line);overflow:hidden}
  .nav-bar i{display:block;height:100%;border-radius:4px}
  .nav-sub{display:flex;justify-content:space-between;font-size:10.5px;
    color:var(--dim);margin-top:6px}
  .nav-badge{font-size:9.5px;padding:1px 6px;border-radius:20px;font-weight:700}
  .bg-bad{background:rgba(239,68,68,.16);color:#fca5a5}
  .bg-warn{background:rgba(245,158,11,.16);color:#fcd34d}

  .side-foot{margin-top:18px;padding-top:16px;border-top:1px solid var(--line);
    font-size:11px;color:var(--dim);line-height:1.7}
  .theme-btn{margin-top:12px;width:100%;border:1px solid var(--line);
    background:var(--panel);color:var(--text);padding:9px;border-radius:10px;
    cursor:pointer;font-family:inherit;font-size:12px}
  .theme-btn:hover{border-color:var(--accent)}

  /* ---- header main ---- */
  .top{display:flex;align-items:flex-end;justify-content:space-between;
    gap:16px;flex-wrap:wrap;margin-bottom:22px}
  .top h1{font-size:22px;font-weight:800;letter-spacing:.2px}
  .top h1 small{font-weight:500;color:var(--muted);font-size:14px}
  .top .gen{font-size:11.5px;color:var(--dim)}

  /* ---- foco (direcao) ---- */
  .focus{background:linear-gradient(135deg,rgba(249,115,22,.16),var(--panel));
    border:1px solid var(--accent);border-radius:var(--radius);padding:18px 20px;
    margin-bottom:22px;box-shadow:var(--shadow);position:relative;overflow:hidden}
  .focus::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:var(--accent)}
  .focus-h{display:flex;align-items:center;gap:9px;font-size:11px;text-transform:uppercase;
    letter-spacing:1.4px;color:var(--accent2);font-weight:800;margin-bottom:9px}
  .focus-task{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
  .focus-id{font-family:var(--mono);font-size:17px;font-weight:800;color:var(--text)}
  .focus-proj{font-size:11px;padding:2px 9px;border-radius:6px;font-weight:700;color:#fff}
  .focus-desc{font-size:14px;color:var(--text);margin-top:7px;line-height:1.45}
  .focus-why{font-size:12px;color:var(--muted);margin-top:7px}
  .focus-cta{display:flex;gap:10px;flex-wrap:wrap;margin-top:13px;align-items:center}
  .focus-squad{font-family:var(--mono);font-size:12px;background:var(--bg2);color:var(--accent2);
    border:1px solid var(--line);padding:5px 11px;border-radius:8px;font-weight:700}
  .focus-wip{font-size:12px;color:#fcd34d;background:rgba(245,158,11,.12);
    padding:5px 11px;border-radius:8px;border:1px solid rgba(245,158,11,.3)}
  .focus-alts{margin-top:11px;padding-top:11px;border-top:1px solid var(--line2);
    font-size:11.5px;color:var(--muted)}
  .focus-alts b{color:var(--dim);text-transform:uppercase;letter-spacing:.5px;font-size:10px}
  .focus-alts a{cursor:pointer}

  /* ---- inbox ---- */
  .ib-box{display:flex;flex-direction:column;gap:8px;margin-bottom:8px}
  .ib-item{display:flex;align-items:center;gap:11px;background:var(--panel);
    border:1px solid var(--line);border-radius:10px;padding:11px 14px;font-size:13px}
  .ib-item:hover{border-color:var(--accent)}
  .ib-tag{font-size:15px;flex:0 0 auto}
  .ib-id{font-family:var(--mono);font-size:11px;color:var(--dim);flex:0 0 auto}
  .ib-text{flex:1;color:var(--text)}
  .ib-proj{font-size:10.5px;color:var(--muted);background:var(--card);
    border:1px solid var(--line);padding:2px 8px;border-radius:20px;flex:0 0 auto}
  .ib-date{font-size:11px;color:var(--dim);flex:0 0 auto}

  /* ---- kpis ---- */
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
    gap:14px;margin-bottom:26px}
  .kpi{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
    padding:16px 18px;box-shadow:var(--shadow)}
  .kpi .v{font-size:30px;font-weight:800;line-height:1}
  .kpi .l{font-size:11px;color:var(--muted);text-transform:uppercase;
    letter-spacing:.6px;margin-top:7px}
  .kpi.ok .v{color:var(--ok)} .kpi.warn .v{color:var(--warn)}
  .kpi.bad .v{color:var(--bad)} .kpi.acc .v{color:var(--accent)}

  /* ---- secao ---- */
  .sec-h{font-size:12px;text-transform:uppercase;letter-spacing:1.4px;
    color:var(--muted);margin:26px 0 14px;font-weight:700;
    display:flex;align-items:center;gap:10px}
  .sec-h .ln{flex:1;height:1px;background:var(--line)}

  /* ---- portfolio cards ---- */
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px}
  .pcard{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
    padding:20px;box-shadow:var(--shadow);cursor:pointer;transition:.18s;position:relative;
    overflow:hidden}
  .pcard:hover{transform:translateY(-3px);border-color:var(--pc)}
  .pcard::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:var(--pc)}
  .pcard-h{display:flex;align-items:center;gap:13px;margin-bottom:16px}
  .donut{width:64px;height:64px;border-radius:50%;flex:0 0 auto;display:grid;place-items:center;
    background:conic-gradient(var(--pc) calc(var(--p)*1%), var(--line) 0)}
  .donut span{width:48px;height:48px;border-radius:50%;background:var(--panel);
    display:grid;place-items:center;font-weight:800;font-size:15px}
  .pcard-t{font-weight:700;font-size:15px}
  .pcard-s{font-size:11.5px;color:var(--muted);margin-top:3px}
  .pcard-stats{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
  .pill{font-size:10.5px;padding:3px 9px;border-radius:20px;background:var(--card);
    border:1px solid var(--line);color:var(--muted);font-weight:600}
  .pill b{color:var(--text)}
  .pcard-foot{display:flex;justify-content:space-between;align-items:center;
    margin-top:15px;padding-top:13px;border-top:1px solid var(--line2);
    font-size:11px;color:var(--dim)}
  .branch{font-family:var(--mono);color:var(--muted);max-width:160px;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

  /* ---- detalhe projeto ---- */
  .pmeta{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:6px}
  .sprints{display:grid;grid-template-columns:repeat(auto-fill,minmax(218px,1fr));gap:14px}
  .scard{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:15px}
  .scard.cur{box-shadow:0 0 0 1px var(--accent),0 0 22px -8px var(--accent)}
  .scard-h{display:flex;align-items:center;gap:8px;margin-bottom:9px}
  .skey{font-size:11px;font-weight:800;color:#fff;padding:2px 9px;border-radius:6px}
  .snow{font-size:8.5px;background:var(--accent);color:#fff;padding:2px 6px;
    border-radius:5px;letter-spacing:.5px;font-weight:700}
  .sname{font-size:12px;color:var(--muted);min-height:34px;margin-bottom:10px;line-height:1.4}
  .bar{height:8px;background:var(--line);border-radius:5px;overflow:hidden}
  .bar i{display:block;height:100%;border-radius:5px;transition:width .5s}
  .scard-f{display:flex;justify-content:space-between;align-items:baseline;
    margin-top:9px;font-size:11px;color:var(--muted)}
  .scard-f b{font-size:17px;color:var(--text)}
  .scard-by{font-size:10px;color:var(--dim);margin-top:7px;font-family:var(--mono)}
  .blocked-tag{font-size:9px;background:rgba(239,68,68,.18);color:#fca5a5;
    padding:1px 6px;border-radius:5px;font-weight:700}

  /* ---- toolbar kanban ---- */
  .toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:6px 0 14px}
  .search{flex:1;min-width:200px;background:var(--panel);border:1px solid var(--line);
    color:var(--text);padding:9px 13px;border-radius:10px;font-family:inherit;font-size:13px}
  .search:focus{outline:none;border-color:var(--accent)}
  .chip{font-size:11.5px;padding:6px 13px;border-radius:20px;cursor:pointer;
    border:1px solid var(--line);background:var(--panel);color:var(--muted);
    font-weight:600;user-select:none;transition:.15s}
  .chip:hover{color:var(--text)}
  .chip.on{color:#fff;border-color:transparent}

  /* ---- kanban ---- */
  .kanban{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
  .kcol{background:var(--panel2);border:1px solid var(--line);border-radius:12px;overflow:hidden}
  .kcol-h{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;
    font-size:12.5px;font-weight:700;border-top:3px solid;background:var(--panel)}
  .kcol-h .cnt{background:var(--card);padding:1px 9px;border-radius:11px;font-size:11.5px;
    color:var(--muted)}
  .kcol-b{padding:12px;display:flex;flex-direction:column;gap:10px;min-height:60px;
    max-height:640px;overflow-y:auto}
  .card{background:var(--card);border-radius:9px;border-left:4px solid var(--accent);
    padding:11px 13px;transition:.15s}
  .card:hover{transform:translateX(2px)}
  .card.blk{box-shadow:inset 0 0 0 1px rgba(239,68,68,.4)}
  .card-t{display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:6px}
  .tid{font-family:var(--mono);font-size:12px;font-weight:700;color:var(--text)}
  .stag{font-size:9.5px;padding:1px 7px;border-radius:5px;font-weight:700}
  .cdesc{font-size:12px;color:var(--muted);line-height:1.45}
  .card-f{display:flex;justify-content:space-between;align-items:center;margin-top:9px;gap:6px}
  .owner{font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px}
  .commit{font-family:var(--mono);font-size:10px;background:var(--bg2);color:var(--ok);
    padding:1px 6px;border-radius:4px}
  .empty{font-size:11.5px;color:var(--dim);text-align:center;padding:14px;font-style:italic}

  /* ---- paineis ---- */
  .panels{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:8px}
  .panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
    padding:18px;box-shadow:var(--shadow)}
  .panel h3{font-size:13.5px;margin-bottom:13px;display:flex;align-items:center;gap:8px}
  .panel h3 .c{font-size:11px;color:var(--dim);font-weight:500}
  table{width:100%;border-collapse:collapse;font-size:12px}
  th{text-align:left;color:var(--dim);font-size:10px;text-transform:uppercase;
    letter-spacing:.5px;padding:6px 8px;border-bottom:1px solid var(--line)}
  td{padding:8px;border-bottom:1px solid var(--line2);color:var(--muted);vertical-align:top}
  td.k{font-family:var(--mono);color:var(--text);white-space:nowrap;font-size:11px}
  .prio{font-size:10px;padding:1px 8px;border-radius:5px;font-weight:700}
  .prio-alta{background:rgba(239,68,68,.16);color:#fca5a5}
  .prio-média,.prio-media{background:rgba(245,158,11,.16);color:#fcd34d}
  .prio-baixa{background:var(--card);color:var(--muted)}

  footer{margin-top:40px;text-align:center;color:var(--dim);font-size:11px}
  .hidden{display:none!important}
  @media(max-width:1200px){.kanban{grid-template-columns:1fr 1fr}.panels{grid-template-columns:1fr}}
  @media(max-width:860px){.app{grid-template-columns:1fr}.side{position:relative;height:auto}
    .kanban{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="app">
  <aside class="side">
    <div class="brand">
      <div class="logo">⌖</div>
      <div><div class="bt" id="brandTitle">north</div>
           <div class="bs">seu norte diário · multi-projeto</div></div>
    </div>
    <div class="nav-h">Visão</div>
    <button class="nav-item" data-go="overview" id="navOverview">
      <div class="nav-top"><span class="dot" style="background:var(--accent)"></span>
        <span class="nav-name">Todos os Projetos</span></div>
      <div class="nav-sub"><span>Portfólio consolidado</span></div>
    </button>
    <div class="nav-h">Projetos</div>
    <div id="navList"></div>
    <div class="side-foot">
      <div id="genFoot">—</div>
      <button class="theme-btn" id="themeBtn">◐ Alternar tema</button>
    </div>
  </aside>

  <main class="main" id="main"></main>
</div>

<script id="painel-data" type="application/json">/*__DATA__*/</script>
<script>
(function(){
  "use strict";
  const DATA = JSON.parse(document.getElementById("painel-data").textContent);
  const SPRINT_PAL = ["#0ea5e9","#8b5cf6","#ec4899","#14b8a6","#eab308","#f97316","#22c55e","#a78bfa"];
  const esc = s => String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const colColor = k => (DATA.columns.find(c=>c.key===k)||{}).color || "#64748b";
  let state = {view:"overview", project:null, filter:new Set(), q:""};

  /* ---------- sidebar ---------- */
  function renderNav(){
    document.getElementById("brandTitle").textContent = DATA.meta.title.split(" ")[0] || "Central";
    const idn=DATA.meta.identity||{};
    const who=idn.github?("@"+idn.github):(idn.name||"");
    document.getElementById("genFoot").innerHTML =
      (who?('<span style="color:var(--accent2)">⎇ '+esc(who)+'</span><br>'):"")+
      "Gerado: "+esc(DATA.meta.generated)+"<br>"+DATA.totals.projects+" projetos · "+
      DATA.totals.commits+" commits hoje";
    const list = document.getElementById("navList");
    list.innerHTML = DATA.projects.map(p=>{
      const r=p.rollup, nb=[];
      if(p.blockers.length) nb.push('<span class="nav-badge bg-bad">'+p.blockers.length+' blk</span>');
      if(p.debt.length) nb.push('<span class="nav-badge bg-warn">'+p.debt.length+' dt</span>');
      return '<button class="nav-item" data-pid="'+esc(p.id)+'" style="--ni:'+p.color+'">'+
        '<div class="nav-top"><span class="dot" style="background:'+p.color+'"></span>'+
        '<span class="nav-name">'+esc(p.name)+'</span><span class="nav-pct">'+r.pct+'%</span></div>'+
        '<div class="nav-bar"><i style="width:'+r.pct+'%;background:'+p.color+'"></i></div>'+
        '<div class="nav-sub"><span>'+r.done+'/'+r.total+' '+(r.level==="task"?"tasks":"sprints")+
        '</span><span>'+nb.join(" ")+'</span></div></button>';
    }).join("");
    bindNav();
  }
  function bindNav(){
    document.getElementById("navOverview").onclick=()=>{state.view="overview";render();};
    document.querySelectorAll("[data-pid]").forEach(b=>b.onclick=()=>{
      state.view="project";state.project=b.dataset.pid;state.filter.clear();state.q="";render();});
  }
  function highlightNav(){
    document.querySelectorAll(".nav-item").forEach(n=>n.classList.remove("active"));
    if(state.view==="overview") document.getElementById("navOverview").classList.add("active");
    else{const b=document.querySelector('[data-pid="'+CSS.escape(state.project)+'"]'); if(b)b.classList.add("active");}
  }

  /* ---------- inbox (captura /btw) ---------- */
  const TAG_EMOJI={idea:"💡",meeting:"🗣️",todo:"✅",question:"❓"};
  function inboxSection(){
    const items=DATA.inbox||[];
    if(!items.length) return "";
    const rows=items.map(e=>'<div class="ib-item"><span class="ib-tag">'+(TAG_EMOJI[e.tag]||"•")+
      '</span><span class="ib-id">'+esc(e.id)+'</span><span class="ib-text">'+esc(e.text)+'</span>'+
      (e.project?'<span class="ib-proj">'+esc(e.project)+'</span>':'')+
      '<span class="ib-date">'+esc(e.date)+'</span></div>').join("");
    return '<div class="sec-h">🗒️ Inbox de ideias <span class="ln"></span>'+
      '<span style="font-size:11px;color:var(--dim)">'+items.length+' p/ revisar · /btw captura · /inbox tria</span></div>'+
      '<div class="ib-box">'+rows+'</div>';
  }

  /* ---------- banner de foco (direcao) ---------- */
  function focusBanner(){
    const f=DATA.focus;
    if(!f) return "";
    const wip=(f.wip||[]).map(w=>'<span class="focus-wip">⚠ '+esc(w.project)+': '+w.count+
      ' em andamento (limite '+w.limit+') — feche antes de abrir</span>').join("");
    const alts=(f.alts||[]).length?('<div class="focus-alts"><b>Se travar:</b> '+
      f.alts.map(a=>esc(a.id)+' ('+esc(a.project)+')').join(" · ")+'</div>'):"";
    const why=(f.reasons||[]).length?'<div class="focus-why">Por quê: '+esc(f.reasons.join("; "))+'</div>':"";
    const warn=f.actionable?"":'<div class="focus-wip" style="margin-top:8px">⚠ A de maior valor está BLOQUEADA — resolva o bloqueio ou pegue uma alternativa.</div>';
    return '<div class="focus" data-go="'+esc(f.projectId)+'">'+
      '<div class="focus-h">🧭 Foco agora — sua próxima ação</div>'+
      '<div class="focus-task"><span class="focus-id">'+esc(f.id)+'</span>'+
      '<span class="focus-proj" style="background:'+f.color+'">'+esc(f.project)+' · '+esc(f.sprint)+'</span></div>'+
      '<div class="focus-desc">'+esc(f.desc)+'</div>'+why+
      '<div class="focus-cta"><span class="focus-squad">▷ /'+esc(f.squad)+'</span>'+wip+'</div>'+
      warn+alts+'</div>';
  }

  /* ---------- overview ---------- */
  function viewOverview(){
    const t=DATA.totals;
    const kpis=[
      ['acc',t.pct+'%','Progresso global'],
      ['', t.done+'/'+t.total,'TASKs concluídas'],
      ['', t.projects,'Projetos ativos'],
      [t.commits?'ok':'', t.commits,'Commits hoje'],
      [t.blockers?'bad':'ok', t.blockers,'Bloqueios abertos'],
      [t.debt?'warn':'', t.debt,'Débito técnico'],
    ].map(k=>'<div class="kpi '+k[0]+'"><div class="v">'+k[1]+'</div><div class="l">'+k[2]+'</div></div>').join("");

    const cards=DATA.projects.map(p=>{
      const r=p.rollup;
      const stats=[];
      stats.push('<span class="pill"><b>'+p.sprints.length+'</b> sprints</span>');
      if(p.blockers.length) stats.push('<span class="pill" style="border-color:var(--bad);color:#fca5a5"><b>'+p.blockers.length+'</b> bloqueios</span>');
      if(p.debt.length) stats.push('<span class="pill"><b>'+p.debt.length+'</b> débito</span>');
      const foot=p.author?('↻ '+esc(p.author.name.split(" ")[0])+' · '+esc(p.author.when)):
        (p.todayCommits.length?('● '+p.todayCommits.length+' commit(s) hoje'):
        (p.dirty?('○ '+p.dirty+' sujos'):'sem mudança'));
      return '<div class="pcard" data-pid="'+esc(p.id)+'" style="--pc:'+p.color+'">'+
        '<div class="pcard-h">'+
          '<div class="donut" style="--p:'+r.pct+';--pc:'+p.color+'"><span style="color:'+p.color+'">'+r.pct+'%</span></div>'+
          '<div><div class="pcard-t">'+esc(p.name)+'</div>'+
          '<div class="pcard-s">'+r.done+'/'+r.total+' '+(r.level==="task"?"tasks":"sprints")+' · '+esc(p.currentSprint).slice(0,42)+'</div>'+
          '<div class="pcard-stats">'+stats.join("")+'</div></div></div>'+
        '<div class="pcard-foot"><span class="branch">⎇ '+esc(p.branch)+'</span><span title="última atualização">'+esc(foot)+'</span></div>'+
        '</div>';
    }).join("");

    return '<div class="top"><div><h1>'+esc(DATA.meta.title)+' <small>— portfólio</small></h1>'+
      '<div class="gen">Visão consolidada de todos os projetos rastreados</div></div></div>'+
      focusBanner()+
      '<div class="kpis">'+kpis+'</div>'+
      '<div class="sec-h">Projetos <span class="ln"></span></div>'+
      '<div class="grid">'+cards+'</div>'+
      inboxSection()+footer();
  }

  /* ---------- projeto ---------- */
  function viewProject(){
    const p=DATA.projects.find(x=>x.id===state.project);
    if(!p) {state.view="overview"; return viewOverview();}
    const r=p.rollup;

    const meta='<div class="pmeta">'+
      '<span class="pill">⎇ <b class="mono">'+esc(p.branch)+'</b></span>'+
      '<span class="pill">Sprint atual: <b>'+esc(p.currentSprint).slice(0,46)+'</b></span>'+
      (p.author?'<span class="pill">↻ última: <b>'+esc(p.author.name.split(" ")[0])+'</b> · '+esc(p.author.when)+'</span>':'')+
      (p.contributors&&p.contributors.length?'<span class="pill">👥 time: <b>'+esc(p.contributors.map(c=>c.split(" ")[0]).join(", "))+'</b></span>':'')+
      (p.todayCommits.length?'<span class="pill" style="border-color:var(--ok)">● <b>'+p.todayCommits.length+'</b> commit(s) hoje</span>':'')+
      (p.dirty?'<span class="pill" style="border-color:var(--warn)">○ <b>'+p.dirty+'</b> não commitado(s)</span>':'')+
      '</div>';

    const kpis=[
      ['acc',r.pct+'%','Progresso'],
      ['', r.done+'/'+r.total,(r.level==="task"?'TASKs':'Sprints')+' done'],
      [p.blockers.length?'bad':'ok', p.blockers.length,'Bloqueios'],
      [p.debt.length?'warn':'', p.debt.length,'Débito técnico'],
    ].map(k=>'<div class="kpi '+k[0]+'"><div class="v">'+k[1]+'</div><div class="l">'+k[2]+'</div></div>').join("");

    const cur=p.currentSprint;
    const scards=p.sprints.map((s,i)=>{
      const col=SPRINT_PAL[i%SPRINT_PAL.length];
      const isCur=cur && (cur.indexOf(s.key.replace(/^S/,''))>=0 || cur.toUpperCase().indexOf(s.key)>=0);
      const frac=(s.done!=null&&s.total!=null)?(s.done+'/'+s.total+' tasks'):(colLabel(s.col));
      return '<div class="scard'+(isCur?' cur':'')+'">'+
        '<div class="scard-h"><span class="skey" style="background:'+col+'">'+esc(s.key)+'</span>'+
        (isCur?'<span class="snow">ATUAL</span>':'')+(s.blocked?'<span class="blocked-tag">BLOQ</span>':'')+'</div>'+
        '<div class="sname">'+esc(s.name||'—')+'</div>'+
        '<div class="bar"><i style="width:'+s.pct+'%;background:'+col+'"></i></div>'+
        '<div class="scard-f"><b>'+s.pct+'%</b><span>'+esc(frac)+'</span></div>'+
        (s.author?'<div class="scard-by">↻ '+esc(s.author.name.split(" ")[0])+' · '+esc(s.author.when)+'</div>':'')+
        '</div>';
    }).join("") || '<div class="empty">Sem sprints detectados neste projeto.</div>';

    let body='<div class="top"><div><h1>'+esc(p.name)+' <small>— acompanhamento</small></h1>'+
      meta+'</div><div class="gen">Gerado '+esc(DATA.meta.generated)+'</div></div>'+
      '<div class="kpis">'+kpis+'</div>'+
      '<div class="sec-h">Sprints <span class="ln"></span></div>'+
      '<div class="sprints">'+scards+'</div>';

    if(p.tasks.length){
      body+='<div class="sec-h">Quadro de Tarefas <span class="ln"></span></div>'+toolbar(p)+kanban(p);
    }
    body+='<div class="panels">'+blockersPanel(p)+debtPanel(p)+'</div>'+footer();
    return body;
  }
  function colLabel(c){return (DATA.columns.find(x=>x.key===c)||{}).key||c;}

  function toolbar(p){
    const chips=DATA.columns.map(c=>{
      const on=state.filter.has(c.key);
      return '<span class="chip'+(on?' on':'')+'" data-col="'+esc(c.key)+'" style="'+
        (on?'background:'+c.color:'')+'">'+c.emoji+' '+esc(c.key)+'</span>';
    }).join("");
    return '<div class="toolbar"><input class="search" id="search" placeholder="Buscar TASK por id ou descrição…" value="'+esc(state.q)+'">'+chips+'</div>';
  }

  function kanban(p){
    const q=state.q.toLowerCase();
    const cols=DATA.columns.map(c=>{
      let ts=p.tasks.filter(t=>t.col===c.key);
      if(q) ts=ts.filter(t=>(t.id+" "+t.desc+" "+t.owner).toLowerCase().indexOf(q)>=0);
      const cards=ts.map(t=>{
        const sc=SPRINT_PAL[Math.max(0,p.sprints.findIndex(s=>s.key===t.sprint))%SPRINT_PAL.length];
        return '<div class="card'+(t.blocked?' blk':'')+'" style="border-left-color:'+sc+'">'+
          '<div class="card-t"><span class="tid">'+esc(t.id)+'</span>'+
          '<span class="stag" style="background:'+sc+'22;color:'+sc+'">'+esc(t.sprint)+'</span></div>'+
          '<div class="cdesc">'+esc((t.desc||t.statusRaw||'').slice(0,150))+'</div>'+
          '<div class="card-f"><span class="owner">'+esc(t.owner||'')+(t.blocked?' · ⛔ bloqueada':'')+'</span>'+
          (t.commit?'<span class="commit">'+esc(t.commit)+'</span>':'')+'</div></div>';
      }).join("") || '<div class="empty">—</div>';
      const hide=(state.filter.size && !state.filter.has(c.key))?' style="display:none"':'';
      return '<div class="kcol"'+hide+'><div class="kcol-h" style="border-top-color:'+c.color+'">'+
        '<span>'+c.emoji+' '+esc(c.key)+'</span><span class="cnt">'+ts.length+'</span></div>'+
        '<div class="kcol-b">'+cards+'</div></div>';
    }).join("");
    return '<div class="kanban">'+cols+'</div>';
  }

  function blockersPanel(p){
    const rows=p.blockers.length? p.blockers.map(b=>'<tr><td class="k">'+esc(b.id)+'</td>'+
      '<td>'+esc(b.desc.slice(0,110))+'</td><td>'+esc(b.status.slice(0,60))+'</td></tr>').join("")
      : '<tr><td colspan="3" class="empty">Nenhum bloqueio aberto 🎉</td></tr>';
    return '<div class="panel"><h3>🚧 Bloqueios Ativos <span class="c">('+p.blockers.length+')</span></h3>'+
      '<table><tr><th>ID</th><th>Bloqueio</th><th>Status</th></tr>'+rows+'</table></div>';
  }
  function debtPanel(p){
    const rows=p.debt.length? p.debt.map(d=>'<tr><td class="k">'+esc(d.id)+'</td>'+
      '<td>'+esc(d.desc.slice(0,95))+'</td><td>'+esc(d.sprint)+'</td>'+
      '<td><span class="prio prio-'+esc(d.prio||'baixa')+'">'+esc(d.prio||'—')+'</span></td></tr>').join("")
      : '<tr><td colspan="4" class="empty">Sem débito aberto</td></tr>';
    return '<div class="panel"><h3>📋 Débito Técnico <span class="c">('+p.debt.length+')</span></h3>'+
      '<table><tr><th>ID</th><th>Descrição</th><th>Sprint</th><th>Prio</th></tr>'+rows+'</table></div>';
  }

  function footer(){
    return '<footer>Central de Produtividade · fonte única: arquivos <span class="mono">plan-build/*.md</span> · '+
      'nenhum dado é editado, apenas lido · '+esc(DATA.meta.generated)+'</footer>';
  }

  /* ---------- render + binds ---------- */
  function render(){
    const m=document.getElementById("main");
    m.innerHTML = state.view==="overview"? viewOverview() : viewProject();
    highlightNav();
    // binds intra-main
    m.querySelectorAll(".pcard[data-pid]").forEach(c=>c.onclick=()=>{
      state.view="project";state.project=c.dataset.pid;state.filter.clear();state.q="";render();});
    const fb=m.querySelector(".focus[data-go]");
    if(fb) fb.style.cursor="pointer", fb.onclick=()=>{
      state.view="project";state.project=fb.dataset.go;state.filter.clear();state.q="";render();};
    const s=document.getElementById("search");
    if(s) s.oninput=e=>{state.q=e.target.value; rerenderKanban();};
    m.querySelectorAll(".chip[data-col]").forEach(ch=>ch.onclick=()=>{
      const k=ch.dataset.col; state.filter.has(k)?state.filter.delete(k):state.filter.add(k); render();});
  }
  function rerenderKanban(){
    // re-render so o kanban, preservando foco no input
    const p=DATA.projects.find(x=>x.id===state.project); if(!p)return;
    const wrap=document.querySelector(".kanban");
    if(wrap){const tmp=document.createElement("div");tmp.innerHTML=kanban(p);wrap.replaceWith(tmp.firstChild);}
  }

  document.getElementById("themeBtn").onclick=()=>{
    const h=document.documentElement;
    h.dataset.theme = h.dataset.theme==="dark" ? "light":"dark";
  };

  renderNav();
  render();
})();
</script>
</body>
</html>"""
