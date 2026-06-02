# -*- coding: utf-8 -*-
"""
generate-dashboard.py — Gera um dashboard.html (hibrido: faixa executiva + kanban)
a partir dos arquivos de planejamento .md do modulo CALCULO-COBRANCA.

FONTE UNICA DE VERDADE: os proprios .md (Progress-*.md + Sprint-CC*.md).
Este script NAO edita nada — so LE os .md e GERA o HTML. Rode quando quiser
o visual atualizado:  python generate-dashboard.py

Reconciliacao: se o "Status Geral" do Progress diz que um sprint esta
"COMPLETO" (✅), todas as TASKs dele entram como Done — mesmo que a tabela do
Sprint-CC*.md ainda esteja com 📋 desatualizado (caso do CC1).
"""

import re
import sys
import html
from pathlib import Path
from datetime import datetime

# Dashboard mora na raiz do Barramento: .../Barramento/dashboard
HERE = Path(__file__).resolve().parent                                   # .../Barramento/dashboard
ROOT = HERE.parent                                                        # .../Barramento
PLAN_DIR = ROOT / "backoffice" / "CALCULO-COBRANCA" / "plan-build"        # fonte dos .md
OUT_FILE = HERE / "dashboard.html"

# Paleta Invista (mesma dos PDFs do modulo)
NAVY = "#1f2937"
ACCENT = "#f97316"
BEIGE = "#fdf8ed"

# ----------------------------------------------------------------------------
# Helpers de parsing de tabelas markdown
# ----------------------------------------------------------------------------

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def split_row(line: str):
    """Quebra uma linha de tabela markdown em celulas (sem as bordas)."""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def is_separator(cells):
    return all(re.fullmatch(r":?-{2,}:?", c) is not None for c in cells if c)


def extract_table(text: str, header_keys):
    """
    Acha a primeira tabela cujo header contem TODAS as strings em header_keys
    e devolve lista de dicts {coluna_normalizada: valor}.
    """
    lines = text.splitlines()
    header_keys_low = [k.lower() for k in header_keys]
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        header = split_row(line)
        header_low = [h.lower() for h in header]
        if all(any(k in h for h in header_low) for k in header_keys_low):
            # achou header — proxima linha deve ser separador
            rows = []
            j = i + 1
            if j < len(lines) and is_separator(split_row(lines[j])):
                j += 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = split_row(lines[j])
                if not is_separator(cells):
                    row = {}
                    for idx, col in enumerate(header):
                        row[col.lower()] = cells[idx] if idx < len(cells) else ""
                    rows.append(row)
                j += 1
            return header, rows
    return [], []


# ----------------------------------------------------------------------------
# Classificacao de status -> coluna do kanban
# ----------------------------------------------------------------------------

COL_DONE = "Done"
COL_CODIGO = "Codigo Completo"
COL_ANDAMENTO = "Em Andamento"
COL_PLANEJADO = "Planejado"

COLUMN_ORDER = [COL_PLANEJADO, COL_ANDAMENTO, COL_CODIGO, COL_DONE]
COLUMN_META = {
    COL_PLANEJADO: {"emoji": "📋", "color": "#64748b"},
    COL_ANDAMENTO: {"emoji": "⚡", "color": ACCENT},
    COL_CODIGO: {"emoji": "🟢", "color": "#22c55e"},
    COL_DONE: {"emoji": "✅", "color": "#16a34a"},
}


def classify_status(status_text: str) -> str:
    s = status_text.strip()
    if s.startswith("✅"):
        return COL_DONE
    if s.startswith("🟢"):
        return COL_CODIGO
    if s[:1] in ("⚡", "🔵", "🟡", "🚧", "🏗", "🔨"):
        return COL_ANDAMENTO
    return COL_PLANEJADO


def find_commit(status_text: str):
    m = re.search(r"`([0-9a-f]{7,40})`", status_text)
    return m.group(1) if m else ""


# ----------------------------------------------------------------------------
# Coleta dos dados
# ----------------------------------------------------------------------------

def collect():
    progress_text = read(PLAN_DIR / "Progress-CalculoCobranca.md")

    # --- Status Geral (nivel sprint) ---
    _, status_rows = extract_table(progress_text, ["sprint", "status", "progresso"])
    sprint_status = {}      # CC1 -> {"name","status_raw","complete","pct","done","total"}
    for r in status_rows:
        sprint_cell = r.get("sprint", "")
        m = re.search(r"Sprint-(CC\d+)", sprint_cell)
        if not m:
            continue
        key = m.group(1)
        status_raw = r.get("status", "")
        pct_m = re.search(r"(\d+)%", r.get("progresso", ""))
        nm_m = re.search(r"\((\d+)/(\d+)\)", r.get("progresso", ""))
        # nome curto do sprint (antes do primeiro parenteses)
        name = re.sub(r"\s*\(.*$", "", sprint_cell).strip()
        sprint_status[key] = {
            "name": name,
            "status_raw": status_raw,
            "complete": status_raw.strip().startswith("✅"),
            "pct": int(pct_m.group(1)) if pct_m else None,
            "done": int(nm_m.group(1)) if nm_m else None,
            "total": int(nm_m.group(2)) if nm_m else None,
        }

    # --- TASKs por sprint ---
    tasks = []
    for sp in sorted(PLAN_DIR.glob("Sprint-CC*.md")):
        key_m = re.search(r"Sprint-(CC\d+)", sp.name)
        key = key_m.group(1) if key_m else sp.stem
        text = read(sp)
        _, rows = extract_table(text, ["task", "descrição", "status"])
        sprint_complete = sprint_status.get(key, {}).get("complete", False)
        for r in rows:
            tid = r.get("task", "")
            if not tid or not re.match(r"S_CC", tid):
                continue
            status_raw = r.get("status", "")
            col = COL_DONE if sprint_complete else classify_status(status_raw)
            tasks.append({
                "id": tid,
                "sprint": key,
                "desc": r.get("descrição", r.get("descricao", "")),
                "owner": r.get("especialista", ""),
                "deps": r.get("dependências", r.get("dependencias", "")),
                "est": r.get("estimativa", ""),
                "status_raw": status_raw,
                "col": col,
                "commit": find_commit(status_raw),
            })

    # --- Bloqueios ---
    _, blk_rows = extract_table(progress_text, ["bloqueio", "impacto", "status"])
    blockers = []
    for r in blk_rows:
        st = r.get("status", "")
        # convencao do projeto: 🟢 = sob controle/resolvido; só 🟡/🔴/sem-emoji conta como bloqueio aberto
        resolved = st.strip().startswith("🟢") or "RESOLVIDO" in st.upper()
        blockers.append({
            "id": r.get("#", ""),
            "desc": r.get("bloqueio", ""),
            "impact": r.get("impacto", ""),
            "status": st,
            "resolved": resolved,
        })

    # --- Debito tecnico ---
    _, dt_rows = extract_table(progress_text, ["id", "descrição", "prioridade"])
    debt = []
    for r in dt_rows:
        did = r.get("id", "")
        if not did.startswith("DT-CC"):
            continue
        desc = r.get("descrição", r.get("descricao", ""))
        closed = "~~" in desc or "✅" in desc
        debt.append({
            "id": did,
            "desc": desc,
            "sprint": r.get("sprint", ""),
            "prio": r.get("prioridade", ""),
            "closed": closed,
        })

    # --- metadados ---
    branch_m = re.search(r"\*\*Branch:\*\*\s*`([^`]+)`", progress_text)
    upd_m = re.search(r"Última atualização:\*\*\s*([0-9-]+)\s*\(([^)]*)\)", progress_text)
    cur_m = re.search(r"\*\*Sprint Atual:\*\*\s*\*\*([^*]+)\*\*", progress_text)
    meta = {
        "branch": branch_m.group(1) if branch_m else "—",
        "updated": upd_m.group(1) if upd_m else "—",
        "updated_note": upd_m.group(2) if upd_m else "",
        "current_sprint": cur_m.group(1).strip() if cur_m else "—",
    }

    return sprint_status, tasks, blockers, debt, meta


# ----------------------------------------------------------------------------
# Render HTML
# ----------------------------------------------------------------------------

SPRINT_COLORS = {
    "CC1": "#0ea5e9",
    "CC2": "#8b5cf6",
    "CC3": "#ec4899",
    "CC4": "#14b8a6",
}


def esc(s):
    return html.escape(str(s))


def clean_desc(s):
    # remove markdown links/backticks pesados pra exibir limpo no card
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = s.replace("`", "")
    return s


def render(sprint_status, tasks, blockers, debt, meta):
    total = len(tasks)
    done = sum(1 for t in tasks if t["col"] == COL_DONE)
    overall_pct = round(done / total * 100) if total else 0

    open_blockers = [b for b in blockers if not b["resolved"]]
    open_debt = [d for d in debt if not d["closed"]]

    # ---- faixa executiva: cards de sprint ----
    sprint_cards = []
    for key in sorted(sprint_status.keys()):
        sp = sprint_status[key]
        sp_tasks = [t for t in tasks if t["sprint"] == key]
        sp_done = sum(1 for t in sp_tasks if t["col"] == COL_DONE)
        sp_total = len(sp_tasks) or (sp["total"] or 0)
        pct = round(sp_done / sp_total * 100) if sp_total else (sp["pct"] or 0)
        color = SPRINT_COLORS.get(key, ACCENT)
        is_current = key in meta["current_sprint"]
        badge = sp["status_raw"].split("(")[0].strip()[:32]
        sprint_cards.append(f"""
        <div class="sp-card {'current' if is_current else ''}">
          <div class="sp-head">
            <span class="sp-key" style="background:{color}">{esc(key)}</span>
            {'<span class="sp-now">ATUAL</span>' if is_current else ''}
          </div>
          <div class="sp-name">{esc(sp['name'].replace('Sprint-'+key+':','').strip())}</div>
          <div class="bar"><div class="fill" style="width:{pct}%;background:{color}"></div></div>
          <div class="sp-foot"><b>{pct}%</b><span>{sp_done}/{sp_total} tasks</span></div>
        </div>""")

    # ---- kanban ----
    columns_html = []
    for col in COLUMN_ORDER:
        meta_c = COLUMN_META[col]
        col_tasks = [t for t in tasks if t["col"] == col]
        cards = []
        for t in col_tasks:
            color = SPRINT_COLORS.get(t["sprint"], ACCENT)
            commit = f'<span class="commit">{esc(t["commit"][:7])}</span>' if t["commit"] else ""
            owner = esc(t["owner"].replace("squad-", ""))
            cards.append(f"""
            <div class="card" style="border-left-color:{color}">
              <div class="card-top">
                <span class="tid">{esc(t['id'])}</span>
                <span class="sprint-tag" style="background:{color}22;color:{color}">{esc(t['sprint'])}</span>
              </div>
              <div class="card-desc">{esc(clean_desc(t['desc'])[:140])}</div>
              <div class="card-foot"><span class="owner">{owner}</span>{commit}</div>
            </div>""")
        if not cards:
            cards.append('<div class="empty">— vazio —</div>')
        columns_html.append(f"""
        <div class="kcol">
          <div class="kcol-head" style="border-top-color:{meta_c['color']}">
            <span>{meta_c['emoji']} {esc(col)}</span>
            <span class="count">{len(col_tasks)}</span>
          </div>
          <div class="kcol-body">{''.join(cards)}</div>
        </div>""")

    # ---- bloqueios ----
    if open_blockers:
        blk_rows = "".join(f"""
          <tr>
            <td class="mono">{esc(b['id'])}</td>
            <td>{esc(clean_desc(b['desc'])[:90])}</td>
            <td>{esc(clean_desc(b['impact'])[:70])}</td>
            <td>{esc(clean_desc(b['status'])[:60])}</td>
          </tr>""" for b in open_blockers)
    else:
        blk_rows = '<tr><td colspan="4" class="empty">Nenhum bloqueio aberto 🎉</td></tr>'

    # ---- debito tecnico aberto (top por prioridade) ----
    prio_order = {"alta": 0, "média": 1, "media": 1, "baixa": 2}
    open_debt_sorted = sorted(open_debt, key=lambda d: prio_order.get(d["prio"].lower(), 3))
    dt_rows = "".join(f"""
      <tr>
        <td class="mono">{esc(d['id'])}</td>
        <td>{esc(clean_desc(d['desc'])[:95])}</td>
        <td>{esc(d['sprint'])}</td>
        <td><span class="prio prio-{esc(d['prio'].lower())}">{esc(d['prio'])}</span></td>
      </tr>""" for d in open_debt_sorted) or '<tr><td colspan="4" class="empty">Sem debito aberto</td></tr>'

    generated = datetime.now().strftime("%d/%m/%Y %H:%M")

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CALCULO-COBRANCA · Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
  a {{ color: {ACCENT}; }}
  .wrap {{ max-width: 1500px; margin: 0 auto; }}

  header {{ display:flex; align-items:flex-end; justify-content:space-between; flex-wrap:wrap; gap:12px;
            border-bottom: 3px solid {ACCENT}; padding-bottom: 16px; margin-bottom: 24px; }}
  header h1 {{ font-size: 24px; letter-spacing:.5px; }}
  header h1 .accent {{ color: {ACCENT}; }}
  .meta {{ font-size: 12px; color: #94a3b8; text-align:right; line-height:1.7; }}
  .meta .mono {{ font-family: ui-monospace, monospace; color:#cbd5e1; }}

  /* faixa executiva */
  .exec {{ display:grid; grid-template-columns: 280px 1fr; gap:20px; margin-bottom:28px; }}
  .overall {{ background: linear-gradient(135deg,{NAVY},#0b1220); border:1px solid #334155; border-radius:14px;
              padding:22px; text-align:center; }}
  .overall .big {{ font-size:54px; font-weight:800; color:{ACCENT}; line-height:1; }}
  .overall .lbl {{ font-size:12px; text-transform:uppercase; letter-spacing:1px; color:#94a3b8; margin-top:6px; }}
  .overall .ring {{ font-size:13px; color:#cbd5e1; margin-top:14px; }}
  .kpis {{ display:flex; gap:14px; margin-top:16px; justify-content:center; }}
  .kpi {{ flex:1; background:#1e293b; border-radius:10px; padding:10px 6px; }}
  .kpi b {{ display:block; font-size:22px; }}
  .kpi span {{ font-size:10px; color:#94a3b8; text-transform:uppercase; }}
  .kpi.warn b {{ color:#f59e0b; }} .kpi.bad b {{ color:#ef4444; }} .kpi.ok b {{ color:#22c55e; }}

  .sprints {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(200px,1fr)); gap:14px; }}
  .sp-card {{ background:#1e293b; border:1px solid #334155; border-radius:12px; padding:16px; }}
  .sp-card.current {{ border-color:{ACCENT}; box-shadow:0 0 0 1px {ACCENT}55; }}
  .sp-head {{ display:flex; align-items:center; gap:8px; margin-bottom:8px; }}
  .sp-key {{ color:#fff; font-weight:700; font-size:12px; padding:2px 8px; border-radius:6px; }}
  .sp-now {{ font-size:9px; background:{ACCENT}; color:#fff; padding:2px 6px; border-radius:4px; letter-spacing:.5px; }}
  .sp-name {{ font-size:12px; color:#cbd5e1; min-height:32px; margin-bottom:8px; }}
  .bar {{ height:8px; background:#0f172a; border-radius:5px; overflow:hidden; }}
  .fill {{ height:100%; border-radius:5px; transition:width .4s; }}
  .sp-foot {{ display:flex; justify-content:space-between; align-items:baseline; margin-top:8px; font-size:11px; color:#94a3b8; }}
  .sp-foot b {{ font-size:18px; color:#e2e8f0; }}

  /* kanban */
  .ktitle {{ font-size:13px; text-transform:uppercase; letter-spacing:1.5px; color:#94a3b8; margin:8px 0 14px; }}
  .kanban {{ display:grid; grid-template-columns: repeat(4,1fr); gap:16px; margin-bottom:30px; }}
  .kcol {{ background:#111c30; border:1px solid #1e293b; border-radius:12px; overflow:hidden; }}
  .kcol-head {{ display:flex; justify-content:space-between; align-items:center; padding:12px 14px;
                font-size:13px; font-weight:700; border-top:3px solid; background:#0b1424; }}
  .kcol-head .count {{ background:#334155; padding:1px 9px; border-radius:10px; font-size:12px; }}
  .kcol-body {{ padding:12px; display:flex; flex-direction:column; gap:10px; min-height:60px; }}
  .card {{ background:#1e293b; border-radius:8px; border-left:4px solid {ACCENT}; padding:11px 12px; }}
  .card-top {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }}
  .tid {{ font-family:ui-monospace,monospace; font-size:12px; font-weight:700; color:#fff; }}
  .sprint-tag {{ font-size:10px; padding:1px 7px; border-radius:5px; font-weight:600; }}
  .card-desc {{ font-size:11.5px; color:#cbd5e1; line-height:1.45; }}
  .card-foot {{ display:flex; justify-content:space-between; align-items:center; margin-top:8px; }}
  .owner {{ font-size:10px; color:#94a3b8; text-transform:uppercase; letter-spacing:.5px; }}
  .commit {{ font-family:ui-monospace,monospace; font-size:10px; background:#0f172a; color:#22c55e; padding:1px 6px; border-radius:4px; }}
  .empty {{ font-size:11px; color:#475569; text-align:center; padding:8px; font-style:italic; }}

  /* paineis */
  .panels {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
  .panel {{ background:#111c30; border:1px solid #1e293b; border-radius:12px; padding:18px; }}
  .panel h2 {{ font-size:14px; margin-bottom:12px; display:flex; align-items:center; gap:8px; }}
  table {{ width:100%; border-collapse:collapse; font-size:12px; }}
  th {{ text-align:left; color:#94a3b8; font-size:10px; text-transform:uppercase; letter-spacing:.5px; padding:6px 8px; border-bottom:1px solid #334155; }}
  td {{ padding:7px 8px; border-bottom:1px solid #1e293b; color:#cbd5e1; vertical-align:top; }}
  td.mono {{ font-family:ui-monospace,monospace; color:#fff; white-space:nowrap; }}
  .prio {{ font-size:10px; padding:1px 8px; border-radius:5px; font-weight:600; }}
  .prio-alta {{ background:#7f1d1d; color:#fecaca; }}
  .prio-média,.prio-media {{ background:#78350f; color:#fed7aa; }}
  .prio-baixa {{ background:#334155; color:#cbd5e1; }}
  footer {{ text-align:center; color:#475569; font-size:11px; margin-top:28px; }}
  @media(max-width:1100px){{ .exec{{grid-template-columns:1fr;}} .kanban{{grid-template-columns:1fr 1fr;}} .panels{{grid-template-columns:1fr;}} }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>CÁLCULO<span class="accent">·</span>COBRANÇA <span style="font-size:14px;color:#64748b">— Dashboard de Sprints</span></h1>
    </div>
    <div class="meta">
      Branch: <span class="mono">{esc(meta['branch'])}</span><br>
      Sprint atual: <span class="mono">{esc(meta['current_sprint'])}</span><br>
      Docs atualizados: {esc(meta['updated'])} · Gerado: {generated}
    </div>
  </header>

  <div class="exec">
    <div class="overall">
      <div class="big">{overall_pct}%</div>
      <div class="lbl">Progresso Global</div>
      <div class="ring">{done} de {total} TASKs concluídas</div>
      <div class="kpis">
        <div class="kpi {'bad' if open_blockers else 'ok'}"><b>{len(open_blockers)}</b><span>Bloqueios</span></div>
        <div class="kpi warn"><b>{len(open_debt)}</b><span>Déb. Téc.</span></div>
        <div class="kpi"><b>{len(sprint_status)}</b><span>Sprints</span></div>
      </div>
    </div>
    <div class="sprints">{''.join(sprint_cards)}</div>
  </div>

  <div class="ktitle">Quadro Kanban — reconciliado da fonte única (.md)</div>
  <div class="kanban">{''.join(columns_html)}</div>

  <div class="panels">
    <div class="panel">
      <h2>🚧 Bloqueios Ativos <span style="font-size:11px;color:#64748b">({len(open_blockers)} abertos)</span></h2>
      <table>
        <tr><th>ID</th><th>Bloqueio</th><th>Impacto</th><th>Status</th></tr>
        {blk_rows}
      </table>
    </div>
    <div class="panel">
      <h2>📋 Débito Técnico Aberto <span style="font-size:11px;color:#64748b">({len(open_debt)} itens)</span></h2>
      <table>
        <tr><th>ID</th><th>Descrição</th><th>Sprint</th><th>Prio</th></tr>
        {dt_rows}
      </table>
    </div>
  </div>

  <footer>
    Gerado por <span style="color:#94a3b8">generate-dashboard.py</span> ·
    fonte única: <span style="color:#94a3b8">Progress-CalculoCobranca.md + Sprint-CC*.md</span> ·
    nenhum dado é editado, só lido.
  </footer>
</div>
</body>
</html>"""


def main():
    sprint_status, tasks, blockers, debt, meta = collect()
    if not tasks:
        print("ERRO: nenhuma TASK encontrada. Confirme o caminho dos .md em", PLAN_DIR)
        sys.exit(1)
    html_out = render(sprint_status, tasks, blockers, debt, meta)
    OUT_FILE.write_text(html_out, encoding="utf-8")
    done = sum(1 for t in tasks if t["col"] == COL_DONE)
    print(f"OK -> {OUT_FILE}")
    print(f"   {len(tasks)} TASKs | {done} done | {len([b for b in blockers if not b['resolved']])} bloqueios abertos | {len([d for d in debt if not d['closed']])} DT abertos")


if __name__ == "__main__":
    main()
