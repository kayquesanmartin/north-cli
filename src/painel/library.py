# -*- coding: utf-8 -*-
"""
library.py — biblioteca de referências de engenharia consultável pelo north.

"Ship the librarian, not the library": o MECANISMO vive no repo; o CONTEÚDO do
usuário fica só na instalação LOCAL (`~/.north/library/`) — material pessoal,
fora do pacote distribuído (respeita copyright). As skills consultam via
`north library find <tópico>` para ancorar mentoria/insights/docs em princípios.

Stdlib-only: índice JSON + busca por palavra-chave (sem embeddings/ML).
"""

import json
import re
import shutil
from pathlib import Path

TEXT_EXT = {".md", ".markdown", ".txt", ".rst", ".adoc"}
OTHER_EXT = {".pdf", ".html", ".htm"}          # indexados como ponteiro (abrir manual)
_STOP = set("a o e de da do das dos para por com sem the of and to in on for is are "
            "as os um uma no na que se ao à é".split())


def _lib_dir(home: Path) -> Path:
    d = home / "library"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _roots(home: Path):
    """Raízes da biblioteca, em ordem de prioridade (dedup: 1ª vence):
      - 'bundled': referências que VÊM no pacote (references/compendium/)
      - 'user'   : material que o usuário adiciona (library add)"""
    return [("bundled", home / "references" / "compendium"),
            ("user", _lib_dir(home))]


def _root_dir(home: Path, scope: str) -> Path:
    return dict(_roots(home)).get(scope, _lib_dir(home))


def _resolve(home: Path, entry) -> Path:
    return _root_dir(home, entry.get("scope", "user")) / entry["file"]


def _index_path(home: Path) -> Path:
    return _lib_dir(home) / "index.json"


def _tokens(text):
    return [w for w in re.findall(r"[a-zà-ú0-9][a-zà-ú0-9+_-]{1,}", (text or "").lower())
            if w not in _STOP and len(w) > 1]


def add(home: Path, src):
    """Ingere um arquivo ou pasta de referências na biblioteca local. Devolve
    (copiados, ignorados). Preserva a estrutura relativa de subpastas."""
    src = Path(src).expanduser()
    lib = _lib_dir(home)
    copied, skipped = 0, 0
    if not src.exists():
        return 0, 0, "origem não existe: {}".format(src)
    files = [src] if src.is_file() else [p for p in src.rglob("*")
                                         if p.is_file() and ".git" not in p.parts]
    base = src.parent if src.is_file() else src
    for f in files:
        ext = f.suffix.lower()
        if ext not in TEXT_EXT and ext not in OTHER_EXT:
            skipped += 1
            continue
        try:
            rel = f.relative_to(base)
        except ValueError:
            rel = Path(f.name)
        dst = lib / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        copied += 1
    build_index(home)
    return copied, skipped, None


def build_index(home: Path):
    """(Re)constrói o índice da biblioteca a partir de TODAS as raízes (bundlado +
    usuário). Dedup por nome de arquivo (a 1ª raiz — bundlado — vence)."""
    entries, seen = [], set()
    for scope, root in _roots(home):
        if not root.exists():
            continue
        for f in sorted(root.rglob("*")):
            if not f.is_file() or f.name == "index.json":
                continue
            ext = f.suffix.lower()
            if ext not in TEXT_EXT and ext not in OTHER_EXT:
                continue
            dedup_key = f.name.lower()
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            rel = f.relative_to(root).as_posix()
            if ext in OTHER_EXT:
                entries.append({"scope": scope, "file": rel, "title": f.stem.replace("-", " "),
                                "kind": ext.lstrip("."), "headers": [], "keywords": [],
                                "pointer": True})
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            hm = re.search(r"^#\s+(.+)$", text, re.M)
            title = (hm.group(1).strip() if hm else f.stem.replace("-", " "))
            headers = re.findall(r"^#{2,3}\s+(.+)$", text, re.M)
            kw = {}
            for w in _tokens(title + " " + " ".join(headers)):
                kw[w] = kw.get(w, 0) + 3        # título/headers pesam mais
            for w in _tokens(text):
                kw[w] = kw.get(w, 0) + 1
            top = sorted(kw, key=lambda w: -kw[w])[:40]
            entries.append({"scope": scope, "file": rel, "title": title, "kind": "doc",
                            "headers": [h.strip() for h in headers][:20],
                            "keywords": top, "pointer": False})
    idx = {"count": len(entries), "entries": entries}
    _index_path(home).write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
    return idx


def load_index(home: Path):
    p = _index_path(home)
    if not p.exists():
        return {"count": 0, "entries": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"count": 0, "entries": []}


def find(home: Path, query, limit=4):
    """Busca por palavra-chave; devolve os arquivos mais relevantes + seções que casam."""
    idx = load_index(home)
    qtok = set(_tokens(query))
    if not qtok:
        return []
    scored = []
    for e in idx["entries"]:
        kw = set(e.get("keywords", []))
        title_tok = set(_tokens(e.get("title", "")))
        header_tok = set(_tokens(" ".join(e.get("headers", []))))
        score = (len(qtok & title_tok) * 5 + len(qtok & header_tok) * 3
                 + len(qtok & kw) * 1)
        if e.get("pointer"):
            score += len(qtok & title_tok) * 2     # PDFs: só pelo nome
        if score <= 0:
            continue
        hits = [h for h in e.get("headers", []) if qtok & set(_tokens(h))][:4]
        scored.append((score, e, hits))
    scored.sort(key=lambda x: -x[0])
    return [{"file": e["file"], "scope": e.get("scope", "user"), "title": e["title"],
             "kind": e.get("kind"), "pointer": e.get("pointer", False),
             "path": str(_resolve(home, e)), "sections": hits, "score": s}
            for s, e, hits in scored[:limit]]


def cmd_library(home: Path, args):
    """CLI: library [list] | add <path> | find <query...> | where"""
    sub = (args[0] if args else "list").lower()
    lib = _lib_dir(home)
    if sub == "add":
        if len(args) < 2:
            print("uso: library add <arquivo-ou-pasta>")
            return 1
        copied, skipped, err = add(home, " ".join(args[1:]).strip().strip('"'))
        if err:
            print("erro: {}".format(err))
            return 1
        print("biblioteca: +{} arquivo(s) ({} ignorado(s)). Índice reconstruído.".format(
            copied, skipped))
        print("local: {}".format(lib))
        return 0
    if sub in ("reindex", "rebuild"):
        idx = build_index(home)
        print("índice reconstruído: {} item(ns).".format(idx["count"]))
        return 0
    if sub == "where":
        print(lib)
        return 0
    if sub in ("find", "search", "q"):
        res = find(home, " ".join(args[1:]))
        if not res:
            print("nada na biblioteca para isso. (popule com: north library add <pasta>)")
            return 0
        print("REFERÊNCIAS RELEVANTES (consulte antes de orientar/ensinar):")
        for r in res:
            tag = " [PDF — abrir]" if r["pointer"] else (" [bundlado]" if r["scope"] == "bundled" else "")
            print("  • {}{}".format(r["title"], tag))
            print("    {}".format(r["path"]))
            if r["sections"]:
                print("    seções: {}".format(" · ".join(r["sections"])))
        return 0
    # list (default)
    idx = load_index(home)
    if not idx["count"]:
        print("biblioteca vazia. Popule com:  north library add \"<pasta de referências>\"")
        print("local: {}".format(lib))
        return 0
    nb = sum(1 for e in idx["entries"] if e.get("scope") == "bundled")
    print("📚 Biblioteca de referências ({} itens · {} bundlado(s) + {} seu(s))".format(
        idx["count"], nb, idx["count"] - nb))
    for e in idx["entries"]:
        tag = " [PDF]" if e.get("pointer") else (" [bundlado]" if e.get("scope") == "bundled" else "")
        print("  • {}{}".format(e["title"], tag))
    print("\nbusque:  north library find \"<tópico>\"   ·   adicione:  north library add \"<pasta>\"")
    return 0
