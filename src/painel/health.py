# -*- coding: utf-8 -*-
"""
health.py — sinais vitais do portfolio.

Deriva ALERTAS de risco a partir do estado atual de cada projeto (point-in-time,
sem precisar de historico). Sao os sinais que dizem "olha aqui antes de travar":

  - dirty   : muito arquivo nao commitado -> risco de perder trabalho
  - stale   : branch parada ha dias -> entrega estagnada
  - blocked : bloqueio aberto agora -> caminho critico travado
  - wip     : tasks demais "Em Andamento" -> viola "termine antes de comecar"

Contrato de um alerta (dict):
  {
    "kind":     "dirty" | "stale" | "blocked" | "wip",
    "severity": "risk" | "warn",          # risk = vermelho, warn = ambar
    "title":    str,                       # rotulo curto
    "detail":   str,                       # explicacao de uma linha
  }

Thresholds vem de settings (com defaults em config.DEFAULT_SETTINGS):
  dirty_risk_files, stale_branch_days, wip_limit.

OBS: metricas que precisam de SERIE TEMPORAL (velocity, burndown, aging WIP,
tendencia) NAO entram aqui — exigem um snapshot store que ainda nao existe.
Este modulo cobre so o que e computavel com o estado de hoje.
"""

from . import parsers as P

_SEV_ORDER = {"risk": 0, "warn": 1}


def compute_alerts(proj, settings):
    """Lista de alertas de saude do projeto, ordenada por severidade (risk antes)."""
    alerts = []
    git = proj.get("git", {}) or {}
    dirty = git.get("dirty", 0) or 0
    idle = git.get("idle_days")

    dirty_risk = settings.get("dirty_risk_files", 8)
    stale_days = settings.get("stale_branch_days", 3)
    wip_limit = settings.get("wip_limit", 3)

    # 1. Trabalho nao commitado em volume -> risco de perda
    if dirty >= dirty_risk:
        alerts.append({
            "kind": "dirty", "severity": "risk",
            "title": "Trabalho nao commitado",
            "detail": "{} arquivos sujos — commite para nao perder".format(dirty),
        })

    # 2. Branch parada (so faz sentido se o projeto tem historico git)
    if isinstance(idle, int) and idle >= stale_days:
        alerts.append({
            "kind": "stale", "severity": "warn",
            "title": "Branch parada",
            "detail": "{} dias sem commit".format(idle),
        })

    # 3. Bloqueio aberto agora -> caminho critico travado
    open_blk = proj.get("open_blockers", []) or []
    if open_blk:
        first = (open_blk[0].get("desc") or "").strip()
        alerts.append({
            "kind": "blocked", "severity": "risk",
            "title": "{} bloqueio(s) aberto(s)".format(len(open_blk)),
            "detail": first[:70] or "resolva o bloqueio do caminho critico",
        })

    # 4. WIP acima do limite (mesmo criterio do /focus: Em Andamento e nao bloqueada)
    wip = sum(1 for t in proj.get("tasks", [])
              if t.get("col") == P.COL_ANDAMENTO and not t.get("blocked"))
    if wip > wip_limit:
        alerts.append({
            "kind": "wip", "severity": "warn",
            "title": "WIP acima do limite",
            "detail": "{} tasks 'Em Andamento' (limite {}) — termine antes de comecar".format(
                wip, wip_limit),
        })

    alerts.sort(key=lambda a: _SEV_ORDER.get(a["severity"], 9))
    return alerts
