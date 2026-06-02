# -*- coding: utf-8 -*-
"""
install.py — O INSTALAVEL do north (copiloto multi-projeto de produtividade).

Rode UMA vez:  python install.py

O que faz (bootstrap completo do ambiente dev):
  1. Detecta ~/.claude (cria se preciso) e a raiz do workspace atual (scan root).
  2. Copia o motor (src/painel + run.py + north_hook.py) para ~/.claude/painel/.
  3. Copia os templates para ~/.claude/painel/templates/.
  4. Instala as skills globais em ~/.claude/skills/: foco, btw, inbox, painel,
     bom-dia, fim-do-dia.
  5. Habilita os plugins do toolchain no ~/.claude/settings.json (code-review,
     code-simplifier, commit-commands, context7, csharp-lsp, frontend-design,
     microsoft-docs, pr-review-toolkit, security-guidance) e checa o gh CLI.
  6. Mostra um MENU para escolher quais projetos acompanhar; gera o primeiro painel.

Idempotente: rodar de novo atualiza motor/skills/plugins e re-descobre projetos
(preserva suas escolhas de config — apelidos, cores, toggles).

Opcional:
  python install.py --scan-root "C:\\caminho\\workspace"   # adiciona/forca raiz
  python install.py --all                                   # acompanha todos (sem menu)
  python install.py --install-gh                            # tenta instalar o gh via winget
  python install.py --skip-plugins                          # nao mexe nos plugins
  python install.py --no-build                              # nao gera o painel agora
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
SKILLS_SRC = Path(__file__).resolve().parent / "skills"
TEMPLATES_SRC = Path(__file__).resolve().parent / "templates"

# Plugins do Claude Code que o north habilita junto (toolchain dev).
# Formato: "<plugin>@<marketplace>". context7 e microsoft-docs trazem MCP que
# conecta sozinho quando o plugin e habilitado.
PLUGINS = [
    "code-review@claude-plugins-official",
    "code-simplifier@claude-plugins-official",
    "commit-commands@claude-plugins-official",
    "context7@claude-plugins-official",
    "csharp-lsp@claude-plugins-official",
    "frontend-design@claude-plugins-official",
    "microsoft-docs@claude-plugins-official",
    "pr-review-toolkit@claude-plugins-official",
    "security-guidance@claude-plugins-official",
]


def claude_home() -> Path:
    return Path.home() / ".claude"


def detect_scan_root() -> Path:
    """Raiz do workspace a rastrear: sobe a partir do install.py procurando uma
    pasta que contenha 'plan-build' em algum nivel. Fallback: pasta do install."""
    here = Path(__file__).resolve().parent
    # install.py mora em .../<workspace>/dashboard/install.py -> workspace = parent.parent
    candidate = here.parent
    return candidate


def copy_engine(home: Path):
    engine = home / "painel"
    # limpa apenas o codigo (preserva config/output/resumos do usuario)
    pkg_dst = engine / "painel"
    if pkg_dst.exists():
        shutil.rmtree(pkg_dst)
    shutil.copytree(SRC / "painel", pkg_dst)
    shutil.copy2(SRC / "run.py", engine / "run.py")
    shutil.copy2(SRC / "north_hook.py", engine / "north_hook.py")   # painel vivo (hook)
    # templates
    tdst = engine / "templates"
    tdst.mkdir(parents=True, exist_ok=True)
    if TEMPLATES_SRC.exists():
        for f in TEMPLATES_SRC.glob("*"):
            shutil.copy2(f, tdst / f.name)
    # dirs de estado
    (engine / "config").mkdir(exist_ok=True)
    (engine / "output").mkdir(exist_ok=True)
    (engine / "resumos").mkdir(exist_ok=True)
    return engine


def install_skills(home: Path):
    skills_dst = home / "skills"
    skills_dst.mkdir(parents=True, exist_ok=True)
    installed = []
    for skill_dir in SKILLS_SRC.glob("*"):
        if not skill_dir.is_dir():
            continue
        dst = skills_dst / skill_dir.name
        dst.mkdir(exist_ok=True)
        shutil.copy2(skill_dir / "SKILL.md", dst / "SKILL.md")
        installed.append(skill_dir.name)
    return installed


def _detect_owner_name():
    """Primeiro nome do dev (git user.name) para a saudacao do bom-dia. Fallback 'dev'."""
    try:
        r = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, timeout=8)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().split()[0]
    except Exception:
        pass
    return "dev"


def seed_config(engine: Path, scan_root: Path, extra_root: str = None):
    cfg_path = engine / "config" / "projects.json"
    if cfg_path.exists():
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    else:
        data = {"scan_roots": [], "exclude": [], "projects": {}, "settings": {}}

    roots = data.setdefault("scan_roots", [])
    for r in [str(scan_root)] + ([extra_root] if extra_root else []):
        if r and r not in roots:
            roots.append(r)

    data.setdefault("settings", {})
    data["settings"].setdefault("owner_name", _detect_owner_name())
    data["settings"].setdefault("title", "north")
    data["settings"].setdefault("theme", "dark")
    data["settings"].setdefault("open_browser", True)
    data["settings"].setdefault("mirror_to_project_docs", True)

    cfg_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return cfg_path


def ensure_plugins(home: Path):
    """Habilita os plugins do toolchain em ~/.claude/settings.json (merge seguro).
    Preserva TODAS as outras configs. Devolve (novos, ja_presentes)."""
    settings = home / "settings.json"
    if settings.exists():
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except Exception:
            print("  plugins        -> settings.json invalido; pulei (corrija manualmente)")
            return [], []
    else:
        data = {}

    ep = data.setdefault("enabledPlugins", {})
    novos, ja = [], []
    for p in PLUGINS:
        if ep.get(p) is True:
            ja.append(p)
        else:
            ep[p] = True
            novos.append(p)

    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return novos, ja


def _which(cmd):
    from shutil import which
    return which(cmd)


def ensure_gh(install_opt=False):
    """Checa o gh CLI (necessario para autoria @github do north). Detecta +
    orienta; com --install-gh tenta instalar via winget. Nunca quebra o install."""
    gh = _which("gh")
    if gh:
        authed = False
        try:
            r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=10)
            authed = r.returncode == 0
        except Exception:
            pass
        if authed:
            login = ""
            try:
                r = subprocess.run(["gh", "api", "user", "--jq", ".login"],
                                   capture_output=True, text=True, timeout=10)
                login = r.stdout.strip() if r.returncode == 0 else ""
            except Exception:
                pass
            print("  gh cli         -> OK{}".format(" (@" + login + ")" if login else " (autenticado)"))
        else:
            print("  gh cli         -> instalado, mas NAO autenticado. Rode: gh auth login")
        return

    # gh ausente
    if install_opt and _which("winget"):
        print("  gh cli         -> instalando via winget...")
        try:
            subprocess.run(["winget", "install", "--id", "GitHub.cli", "-e",
                            "--source", "winget", "--accept-package-agreements",
                            "--accept-source-agreements"], timeout=300)
            print("  gh cli         -> instalado. Agora rode: gh auth login")
        except Exception as e:
            print("  gh cli         -> falha no winget ({}); instale manualmente".format(e))
        return

    mgr = next((m for m in ("winget", "scoop", "choco") if _which(m)), None)
    hint = {
        "winget": "winget install --id GitHub.cli -e",
        "scoop": "scoop install gh",
        "choco": "choco install gh",
    }.get(mgr, "baixe em https://cli.github.com")
    print("  gh cli         -> NAO encontrado. A autoria @github do north precisa dele.")
    print("                    Instale: {}   (depois: gh auth login)".format(hint))
    print("                    Ou rode o instalador com --install-gh")


def _parse_selection(raw, n):
    """Interpreta '1,3', '1-2,4', 'todos', '' (=todos), 'nenhum'. Devolve set 1-based."""
    raw = (raw or "").strip().lower()
    if raw in ("", "todos", "tudo", "all", "t"):
        return set(range(1, n + 1))
    if raw in ("nenhum", "none", "0"):
        return set()
    picked = set()
    for part in re.split(r"[,\s]+", raw):
        if not part:
            continue
        if "-" in part:
            try:
                a, b = part.split("-", 1)
                for k in range(int(a), int(b) + 1):
                    if 1 <= k <= n:
                        picked.add(k)
            except ValueError:
                pass
        elif part.isdigit():
            k = int(part)
            if 1 <= k <= n:
                picked.add(k)
    return picked


def select_projects(candidates, auto_all):
    """Mostra o menu de projetos descobertos e devolve o set de ids selecionados.
    Sem TTY ou com --all: seleciona todos os nao-template."""
    real = [c for c in candidates if not c["is_template"]]
    templates = [c for c in candidates if c["is_template"]]

    print("")
    print("-" * 64)
    print("  Projetos rastreaveis encontrados:")
    print("-" * 64)
    for i, c in enumerate(real, 1):
        print("   [{}] {:<24} {} sprints | {} tasks".format(
            i, c["id"][:24], c["sprints"], c["tasks"]))
    for c in templates:
        print("       {:<24} (template - ignorado)".format(c["id"][:24]))
    print("-" * 64)

    if not real:
        return set()

    if auto_all or not sys.stdin.isatty():
        print("  Selecionando todos automaticamente.")
        return {c["id"] for c in real}

    try:
        raw = input("  Quais acompanhar? [numeros ex '1,3', intervalo '1-2', Enter=todos]: ")
    except (EOFError, KeyboardInterrupt):
        raw = ""
    idxs = _parse_selection(raw, len(real))
    return {real[i - 1]["id"] for i in idxs}


def apply_selection(cfg_path, selected_ids, all_ids):
    """Grava enabled=True/False por projeto na config conforme a selecao."""
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    projs = data.setdefault("projects", {})
    for pid in all_ids:
        entry = projs.setdefault(pid, {"enabled": True, "alias": "", "color": "", "order": 0})
        entry["enabled"] = pid in selected_ids
    cfg_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # console limpo em qualquer terminal Windows
    except Exception:
        pass
    args = sys.argv[1:]
    extra_root = None
    do_build = True
    auto_all = "--all" in args
    install_gh = "--install-gh" in args
    skip_plugins = "--skip-plugins" in args
    if "--no-build" in args:
        do_build = False
    if "--scan-root" in args:
        i = args.index("--scan-root")
        if i + 1 < len(args):
            extra_root = args[i + 1]

    print("=" * 64)
    print("  Instalando o north")
    print("=" * 64)

    home = claude_home()
    home.mkdir(parents=True, exist_ok=True)
    print("  .claude        -> {}".format(home))

    engine = copy_engine(home)
    print("  motor          -> {}".format(engine))

    skills = install_skills(home)
    print("  skills         -> {} ({})".format(home / "skills", ", ".join(skills)))

    # ---- plugins do toolchain + gh cli ----
    if not skip_plugins:
        novos, ja = ensure_plugins(home)
        print("  plugins        -> {} habilitado(s) ({} novo(s), {} ja ativo(s))".format(
            len(novos) + len(ja), len(novos), len(ja)))
    ensure_gh(install_gh)

    scan_root = detect_scan_root()
    cfg_path = seed_config(engine, scan_root, extra_root)
    print("  config         -> {}".format(cfg_path))
    print("  scan root      -> {}".format(scan_root))

    # ---- menu interativo: escolher quais projetos acompanhar ----
    sys.path.insert(0, str(engine))
    from painel.discovery import scan_candidates  # noqa
    roots = [scan_root] + ([Path(extra_root)] if extra_root else [])
    candidates = scan_candidates(roots)
    if candidates:
        selected = select_projects(candidates, auto_all)
        apply_selection(cfg_path, selected, [c["id"] for c in candidates])
        print("  acompanhando   -> {}".format(
            ", ".join(sorted(selected)) if selected else "(nenhum selecionado)"))
    else:
        print("  acompanhando   -> nenhum projeto rastreavel encontrado sob a raiz")

    if do_build:
        print("  gerando o primeiro painel (auto-descoberta)...")
        sys.path.insert(0, str(engine))
        from painel.cli import main as cli_main  # noqa
        cli_main(["build"], engine)

    out = engine / "output" / "dashboard.html"
    print("")
    print("=" * 64)
    print("  PRONTO. Como usar:")
    print("=" * 64)
    print("  No Claude Code (de QUALQUER projeto):")
    print("    /foco          a próxima ação + squad sugerido")
    print("    /btw <ideia>   captura rápida sem quebrar o fluxo")
    print("    /inbox         tria as ideias capturadas")
    print("    /bom-dia       foco do dia + lembretes + abre o painel")
    print("    /fim-do-dia    resumos do dia por projeto")
    print("    /painel        regenera e abre o painel")
    print("")
    print("  Direto no terminal:")
    print('    python "{}" foco'.format(engine / "run.py"))
    print("")
    print("  Painel: {}".format(out))
    print("  Config (apelidos/cores/toggles): {}".format(cfg_path))
    print("  Plugins habilitados: reinicie o Claude Code (ou /hooks) para carregar.")
    print("=" * 64)


if __name__ == "__main__":
    main()
