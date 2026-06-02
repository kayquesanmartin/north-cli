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

import os
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


def cmd_build(home: Path, cfg, projects, quiet=False):
    out_dir = home / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "dashboard.html"
    html = R.render(projects, cfg.settings, IN.open_items(home))
    out_file.write_text(html, encoding="utf-8")
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
        print("Use: build | bom-dia | fim-do-dia | foco | btw <ideia> | inbox | open")
        return 2
    return 0
