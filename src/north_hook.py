# -*- coding: utf-8 -*-
"""
north_hook.py — "painel vivo". Roda como PostToolUse hook do Claude Code.

Le o payload do hook (JSON no stdin) e regenera o dashboard SILENCIOSAMENTE
apenas quando algo relevante acontece:
  - um `git commit` foi executado (Bash), OU
  - um arquivo de plano foi editado (Edit/Write em plan-build / Progress / Sprint).

Barato e seguro (apenas LE os .md e regenera o HTML — nunca edita planos nem
bloqueia o fluxo). Sempre sai com codigo 0.
"""

import io
import json
import os
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

HOME = Path(__file__).resolve().parent          # tool home (~/.claude/painel)
RELEVANT_FILE = re.compile(r"plan-build|[Pp]rogress|[Ss]print", re.I)


def should_regen(payload) -> bool:
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input", {}) or {}
    if tool == "Bash":
        cmd = ti.get("command", "") or ""
        return ("git commit" in cmd) or ("git push" in cmd) or ("gh pr create" in cmd)
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        return bool(RELEVANT_FILE.search(ti.get("file_path", "") or ""))
    return False


def handle_post(payload):
    """PostToolUse: regenera o painel silenciosamente quando algo relevante muda."""
    if not should_regen(payload):
        return 0
    try:
        sys.path.insert(0, str(HOME))
        from painel.cli import main as cli_main
        with redirect_stdout(io.StringIO()):  # nao polui o contexto do Claude
            cli_main(["build"], HOME)
    except Exception:
        pass
    return 0


def handle_pre(payload):
    """PreToolUse: antes de `git push`/`gh pr create`, avisa se a branch esta atrasada
    (evita conflito). Best-effort, NAO bloqueia (sai 0)."""
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = (payload.get("tool_input", {}) or {}).get("command", "") or ""
    if not ("git push" in cmd or "gh pr create" in cmd):
        return 0
    cwd = payload.get("cwd") or os.getcwd()
    try:
        sys.path.insert(0, str(HOME))
        from painel.discovery import _git, _git_sync
        _git(["fetch", "--quiet"], Path(cwd))  # best-effort: dados frescos
        branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], Path(cwd))
        sy = _git_sync(Path(cwd), branch)
    except Exception:
        return 0
    behind, base_behind = sy.get("behind") or 0, sy.get("base_behind") or 0
    if behind or base_behind:
        bits = []
        if behind:
            bits.append("{} commit(s) atras de {}".format(behind, sy.get("upstream") or "upstream"))
        if base_behind:
            bits.append("{} atras de {}".format(base_behind, sy.get("base") or "base"))
        print("north [!] antes de pushar: {} — rode `git pull --rebase` "
              "para evitar conflito.".format("; ".join(bits)))
    return 0


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0
    if payload.get("hook_event_name") == "PreToolUse":
        return handle_pre(payload)
    return handle_post(payload)


if __name__ == "__main__":
    raise SystemExit(main())
