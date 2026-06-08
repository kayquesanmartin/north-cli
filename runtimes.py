# -*- coding: utf-8 -*-
"""
runtimes.py — instala o MOTOR do north uma vez e gera as "cascas" de integração
por runtime de IA (Claude Code, Codex, Gemini CLI).

Filosofia: o north é um motor Python (painel) que mora num home neutro
(`~/.north`). Cada runtime só ganha comandos que CHAMAM esse motor:
  - Claude Code -> skills SKILL.md em ~/.claude/skills/
  - Codex       -> prompts .md em ~/.codex/prompts/   (mesma ideia; agente roda o motor)
  - Gemini CLI  -> comandos TOML em ~/.gemini/commands/north/  (usa !{shell})

O caminho do interpretador + run.py é ASSADO no momento do install (absoluto),
para não depender de PATH nem do nome do python em cada SO.
"""

import json
import os
import shutil
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
SKILLS_SRC = HERE / "skills"
TEMPLATES_SRC = HERE / "templates"

# Runtimes suportados: nome -> (rótulo, home global)
RUNTIMES = {
    "claude": ("Claude Code", Path.home() / ".claude"),
    "codex":  ("Codex",       Path.home() / ".codex"),
    "gemini": ("Gemini CLI",  Path.home() / ".gemini"),
}

# Comandos do north expostos em cada runtime.
#   name: nome do comando/skill   sub: subcomando do run.py   args: aceita texto livre
CMDSPEC = [
    {"name": "focus", "sub": "focus", "args": False, "aliases": ["foco"],
     "desc": "north — a próxima ação de maior valor entre todos os projetos + squad sugerido."},
    {"name": "morning", "sub": "morning", "args": False, "aliases": ["bom-dia"],
     "desc": "north — ritual de início do dia: foco consolidado + abre o painel."},
    {"name": "wrap-up", "sub": "wrap-up", "args": False, "aliases": ["fim-do-dia"],
     "desc": "north — ritual de fim do dia: resumo por projeto."},
    {"name": "panel", "sub": "build", "args": False, "aliases": ["painel"],
     "desc": "north — regenera a Central de Produtividade (dashboard multi-projeto)."},
    {"name": "note", "sub": "note", "args": True, "aliases": [],
     "desc": "north — captura rápida de uma ideia na inbox, sem quebrar o fluxo."},
    {"name": "inbox", "sub": "inbox", "args": False, "aliases": [],
     "desc": "north — tria as ideias capturadas com /note."},
    {"name": "status", "sub": "status", "args": False, "aliases": [],
     "desc": "north — o que está instalado, scan_roots e projetos rastreados."},
    {"name": "help", "sub": "help", "args": False, "aliases": ["ajuda"],
     "desc": "north — guia: tudo que a ferramenta oferece e como usar (terminal + IA)."},
    {"name": "library", "sub": "library", "args": True, "aliases": ["biblioteca"],
     "desc": "north — biblioteca de referências de engenharia (consultar/popular): library find <tópico>."},
    {"name": "config", "sub": "config", "args": True, "aliases": [],
     "desc": "north — ajusta a configuração (scan_roots, settings, projetos) sem reinstalar."},
    {"name": "learn", "sub": "", "args": True, "aliases": [], "behavior": True,
     "desc": "north — modo mentor: a IA orienta e você implementa (entender o código, não só copiar)."},
    {"name": "review", "sub": "", "args": True, "aliases": [], "behavior": True,
     "desc": "north — trilha mentor de code review: te guia a revisar o seu próprio diff."},
    {"name": "test", "sub": "", "args": True, "aliases": [], "behavior": True,
     "desc": "north — trilha mentor de testes: validar de verdade (API/banco/front), você executa."},
    {"name": "codebase", "sub": "", "args": True, "aliases": [], "behavior": True,
     "desc": "north — trilha mentor para entender um projeto: arquitetura, onde as coisas vivem, banco, organização."},
    {"name": "standup", "sub": "", "args": True, "aliases": [], "behavior": True,
     "desc": "north — trilha mentor de conduta em daily/reuniões: reportar, destravar, alinhar."},
    {"name": "insight", "sub": "", "args": True, "aliases": [], "behavior": True,
     "desc": "north — insights passivos: enquanto a IA coda, te ensina por cima o que usou (sem repetir, ranqueado por dificuldade)."},
    {"name": "dev", "sub": "", "args": True, "aliases": [], "behavior": True,
     "desc": "north — codar com TDD-first: escreve os testes a partir dos critérios de aceite ANTES do código (red→green→refactor)."},
    {"name": "task", "sub": "task", "args": True, "aliases": [],
     "desc": "north — mostra o contrato de uma task (o que entregar + critérios de aceite)."},
]


def engine_home(scope: str) -> Path:
    """Home neutro do motor. global -> ~/.north ; local -> ./.north"""
    return (Path.cwd() / ".north") if scope == "local" else (Path.home() / ".north")


def _fwd(p) -> str:
    return str(p).replace("\\", "/")


def install_engine(tool_home: Path):
    """Copia o motor (painel + run.py + north_hook.py + templates) para o home neutro.
    Preserva config/output/resumos do usuário."""
    tool_home.mkdir(parents=True, exist_ok=True)
    pkg_dst = tool_home / "painel"
    if pkg_dst.exists():
        shutil.rmtree(pkg_dst)
    shutil.copytree(SRC / "painel", pkg_dst, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(SRC / "run.py", tool_home / "run.py")
    shutil.copy2(SRC / "north_hook.py", tool_home / "north_hook.py")
    tdst = tool_home / "templates"
    tdst.mkdir(parents=True, exist_ok=True)
    if TEMPLATES_SRC.exists():
        for f in TEMPLATES_SRC.glob("*"):
            shutil.copy2(f, tdst / f.name)
    # references/ (catálogo de conceitos p/ insights, princípios) — read-only, bundlado
    refs_src = HERE / "references"
    if refs_src.exists():
        refs_dst = tool_home / "references"
        if refs_dst.exists():
            shutil.rmtree(refs_dst)
        shutil.copytree(refs_src, refs_dst, ignore=shutil.ignore_patterns("__pycache__"))
    for d in ("config", "output", "resumos"):
        (tool_home / d).mkdir(exist_ok=True)
    return tool_home


def migrate_legacy_config(tool_home: Path):
    """Se houver uma config antiga em ~/.claude/painel e o ~/.north ainda não tiver,
    migra (preserva scan_roots, toggles, settings do usuário). Devolve True se migrou."""
    new_cfg = tool_home / "config" / "projects.json"
    if new_cfg.exists():
        return False
    legacy = Path.home() / ".claude" / "painel" / "config" / "projects.json"
    if legacy.exists():
        new_cfg.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy, new_cfg)
        return True
    return False


def engine_cmd(pyexe: str, tool_home: Path) -> str:
    """Comando base (absoluto) para invocar o motor, assado no install."""
    return '"{}" "{}"'.format(_fwd(pyexe), _fwd(tool_home / "run.py"))


# ---------------------------------------------------------------------------
# Launcher de terminal (opcional) — cria o comando `north` fora da IA.
#
# Quando o north é instalado via `python install.py` (e não via shim global do
# npm), não existe nenhum `north` no PATH. Aqui criamos um launcher em
# `<tool_home>/bin` e, opcionalmente, anexamos esse dir ao PATH do usuário.
# Tudo é opt-in e reversível (a desinstalação limpa o launcher e o PATH).
# ---------------------------------------------------------------------------
PATH_MARKER = "# north terminal launcher"


def launcher_dir(tool_home: Path) -> Path:
    return tool_home / "bin"


def install_launcher(tool_home: Path, pyexe: str):
    """Escreve o(s) launcher(s) `north` em <tool_home>/bin. No Windows cria
    `north.cmd` (cmd/PowerShell) e `north` (Git Bash); em Unix, `north` (+x).
    Devolve (bindir, [arquivos])."""
    bindir = launcher_dir(tool_home)
    bindir.mkdir(parents=True, exist_ok=True)
    run_py = tool_home / "run.py"
    written = []

    # launcher POSIX (Unix shells e Git Bash no Windows) — LF puro (newline="\n",
    # senao o text-mode do Windows quebraria o shebang com CR).
    sh = ("#!/bin/sh\n" + PATH_MARKER + "\n"
          'exec "{}" "{}" "$@"\n').format(_fwd(pyexe), _fwd(run_py))
    shp = bindir / "north"
    with shp.open("w", encoding="utf-8", newline="\n") as f:
        f.write(sh)
    try:
        shp.chmod(shp.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass
    written.append("north")

    if os.name == "nt":
        # CRLF para o cmd.exe (newline="\r\n" converte os \n do conteudo)
        cmd = ("@echo off\nrem " + PATH_MARKER + "\n"
               '"{}" "{}" %*\n').format(str(pyexe), str(run_py))
        cp = bindir / "north.cmd"
        with cp.open("w", encoding="utf-8", newline="\r\n") as f:
            f.write(cmd)
        written.append("north.cmd")
    return bindir, written


def _path_norm(p):
    return os.path.normcase(os.path.normpath(str(p)))


def _on_path(bindir) -> bool:
    nb = _path_norm(bindir)
    return any(_path_norm(p) == nb for p in os.environ.get("PATH", "").split(os.pathsep) if p)


def add_to_path(bindir):
    """Anexa bindir ao PATH persistente do usuário (idempotente).
    Devolve (status, detail): 'already' | 'added'(+rc/None) | 'manual'(+bindir)."""
    bindir = str(bindir)
    if _on_path(bindir):
        return "already", None
    return _win_path_add(bindir) if os.name == "nt" else _unix_path_add(bindir)


def _win_path_add(bindir):
    """Anexa ao PATH do usuário via registro (HKCU\\Environment) — sem o limite
    de 1024 do `setx`, preservando as entradas existentes. Faz broadcast para
    novas shells. Em qualquer falha, degrada para 'manual'."""
    try:
        import winreg
    except Exception:
        return "manual", bindir
    key = None
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                             winreg.KEY_READ | winreg.KEY_WRITE)
        try:
            cur, typ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            cur, typ = "", winreg.REG_EXPAND_SZ
        if typ not in (winreg.REG_EXPAND_SZ, winreg.REG_SZ):
            typ = winreg.REG_EXPAND_SZ
        parts = [p for p in (cur or "").split(";") if p]
        nb = _path_norm(bindir)
        if any(_path_norm(p) == nb for p in parts):
            return "already", None
        parts.append(bindir)
        winreg.SetValueEx(key, "Path", 0, typ, ";".join(parts))
    except Exception:
        return "manual", bindir
    finally:
        if key is not None:
            try:
                winreg.CloseKey(key)
            except Exception:
                pass
    try:
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x1A, 0, "Environment", 0, 5000, ctypes.byref(ctypes.c_ulong()))
    except Exception:
        pass
    return "added", None


def _unix_rc_file() -> Path:
    shell = os.environ.get("SHELL", "")
    home = Path.home()
    if "zsh" in shell:
        return home / ".zshrc"
    if "bash" in shell:
        return home / ".bashrc"
    return home / ".profile"


def _unix_path_add(bindir):
    rc = _unix_rc_file()
    block = "\n{}\nexport PATH=\"{}:$PATH\"\n".format(PATH_MARKER, bindir)
    try:
        existing = rc.read_text(encoding="utf-8") if rc.exists() else ""
        if PATH_MARKER in existing or bindir in existing:
            return "already", None
        with rc.open("a", encoding="utf-8") as f:
            f.write(block)
        return "added", str(rc)
    except Exception:
        return "manual", bindir


def remove_from_path(bindir):
    """Remove a entrada de PATH criada pelo north (uninstall). Best-effort."""
    bindir = str(bindir)
    if os.name == "nt":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                                 winreg.KEY_READ | winreg.KEY_WRITE)
            try:
                cur, typ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                cur, typ = "", winreg.REG_EXPAND_SZ
            nb = _path_norm(bindir)
            parts = [p for p in (cur or "").split(";") if p and _path_norm(p) != nb]
            winreg.SetValueEx(key, "Path", 0,
                              typ if typ in (winreg.REG_EXPAND_SZ, winreg.REG_SZ) else winreg.REG_EXPAND_SZ,
                              ";".join(parts))
            winreg.CloseKey(key)
        except Exception:
            pass
        return
    # Unix: remove o bloco marcado do rc
    rc = _unix_rc_file()
    try:
        if not rc.exists():
            return
        lines = rc.read_text(encoding="utf-8").splitlines(keepends=True)
        out, skip = [], 0
        for ln in lines:
            if PATH_MARKER in ln:
                skip = 1            # pula o marcador e a proxima (export)
                continue
            if skip:
                skip = 0
                continue
            out.append(ln)
        rc.write_text("".join(out), encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Adapter: Claude Code (skills SKILL.md) — copia as skills prontas do repo.
# ---------------------------------------------------------------------------
_ALIAS_SKILL_TMPL = """---
name: {alias}
description: north — alias de /{name} (mesmo comando, nome em pt-BR).
allowed-tools: Bash
---

# /{alias} — alias de /{name}

Execute exatamente o mesmo que `/{name}`:

```bash
python3 ~/.north/run.py {sub}{argh}
```

Siga as mesmas regras de `/{name}`.
"""


def _alias_skill_md(ns_alias, c):
    """SKILL.md leve para um alias pt-BR (namespaced) que delega ao comando canônico."""
    argh = ' "<texto>"' if c["args"] else ""
    return _ALIAS_SKILL_TMPL.format(alias=ns_alias, name="north-" + c["name"],
                                    sub=c["sub"], argh=argh)


def adapter_claude(home: Path, tool_home: Path, pyexe: str):
    skills_dst = home / "skills"
    skills_dst.mkdir(parents=True, exist_ok=True)
    # migração: remove instalações antigas SEM namespace (focus, foco, status, btw, ...)
    for old in _legacy_bare_skill_names():
        d = skills_dst / old
        if d.is_dir():
            shutil.rmtree(d, ignore_errors=True)
    installed = []
    for skill_dir in SKILLS_SRC.glob("*"):
        if not skill_dir.is_dir():
            continue
        dst = skills_dst / skill_dir.name          # dirs já são north-*
        dst.mkdir(exist_ok=True)
        shutil.copy2(skill_dir / "SKILL.md", dst / "SKILL.md")
        installed.append(skill_dir.name)
    for c in CMDSPEC:
        for alias in c.get("aliases", []):
            ns = "north-" + alias
            adst = skills_dst / ns
            adst.mkdir(exist_ok=True)
            (adst / "SKILL.md").write_text(_alias_skill_md(ns, c), encoding="utf-8")
            installed.append(ns)
    return installed


# ---------------------------------------------------------------------------
# Adapter: Codex (prompts .md em ~/.codex/prompts) — o agente roda o motor.
# ---------------------------------------------------------------------------
_CODEX_PROMPT = """---
description: {desc}
---

Você é o north (copiloto de produtividade multi-projeto). Para responder a este
comando, RODE no shell e mostre a saída ao usuário, formatada:

```
{cmd} {sub}{argline}
```

(No Windows, troque o interpretador por `python`/`py` se necessário.)
Regras: o north só LÊ os planos — nunca edite arquivos de plano. Não acione
outras ferramentas; apenas execute e apresente o resultado.{argnote}
"""


def _skill_body(ns_name):
    """Corpo do SKILL.md (sem frontmatter) — fonte das behavior skills no Codex/Gemini."""
    f = SKILLS_SRC / ns_name / "SKILL.md"
    if not f.exists():
        return ""
    txt = f.read_text(encoding="utf-8")
    if txt.startswith("---"):
        parts = txt.split("---", 2)
        if len(parts) == 3:
            txt = parts[2]
    return txt.strip()


def adapter_codex(home: Path, tool_home: Path, pyexe: str):
    prompts = home / "prompts"
    prompts.mkdir(parents=True, exist_ok=True)
    base = engine_cmd(pyexe, tool_home)
    installed = []
    for c in CMDSPEC:
        argline = ' "$ARGUMENTS"' if c["args"] else ""
        argnote = ("\nO texto livre do usuário chega em $ARGUMENTS." if c["args"] else "")
        body = _CODEX_PROMPT.format(desc=c["desc"], cmd=base, sub=c["sub"],
                                    argline=argline, argnote=argnote)
        if c.get("behavior"):
            inner = _skill_body("north-" + c["name"])
            if c["args"]:
                inner = inner + chr(10)*2 + "---" + chr(10) + "Tópico/contexto do usuário: $ARGUMENTS"
            body = "---" + chr(10) + "description: " + c["desc"] + chr(10) + "---" + chr(10)*2 + inner + chr(10)
        for nm in [c["name"]] + c.get("aliases", []):
            (prompts / "north-{}.md".format(nm)).write_text(body, encoding="utf-8")
            installed.append("north-" + nm)
    return installed


# ---------------------------------------------------------------------------
# Adapter: Gemini CLI (comandos TOML com !{shell}) — roda o motor direto.
# ---------------------------------------------------------------------------
def _toml_escape(s: str) -> str:
    return s.replace('\\', '\\\\').replace('"', '\\"')


def adapter_gemini(home: Path, tool_home: Path, pyexe: str):
    cmds = home / "commands" / "north"
    cmds.mkdir(parents=True, exist_ok=True)
    base = engine_cmd(pyexe, tool_home)
    installed = []
    for c in CMDSPEC:
        shell = "{} {}{}".format(base, c["sub"], " {{args}}" if c["args"] else "")
        prompt = (
            "Saída do north (comando `{name}`):\n\n"
            "!{{{shell}}}\n\n"
            "Apresente essa saída ao usuário, formatada e em português. "
            "O north só lê os planos — não edite nada."
        ).format(name=c["name"], shell=shell)
        if c.get("behavior"):
            prompt = _skill_body("north-" + c["name"])
            if c["args"]:
                prompt = prompt + chr(10)*2 + "Tópico/contexto: {{args}}"
        toml = 'description = "{}"\nprompt = """\n{}\n"""\n'.format(
            _toml_escape(c["desc"]), prompt)
        for nm in [c["name"]] + c.get("aliases", []):
            (cmds / "{}.toml".format(nm)).write_text(toml, encoding="utf-8")
            installed.append("/north:" + nm)
    return installed


ADAPTERS = {"claude": adapter_claude, "codex": adapter_codex, "gemini": adapter_gemini}


# ---------------------------------------------------------------------------
# Uninstall: reverte exatamente o que os adapters/o motor criaram.
# ---------------------------------------------------------------------------
def _legacy_bare_skill_names():
    """Nomes SEM namespace (instalações pré-north-): para migração/limpeza."""
    names = set()
    for c in CMDSPEC:
        names.add(c["name"])
        names.update(c.get("aliases", []))
    names.update({"btw", "uninstall"})
    return names


def _north_skill_names():
    """Nomes de skills/diretórios do north — namespaced (atual) + bare (migração)."""
    bare = _legacy_bare_skill_names()
    names = set(bare) | {"north-" + n for n in bare}
    return names


def _strip_north_statusline(settings_path):
    """Remove a statusLine do north de settings.json (preserva o resto). True se removeu."""
    if not settings_path.exists():
        return False
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    sl = data.get("statusLine")
    cmd = (sl or {}).get("command", "") if isinstance(sl, dict) else ""
    if "run.py" in cmd and "statusline" in cmd:
        data.pop("statusLine", None)
        settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    return False


def _strip_north_hooks(settings_path):
    """Remove os hooks do north (north_hook.py) de settings.json, preservando os demais."""
    if not settings_path.exists():
        return False
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return False
    changed = False
    for event in list(hooks.keys()):
        new_entries = []
        for entry in (hooks.get(event) or []):
            inner = entry.get("hooks", []) if isinstance(entry, dict) else []
            kept = [h for h in inner if "north_hook.py" not in (h.get("command", "") or "")]
            if len(kept) != len(inner):
                changed = True
            if kept:
                entry["hooks"] = kept
                new_entries.append(entry)
            elif not inner:
                new_entries.append(entry)
        if new_entries:
            hooks[event] = new_entries
        else:
            del hooks[event]
            changed = True
    if not hooks:
        data.pop("hooks", None)
    if changed:
        settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return changed


def runtime_installed(rt_key):
    """True se houver artefatos do north para aquele runtime."""
    _, home = RUNTIMES[rt_key]
    if rt_key == "claude":
        sk = home / "skills"
        return any((sk / n).exists() for n in _north_skill_names())
    if rt_key == "codex":
        p = home / "prompts"
        return p.exists() and any(p.glob("north-*.md"))
    if rt_key == "gemini":
        return (home / "commands" / "north").exists()
    return False


def uninstall_runtime(rt_key):
    """Remove os adapters do north de um runtime. Devolve a lista do que saiu."""
    _, home = RUNTIMES[rt_key]
    removed = []
    if rt_key == "claude":
        sk = home / "skills"
        for n in _north_skill_names():
            d = sk / n
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)
                removed.append("skills/" + n)
        if _strip_north_statusline(home / "settings.json"):
            removed.append("statusLine")
        if _strip_north_hooks(home / "settings.json"):
            removed.append("hooks")
    elif rt_key == "codex":
        p = home / "prompts"
        if p.exists():
            for f in sorted(p.glob("north-*.md")):
                f.unlink()
                removed.append("prompts/" + f.name)
    elif rt_key == "gemini":
        d = home / "commands" / "north"
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
            removed.append("commands/north/")
    return removed


def uninstall_engine(tool_home, purge=False):
    """Remove o motor (~/.north). Preserva config/output/resumos salvo purge=True.
    Sempre remove o launcher de terminal e a entrada de PATH que ele criou."""
    removed = []
    if not tool_home.exists():
        return removed
    # launcher de terminal + entrada de PATH (independe de purge)
    bindir = launcher_dir(tool_home)
    if bindir.exists():
        remove_from_path(bindir)
        shutil.rmtree(bindir, ignore_errors=True)
        removed.append("bin/ (launcher + PATH)")
    if purge:
        shutil.rmtree(tool_home, ignore_errors=True)
        return [str(tool_home) + " (tudo, inclusive dados)"]
    for f in ("run.py", "north_hook.py"):
        fp = tool_home / f
        if fp.exists():
            fp.unlink()
            removed.append(f)
    for d in ("painel", "templates"):
        dp = tool_home / d
        if dp.exists():
            shutil.rmtree(dp, ignore_errors=True)
            removed.append(d + "/")
    return removed
