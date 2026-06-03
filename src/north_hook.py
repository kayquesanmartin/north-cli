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


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0
    if not should_regen(payload):
        return 0
    try:
        sys.path.insert(0, str(HOME))
        from painel.cli import main as cli_main
        # build silencioso: nao polui o contexto do Claude
        with redirect_stdout(io.StringIO()):
            cli_main(["build"], HOME)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
