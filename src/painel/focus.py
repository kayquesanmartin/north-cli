# -*- coding: utf-8 -*-
"""
focus.py — motor de DIREÇÃO ("o que faço agora?") + WIP guard.

Coluna 1 do north: tira a fadiga de decisão. Dado o estado de todos os projetos,
escolhe A próxima ação de maior valor e explica o porquê — respeitando o
princípio ágil de "termine antes de começar" (WIP).

Heuristica de score (maior = mais urgente fazer agora):
  - Em Andamento  : +100  (nao deixe pela metade)
  - Codigo Completo: +90  (quase la — empurre pro Done / review)
  - Planejado     : +40
  + sprint atual  : +50
  + desbloqueada  : +15   (Planejado sem dependencia pendente)
  - bloqueada     : -1000 (nao da pra agir agora)
  - tem dependencia pendente (Planejado): -25
"""

import re

from . import parsers as P

WIP_LIMIT = 3  # acima disso, alerta para fechar antes de abrir

# Palavra-chave -> squad sugerido (ordem = prioridade de match)
SQUAD_RULES = [
    (r"\btest|teste|smoke|xunit|cobertura|mock|qa\b", "squad-qa"),
    (r"auth|jwt|oauth|seguran|lgpd|secret|cors|permiss|hardening|owasp", "squad-security"),
    (r"docker|deploy|pipeline|\bci\b|infra|kubernetes|nginx|compose|harness", "squad-devops"),
    (r"front|tela|component|react|next|css|tailwind|\bui\b|\bux\b|layout|p[aá]gina|formul", "squad-frontend"),
    (r"custo|performance|otimiz|query lenta|\bcache\b|redis", "squad-finops"),
    (r"adr|contrato|arquitet|modela|design de|spec\b", "squad-arquitetura"),
    (r"domain|application|infrastr|handler|query|reposit|ef ?core|migration|"
     r"grpc|proto|endpoint|\bapi\b|worker|dbcontext|c#|\.net|controller|service", "squad-backend"),
]


def suggest_squad(text: str) -> str:
    for rx_s, squad in SQUAD_RULES:
        if re.search(rx_s, text or "", re.I):
            return squad
    return "squad-backend"


def _current_sprint_keys(project):
    """Chaves de sprint que aparecem no 'Sprint Atual' do projeto."""
    cur = (project.get("current_sprint") or "").upper()
    keys = set()
    for s in project["sprints"]:
        k = s["key"].upper()
        if k in cur or k.replace("S", "", 1) in cur:
            keys.add(s["key"])
    return keys


def score_task(t, cur_keys):
    if t["col"] == P.COL_DONE:
        return None
    base = {P.COL_ANDAMENTO: 100, P.COL_CODIGO: 90, P.COL_PLANEJADO: 40}.get(t["col"], 30)
    score = base
    reasons = []
    if t["sprint"] in cur_keys:
        score += 50
        reasons.append("sprint atual")
    if t["blocked"]:
        score -= 1000
        reasons.append("BLOQUEADA")
    deps = (t.get("deps") or "").strip()
    has_dep = deps not in ("", "—", "-", "–")
    if t["col"] == P.COL_PLANEJADO:
        if has_dep:
            score -= 25
            reasons.append("tem dependência")
        else:
            score += 15
            reasons.append("desbloqueada")
    if t["col"] == P.COL_ANDAMENTO:
        reasons.insert(0, "em andamento — não deixe pela metade")
    elif t["col"] == P.COL_CODIGO:
        reasons.insert(0, "código pronto — empurre pro review/Done")
    return score, reasons


def compute_focus(projects, wip_limit=WIP_LIMIT):
    """Devolve estrutura de foco: pick global, alternativas, alertas de WIP."""
    scored = []
    wip_alerts = []
    for p in projects:
        cur_keys = _current_sprint_keys(p)
        # peso de pertencimento: ranqueia o que VOCE esta tocando primeiro (soft —
        # nunca esconde nada). 0 quando nao ha sinal seu -> comporta como leitura pura.
        mine = p.get("mine", {}) or {}
        mine_boost = mine.get("score", 0) or 0
        mine_active = bool(mine.get("active"))
        mine_reason = ("seu foco ativo: " + "; ".join(mine.get("signals", []))) if mine_active else ""
        in_progress = [t for t in p["tasks"] if t["col"] == P.COL_ANDAMENTO and not t["blocked"]]
        if len(in_progress) > wip_limit:
            wip_alerts.append({
                "project": p["name"],
                "count": len(in_progress),
                "limit": wip_limit,
            })
        for t in p["tasks"]:
            sc = score_task(t, cur_keys)
            if sc is None:
                continue
            score, reasons = sc
            score += mine_boost
            if mine_reason:
                reasons = reasons + [mine_reason]
            scored.append({
                "score": score,
                "reasons": reasons,
                "project": p["name"],
                "project_id": p["id"],
                "color": p["color"],
                "task": t,
                "squad": suggest_squad(t["desc"] + " " + t.get("status_raw", "")),
                "actionable": not t["blocked"],
                "mine": mine_active,
            })

    scored.sort(key=lambda x: (-x["score"], x["project"], x["task"]["id"]))
    actionable = [s for s in scored if s["actionable"]]
    pick = actionable[0] if actionable else (scored[0] if scored else None)

    # alternativas: proximas acionaveis de OUTRA task/projeto
    alts = []
    seen = {pick["task"]["id"]} if pick else set()
    for s in actionable[1:]:
        if s["task"]["id"] in seen:
            continue
        seen.add(s["task"]["id"])
        alts.append(s)
        if len(alts) >= 4:
            break

    blocked = [s for s in scored if not s["actionable"]]

    return {"pick": pick, "alts": alts, "wip_alerts": wip_alerts, "blocked": blocked}


def build_focus_text(projects, wip_limit=WIP_LIMIT):
    f = compute_focus(projects, wip_limit)
    L = []
    bar = "=" * 64
    L.append("")
    L.append(bar)
    L.append("  NORTH · FOCO AGORA")
    L.append(bar)

    pick = f["pick"]
    if not pick:
        L.append("  Nenhuma task aberta nos projetos ativos. Tudo fechado! 🎉")
        L.append(bar)
        return "\n".join(L)

    t = pick["task"]
    L.append("  Sua próxima ação:")
    L.append("    ▸ [{} · {}] {}".format(pick["project"], t["sprint"] or "—", t["id"]))
    L.append("      {}".format(P.clean_desc(t["desc"])[:72] or t.get("status_raw", "")[:72]))
    if pick["reasons"]:
        L.append("      Por quê: {}".format("; ".join(pick["reasons"])))
    L.append("      Squad sugerido: /{}".format(pick["squad"].replace("squad-", "squad ")))
    if not pick["actionable"]:
        L.append("      ⚠ Atenção: a de maior valor está BLOQUEADA — resolva o bloqueio ou pegue uma alternativa.")

    if f["wip_alerts"]:
        L.append("  " + "-" * 50)
        for w in f["wip_alerts"]:
            L.append("  ⚠ WIP: {} tem {} tasks 'Em Andamento' (limite {}) — termine antes de começar novas.".format(
                w["project"], w["count"], w["limit"]))

    if f["alts"]:
        L.append("  " + "-" * 50)
        L.append("  Se travar, alternativas já desbloqueadas:")
        for s in f["alts"]:
            st = s["task"]
            L.append("    - [{} · {}] {}  {}".format(
                s["project"], st["sprint"] or "—", st["id"], P.clean_desc(st["desc"])[:50]))

    L.append(bar)
    return "\n".join(L)
