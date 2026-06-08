# -*- coding: utf-8 -*-
"""
install.py — O INSTALAVEL do north (copiloto multi-projeto de produtividade).

Rode UMA vez:  python install.py

O que faz (bootstrap completo do ambiente dev):
  1. Detecta ~/.claude (cria se preciso) e a raiz do workspace atual (scan root).
  2. Copia o motor (src/painel + run.py + north_hook.py) para ~/.claude/painel/.
  3. Copia os templates para ~/.claude/painel/templates/.
  4. Instala as skills globais em ~/.claude/skills/: focus, note, inbox, panel, status, config,
     morning, wrap-up (+ aliases pt-BR).
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
  python install.py --statusline                            # FORCA a statusline do north (substitui a atual)
  python install.py --no-statusline                         # nao configura a statusline
  python install.py --add-to-path                           # cria o comando `north` no terminal (+PATH)
  python install.py --no-path                               # nao mexe no PATH (sem prompt)
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import runtimes as RT

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
    """Raiz do workspace a rastrear. Cross-contexto (clone, npm global, npx):
      1. o diretorio atual onde o usuario invocou (caso npx/terminal — o mais comum);
      2. se invocado de DENTRO do proprio pacote/repo do north, sobe um nivel
         (clone: .../<workspace>/north/install.py -> workspace).
    O scan_root e apenas ANEXADO a config (nunca substitui), entao e seguro."""
    here = Path(__file__).resolve().parent
    try:
        cwd = Path.cwd().resolve()
    except Exception:
        return here.parent
    # rodando de dentro do pacote (ex.: node_modules/north-cli, ou o proprio repo)
    if cwd == here:
        return here.parent
    return cwd


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


def setup_hooks(home: Path, engine: Path):
    """Registra o north_hook (PostToolUse) em settings.json — NAO-destrutivo.
    Regenera o painel quando ha git commit/push ou edicao de plano. 'set'|'updated'|'invalid'."""
    settings = home / "settings.json"
    if settings.exists():
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except Exception:
            return "invalid"
    else:
        data = {}
    command = '"{}" "{}"'.format(
        sys.executable.replace("\\", "/"), str(engine / "north_hook.py").replace("\\", "/"))
    hooks = data.setdefault("hooks", {})
    status = "set"
    # PostToolUse: regenera o painel (commit/push/PR/edicao de plano)
    # PreToolUse:  avisa antes de push/PR se a branch esta atrasada
    for event, matcher in (("PostToolUse", "Bash|Edit|Write|MultiEdit|NotebookEdit"),
                           ("PreToolUse", "Bash")):
        bucket = hooks.setdefault(event, [])
        found = False
        for entry in bucket:
            for h in entry.get("hooks", []):
                if "north_hook.py" in (h.get("command", "") or ""):
                    h["command"] = command  # migra caminho antigo
                    found = True
                    status = "updated"
        if not found:
            bucket.append({"matcher": matcher,
                           "hooks": [{"type": "command", "command": command}]})
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return status


def setup_statusline(home: Path, engine: Path, force=False):
    """Configura a statusline do north em ~/.claude/settings.json (NAO-destrutivo).
    So escreve se nao houver statusLine, a menos que force=True. Devolve um status:
    'set' | 'exists' | 'forced' | 'invalid'."""
    settings = home / "settings.json"
    if settings.exists():
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except Exception:
            return "invalid", None
    else:
        data = {}

    run_py = str(engine / "run.py").replace("\\", "/")
    py = sys.executable.replace("\\", "/")
    command = '"{}" "{}" statusline'.format(py, run_py)
    new_sl = {"type": "command", "command": command, "padding": 1}

    existing = data.get("statusLine")
    existing_cmd = (existing or {}).get("command", "") if isinstance(existing, dict) else ""
    # statusline que JA e do north (aponta pro nosso run.py statusline) -> atualiza
    # livremente (migra do engine antigo p/ o novo). Outra (ex.: GSD) -> preserva.
    is_ours = "run.py" in existing_cmd and "statusline" in existing_cmd
    if existing and not force and not is_ours:
        return "exists", command

    data["statusLine"] = new_sl
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    if is_ours and not force:
        return "updated", command
    return ("forced" if existing else "set"), command


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

    mgr = next((m for m in ("brew", "winget", "scoop", "choco", "apt", "dnf", "pacman")
                if _which(m)), None)
    hint = {
        "brew": "brew install gh",
        "winget": "winget install --id GitHub.cli -e",
        "scoop": "scoop install gh",
        "choco": "choco install gh",
        "apt": "sudo apt install gh",
        "dnf": "sudo dnf install gh",
        "pacman": "sudo pacman -S github-cli",
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


def _arg_value(args, flag, default=None):
    if flag in args:
        i = args.index(flag)
        if i + 1 < len(args):
            return args[i + 1]
    return default


def do_uninstall(args):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    purge = "--purge" in args
    assume_yes = ("--yes" in args) or ("-y" in args)
    all_rt = "--all" in args
    rt_csv = _arg_value(args, "--runtimes")
    tool_home = RT.engine_home("global")

    installed = [k for k in RT.RUNTIMES if RT.runtime_installed(k)]
    print("=" * 64)
    print("  Desinstalar o north")
    print("=" * 64)
    if not installed and not tool_home.exists():
        print("  Nada do north encontrado. Nada a fazer.")
        return 0
    print("  Runtimes com north: {}".format(", ".join(installed) or "nenhum"))
    print("  Motor: {}{}".format(tool_home, "" if tool_home.exists() else " (ausente)"))

    # --- seleção de runtimes (flags > --all > menu interativo > todos) ---
    if rt_csv:
        sel = [r.strip() for r in rt_csv.split(",") if r.strip() in RT.RUNTIMES]
    elif all_rt or not sys.stdin.isatty():
        sel = list(installed)
    else:
        print("")
        print("  De quais runtimes remover?")
        for i, k in enumerate(installed, 1):
            print("   [{}] {}".format(i, RT.RUNTIMES[k][0]))
        print("   [a] todos")
        try:
            raw = input("  Escolha [Enter = todos]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            raw = ""
        if raw in ("", "a", "todos"):
            sel = list(installed)
        else:
            idxs = _parse_selection(raw, len(installed))
            sel = [installed[i - 1] for i in idxs] or list(installed)

    # --- apagar dados? ---
    if not purge and not assume_yes and sys.stdin.isatty():
        try:
            ans = input("  Apagar tambem seus DADOS (config/inbox/resumos)? [s/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = ""
        purge = ans in ("s", "sim", "y", "yes")

    # --- confirmação ---
    if not assume_yes and sys.stdin.isatty():
        extra = " + DADOS" if purge else " (dados preservados)"
        try:
            ans = input("  Confirmar remocao de [{}]{}? [s/N]: ".format(", ".join(sel), extra)).strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = ""
        if ans not in ("s", "sim", "y", "yes"):
            print("  Cancelado.")
            return 1

    for k in sel:
        rem = RT.uninstall_runtime(k)
        print("  {:<12} -> {}".format(RT.RUNTIMES[k][0], ", ".join(rem) or "nada"))

    remaining = [k for k in RT.RUNTIMES if RT.runtime_installed(k)]
    if purge or all_rt or not remaining:
        rem = RT.uninstall_engine(tool_home, purge=purge)
        print("  {:<12} -> {}".format("Motor", ", ".join(rem) or "nada"))
        if not purge and tool_home.exists():
            print("  (seus dados ficaram preservados em {})".format(tool_home))
    else:
        print("  Motor preservado (ainda usado por: {}).".format(", ".join(remaining)))
    print("")
    print("  north desinstalado.")
    return 0


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = sys.argv[1:]
    if args and args[0] in ("uninstall", "remove"):
        sys.exit(do_uninstall(args[1:]))
    auto_all = "--all" in args
    install_gh = "--install-gh" in args
    skip_plugins = "--skip-plugins" in args
    skip_statusline = "--no-statusline" in args
    skip_hooks = "--no-hooks" in args
    force_statusline = "--statusline" in args
    do_build = "--no-build" not in args
    extra_root = _arg_value(args, "--scan-root")
    scope = (_arg_value(args, "--scope", "global") or "global").lower()
    # runtimes alvo (csv). Default: claude (compat). Node passa a seleção do usuario.
    runtimes_csv = _arg_value(args, "--runtimes", "claude")
    targets = [r.strip() for r in runtimes_csv.split(",") if r.strip() in RT.RUNTIMES]
    if not targets:
        targets = ["claude"]

    print("=" * 64)
    print("  Instalando o north  ({} | runtimes: {})".format(
        scope, ", ".join(RT.RUNTIMES[t][0] for t in targets)))
    print("=" * 64)

    # ---- motor (uma vez, home neutro ~/.north) ----
    tool_home = RT.engine_home(scope)
    RT.install_engine(tool_home)
    if RT.migrate_legacy_config(tool_home):
        print("  config         -> migrada de ~/.claude/painel (preservada)")
    print("  motor          -> {}".format(tool_home))

    # ---- scan root (pasta dos projetos) ----
    scan_root = Path(extra_root).expanduser() if extra_root else detect_scan_root()
    if sys.stdin.isatty() and not auto_all and not extra_root:
        print("")
        print("  Onde ficam seus projetos? O north varre essa pasta (e subpastas)")
        print("  atras de projetos com plan-build/ ou .planning/.")
        print("  Dica: aponte para a pasta-raiz que contem todos os seus repos.")
        print("  Exemplos: ~/code  ~/projetos  ./workspace   (Enter = sugestao)")
        try:
            ans = input("  Pasta dos projetos [{}]: ".format(scan_root)).strip().strip('"').strip("'")
        except (EOFError, KeyboardInterrupt):
            ans = ""
        if ans:
            scan_root = Path(ans).expanduser()
        if not scan_root.exists():
            try:
                yn = input("  '{}' nao existe. Criar agora? [S/n]: ".format(scan_root)).strip().lower()
            except (EOFError, KeyboardInterrupt):
                yn = ""
            if yn in ("", "s", "sim", "y", "yes"):
                try:
                    scan_root.mkdir(parents=True, exist_ok=True)
                    print("  (criada: {})".format(scan_root))
                except Exception as e:
                    print("  (nao consegui criar: {} — registrando assim mesmo)".format(e))
            else:
                print("  (registrando '{}' sem existir — crie depois)".format(scan_root))
    cfg_path = seed_config(tool_home, scan_root)
    print("  scan root      -> {}".format(scan_root))

    pyexe = sys.executable

    # ---- cascas por runtime ----
    def rt_home(rt):
        return (Path.cwd() / ("." + rt)) if scope == "local" else RT.RUNTIMES[rt][1]

    sl_status = None
    for rt in targets:
        home = rt_home(rt)
        home.mkdir(parents=True, exist_ok=True)
        installed = RT.ADAPTERS[rt](home, tool_home, pyexe)
        print("  [{:<11}] {} comando(s) -> {}".format(
            RT.RUNTIMES[rt][0], len(installed), home))
        # extras especificos do Claude Code: plugins + statusline
        if rt == "claude":
            if not skip_plugins:
                novos, ja = ensure_plugins(home)
                print("               plugins: {} habilitado(s)".format(len(novos) + len(ja)))
            if not skip_statusline:
                sl_status, sl_cmd = setup_statusline(home, tool_home, force=force_statusline)
                if sl_status == "set":
                    print("               statusline configurada")
                elif sl_status == "updated":
                    print("               statusline do north atualizada (-> ~/.north)")
                elif sl_status == "forced":
                    print("               statusline SUBSTITUIDA (--statusline)")
                elif sl_status == "exists":
                    print("               statusline ja existe (outra); preservada (--statusline forca)")
            if not skip_hooks:
                hk = setup_hooks(home, tool_home)
                if hk == "set":
                    print("               hook 'painel vivo' registrado (regenera no commit/push/edicao)")
                elif hk == "updated":
                    print("               hook 'painel vivo' atualizado (-> ~/.north)")

    ensure_gh(install_gh)

    # ---- launcher de terminal (opcional, opt-in) — comando `north` fora da IA ----
    # Precedencia: flags explicitas > prompt interativo (global) > nao instala.
    if "--add-to-path" in args:
        want_path = True
    elif "--no-path" in args:
        want_path = False
    elif scope == "global" and sys.stdin.isatty():
        print("")
        print("  Quer usar o comando 'north' direto no terminal (fora da IA)?")
        print("  Isso cria um launcher em {} e o adiciona ao seu PATH.".format(tool_home / "bin"))
        try:
            ans = input("  Habilitar 'north' no terminal? [s/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = ""
        want_path = ans in ("s", "sim", "y", "yes")
    else:
        want_path = False

    if want_path and scope == "global":
        bindir, _w = RT.install_launcher(tool_home, pyexe)
        st, detail = RT.add_to_path(bindir)
        if st == "already":
            print("  terminal       -> 'north' pronto ({} ja no PATH)".format(bindir))
        elif st == "added":
            print("  terminal       -> 'north' instalado; PATH atualizado{}".format(
                " (" + detail + ")" if detail else ""))
            print("                    Abra um NOVO terminal para o 'north' funcionar.")
        else:  # manual
            print("  terminal       -> launcher criado em {}".format(bindir))
            print("                    Adicione esse diretorio ao PATH para usar 'north'.")
    elif want_path and scope == "local":
        print("  terminal       -> PATH so e configurado no escopo global (pulei no local)")

    if do_build:
        sys.path.insert(0, str(tool_home))
        try:
            from painel.cli import main as cli_main  # noqa
            cli_main(["build"], tool_home)
        except Exception as e:
            print("  (painel sera gerado no primeiro uso — {})".format(e))

    print("")
    print("=" * 64)
    print("  ✅ PRONTO — north instalado para: {}".format(
        ", ".join(RT.RUNTIMES[t][0] for t in targets)))
    print("=" * 64)
    print("")
    print("  ▶ Comece agora, DENTRO da sua IA (é onde o north vive):")
    if "claude" in targets:
        print("      Claude Code   digite  /north-focus   (depois: /north-morning · /north-panel)")
    if "codex" in targets:
        print("      Codex         digite  /north-focus   (depois: /north-morning · /north-panel)")
    if "gemini" in targets:
        print("      Gemini CLI    digite  /north:focus   (depois: /north:morning · /north:panel)")
    print("")
    print("  Comandos: focus · morning · wrap-up · panel · note · inbox · status · config · learn · review · test · uninstall")
    print("            (todos viram /north-<cmd> na sua IA; /north:<cmd> no Gemini)")
    print("")
    if want_path and scope == "global":
        print("  Terminal: north status · north config add-root \"<pasta>\"  (novo terminal)")
    else:
        print("  Terminal (opcional): habilite com  python install.py --add-to-path")
        print("            depois: north status · north panel · north config add-root \"<pasta>\"")
    print("  Config: {}".format(cfg_path))
    if sl_status in ("set", "forced", "updated"):
        print("  ↻ Reinicie o Claude Code para a statusline aparecer.")
    print("=" * 64)


if __name__ == "__main__":
    main()
