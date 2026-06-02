# -*- coding: utf-8 -*-
"""
bom-dia.py — Ritual de início de dia (100% local, sem 365/Monday).

Faz:
  1. Regenera o dashboard.html.
  2. Calcula e imprime o FOCO DO DIA: TASKs do sprint atual ainda abertas +
     próximas TASKs já desbloqueadas + bloqueios que pedem ação + pendências de
     alta prioridade.
  3. Abre o dashboard no navegador.

Uso:  python bom-dia.py
"""

import importlib.util
import os
import re
import sys
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).resolve().parent                  # .../Barramento/dashboard
ROOT = HERE.parent                                       # .../Barramento
MODULE_DIR = ROOT / "backoffice" / "CALCULO-COBRANCA"
DASH_HTML = HERE / "dashboard.html"


def load_generator():
    spec = importlib.util.spec_from_file_location("gen_dash", HERE / "generate-dashboard.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_startable(task):
    """TASK planejada cujas dependências já não travam (sem deps)."""
    deps = task.get("deps", "").strip()
    return task["col"] == "Planejado" and deps in ("—", "-", "", "–")


# Mapa: tipo-de-trabalho (palavras-chave na descrição/coluna da TASK) -> plugins
# instalados que agregam valor naquele tipo de trabalho. Ordem = prioridade.
TOOL_RULES = [
    (r"\btest|teste|smoke|parida|integration|idempot|xunit|cobertura|mock",
     "code-review (revisar diff antes do PR) + csharp-lsp"),
    (r"front|tela|component|react|next|css|tailwind|\bui\b|\bux\b|layout|p[aá]gina|formul",
     "context7 (docs live da lib) + frontend-design"),
    (r"auth|jwt|oauth|seguran|lgpd|secret|cors|permiss|hardening",
     "security-review (OWASP/LGPD) + microsoft-docs"),
    (r"domain|application|infrastr|calculator|handler|query|reposit|ef ?core|"
     r"migration|grpc|proto|endpoint|\bapi\b|worker|dbcontext|c#|\.net",
     "csharp-lsp (navegação semântica) + microsoft-docs (.NET/EF/ASP.NET)"),
]


def recommend_tools(tasks, clean):
    """Dado o conjunto de TASKs do foco, devolve a lista de ferramentas
    recomendadas (sem duplicar), preservando a ordem de prioridade das regras."""
    out = []
    for label_re, label in TOOL_RULES:
        rx = re.compile(label_re, re.IGNORECASE)
        for t in tasks:
            hay = f"{clean(t['desc'])} {t.get('col', '')}"
            if rx.search(hay):
                if label not in out:
                    out.append(label)
                break
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # console limpo em qualquer terminal Windows
    except Exception:
        pass

    gd = load_generator()
    gd.main()  # regenera o dashboard

    sprint_status, tasks, blockers, debt, meta = gd.collect()
    total = len(tasks)
    done = sum(1 for t in tasks if t["col"] == "Done")
    pct = round(done / total * 100) if total else 0

    cur_key_m = re.search(r"(CC\d+)", meta["current_sprint"])
    cur_key = cur_key_m.group(1) if cur_key_m else ""

    # remanescentes do sprint atual (não-Done)
    remaining = sorted(
        [t for t in tasks if t["sprint"] == cur_key and t["col"] != "Done"],
        key=lambda t: t["id"],
    )
    # próximas já desbloqueadas (qualquer sprint), excluindo o atual já listado
    startable = sorted(
        [t for t in tasks if is_startable(t) and t["sprint"] != cur_key],
        key=lambda t: t["id"],
    )
    open_blk = [b for b in blockers if not b["resolved"]]
    high_debt = [d for d in debt if not d["closed"] and d["prio"].lower() == "alta"]

    now = datetime.now()
    L = []
    L.append("")
    L.append("=" * 64)
    L.append(f"  BOM DIA, KAYQUE — {now.strftime('%d/%m/%Y')}")
    L.append("=" * 64)
    L.append(f"  Sprint atual: {cur_key}   |   Progresso global: {pct}% ({done}/{total} TASKs)")
    L.append("")

    L.append("  FOCO DE HOJE")
    L.append("  " + "-" * 30)
    if remaining:
        L.append(f"  > Fechar o sprint {cur_key} ({len(remaining)} TASK(s) em aberto):")
        for t in remaining:
            short = gd.clean_desc(t["desc"])[:70]
            L.append(f"      [{t['col']:>16}] {t['id']}  {short}")
    else:
        L.append(f"  > Sprint {cur_key} fechado. Atacar próximo sprint.")
    if startable:
        L.append("")
        L.append("  > Próximas TASKs já desbloqueadas (sem dependência pendente):")
        for t in startable[:4]:
            short = gd.clean_desc(t["desc"])[:70]
            L.append(f"      [{t['sprint']}] {t['id']}  {short}")
    L.append("")

    # Ferramentas recomendadas para o que vai ser atacado hoje.
    focus_tasks = remaining if remaining else startable[:2]
    tools = recommend_tools(focus_tasks, gd.clean_desc)
    if tools:
        L.append("  FERRAMENTAS PARA O FOCO")
        L.append("  " + "-" * 30)
        for tip in tools:
            L.append(f"      -> {tip}")
        L.append("")

    L.append("  BLOQUEIOS QUE PEDEM AÇÃO")
    L.append("  " + "-" * 30)
    if open_blk:
        for b in open_blk:
            L.append(f"      {b['id']}: {gd.clean_desc(b['desc'])[:75]}")
    else:
        L.append("      Nenhum bloqueio aberto.")
    L.append("")

    if high_debt:
        L.append("  PENDÊNCIAS DE ALTA PRIORIDADE")
        L.append("  " + "-" * 30)
        for d in high_debt:
            L.append(f"      {d['id']}: {gd.clean_desc(d['desc'])[:75]}")
        L.append("")

    L.append("=" * 64)
    L.append(f"  Dashboard atualizado e abrindo no navegador.")
    L.append("=" * 64)
    print("\n".join(L))

    # abre o board
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(DASH_HTML))  # noqa
        elif sys.platform == "darwin":
            os.system(f'open "{DASH_HTML}"')
        else:
            os.system(f'xdg-open "{DASH_HTML}"')
    except Exception as e:
        print(f"  (não consegui abrir o navegador automaticamente: {e})")
        print(f"  Abra manualmente: {DASH_HTML}")


if __name__ == "__main__":
    main()
