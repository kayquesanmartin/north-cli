# -*- coding: utf-8 -*-
"""
fsutil.py — varredura de filesystem compartilhada pela descoberta de projetos.

Centraliza a busca PODADA por diretorios de planejamento. Poda dirs que nunca
contem projetos reais (VCS, dependencias, caches) e — o ponto critico — os
worktrees do Claude Code em `.claude/worktrees/<branch>/...`. Cada worktree e um
CHECKOUT do mesmo repo, com o mesmo plan-build/.planning dentro; sem podar,
cada um virava um "projeto" distinto no painel, renderizando sprints/tasks
identicos (projetos-fantasma). Podar `.claude` resolve isso na raiz.

Bonus: podar `node_modules`/caches deixa a varredura muito mais rapida.
"""

import os
from pathlib import Path

# Diretorios podados (case-insensitive). `.claude` cobre os worktrees do
# Claude Code (.claude/worktrees/...), que sao espelhos do mesmo repo.
IGNORE_DIRS = {
    ".git", ".hg", ".svn", ".claude",
    "node_modules", "bower_components",
    ".venv", "venv", "__pycache__", ".tox", ".mypy_cache", ".pytest_cache",
    ".idea", ".vscode", ".cache", "archive",
}


def find_dirs_named(scan_roots, name, max_depth=6):
    """Acha todas as pastas chamadas `name` sob os scan_roots, podando os dirs
    de IGNORE_DIRS e respeitando a profundidade maxima (parts relativas ao root).

    Devolve uma lista de Paths SEM dedup — o caller aplica a chave de dedup que
    fizer sentido (ex.: resolve().lower()). O case do nome no disco e preservado
    (importa em SOs case-sensitive)."""
    found = []
    target = name.lower()
    for root in scan_roots:
        root = Path(root)
        if not root.exists():
            continue
        for dirpath, dirnames, _files in os.walk(root):
            rel = Path(dirpath).relative_to(root)
            depth = 0 if str(rel) == "." else len(rel.parts)
            # registra os matches deste nivel (antes de podar dirnames)
            if depth + 1 <= max_depth:
                for d in dirnames:
                    if d.lower() == target:
                        found.append(Path(dirpath) / d)
            # poda in-place: nao desce em ignorados nem alem da profundidade
            dirnames[:] = [d for d in dirnames
                           if d.lower() not in IGNORE_DIRS and depth + 1 <= max_depth]
    return found
