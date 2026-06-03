# -*- coding: utf-8 -*-
"""
rituals.py — bom-dia e fim-do-dia, agora multi-projeto.

bom-dia  : regenera o painel + imprime o FOCO DO DIA consolidado (todos os
           projetos): tasks do sprint atual abertas, proximas desbloqueadas,
           bloqueios que pedem acao, debito de alta prioridade + ferramentas.
fim-do-dia: regenera o painel + gera um RESUMO-DO-DIA central por projeto
           (e espelha em <proj>/docs quando existir).
"""

import re
from datetime import datetime
from pathlib import Path

from . import parsers as P


# Ferramentas recomendadas por tipo de trabalho (heuristica por palavra-chave)
TOOL_RULES = [
    (r"\btest|teste|smoke|parida|integration|idempot|xunit|cobertura|mock",
     "code-review (revisar o diff antes do PR)"),
    (r"front|tela|component|react|next|css|tailwind|\bui\b|\bux\b|layout|p[aá]gina|formul",
     "frontend-design + context7 (docs live da lib)"),
    (r"auth|jwt|oauth|seguran|lgpd|secret|cors|permiss|hardening",
     "squad-security (OWASP/LGPD) + security-review"),
    (r"domain|application|infrastr|calculator|handler|query|reposit|ef ?core|"
     r"migration|grpc|proto|endpoint|\bapi\b|worker|dbcontext|c#|\.net",
     "microsoft-docs (.NET/EF/ASP.NET) + csharp-lsp"),
    (r"docker|deploy|pipeline|ci\b|infra|kubernetes|nginx|compose",
     "squad-devops"),
]


def _recommend_tools(tasks):
    out = []
    for rx_s, label in TOOL_RULES:
        rx = re.compile(rx_s, re.I)
        for t in tasks:
            if rx.search((t.get("desc", "") + " " + t.get("status_raw", ""))):
                if label not in out:
                    out.append(label)
                break
    return out


def _startable(t):
    deps = (t.get("deps") or "").strip()
    return t["col"] == P.COL_PLANEJADO and deps in ("", "—", "-", "–")


def build_bom_dia(projects, owner="Kayque"):
    now = datetime.now()
    total = sum(p["rollup"]["total"] for p in projects)
    done = sum(p["rollup"]["done"] for p in projects)
    pct = round(done / total * 100) if total else 0

    L = []
    bar = "=" * 66
    L.append("")
    L.append(bar)
    L.append("  BOM DIA, {} — {}".format(owner.upper(), now.strftime("%d/%m/%Y")))
    L.append(bar)
    L.append("  Portfolio: {} projeto(s) | progresso global {}% ({}/{} TASKs)".format(
        len(projects), pct, done, total))
    L.append("")

    all_focus = []
    for p in projects:
        cur = p["current_sprint"]
        cur_key = None
        km = re.search(r"(CC\d+|\d+[A-Z]?)", cur)
        # remanescentes do sprint atual
        remaining = []
        if p["tasks"]:
            # tenta casar pelo nome do sprint atual
            cur_norm = cur.upper()
            for t in p["tasks"]:
                if t["col"] != P.COL_DONE and (
                        t["sprint"] in cur_norm or t["sprint"].replace("S", "") in cur_norm):
                    remaining.append(t)
            remaining = sorted(remaining, key=lambda t: t["id"])
        startable = sorted([t for t in p["tasks"] if _startable(t)], key=lambda t: t["id"])
        open_blk = p["open_blockers"]
        high_debt = [d for d in p["open_debt"] if d["prio"] == "alta"]

        if not (remaining or startable or open_blk or high_debt):
            continue

        L.append("  ▸ {}  [{}%]".format(p["name"], p["rollup"]["pct"]))
        L.append("  " + "-" * 50)
        if remaining:
            L.append("    Fechar sprint atual ({} aberta(s)):".format(len(remaining)))
            for t in remaining[:6]:
                L.append("      [{:>14}] {}  {}".format(t["col"], t["id"], t["desc"][:58]))
            all_focus.extend(remaining)
        elif startable:
            L.append("    Proximas desbloqueadas:")
            for t in startable[:4]:
                L.append("      [{}] {}  {}".format(t["sprint"], t["id"], t["desc"][:58]))
            all_focus.extend(startable[:4])
        if open_blk:
            L.append("    Bloqueios:")
            for b in open_blk[:4]:
                L.append("      {} {}".format((b["id"] + ":") if b["id"] else "-", b["desc"][:62]))
        if high_debt:
            L.append("    Debito ALTA:")
            for d in high_debt[:4]:
                L.append("      {}: {}".format(d["id"], d["desc"][:62]))
        L.append("")

    if not all_focus and not any(p["open_blockers"] for p in projects):
        L.append("  Tudo tranquilo — nenhum foco urgente detectado. Bom dia! ☕")
        L.append("")

    tools = _recommend_tools(all_focus)
    if tools:
        L.append("  FERRAMENTAS / SQUADS PARA O FOCO DE HOJE")
        L.append("  " + "-" * 50)
        for tip in tools:
            L.append("      -> {}".format(tip))
        L.append("")

    sync_lines = []
    for p in projects:
        sy = (p["git"] or {}).get("sync", {}) or {}
        bits = []
        if sy.get("behind"):
            bits.append("{} atras de {}".format(sy["behind"], sy.get("upstream") or "upstream"))
        if sy.get("base_behind"):
            bits.append("{} atras de {}".format(sy["base_behind"], sy.get("base") or "base"))
        if bits:
            sync_lines.append("    {} — {} (rode: git pull --rebase antes de novos commits)".format(
                p["name"], "; ".join(bits)))
    if sync_lines:
        L.append("  ⚠ VERSIONAMENTO — atualize antes de trabalhar (evita conflito)")
        L.append("  " + "-" * 50)
        L.extend(sync_lines)
        L.append("")

    L.append(bar)
    L.append("  Painel atualizado e abrindo no navegador.")
    L.append(bar)
    return "\n".join(L)


def _derive_status(text):
    s = (text or "").upper()
    if "VERDE" in s or "CODIGO COMPLETO" in s or "CÓDIGO COMPLETO" in s:
        return "Em revisão / Em QA"
    if "COMPLETO" in s or "CONCLU" in s or "✅" in (text or ""):
        return "Aguardando aceite"
    if "BLOQUEAD" in s:
        return "Bloqueado"
    return "Em desenvolvimento"


def build_resumo_projeto(p, data_br):
    git = p["git"]
    commits = git["today_commits"]
    dirty = git["dirty"]
    r = p["rollup"]

    if commits:
        resumo = "{} commit(s) hoje. {} — progresso {}% ({}/{} {}).".format(
            len(commits), p["name"], r["pct"], r["done"], r["total"],
            "TASKs" if r["level"] == "task" else "sprints")
        entregue = "\n".join("- {}  ({})".format(s, h) for h, s in commits)
        revisao = ("- [PREENCHER via /code-review] rodar a revisao no diff do dia e resumir: "
                   "n de achados, severidade e acao. Sem achados -> \"limpo\".")
    elif dirty:
        resumo = "Trabalho em andamento ({} arquivo(s) nao commitados). {} — {}% ({}/{}).".format(
            dirty, p["name"], r["pct"], r["done"], r["total"])
        entregue = "- Alteracoes em {} arquivo(s) ainda nao commitadas (revisar `git status`).".format(dirty)
        revisao = "- [PREENCHER via /code-review] revisar o diff ainda nao commitado."
    else:
        resumo = "Sem alteracoes de codigo hoje. {} — {}% ({}/{}).".format(
            p["name"], r["pct"], r["done"], r["total"])
        entregue = "- [PREENCHER] nenhum commit detectado hoje — descrever avanco manual se houver."
        revisao = "- Sem alteracoes de codigo para revisar hoje."

    sy = git.get("sync", {}) or {}
    if (sy.get("behind") or 0) or (sy.get("base_behind") or 0):
        ref = sy.get("upstream") or sy.get("base") or "o remoto"
        entregue += "\n- ANTES DE PUSHAR: {} esta a frente — rode `git pull --rebase` para evitar conflito.".format(ref)
    elif (sy.get("ahead") or 0):
        entregue += "\n- {} commit(s) local(is) ainda nao pushado(s).".format(sy["ahead"])

    open_blk = p["open_blockers"]
    bloqueios = ("\n".join("- {} {}".format((b["id"] + ":") if b["id"] else "-", b["desc"][:110])
                           for b in open_blk) if open_blk else "- Nenhum")

    nxt = next((t for t in sorted(p["tasks"], key=lambda t: t["id"]) if t["col"] == P.COL_PLANEJADO), None)
    if nxt:
        proximos = "- {} ({}): {}".format(nxt["id"], nxt["sprint"], nxt["desc"][:90])
        if nxt.get("owner"):
            proximos += "\n- Responsavel: {}".format(nxt["owner"])
    else:
        proximos = "- [PREENCHER] definir proxima TASK"

    status_line = _derive_status(p["current_sprint"])
    branch = p["branch"]

    return """Atualizacao da entrega - {data} — {proj}

Resumo:
{resumo}

O que foi entregue:
{entregue}

Revisao do diff (code-review):
{revisao}

Estado atual:
- Status: {status}
- Ambiente: Dev
- Evidencias/links: dashboard.html (Central de Produtividade) · branch {branch}

Bloqueios/Riscos:
{bloqueios}

Proximos passos:
{proximos}
""".format(data=data_br, proj=p["name"], resumo=resumo, entregue=entregue,
           revisao=revisao, status=status_line, branch=branch,
           bloqueios=bloqueios, proximos=proximos)
