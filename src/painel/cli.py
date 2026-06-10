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
    projects, new_ids, removed_ids = discover_projects(cfg)
    # identidade do dev (gh @login + git): detecta uma vez e cacheia na config,
    # para nao chamar o gh a cada regeneracao do painel vivo
    if not cfg.data.get("settings", {}).get("identity", {}).get("github") and \
       not cfg.data.get("settings", {}).get("identity", {}).get("name"):
        sample = Path(projects[0]["path"]) if projects else home
        cfg.data.setdefault("settings", {})["identity"] = current_identity(sample)
    cfg.save()  # persiste projetos recem-descobertos, removidos e identidade
    return cfg, projects, new_ids, removed_ids


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


def _focus_subset(cfg, projects):
    """Lente do dia: restringe a saida dos rituais ao projeto focado (se houver).
    Devolve (lista, focused_id|None). Nunca filtra o dashboard — so o texto."""
    fp = getattr(cfg, "focused_project", None)
    if not fp:
        return projects, None
    sub = [p for p in projects if p["id"] == fp]
    return (sub, fp) if sub else (projects, None)


def _focus_banner(fp):
    print("📌 Foco do dia: {}  (north focus --all para o portfolio completo)".format(fp))


def _print_learnings_reminder(home: Path, projects):
    """Devolve aprendizados recentes dos projetos ATIVOS (sinal git) — não repita o erro."""
    from . import learnings as L
    active = [p for p in projects if (p.get("mine", {}) or {}).get("active")] or projects[:1]
    blocks = []
    for p in active:
        rec = L.recent(home, p["id"], limit=3)
        if rec:
            lines = "\n".join("    • " + L._fmt(e) for e in rec)
            blocks.append("  {}:\n{}".format(p["name"], lines))
    if blocks:
        print("\n  💡 APRENDIZADOS RECENTES (não repita o erro):")
        print("\n".join(blocks))


def cmd_bom_dia(home: Path, cfg, projects):
    out_file = cmd_build(home, cfg, projects, quiet=True)
    projs, fp = _focus_subset(cfg, projects)
    if fp:
        _focus_banner(fp)
    txt = rituals.build_bom_dia(projs, cfg.settings.get("owner_name", "dev"))
    print(txt)
    _print_learnings_reminder(home, projects)
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
    projs, fp = _focus_subset(cfg, projects)
    if fp:
        _focus_banner(fp)
    written = []
    for p in projs:
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


def cmd_foco(home: Path, cfg, projects, args=None):
    """Imprime a proxima acao (direcao). Tambem regenera o painel (silencioso).
    Flags: --only <id> fixa o foco do dia; --all/--clear volta ao portfolio."""
    args = args or []
    if ("--all" in args) or ("--clear" in args):
        cfg.set_focused_project(None)
        print("📌 Foco limpo — acompanhando todos os projetos.")
    elif "--only" in args:
        i = args.index("--only")
        pid = args[i + 1] if i + 1 < len(args) else ""
        ids = {p["id"] for p in projects}
        if pid not in ids:
            print("Projeto '{}' nao encontrado.".format(pid))
            print("Disponiveis: {}".format(", ".join(sorted(ids))))
            return
        cfg.set_focused_project(pid)
        print("📌 Foco do dia fixado: {}".format(pid))
    cmd_build(home, cfg, projects, quiet=True)
    projs, fp = _focus_subset(cfg, projects)
    if fp:
        _focus_banner(fp)
    print(F.build_focus_text(projs, cfg.settings.get("wip_limit", F.WIP_LIMIT)))


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
#
# Mostra num so lugar: modelo · proxima acao do projeto atual (foco) · sinais
# vitais · diretorio · medidor de janela de contexto.
# ---------------------------------------------------------------------------
_ANSI = {
    "reset": "\033[0m", "dim": "\033[2m", "north": "\033[38;5;208m",
    "risk": "\033[38;5;203m", "warn": "\033[38;5;221m",
    "ok": "\033[38;5;114m", "squad": "\033[38;5;111m", "sep": "\033[2m│\033[0m",
}


def _read_hook():
    """Le o JSON do Claude Code (stdin): cwd, modelo e janela de contexto.
    Nao bloqueia em terminal interativo (so le quando ha pipe)."""
    out = {"cwd": "", "model": "", "remaining": None, "total": 1_000_000}
    try:
        if sys.stdin.isatty():
            return out
        raw = sys.stdin.read()
        if not raw.strip():
            return out
        j = json.loads(raw)
        ws = j.get("workspace") or {}
        out["cwd"] = ws.get("current_dir") or j.get("cwd") or ""
        out["model"] = ((j.get("model") or {}).get("display_name")) or ""
        cw = j.get("context_window") or {}
        out["remaining"] = cw.get("remaining_percentage")
        out["total"] = cw.get("total_tokens") or 1_000_000
    except Exception:
        pass
    return out


def _ctx_meter(remaining, total):
    """Medidor de janela de contexto (paridade com o GSD): normaliza o buffer de
    auto-compact, monta barra de 10 segmentos e colore por uso. '' se ausente."""
    if remaining is None:
        return ""
    try:
        acw = int(os.environ.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW", "0") or "0")
    except ValueError:
        acw = 0
    buffer_pct = min(100, (acw / total) * 100) if (acw > 0 and total) else 16.5
    usable = max(0.0, ((remaining - buffer_pct) / (100 - buffer_pct)) * 100) if buffer_pct < 100 else 0.0
    used = max(0, min(100, round(100 - usable)))
    bar = "█" * (used // 10) + "░" * (10 - used // 10)
    if used < 50:
        col = "\033[32m"
    elif used < 65:
        col = "\033[33m"
    elif used < 80:
        col = "\033[38;5;208m"
    else:
        return " \033[5;31m\U0001f480 {} {}%\033[0m".format(bar, used)
    return " {}{} {}%\033[0m".format(col, bar, used)


def _badge(risk, warn):
    a = _ANSI
    if risk:
        return "{}⛔{}{}".format(a["risk"], risk, a["reset"])
    if warn:
        return "{}●{}{}".format(a["warn"], warn, a["reset"])
    return "{}●{}".format(a["ok"], a["reset"])


def _focus_block(state, cwd):
    """Bloco do foco: escopo = projeto do cwd (com % de progresso), ou portfolio.
    Inclui a proxima acao, o squad sugerido e o badge de sinais vitais."""
    a = _ANSI
    projs = state.get("projects", {})
    parts = set(re.split(r"[\\/]+", cwd)) if cwd else set()
    pid = next((k for k in projs if k and k in parts), "")
    if pid:
        pd = projs[pid]
        nxt, risk, warn = pd.get("next"), pd.get("alertsRisk", 0), pd.get("alertsWarn", 0)
        scope, pct = pd.get("name", pid), pd.get("pct")
    else:
        nxt = state.get("focus")
        tot = state.get("totals", {})
        risk, warn = tot.get("alertsRisk", 0), tot.get("alertsWarn", 0)
        scope, pct = "", None

    head = "{}\U0001f9ed{}".format(a["north"], a["reset"])
    badge = _badge(risk, warn)
    if scope and pct is not None:
        scope_txt = "{}{} {}%{} ".format(a["dim"], scope, pct, a["reset"])
    elif scope:
        scope_txt = "{}{}{} ".format(a["dim"], scope, a["reset"])
    else:
        scope_txt = ""
    if not nxt:
        return "{} {}{}tudo fechado{} {}".format(head, scope_txt, a["ok"], a["reset"], badge)

    try:
        cols = int(os.environ.get("COLUMNS", "0")) or 110
    except ValueError:
        cols = 110
    desc = nxt.get("desc", "")
    max_desc = max(16, min(50, cols - 60))
    if len(desc) > max_desc:
        desc = desc[:max_desc - 1].rstrip() + "…"
    block = "⚠ " if not nxt.get("actionable") else ""
    return "{} {}{}{}{}{} {}{}{} {}/{}{} {}".format(
        head, scope_txt, block, a["north"], nxt.get("id", ""), a["reset"],
        a["dim"], desc, a["reset"], a["squad"], nxt.get("squad", ""), a["reset"], badge)


def _statusline_text(state, hook):
    """Compoe a linha: modelo │ foco+vitais │ dir [medidor de contexto]."""
    a = _ANSI
    segs = []
    if hook.get("model"):
        segs.append("{}{}{}".format(a["dim"], hook["model"], a["reset"]))
    segs.append(_focus_block(state, hook.get("cwd", "")))
    cwd = hook.get("cwd", "")
    dirname = re.split(r"[\\/]+", cwd.rstrip("/\\"))[-1] if cwd else ""
    tail = "{}{}{}".format(a["dim"], dirname, a["reset"]) if dirname else ""
    tail += _ctx_meter(hook.get("remaining"), hook.get("total", 1_000_000))
    if tail.strip():
        segs.append(tail)
    return (" " + a["sep"] + " ").join(s for s in segs if s)


def cmd_statusline(home: Path):
    hook = _read_hook()
    state_file = home / "output" / "state.json"
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        # sem cache: nao deixa a barra vazia; ainda mostra modelo + contexto
        a = _ANSI
        base = "{}\U0001f9ed north{} {}rode /panel{}".format(
            a["north"], a["reset"], a["dim"], a["reset"])
        if hook.get("model"):
            base = "{}{}{} {} {}".format(
                a["dim"], hook["model"], a["reset"], a["sep"], base)
        print(base + _ctx_meter(hook.get("remaining"), hook.get("total", 1_000_000)))
        return 0
    print(_statusline_text(state, hook))
    return 0


def cmd_config(home: Path, args):
    """CRUD leve da config (projects.json) — sem discovery. Subcomandos:
       show | add-root <p> | remove-root <p> | set <chave> <valor> |
       project <id> <enable|disable|source <v>|alias <v>|order <n>|clear-source>"""
    cfg = load_config(_config_path(home))
    sub = args[0] if args else "show"

    if sub in ("show", "list"):
        s = cfg.settings
        print("north — configuração")
        print("  config:  {}".format(_config_path(home)))
        print("  scan_roots:")
        for r in (cfg.data.get("scan_roots") or ["(nenhum — use: north config add-root \"<pasta>\")"]):
            print("    - {}".format(r))
        print("  settings:")
        for k in ("owner_name", "theme", "wip_limit", "dirty_risk_files",
                  "stale_branch_days", "open_browser", "mirror_to_project_docs"):
            print("    {:<22} {}".format(k, s.get(k)))
        projs = cfg.data.get("projects", {})
        if projs:
            print("  projetos ({}):".format(len(projs)))
            for pid, pc in sorted(projs.items()):
                flags = []
                if pc.get("enabled", True) is False:
                    flags.append("OFF")
                if pc.get("source"):
                    flags.append("source=" + pc["source"])
                if pc.get("alias"):
                    flags.append("alias=" + pc["alias"])
                print("    {:<26} {}".format(pid, " ".join(flags) or "on"))
        print("\n  Ex.: north config add-root \"<pasta>\"  |  set theme light  |  "
              "project backoffice source gsd")
        return 0

    if sub in ("add-root", "add_root"):
        if len(args) < 2:
            print("uso: north config add-root \"<caminho>\""); return 1
        roots = cfg.data.setdefault("scan_roots", [])
        if args[1] in roots:
            print("já existe:", args[1])
        else:
            roots.append(args[1]); cfg.save(); print("✓ raiz adicionada:", args[1])
        return 0

    if sub in ("remove-root", "rm-root", "remove_root"):
        if len(args) < 2:
            print("uso: north config remove-root \"<caminho>\""); return 1
        roots = cfg.data.setdefault("scan_roots", [])
        if args[1] in roots:
            roots.remove(args[1]); cfg.save(); print("✓ raiz removida:", args[1])
        else:
            print("não encontrada:", args[1])
        return 0

    if sub == "set":
        if len(args) < 3:
            print("uso: north config set <chave> <valor>"); return 1
        key, val = args[1], args[2]
        st = cfg.data.setdefault("settings", {})
        if key in ("wip_limit", "dirty_risk_files", "stale_branch_days"):
            try:
                val = int(val)
            except ValueError:
                print("valor inteiro esperado para", key); return 1
        elif key in ("open_browser", "mirror_to_project_docs"):
            val = val.lower() in ("1", "true", "sim", "yes", "on")
        st[key] = val; cfg.save(); print("✓ {} = {}".format(key, val))
        return 0

    if sub == "project":
        if len(args) < 3:
            print("uso: north config project <id> <enable|disable|source <v>|"
                  "alias <v>|order <n>|clear-source>"); return 1
        pid, action = args[1], args[2]
        pc = cfg.data.setdefault("projects", {}).setdefault(
            pid, {"enabled": True, "alias": "", "color": "", "order": 0})
        if action == "enable":
            pc["enabled"] = True
        elif action == "disable":
            pc["enabled"] = False
        elif action == "clear-source":
            pc.pop("source", None)
        elif action == "order" and len(args) >= 4:
            try:
                pc["order"] = int(args[3])
            except ValueError:
                print("order deve ser inteiro"); return 1
        elif action in ("source", "alias", "color") and len(args) >= 4:
            pc[action] = args[3]
        else:
            print("ação inválida ou falta valor:", action); return 1
        cfg.save(); print("✓ {} -> {} {}".format(pid, action, args[3] if len(args) >= 4 else ""))
        return 0

    print("config: subcomando desconhecido '{}'. Use: show | add-root | remove-root | "
          "set | project".format(sub))
    return 2


def cmd_status(home: Path):
    """Mostra o que o north tem instalado, o que rastreia e onde estão as coisas."""
    a = _ANSI
    print("{}\U0001f9ed north{} — status\n".format(a["north"], a["reset"]))
    ok = lambda c: "{}ok{}".format(a["ok"], a["reset"]) if c else "{}ausente{}".format(a["risk"], a["reset"])
    print("  motor:   {}  ({})".format(home, ok((home / "run.py").exists())))
    cfgp = _config_path(home)
    print("  config:  {}  ({})".format(cfgp, ok(cfgp.exists())))
    dash = home / "output" / "dashboard.html"
    print("  painel:  {}  ({})".format(
        dash, "{}gerado{}".format(a["ok"], a["reset"]) if dash.exists()
        else "{}rode: north build{}".format(a["warn"], a["reset"])))
    try:
        cfg = load_config(cfgp)
        mode = cfg.discovery_mode
        print("\n  modo de descoberta: {}{}{}".format(
            a["north"], mode, a["reset"]))
        if mode == "enrolled":
            enr = cfg.data.get("enrolled", [])
            print("  projetos plugados ({}):  {}(north init p/ plugar · north forget p/ remover){}".format(
                len(enr), a["dim"], a["reset"]))
            for p in (enr or ["(nenhum — rode `north init` na raiz de um projeto)"]):
                print("    - {}".format(p))
        else:
            roots = cfg.data.get("scan_roots", [])
            print("  scan_roots ({}):  {}(legado — `north init` migra p/ enrolled){}".format(
                len(roots), a["dim"], a["reset"]))
            for r in (roots or ["(nenhum — north config add-root \"<pasta>\")"]):
                print("    - {}".format(r))
    except Exception:
        pass
    try:
        st = json.loads((home / "output" / "state.json").read_text(encoding="utf-8"))
        projs = st.get("projects", {})
        print("\n  projetos rastreados ({}):".format(len(projs)))
        for pid, pd in projs.items():
            print("    {:<26} {:>3}%   [{}]".format(pd.get("name", pid)[:26], pd.get("pct", 0), pid))
    except Exception:
        print("\n  projetos: rode 'north build' para descobrir/listar")
    return 0


_DOC_CORE = ["PRD", "SPEC", "SDD", "TDD", "ADR", "SECURITY"]
# Docs "vivos" (briefing + porquê), gravados na raiz do projeto, fora do gap SDLC.
_DOC_LIVING = ["DECISIONS", "CONTEXT"]
# Planos (não-docs): geram Sprint*.md no plan-build, lidos pelo kanban — fora do gap SDLC.
_DOC_PLANS = ["SPRINT"]
_DOC_ALL = _DOC_CORE + _DOC_LIVING + _DOC_PLANS


def _doc_template_path(home: Path, tipo: str):
    rel = Path("references") / "doc-templates" / (tipo.lower() + ".md")
    for base in (home, Path(__file__).resolve().parent.parent.parent):
        p = base / rel
        if p.exists():
            return p
    return None


def cmd_init(home: Path, args):
    """Pluga o projeto atual (ou <caminho>) no north — modo enrolled (opt-in).
    O north passa a rastrear SÓ o que foi plugado. Read-only: registra o caminho
    em ~/.north — nada é escrito dentro do projeto."""
    from . import fsutil
    a = _ANSI
    target = Path(args[0]).expanduser() if args else Path.cwd()
    if not target.is_dir():
        print("Pasta não encontrada: {}".format(target))
        return 1
    cfg = load_config(_config_path(home))
    ap = target.resolve()
    added = cfg.add_enrolled(ap)
    print("{}🧭 north{} · init  {}enrollment opt-in{}".format(
        a["north"], a["reset"], a["dim"], a["reset"]))
    if added:
        print("  {}✓ projeto plugado:{} {}  {}({}){}".format(
            a["ok"], a["reset"], ap.name, a["dim"], ap, a["reset"]))
    else:
        print("  {}• já estava plugado:{} {}".format(a["dim"], a["reset"], ap.name))
    has = (fsutil.find_dirs_named([ap], "plan-build", 3)
           or fsutil.find_dirs_named([ap], ".planning", 3))
    if not has:
        print("  {}→ não achei plan-build/.planning aqui — o projeto aparece no painel "
              "quando tiver um plano.{}".format(a["dim"], a["reset"]))
    print("  {}→ rastreando só o que você plugou · ver: north status · remover: "
          "north forget {}{}".format(a["dim"], ap.name, a["reset"]))
    return 0


def cmd_forget(home: Path, args):
    """Des-pluga um projeto do tracking (modo enrolled). Uso: forget <projeto|caminho>."""
    a = _ANSI
    if not args:
        print("uso: north forget <projeto|caminho>")
        return 1
    cfg = load_config(_config_path(home))
    ok = cfg.remove_enrolled(args[0])
    if ok:
        print("  {}✓ des-plugado:{} {}".format(a["ok"], a["reset"], args[0]))
    else:
        print("  não encontrei '{}' entre os plugados. ver: north status".format(args[0]))
    return 0 if ok else 1


def cmd_doc(home: Path, cfg, projects, args):
    """Apoio ao /north-doc (read-only): gaps de docs por projeto + esqueletos.
    Uso: doc [list [<project>]] | template <tipo> | types."""
    a = _ANSI
    sub = (args[0].lower() if args else "list")
    if sub in ("template", "tpl"):
        if len(args) < 2:
            print("uso: north doc template <prd|spec|sdd|tdd|adr|security>")
            return 1
        p = _doc_template_path(home, args[1])
        if not p:
            print("template '{}' não existe. Tipos: {}".format(
                args[1], ", ".join(t.lower() for t in _DOC_ALL)))
            return 1
        print(p.read_text(encoding="utf-8"))
        return 0
    if sub in ("types", "templates"):
        print("SDLC:    {}".format(", ".join(t.lower() for t in _DOC_CORE)))
        print("vivos:   {}  (briefing + porquê, na raiz do projeto)".format(
            ", ".join(t.lower() for t in _DOC_LIVING)))
        print("planos:  {}  (gera Sprint*.md no plan-build, lido pelo kanban)".format(
            ", ".join(t.lower() for t in _DOC_PLANS)))
        print("gere com /north-doc <tipo> [alvo]  ·  esqueleto: north doc template <tipo>")
        return 0
    proj_filter = args[1] if len(args) > 1 else None
    print("{}📚 Documentos de SDLC por projeto{}  (detectados vs faltando)".format(
        a["north"], a["reset"]))
    for p in projects:
        if proj_filter and p["id"] != proj_filter:
            continue
        have = sorted({d["type"] for d in p.get("docs", [])})
        missing = [t for t in _DOC_CORE if t not in have]
        living = [t for t in _DOC_LIVING if t in have]
        living_missing = [t for t in _DOC_LIVING if t not in have]
        print("\n  {}{}{}".format(a["north"], p["name"], a["reset"]))
        print("    {}SDLC:{}     tem: {} · faltando: {}".format(
            a["ok"], a["reset"],
            ", ".join(t for t in have if t in _DOC_CORE) or "—",
            ", ".join(missing) or "—"))
        print("    {}📌 vivos:{} tem: {} · faltando: {}".format(
            a["north"], a["reset"], ", ".join(living) or "—", ", ".join(living_missing) or "—"))
    print("\n  gerar:  /north-doc <tipo> [alvo]   (ex.: /north-doc context · /north-doc decisions)")
    return 0


def cmd_task(home: Path, cfg, projects, args):
    """Contrato de uma TASK (o quê + critérios de aceite) — insumo do /north-dev
    (TDD-first). Uso: task <id> [--project <id>]."""
    a = _ANSI
    if not args:
        print("uso: north task <id>   (ex.: north task TASK-01)")
        return 1
    tid_l = args[0].strip().lower()
    proj_filter = args[args.index("--project") + 1] if "--project" in args and \
        args.index("--project") + 1 < len(args) else None
    matches = [(p, t) for p in projects if not (proj_filter and p["id"] != proj_filter)
               for t in p["tasks"] if t["id"].lower() == tid_l]
    if not matches:
        print("Task '{}' não encontrada. Veja os ids no painel (north panel) ou no Sprint*.md.".format(args[0]))
        return 1
    for p, t in matches:
        sp = next((s for s in p["sprints"] if s["key"] == t["sprint"]
                   and s.get("feature", "") == t.get("feature", "")), None)
        print("{}{}{}  ({} · sprint {})".format(a["north"], t["id"], a["reset"],
                                                 p["name"], t["sprint"] or "—"))
        print("  {}o que entregar:{} {}".format(a["dim"], a["reset"],
              t.get("desc") or t.get("status_raw") or "—"))
        if sp and (sp.get("brief") or {}).get("objetivo"):
            print("  {}objetivo da sprint:{} {}".format(a["dim"], a["reset"], sp["brief"]["objetivo"]))
        if t.get("entrega"):
            print("\n  {}📦 entregáveis:{}".format(a["ok"], a["reset"]))
            for item in t["entrega"].split("; "):
                print("    - {}".format(item))
        if t.get("aceite"):
            print("\n  {}✅ critérios de aceite (escreva os testes PRIMEIRO a partir daqui):{}".format(
                a["ok"], a["reset"]))
            for item in t["aceite"].split("; "):
                print("    - {}".format(item))
        if not t.get("aceite") and not t.get("entrega"):
            print("  {}(sem contrato no Sprint*.md — defina os critérios com PO/time antes de testar){}".format(
                a["dim"], a["reset"]))
        print("  {}coluna:{} {}  {}deps:{} {}".format(a["dim"], a["reset"], t["col"],
              a["dim"], a["reset"], t.get("deps") or "—"))
        print("")
    return 0


# Catálogo de comandos para o `north help` — fonte única no terminal.
# (terminal, /skill na IA, descrição curta, exemplo)
_HELP_GROUPS = [
    ("🧭 Direção & rituais", [
        ("focus", "north-focus", "a próxima ação de maior valor (respeita seu foco real via git)", "north focus"),
        ("morning", "north-morning", "início do dia: foco consolidado + abre o painel", "north morning"),
        ("wrap-up", "north-wrap-up", "fim do dia: resumo por projeto (seus commits vs time)", "north wrap-up"),
    ]),
    ("📊 Painel", [
        ("panel", "north-panel", "regenera/abre a Central de Produtividade (dashboard)", "north panel"),
        ("open", "—", "só abre o dashboard já gerado", "north open"),
    ]),
    ("🗒️ Captura", [
        ("note <ideia>", "north-note", "captura rápida na inbox sem quebrar o fluxo", "north note \"checar cache\""),
        ("inbox", "north-inbox", "tria as ideias capturadas", "north inbox"),
    ]),
    ("🎓 Mentor (você implementa, a IA orienta)", [
        ("—", "north-learn", "modo mentor: entender o código, não só copiar", "/north-learn"),
        ("—", "north-review", "revisar o seu próprio diff antes do PR", "/north-review"),
        ("—", "north-test", "validar de verdade (API/banco/front)", "/north-test"),
        ("—", "north-codebase", "entender um projeto: arquitetura, onde tudo vive", "/north-codebase"),
        ("—", "north-standup", "conduta em daily/reuniões: reportar, destravar", "/north-standup"),
    ]),
    ("🧪 Desenvolvimento (TDD-first)", [
        ("—", "north-dev", "codar com TDD: testes a partir dos critérios de aceite, depois o código", "/north-dev S3B-2"),
        ("task <id>", "—", "contrato da task: o que entregar + critérios de aceite", "north task TASK-01"),
    ]),
    ("📄 Documentos (SDLC)", [
        ("—", "north-doc", "gera PRD/SPEC/SDD/TDD/ADR/SECURITY + CONTEXT/DECISIONS ancorado no projeto + biblioteca", "/north-doc context"),
        ("doc [list|template]", "—", "gaps de docs por projeto + esqueletos dos templates", "north doc list"),
    ]),
    ("💡 Conhecimento & aprendizado", [
        ("insight check/record/log", "north-insight", "micro-aulas do que a IA usou, sem repetir, por dificuldade", "/north-insight"),
        ("library find/add", "north-library", "biblioteca de referências (bundlada + sua) que a IA consulta", "north library find tdd"),
        ("learnings add/list/find", "—", "ledger do projeto: decisões, bugs, padrões, gotchas (volta no bom-dia)", "north learnings list <proj>"),
    ]),
    ("⚙️ Config & sistema", [
        ("status", "north-status", "o que está instalado, scan_roots, projetos", "north status"),
        ("config", "north-config", "ajusta scan_roots/preferências/projetos", "north config add-root \"<pasta>\""),
        ("help", "north-help", "esta ajuda", "north help"),
        ("uninstall", "north-uninstall", "remove o north (preserva seus dados)", "north uninstall"),
    ]),
]


def cmd_help(home: Path):
    """Explica tudo que o north oferece e como usar — terminal e dentro da IA."""
    a = _ANSI
    print("{}\U0001f9ed north{} — copiloto de produtividade multi-projeto para IAs\n".format(
        a["north"], a["reset"]))
    print("  {}Dois caminhos para o MESMO comando:{}".format(a["dim"], a["reset"]))
    print("    • Terminal:  {}north <cmd>{}".format(a["squad"], a["reset"]))
    print("    • Na IA:     {}/north-<cmd>{}  {}(Gemini: /north:<cmd>){}\n".format(
        a["squad"], a["reset"], a["dim"], a["reset"]))
    for title, items in _HELP_GROUPS:
        print("  {}{}{}".format(a["north"], title, a["reset"]))
        for term, skill, desc, _ex in items:
            left = term if term != "—" else "(só na IA)"
            sk = ("/" + skill) if skill not in ("—", "") else "(terminal)"
            print("    {}{:<26}{} {}{:<15}{} {}".format(
                a["ok"], left, a["reset"], a["squad"], sk, a["reset"], desc))
        print("")
    print("  {}Primeiros passos:{}".format(a["north"], a["reset"]))
    print("    1) {}north morning{}  — vê o foco do dia e abre o painel".format(a["squad"], a["reset"]))
    print("    2) {}north focus{}    — a próxima ação concreta".format(a["squad"], a["reset"]))
    print("    3) {}/north-insight{} — ligue e a IA te ensina enquanto coda".format(a["squad"], a["reset"]))
    print("\n  {}north é READ-ONLY sobre seus planos — só lê, nunca edita.{}".format(a["dim"], a["reset"]))
    print("  {}Config: {}{}".format(a["dim"], _config_path(home), a["reset"]))
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

    # --- config / status: LEVES, sem discovery (so leem/escrevem a config) ---
    if cmd in ("config", "cfg"):
        return cmd_config(home, argv[1:])
    if cmd in ("status", "where", "info"):
        return cmd_status(home)
    if cmd in ("help", "ajuda", "-h", "--help", "h"):
        return cmd_help(home)

    # --- comandos de inbox: LEVES, sem discovery (captura instantanea) ---
    if cmd in ("inbox-add", "note", "btw", "capturar"):
        text = " ".join(argv[1:]).strip()
        if not text:
            print("Nada para capturar. Uso: note <sua ideia>")
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

    # --- insights passivos: LEVE, sem discovery (só ledger + catálogo) ---
    if cmd in ("insight", "insights"):
        from . import insights
        return insights.cmd_insight(home, argv[1:])

    # --- biblioteca de referências: LEVE, sem discovery (índice local) ---
    if cmd in ("library", "lib", "ref", "refs"):
        from . import library
        return library.cmd_library(home, argv[1:])

    # --- ledger de aprendizado: LEVE, sem discovery ---
    if cmd in ("learnings", "learning", "ledger"):
        from . import learnings
        return learnings.cmd_learnings(home, argv[1:])

    # --- enrollment opt-in: LEVE, sem discovery (só registra o caminho na config) ---
    if cmd in ("init", "track", "enroll"):
        return cmd_init(home, argv[1:])
    if cmd in ("forget", "untrack", "unenroll"):
        return cmd_forget(home, argv[1:])

    cfg, projects, new_ids, removed_ids = _load_and_discover(home)
    if new_ids:
        print("  + {} novo(s) projeto(s) descoberto(s): {}".format(
            len(new_ids), ", ".join(new_ids)))
    if removed_ids:
        print("  - {} projeto(s) removido(s) (pasta nao existe mais): {}".format(
            len(removed_ids), ", ".join(removed_ids)))
    if not projects:
        if cfg.discovery_mode == "enrolled":
            print("Nenhum projeto plugado ainda.")
            print("Rode `north init` na raiz de um projeto (com plan-build/.planning) para rastreá-lo.")
        else:
            print("Nenhum projeto com tracking encontrado.")
            print("Verifique scan_roots em: {}".format(home / "config" / "projects.json"))
        return 1

    if cmd in ("build", "dashboard", "panel", "painel"):
        cmd_build(home, cfg, projects)
    elif cmd in ("morning", "bom-dia", "bomdia", "bom_dia"):
        cmd_bom_dia(home, cfg, projects)
    elif cmd in ("wrap-up", "wrapup", "wrap_up", "fim-do-dia", "fimdodia", "fim_do_dia"):
        cmd_fim_do_dia(home, cfg, projects)
    elif cmd in ("focus", "foco", "agora", "next"):
        cmd_foco(home, cfg, projects, argv[1:])
    elif cmd in ("task", "tasks"):
        return cmd_task(home, cfg, projects, argv[1:])
    elif cmd in ("doc", "docs"):
        return cmd_doc(home, cfg, projects, argv[1:])
    else:
        print("Comando desconhecido: {}".format(cmd))
        print("Rode 'north help' para ver tudo. Principais: build | morning | wrap-up | "
              "focus | note | inbox | insight | config | status | open")
        return 2
    return 0
