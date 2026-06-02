# -*- coding: utf-8 -*-
"""
cli.py — ponto de entrada da central. Comandos:

  build       regenera output/dashboard.html
  bom-dia     regenera + imprime foco do dia + abre no navegador
  fim-do-dia  regenera + gera RESUMO-DO-DIA central por projeto
  open        so abre o dashboard ja existente

Uso (via run.py):  python run.py <comando>
A "tool home" e o diretorio que contem config/, output/, resumos/, templates/.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .config import load_config
from .discovery import discover_projects, current_identity
from . import render as R
from . import rituals
from . import focus as F
from . import inbox as IN
from . import parsers as P


def _config_path(home: Path) -> Path:
    return home / "config" / "projects.json"


def _infer_project(cfg) -> str:
    """Infere o projeto a partir do diretorio atual, casando com ids conhecidos."""
    try:
        cwd = Path(os.getcwd()).resolve()
    except Exception:
        return ""
    keys = set(cfg.projects.keys())
    for p in [cwd] + list(cwd.parents):
        if p.name in keys:
            return p.name
    return ""


def _utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _open_browser(path: Path):
    # path e sempre o output/dashboard.html interno (nunca input do usuario).
    # Usa subprocess.run([...]) sem shell para evitar qualquer command-injection.
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # noqa  (API nativa Windows, sem shell)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
        return True
    except Exception:
        return False


def _load_and_discover(home: Path):
    cfg_path = home / "config" / "projects.json"
    cfg = load_config(cfg_path)
    projects, new_ids = discover_projects(cfg)
    # identidade do dev (gh @login + git): detecta uma vez e cacheia na config,
    # para nao chamar o gh a cada regeneracao do painel vivo
    if not cfg.data.get("settings", {}).get("identity", {}).get("github") and \
       not cfg.data.get("settings", {}).get("identity", {}).get("name"):
        sample = Path(projects[0]["path"]) if projects else home
        cfg.data.setdefault("settings", {})["identity"] = current_identity(sample)
    cfg.save()  # persiste projetos recem-descobertos + identidade
    return cfg, projects, new_ids


def _pick_json(pk):
    """Compacta um 'pick' do focus.compute_focus para o state.json (statusline)."""
    if not pk:
        return None
    t = pk["task"]
    desc = P.clean_desc(t["desc"])[:80] or (t.get("status_raw", "") or "")[:80]
    return {
        "id": t["id"], "sprint": t["sprint"] or "", "desc": desc,
        "projectId": pk["project_id"], "project": pk["project"],
        "squad": pk["squad"].replace("squad-", ""), "actionable": pk["actionable"],
    }


def _compute_state(projects, settings):
    """Estado compacto para a statusline: foco global + por projeto + alertas.
    Sem I/O e sem git — opera sobre o modelo ja montado em memoria."""
    wip_limit = settings.get("wip_limit", F.WIP_LIMIT)
    g = F.compute_focus(projects, wip_limit)
    projs, risk_total, warn_total = {}, 0, 0
    for p in projects:
        al = p.get("alerts", [])
        pr = sum(1 for a in al if a["severity"] == "risk")
        pw = sum(1 for a in al if a["severity"] == "warn")
        risk_total += pr
        warn_total += pw
        pf = F.compute_focus([p], wip_limit)   # proxima acao DESTE projeto
        projs[p["id"]] = {
            "name": p["name"], "color": p["color"], "pct": p["rollup"]["pct"],
            "alertsRisk": pr, "alertsWarn": pw, "next": _pick_json(pf["pick"]),
        }
    return {
        "focus": _pick_json(g["pick"]),
        "wip": [{"project": w["project"], "count": w["count"], "limit": w["limit"]}
                for w in g["wip_alerts"]],
        "totals": {"projects": len(projects),
                   "alertsRisk": risk_total, "alertsWarn": warn_total},
        "projects": projs,
    }


def cmd_build(home: Path, cfg, projects, quiet=False):
    out_dir = home / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "dashboard.html"
    html = R.render(projects, cfg.settings, IN.open_items(home))
    out_file.write_text(html, encoding="utf-8")
    # cache leve para a statusline (lido sem rodar discovery/git)
    try:
        (out_dir / "state.json").write_text(
            json.dumps(_compute_state(projects, cfg.settings), ensure_ascii=False),
            encoding="utf-8")
    except Exception:
        pass
    if not quiet:
        done = sum(p["rollup"]["done"] for p in projects)
        total = sum(p["rollup"]["total"] for p in projects)
        blk = sum(len(p["open_blockers"]) for p in projects)
        print("OK -> {}".format(out_file))
        print("   {} projeto(s) | {}/{} TASKs done | {} bloqueio(s) aberto(s)".format(
            len(projects), done, total, blk))
    return out_file


def cmd_bom_dia(home: Path, cfg, projects):
    out_file = cmd_build(home, cfg, projects, quiet=True)
    txt = rituals.build_bom_dia(projects, cfg.settings.get("owner_name", "Kayque"))
    print(txt)
    reminder = _inbox_reminder_block(
        home, "LEMBRETE — ideias/notas capturadas que ainda pedem decisão:")
    if reminder:
        print(reminder)
        print("\n  (valide agora, ou mantenha pra depois — '/inbox' para triar)")
    if cfg.settings.get("open_browser", True):
        if not _open_browser(out_file):
            print("  (abra manualmente: {})".format(out_file))
    return out_file


def cmd_fim_do_dia(home: Path, cfg, projects):
    out_file = cmd_build(home, cfg, projects, quiet=True)
    now = datetime.now()
    data_iso = now.strftime("%Y-%m-%d")
    data_br = now.strftime("%d/%m/%Y")
    resumos_root = home / "resumos"
    written = []
    for p in projects:
        body = rituals.build_resumo_projeto(p, data_br)
        # central
        pdir = resumos_root / p["id"]
        pdir.mkdir(parents=True, exist_ok=True)
        central = pdir / "RESUMO-DO-DIA-{}.txt".format(data_iso)
        central.write_text(body, encoding="utf-8")
        written.append(central)
        # espelho no docs do projeto, se existir e a config permitir
        if cfg.settings.get("mirror_to_project_docs", True) and p.get("has_docs"):
            docs = Path(p["path"]) / "docs"
            try:
                docs.mkdir(exist_ok=True)
                (docs / "RESUMO-DO-DIA-{}.txt".format(data_iso)).write_text(body, encoding="utf-8")
            except Exception:
                pass

    print("\nFIM DO DIA — {}".format(data_br))
    print("  Painel regenerado: {}".format(out_file))
    print("  Resumos gerados ({} projeto(s)) em: {}".format(len(written), resumos_root))
    for w in written:
        print("    - {}".format(w))

    reminder = _inbox_reminder_block(
        home, "IDEIAS/NOTAS CAPTURADAS HOJE (e pendentes) — validar agora ou rever depois?")
    if reminder:
        print(reminder)
        print("\n  Decida cada uma: validar agora, ou manter na inbox pro próximo bom-dia.")
        print("  ('/inbox' para triar · 'inbox-done <id>' / 'inbox-dismiss <id>')")
    return out_file


def cmd_foco(home: Path, cfg, projects):
    """Imprime a proxima acao (direcao). Tambem regenera o painel (silencioso)."""
    cmd_build(home, cfg, projects, quiet=True)
    print(F.build_focus_text(projects, cfg.settings.get("wip_limit", F.WIP_LIMIT)))


def cmd_inbox_add(home: Path, text: str):
    """Captura rapida — LEVE (so le config, sem discovery). Nao atrapalha a task."""
    cfg = load_config(_config_path(home))
    project = _infer_project(cfg)
    entry = IN.add(home, text, project=project)
    proj = " · {}".format(entry["project"]) if entry["project"] else ""
    print("✓ Capturado [{}] {} {}{}".format(
        entry["id"], IN.TAG_EMOJI.get(entry["tag"], ""), entry["text"][:70], proj))
    n = len(IN.open_items(home))
    print("  ({} item(ns) na inbox — revise com /inbox, ou eu lembro no fim do dia)".format(n))


def cmd_inbox_list(home: Path):
    items = IN.open_items(home)
    if not items:
        print("Inbox vazia. Nada pendente. 🎉")
        return
    print("\nINBOX — {} item(ns) aberto(s):".format(len(items)))
    print(IN.format_list(items))
    print("\n  Resolver: 'inbox-done <id>' (validado/feito) | 'inbox-dismiss <id>' (descartar)")


def cmd_inbox_resolve(home: Path, item_id: str, status: str):
    ok = IN.resolve(home, item_id, status)
    if ok:
        verbo = "concluido" if status == "done" else "descartado"
        print("✓ {} marcado como {}.".format(item_id, verbo))
    else:
        print("Item '{}' nao encontrado na inbox.".format(item_id))


def _inbox_reminder_block(home: Path, header: str):
    items = IN.open_items(home)
    if not items:
        return ""
    L = ["", "  " + header, "  " + "-" * 50]
    L.append(IN.format_list(items))
    return "\n".join(L)


# ---------------------------------------------------------------------------
# statusline — UMA linha para a barra de status do Claude Code.
# LEVE: le so o output/state.json (gerado no build). Nunca roda discovery/git.
# ---------------------------------------------------------------------------
_ANSI = {
    "reset": "\033[0m", "dim": "\033[2m", "north": "\033[38;5;208m",
    "risk": "\033[38;5;203m", "warn": "\033[38;5;221m",
    "ok": "\033[38;5;114m", "squad": "\033[38;5;111m",
}


def _read_stdin_cwd():
    """Le o JSON que o Claude Code envia no stdin e extrai o diretorio atual.
    Nao bloqueia em terminal interativo (so le quando ha pipe)."""
    try:
        if sys.stdin.isatty():
            return ""
        raw = sys.stdin.read()
        if not raw.strip():
            return ""
        j = json.loads(raw)
        ws = j.get("workspace") or {}
        return ws.get("current_dir") or j.get("cwd") or ""
    except Exception:
        return ""


def _badge(risk, warn):
    a = _ANSI
    if risk:
        return "{}●{}{}".format(a["risk"], risk, a["reset"])
    if warn:
        return "{}●{}{}".format(a["warn"], warn, a["reset"])
    return "{}●{}".format(a["ok"], a["reset"])


def _statusline_text(state, cwd):
    a = _ANSI
    projs = state.get("projects", {})
    parts = set(re.split(r"[\\/]+", cwd)) if cwd else set()
    pid = next((k for k in projs if k and k in parts), "")
    if pid:
        pd = projs[pid]
        nxt, risk, warn = pd.get("next"), pd.get("alertsRisk", 0), pd.get("alertsWarn", 0)
        scope = pd.get("name", pid)
    else:
        nxt = state.get("focus")
        tot = state.get("totals", {})
        risk, warn = tot.get("alertsRisk", 0), tot.get("alertsWarn", 0)
        scope = ""

    head = "{}\U0001f9ed north{}".format(a["north"], a["reset"])
    badge = _badge(risk, warn)
    if not nxt:
        return "{} {}tudo fechado{}  {}".format(head, a["ok"], a["reset"], badge)

    # largura disponivel (Claude Code seta COLUMNS); trunca a descricao
    try:
        cols = int(os.environ.get("COLUMNS", "0")) or 100
    except ValueError:
        cols = 100
    desc = nxt.get("desc", "")
    max_desc = max(18, min(56, cols - 46))
    if len(desc) > max_desc:
        desc = desc[:max_desc - 1].rstrip() + "…"

    block = "⚠ " if not nxt.get("actionable") else ""
    scope_txt = "{} · ".format(scope) if scope else ""
    return "{} {}{}{}{}{}  {}{}{}  {}/{}{}  {}".format(
        head, block, a["north"], scope_txt, nxt.get("id", ""), a["reset"],
        a["dim"], desc, a["reset"],
        a["squad"], nxt.get("squad", ""), a["reset"], badge)


def cmd_statusline(home: Path):
    cwd = _read_stdin_cwd()
    state_file = home / "output" / "state.json"
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        # sem cache ainda: linha minima, mas NUNCA vazia (vazio = barra em branco)
        print("\033[38;5;208m\U0001f9ed north\033[0m \033[2mrode /painel para iniciar\033[0m")
        return 0
    print(_statusline_text(state, cwd))
    return 0


def cmd_open(home: Path):
    out_file = home / "output" / "dashboard.html"
    if not out_file.exists():
        print("Dashboard ainda nao gerado. Rode 'build' primeiro.")
        return
    _open_browser(out_file)


def main(argv, home: Path):
    _utf8()
    cmd = (argv[0] if argv else "build").lower()

    if cmd == "open":
        cmd_open(home)
        return 0

    # --- statusline: LEVE, sem discovery (le so o cache output/state.json) ---
    if cmd in ("statusline", "status-line"):
        return cmd_statusline(home)

    # --- comandos de inbox: LEVES, sem discovery (captura instantanea) ---
    if cmd in ("inbox-add", "btw", "capturar"):
        text = " ".join(argv[1:]).strip()
        if not text:
            print("Nada para capturar. Uso: btw <sua ideia>")
            return 1
        cmd_inbox_add(home, text)
        return 0
    if cmd in ("inbox", "inbox-list"):
        cmd_inbox_list(home)
        return 0
    if cmd in ("inbox-done", "inbox-dismiss"):
        if len(argv) < 2:
            print("Informe o id. Ex: inbox-done BTW-0003")
            return 1
        cmd_inbox_resolve(home, argv[1], "done" if cmd == "inbox-done" else "dismissed")
        return 0

    cfg, projects, new_ids = _load_and_discover(home)
    if new_ids:
        print("  + {} novo(s) projeto(s) descoberto(s): {}".format(
            len(new_ids), ", ".join(new_ids)))
    if not projects:
        print("Nenhum projeto com tracking encontrado.")
        print("Verifique scan_roots em: {}".format(home / "config" / "projects.json"))
        return 1

    if cmd in ("build", "dashboard", "painel"):
        cmd_build(home, cfg, projects)
    elif cmd in ("bom-dia", "bomdia", "bom_dia"):
        cmd_bom_dia(home, cfg, projects)
    elif cmd in ("fim-do-dia", "fimdodia", "fim_do_dia"):
        cmd_fim_do_dia(home, cfg, projects)
    elif cmd in ("foco", "focus", "agora", "next"):
        cmd_foco(home, cfg, projects)
    else:
        print("Comando desconhecido: {}".format(cmd))
        print("Use: build | bom-dia | fim-do-dia | foco | btw <ideia> | inbox | statusline | open")
        return 2
    return 0
