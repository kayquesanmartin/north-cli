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
    {"name": "foco", "sub": "foco", "args": False,
     "desc": "north — a próxima ação de maior valor entre todos os projetos + squad sugerido."},
    {"name": "bom-dia", "sub": "bom-dia", "args": False,
     "desc": "north — ritual de início do dia: foco consolidado + abre o painel."},
    {"name": "fim-do-dia", "sub": "fim-do-dia", "args": False,
     "desc": "north — ritual de fim do dia: resumo por projeto."},
    {"name": "painel", "sub": "build", "args": False,
     "desc": "north — regenera a Central de Produtividade (dashboard multi-projeto)."},
    {"name": "btw", "sub": "btw", "args": True,
     "desc": "north — captura rápida de uma ideia na inbox, sem quebrar o fluxo."},
    {"name": "inbox", "sub": "inbox", "args": False,
     "desc": "north — tria as ideias capturadas com /btw."},
    {"name": "status", "sub": "status", "args": False,
     "desc": "north — o que está instalado, scan_roots e projetos rastreados."},
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
        (prompts / "north-{}.md".format(c["name"])).write_text(body, encoding="utf-8")
        installed.append("north-" + c["name"])
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
        (cmds / "{}.toml".format(c["name"])).write_text(toml, encoding="utf-8")
        installed.append("/north:" + c["name"])
    return installed


ADAPTERS = {"claude": adapter_claude, "codex": adapter_codex, "gemini": adapter_gemini}
