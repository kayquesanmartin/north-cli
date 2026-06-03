# -*- coding: utf-8 -*-
"""
config.py — carga/persistencia da configuracao da central (projects.json).

A config controla:
  - scan_roots : pastas onde procurar projetos (auto-descoberta)
  - exclude    : ids de projeto a ignorar
  - projects   : por-projeto -> enabled / alias / color / order / source
                 (source fixa a fonte primaria quando o projeto tem varias
                  estruturas de planejamento; ausente = automatica por recencia)
  - settings   : comportamento global (abrir browser, espelhar resumo, tema)

Filosofia "auto + config": a descoberta encontra os projetos sozinha; a config
apenas ajusta (liga/desliga, apelido, cor, ordem). Projeto novo aparece
automaticamente na proxima execucao, ja habilitado.
"""

import json
from pathlib import Path

# Paleta profissional (atribuida por ordem de projeto).
PALETTE = [
    "#f97316",  # orange (accent)
    "#0ea5e9",  # sky
    "#8b5cf6",  # violet
    "#14b8a6",  # teal
    "#ec4899",  # pink
    "#eab308",  # amber
    "#22c55e",  # green
    "#ef4444",  # red
]

DEFAULT_SETTINGS = {
    "open_browser": True,
    "mirror_to_project_docs": True,   # alem do resumo central, escreve copia em <proj>/docs
    "theme": "dark",                   # dark | light
    "owner_name": "Kayque",            # saudacao do bom-dia
    "title": "north",                  # nome do produto (vira o brand do painel)
    "wip_limit": 3,                    # limite de tasks "Em Andamento" antes do alerta
    "dirty_risk_files": 8,             # arquivos sujos a partir dos quais vira "risco de perda"
    "stale_branch_days": 3,            # dias sem commit a partir dos quais a branch e' "parada"
}


class Config:
    def __init__(self, path: Path, data: dict):
        self.path = path
        self.data = data

    # ---- acessores convenientes ----
    @property
    def scan_roots(self):
        return [Path(p) for p in self.data.get("scan_roots", [])]

    @property
    def exclude(self):
        return set(self.data.get("exclude", []))

    @property
    def projects(self):
        return self.data.setdefault("projects", {})

    @property
    def settings(self):
        s = dict(DEFAULT_SETTINGS)
        s.update(self.data.get("settings", {}))
        return s

    def project_cfg(self, pid: str) -> dict:
        return self.projects.get(pid, {})

    def color_for(self, pid: str, order: int) -> str:
        cfg = self.project_cfg(pid)
        if cfg.get("color"):
            return cfg["color"]
        return PALETTE[order % len(PALETTE)]

    def is_enabled(self, pid: str) -> bool:
        if pid in self.exclude:
            return False
        return self.project_cfg(pid).get("enabled", True)

    def alias_for(self, pid: str, fallback: str) -> str:
        return self.project_cfg(pid).get("alias") or fallback

    def order_for(self, pid: str, fallback: int) -> int:
        v = self.project_cfg(pid).get("order")
        return v if isinstance(v, int) else fallback

    # ---- persistencia ----
    def register_discovered(self, pid: str, order_hint: int):
        """Garante que um projeto recem-descoberto exista na config (defaults)."""
        if pid not in self.projects:
            self.projects[pid] = {
                "enabled": True,
                "alias": "",
                "color": "",
                "order": order_hint,
            }
            return True
        return False

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def load_config(path: Path, default_scan_root: Path = None) -> Config:
    """Carrega projects.json; se nao existir, cria com scan_root padrao."""
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    else:
        data = {}

    data.setdefault("scan_roots", [])
    if not data["scan_roots"] and default_scan_root:
        data["scan_roots"] = [str(default_scan_root)]
    data.setdefault("exclude", [])
    data.setdefault("projects", {})
    data.setdefault("settings", {})

    return Config(path, data)
