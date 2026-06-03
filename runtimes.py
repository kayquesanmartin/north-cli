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
import shutil
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
    {"name": "config", "sub": "config", "args": True, "aliases": [],
     "desc": "north — ajusta a configuração (scan_roots, settings, projetos) sem reinstalar."},
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


def _alias_skill_md(alias, c):
    """SKILL.md leve para um alias pt-BR que delega ao comando canônico."""
    argh = ' "<texto>"' if c["args"] else ""
    return _ALIAS_SKILL_TMPL.format(alias=alias, name=c["name"], sub=c["sub"], argh=argh)


def adapter_claude(home: Path, tool_home: Path, pyexe: str):
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
    for c in CMDSPEC:
        for alias in c.get("aliases", []):
            adst = skills_dst / alias
            adst.mkdir(exist_ok=True)
            (adst / "SKILL.md").write_text(_alias_skill_md(alias, c), encoding="utf-8")
            installed.append(alias)
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
def _north_skill_names():
    """Nomes de skills/diretórios que pertencem ao north (canônicos + aliases + legados)."""
    names = set()
    for c in CMDSPEC:
        names.add(c["name"])
        names.update(c.get("aliases", []))
    names.update({"btw", "uninstall"})  # legado (pré-rename) + a própria skill de uninstall
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
    """Remove o motor (~/.north). Preserva config/output/resumos salvo purge=True."""
    removed = []
    if not tool_home.exists():
        return removed
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
