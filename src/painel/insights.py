# -*- coding: utf-8 -*-
"""
insights.py — memória + agendador dos "insights passivos" (teach-on-write).

O north NÃO detecta conceitos (stdlib, sem parse semântico) — quem identifica e
ranqueia os conceitos usados é a IA do runtime, que escreveu o código. Este motor
é a MEMÓRIA e o AGENDADOR:
  - guarda o que já foi ensinado num ledger .md por linguagem (read-only sobre o
    código do usuário; escreve só em ~/.north/learnings/taught/<lang>.md);
  - decide o que está "devido" (conceito novo, ou cooldown vencido) e RANQUEIA por
    dificuldade, para a IA ensinar só o mais difícil/importante e nunca repetir.

Catálogo de conceitos (dificuldade/categoria) em references/concepts/<lang>.md.
"""

import re
from datetime import datetime, date
from pathlib import Path

from . import parsers as P

DIFF_RANK = {"jr": 1, "junior": 1, "júnior": 1, "pl": 2, "pleno": 2,
             "sr": 3, "senior": 3, "sênior": 3}
DIFF_LABEL = {1: "jr", 2: "pl", 3: "sr"}
DEFAULT_COOLDOWN = 7


def _rank(diff):
    return DIFF_RANK.get((diff or "").strip().lower(), 2)


def _learn_dir(home: Path) -> Path:
    d = home / "learnings" / "taught"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ledger_path(home: Path, lang: str) -> Path:
    safe = re.sub(r"[^a-z0-9_+-]", "", (lang or "geral").lower()) or "geral"
    return _learn_dir(home) / (safe + ".md")


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _days_since(iso: str):
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        return (date.today() - date(y, m, d)).days
    except Exception:
        return None


# ----------------------------------------------------------------------------
# Catálogo de conceitos (referências bundladas) — conceito/alias -> meta
# ----------------------------------------------------------------------------
def _catalog_paths(home: Path, lang: str):
    safe = re.sub(r"[^a-z0-9_+-]", "", (lang or "").lower())
    rel = Path("references") / "concepts" / (safe + ".md")
    # 1) instalado em ~/.north/references  2) repo (rodando do source)
    return [home / rel, Path(__file__).resolve().parent.parent.parent / rel]


def load_catalog(home: Path, lang: str):
    """alias_lower -> {concept, category, difficulty}. {} se não houver catálogo."""
    text = ""
    for p in _catalog_paths(home, lang):
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8")
                break
            except Exception:
                pass
    out = {}
    if not text:
        return out
    _, rows = P.extract_table(text, ["conceito", "dificuldade"])
    for r in rows:
        concept = P.clean_desc(r.get("conceito", ""))
        if not concept:
            continue
        meta = {
            "concept": concept,
            "category": P.clean_desc(r.get("categoria", "")) or "geral",
            "difficulty": P.clean_desc(r.get("dificuldade", "")).lower() or "pl",
        }
        names = [concept] + [a.strip() for a in re.split(r"[;,]", r.get("aliases", "")) if a.strip()]
        for n in names:
            out[P.clean_desc(n).lower()] = meta
    return out


# ----------------------------------------------------------------------------
# Ledger (tabela markdown) — leitura/escrita
# ----------------------------------------------------------------------------
_LEDGER_HEADER = ("| Conceito | Categoria | Dificuldade | Usado | Ensinado | Último ensino |\n"
                  "|---|---|---|---|---|---|")


def load_ledger(home: Path, lang: str):
    """concept_lower -> {concept, category, difficulty, used, taught, last_taught}."""
    path = _ledger_path(home, lang)
    out = {}
    if not path.exists():
        return out
    _, rows = P.extract_table(path.read_text(encoding="utf-8"), ["conceito", "usado"])
    for r in rows:
        c = P.clean_desc(r.get("conceito", ""))
        if not c:
            continue
        def _int(v):
            m = re.search(r"\d+", v or "")
            return int(m.group()) if m else 0
        out[c.lower()] = {
            "concept": c,
            "category": P.clean_desc(r.get("categoria", "")) or "geral",
            "difficulty": P.clean_desc(r.get("dificuldade", "")).lower() or "pl",
            "used": _int(r.get("usado", "")),
            "taught": _int(r.get("ensinado", "")),
            "last_taught": P.clean_desc(r.get("último ensino", r.get("ultimo ensino", ""))),
        }
    return out


def save_ledger(home: Path, lang: str, ledger: dict):
    rows = sorted(ledger.values(),
                  key=lambda e: (-_rank(e["difficulty"]), e["concept"].lower()))
    lines = ["# Conceitos ensinados — {}".format(lang), "",
             "> Gerado pelo north (insights passivos). Não edite à mão durante a sessão.",
             "", _LEDGER_HEADER]
    for e in rows:
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            e["concept"], e.get("category", "geral"), e.get("difficulty", "pl"),
            e.get("used", 0), e.get("taught", 0), e.get("last_taught", "") or "—"))
    _ledger_path(home, lang).write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------
# Operações
# ----------------------------------------------------------------------------
def check(home, lang, concepts, cooldown_days=DEFAULT_COOLDOWN, min_level="jr"):
    """Registra USO dos conceitos e devolve os DEVIDOS p/ ensinar, ranqueados.
    devido = nunca ensinado OU (cooldown vencido). concepts: lista de nomes."""
    catalog = load_catalog(home, lang)
    ledger = load_ledger(home, lang)
    min_rank = _rank(min_level)
    seen, due = [], []
    for raw in concepts:
        name = P.clean_desc(raw)
        if not name:
            continue
        key = name.lower()
        cat = catalog.get(key)
        entry = ledger.get(key)
        if entry is None:
            entry = {"concept": (cat["concept"] if cat else name),
                     "category": (cat["category"] if cat else "geral"),
                     "difficulty": (cat["difficulty"] if cat else "pl"),
                     "used": 0, "taught": 0, "last_taught": ""}
            ledger[entry["concept"].lower()] = entry
        elif cat:                      # refina meta a partir do catálogo
            entry["category"] = entry.get("category") or cat["category"]
            entry["difficulty"] = cat["difficulty"]
        entry["used"] = entry.get("used", 0) + 1
        ds = _days_since(entry.get("last_taught", "")) if entry.get("last_taught") else None
        is_new = entry.get("taught", 0) == 0
        is_stale = ds is not None and ds >= cooldown_days
        if _rank(entry["difficulty"]) >= min_rank and (is_new or is_stale):
            due.append({"concept": entry["concept"], "category": entry["category"],
                        "difficulty": entry["difficulty"],
                        "reason": "novo" if is_new else "cooldown vencido ({}d)".format(ds)})
        seen.append(entry["concept"])
    save_ledger(home, lang, ledger)
    due.sort(key=lambda e: (-_rank(e["difficulty"]), e["concept"].lower()))
    return {"due": due, "seen": seen}


def record(home, lang, concept):
    ledger = load_ledger(home, lang)
    key = P.clean_desc(concept).lower()
    e = ledger.get(key)
    if e is None:
        e = {"concept": P.clean_desc(concept), "category": "geral",
             "difficulty": "pl", "used": 1, "taught": 0, "last_taught": ""}
        ledger[key] = e
    e["taught"] = e.get("taught", 0) + 1
    e["last_taught"] = _today()
    save_ledger(home, lang, ledger)
    return e


def cmd_insight(home: Path, args):
    """CLI: insight check <lang> "<csv>" [--cooldown N] [--min jr|pl|sr]
            insight record <lang> <conceito>
            insight log <lang>"""
    sub = (args[0] if args else "").lower()
    if sub == "check":
        lang = args[1] if len(args) > 1 else "geral"
        csv = args[2] if len(args) > 2 else ""
        cooldown = DEFAULT_COOLDOWN
        min_level = "jr"
        if "--cooldown" in args:
            try:
                cooldown = int(args[args.index("--cooldown") + 1])
            except (ValueError, IndexError):
                pass
        if "--min" in args:
            try:
                min_level = args[args.index("--min") + 1]
            except IndexError:
                pass
        concepts = [c for c in re.split(r"[;,]", csv) if c.strip()]
        res = check(home, lang, concepts, cooldown, min_level)
        if not res["due"]:
            print("nada a ensinar agora ({} conceito(s) já cobertos no cooldown).".format(
                len(res["seen"])))
            return 0
        print("ENSINAR (ranqueado por dificuldade — pegue o 1º):")
        for d in res["due"]:
            print("  [{}] {} · {} — {}".format(
                d["difficulty"], d["concept"], d["category"], d["reason"]))
        print("\napós ensinar, registre: north insight record {} \"<conceito>\"".format(lang))
        return 0
    if sub == "record":
        if len(args) < 3:
            print("uso: insight record <lang> <conceito>")
            return 1
        e = record(home, args[1], " ".join(args[2:]))
        print("registrado: {} (ensinado {}x, último {}).".format(
            e["concept"], e["taught"], e["last_taught"]))
        return 0
    if sub == "log":
        lang = args[1] if len(args) > 1 else "geral"
        path = _ledger_path(home, lang)
        if not path.exists():
            print("sem ledger para '{}' ainda.".format(lang))
            return 0
        print(path.read_text(encoding="utf-8"))
        return 0
    print("uso: insight check|record|log <lang> ...")
    return 1
