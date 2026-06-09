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
    "owner_name": "dev",               # saudacao do bom-dia (install detecta o nome do git)
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

    @property
    def focused_project(self):
        """Projeto unico em foco no dia (None = portfolio completo)."""
        return (self.data.get("settings", {}) or {}).get("focused_project") or None

    def set_focused_project(self, pid):
        """Fixa (ou limpa, com pid falsy) o projeto em foco e persiste."""
        st = self.data.setdefault("settings", {})
        if pid:
            st["focused_project"] = pid
        else:
            st.pop("focused_project", None)
        self.save()

    def is_enabled(self, pid: str) -> bool:
        if pid in self.exclude:
            return False
        return self.project_cfg(pid).get("enabled", True)

    # ---- enrollment opt-in (north init) ----
    @property
    def discovery_mode(self):
        """'enrolled' = rastreia SÓ os projetos plugados (`north init`); 'scan' =
        auto-descoberta legada nos scan_roots. Inferido p/ retrocompatibilidade:
        explícito em settings vence; senão enrolled se há lista de enrolled, scan
        se há scan_roots (quem já usava não quebra), enrolled numa casa limpa."""
        m = (self.data.get("settings", {}) or {}).get("discovery_mode")
        if m in ("enrolled", "scan"):
            return m
        if self.data.get("enrolled"):
            return "enrolled"
        if self.data.get("scan_roots"):
            return "scan"
        return "enrolled"

    @property
    def enrolled(self):
        return [Path(p) for p in self.data.get("enrolled", [])]

    def discovery_roots(self):
        """Raízes a varrer: os projetos plugados (enrolled) ou os scan_roots (legado)."""
        return self.enrolled if self.discovery_mode == "enrolled" else self.scan_roots

    def add_enrolled(self, path: Path) -> bool:
        """Pluga um projeto (registra o caminho absoluto em ~/.north) e ativa o
        modo enrolled. Idempotente; devolve False se já estava plugado."""
        ap = str(Path(path).expanduser().resolve())
        lst = self.data.setdefault("enrolled", [])
        existing = {str(Path(p).expanduser().resolve()) for p in lst}
        self.data.setdefault("settings", {})["discovery_mode"] = "enrolled"
        added = ap not in existing
        if added:
            lst.append(ap)
        self.save()
        return added

    def remove_enrolled(self, path_or_id: str) -> bool:
        """Des-pluga por caminho absoluto OU por nome do projeto (basename)."""
        lst = self.data.get("enrolled", [])
        target = str(Path(path_or_id).expanduser().resolve())
        kept, removed = [], False
        for p in lst:
            rp = str(Path(p).expanduser().resolve())
            if rp == target or Path(rp).name == path_or_id:
                removed = True
                continue
            kept.append(p)
        if removed:
            self.data["enrolled"] = kept
            self.save()
        return removed

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
    data.setdefault("enrolled", [])
    data.setdefault("exclude", [])
    data.setdefault("projects", {})
    data.setdefault("settings", {})

    return Config(path, data)
