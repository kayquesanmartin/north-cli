# -*- coding: utf-8 -*-
"""
fim-do-dia.py — Ritual de fim de dia (100% local, sem 365/Monday).

Faz duas coisas:
  1. Regenera o dashboard.html (chama generate-dashboard.py).
  2. Gera docs/RESUMO-DO-DIA-<AAAA-MM-DD>.txt preenchido com o que foi feito hoje,
     seguindo o template docs/RESUMO-DO-DIA-EX.txt.

O EX.txt permanece intocado (é o template). Cada dia gera um arquivo datado novo.

Uso:  python fim-do-dia.py
"""

import importlib.util
import subprocess
import re
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).resolve().parent                          # .../Barramento/dashboard
ROOT = HERE.parent                                               # .../Barramento
MODULE_DIR = ROOT / "backoffice" / "CALCULO-COBRANCA"            # módulo alvo
PLAN_DIR = MODULE_DIR / "plan-build"                             # fonte dos .md
DOCS_DIR = MODULE_DIR / "docs"                                   # destino do resumo


def load_generator():
    """Importa generate-dashboard.py (nome com hífen) como módulo."""
    spec = importlib.util.spec_from_file_location("gen_dash", HERE / "generate-dashboard.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git_today_commits():
    """Commits feitos hoje na branch atual. Lista de (hash, assunto)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(MODULE_DIR), "log", "--since=midnight",
             "--pretty=format:%h\t%s"],
            capture_output=True, text=True, timeout=15,
        )
        if out.returncode != 0 or not out.stdout.strip():
            return []
        commits = []
        for line in out.stdout.strip().splitlines():
            if "\t" in line:
                h, s = line.split("\t", 1)
                commits.append((h.strip(), s.strip()))
        return commits
    except Exception:
        return []


def git_branch():
    """Nome da branch atual (fonte de verdade real, não o .md que pode estar stale)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(MODULE_DIR), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=15,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return None


def git_dirty_count():
    """Quantidade de arquivos modificados/não commitados (trabalho do dia ainda solto)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(MODULE_DIR), "status", "--short"],
            capture_output=True, text=True, timeout=15,
        )
        if out.returncode != 0:
            return 0
        return len([l for l in out.stdout.splitlines() if l.strip()])
    except Exception:
        return 0


def derive_status(current_sprint_raw: str) -> str:
    s = current_sprint_raw.upper()
    if "VERDE" in s or "CÓDIGO COMPLETO" in s or "CODIGO COMPLETO" in s:
        return "Em revisão / Em QA"
    if "COMPLETO" in s or "✅" in current_sprint_raw:
        return "Aguardando aceite"
    return "Em desenvolvimento"


def next_planned_task(tasks, current_sprint_key):
    """Primeira TASK Planejada — preferindo o sprint atual, depois os seguintes."""
    planejadas = [t for t in tasks if t["col"] == "Planejado"]
    if not planejadas:
        return None
    # tenta no sprint atual primeiro
    same = [t for t in planejadas if t["sprint"] == current_sprint_key]
    pool = same or planejadas
    return sorted(pool, key=lambda t: t["id"])[0]


def build_resumo(gd, data_iso, data_br):
    sprint_status, tasks, blockers, debt, meta = gd.collect()
    commits = git_today_commits()
    dirty = git_dirty_count()

    total = len(tasks)
    done = sum(1 for t in tasks if t["col"] == "Done")
    pct = round(done / total * 100) if total else 0

    cur_key_m = re.search(r"(CC\d+)", meta["current_sprint"])
    cur_key = cur_key_m.group(1) if cur_key_m else ""
    cur_raw = sprint_status.get(cur_key, {}).get("status_raw", meta["current_sprint"])
    branch = git_branch() or meta["branch"]

    # --- Resumo (1 linha) ---
    if commits:
        resumo = (f"{len(commits)} commit(s) hoje. Sprint atual {cur_key} — "
                  f"progresso global {pct}% ({done}/{total} TASKs).")
    elif dirty:
        resumo = (f"Trabalho em andamento ({dirty} arquivo(s) não commitados). "
                  f"Sprint atual {cur_key} — progresso global {pct}% ({done}/{total} TASKs).")
    else:
        resumo = f"Sem alterações de código hoje. Sprint atual {cur_key} — {pct}% ({done}/{total} TASKs)."

    # --- O que foi entregue ---
    if commits:
        entregue = "\n".join(f"- {s}  ({h})" for h, s in commits)
    elif dirty:
        entregue = f"- Alterações em {dirty} arquivo(s) ainda não commitadas (revisar `git status`)."
    else:
        entregue = "- [PREENCHER] nenhum commit detectado hoje — descrever avanço manual se houver."

    # --- Revisão do diff (preenchida pelo Claude via /code-review) ---
    if commits or dirty:
        revisao = ("- [PREENCHER via /code-review] rodar a revisão no diff do dia e "
                   "resumir aqui: nº de achados, severidade e ação. Sem achados → "
                   "registrar \"limpo\".")
    else:
        revisao = "- Sem alterações de código para revisar hoje."

    # --- Bloqueios abertos ---
    open_blk = [b for b in blockers if not b["resolved"]]
    if open_blk:
        def trunc(s, n=110):
            s = gd.clean_desc(s)
            return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"
        bloqueios = "\n".join(f"- {b['id']}: {trunc(b['desc'])}" for b in open_blk)
    else:
        bloqueios = "- Nenhum"

    # --- Próximos passos ---
    nxt = next_planned_task(tasks, cur_key)
    if nxt:
        proximos = f"- {nxt['id']} ({nxt['sprint']}): {gd.clean_desc(nxt['desc'])[:90]}"
        if nxt.get("owner"):
            proximos += f"\n- Responsável: {nxt['owner']}"
    else:
        proximos = "- [PREENCHER] definir próxima TASK"

    status_line = derive_status(cur_raw)

    return f"""Atualização da entrega - {data_br}

Resumo:
{resumo}

O que foi entregue:
{entregue}

Revisão do diff (code-review):
{revisao}

Estado atual:
- Status: {status_line}
- Ambiente: Dev
- Evidências/links: dashboard/dashboard.html (raiz Barramento) · branch {branch}

Bloqueios/Riscos:
{bloqueios}

Próximos passos:
{proximos}

Ação necessária do PO:
- [REVISAR] confirmar prioridade do próximo passo e validar entregas do dia.
"""


def main():
    gd = load_generator()

    # 1. Regenera o dashboard
    gd.main()

    # 2. Gera o resumo datado
    now = datetime.now()
    data_iso = now.strftime("%Y-%m-%d")
    data_br = now.strftime("%d/%m/%Y")
    DOCS_DIR.mkdir(exist_ok=True)
    out = DOCS_DIR / f"RESUMO-DO-DIA-{data_iso}.txt"
    out.write_text(build_resumo(gd, data_iso, data_br), encoding="utf-8")

    print(f"\nFIM DO DIA — {data_br}")
    print(f"  Dashboard regenerado: {HERE / 'dashboard.html'}")
    print(f"  Resumo do dia gerado: {out}")
    print("  (EX.txt preservado como template)")


if __name__ == "__main__":
    main()
