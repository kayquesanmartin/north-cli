# -*- coding: utf-8 -*-
"""
parsers.py — normalizacao de formatos heterogeneos de tracking em .md.

Tres formatos comuns sao suportados:
  A) sprint+tasks por arquivo : tabela "Status Geral" (Sprint|Status|Commits|Progresso)
                        + Sprint-*.md com tabela de TASKs (TASK|Descricao|...|Status)
  B) tasks em code-block      : tabela "Visao Geral" (Sprint|Status|Inicio|Conclusao)
                        + STATUS em CODE-BLOCK: "TASK-01 | [####] | desc | OK"
  C) tasks no proprio Progress: tabela "Status Geral" (Sprint|Status|Commits|Progresso com barra)
                        + tabela de TASKs (TASK|Descricao|Especialista|Status|Sessao)

Estrategia: extrair TUDO que der (tabelas + code-blocks), classificar status por
emoji/texto, derivar progresso de fracao (N/M) > percentual (NN%) > barra (####) >
emoji. Degrada com elegancia: se um projeto so tem nivel-sprint, mostramos so isso.
"""

import re

# ----------------------------------------------------------------------------
# Colunas do kanban
# ----------------------------------------------------------------------------
COL_PLANEJADO = "Planejado"
COL_ANDAMENTO = "Em Andamento"
COL_CODIGO = "Codigo Completo"
COL_DONE = "Concluido"

COLUMN_ORDER = [COL_PLANEJADO, COL_ANDAMENTO, COL_CODIGO, COL_DONE]
COLUMN_META = {
    COL_PLANEJADO: {"emoji": "\U0001F4CB", "color": "#64748b"},   # 📋
    COL_ANDAMENTO: {"emoji": "⚡", "color": "#f97316"},        # ⚡
    COL_CODIGO:    {"emoji": "\U0001F7E2", "color": "#22c55e"},   # 🟢
    COL_DONE:      {"emoji": "✅", "color": "#16a34a"},        # ✅
}


# ----------------------------------------------------------------------------
# Tabelas markdown
# ----------------------------------------------------------------------------
def split_row(line: str):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_separator(cells):
    return all(re.fullmatch(r":?-{2,}:?", c) is not None for c in cells if c)


def extract_table(text: str, header_keys):
    """Primeira tabela cujo header contenha TODAS as strings de header_keys.
    Devolve (header, [ {coluna_lower: valor} ])."""
    lines = text.splitlines()
    keys = [k.lower() for k in header_keys]
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        header = split_row(line)
        header_low = [h.lower() for h in header]
        if all(any(k in h for h in header_low) for k in keys):
            rows = []
            j = i + 1
            if j < len(lines) and is_separator(split_row(lines[j])):
                j += 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = split_row(lines[j])
                if not is_separator(cells):
                    row = {}
                    for idx, col in enumerate(header):
                        row[col.lower()] = cells[idx] if idx < len(cells) else ""
                    rows.append(row)
                j += 1
            return header, rows
    return [], []


def extract_all_tables(text: str, header_keys):
    """Como extract_table, mas devolve TODAS as tabelas que batem (lista de rows)."""
    lines = text.splitlines()
    keys = [k.lower() for k in header_keys]
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|"):
            header = split_row(line)
            header_low = [h.lower() for h in header]
            if all(any(k in h for h in header_low) for k in keys):
                rows = []
                j = i + 1
                if j < len(lines) and is_separator(split_row(lines[j])):
                    j += 1
                while j < len(lines) and lines[j].strip().startswith("|"):
                    cells = split_row(lines[j])
                    if not is_separator(cells):
                        row = {}
                        for idx, col in enumerate(header):
                            row[col.lower()] = cells[idx] if idx < len(cells) else ""
                        rows.append(row)
                    j += 1
                out.append(rows)
                i = j
                continue
        i += 1
    return out


# ----------------------------------------------------------------------------
# Classificacao de status / progresso
# ----------------------------------------------------------------------------
_DONE_RX = re.compile(r"✅|conclu|completo|done|finaliz|entregue", re.I)
_GREEN_RX = re.compile(r"\U0001F7E2|c[oó]digo completo|verde", re.I)
_PROG_RX = re.compile(
    r"⚡|\U0001F535|\U0001F7E1|\U0001F6A7|\U0001F3D7|\U0001F528|"
    r"em andamento|em revis|em qa|wip|progress", re.I)
_BLOCK_RX = re.compile(r"⛔|bloquead|blocked|⏸", re.I)   # ⛔ / ⏸
_PLAN_RX = re.compile(r"\U0001F4CB|planejad|pendente|backlog|todo|a fazer", re.I)


def classify_status(status_text: str):
    """Devolve (coluna_kanban, blocked_flag)."""
    s = (status_text or "").strip()
    blocked = bool(_BLOCK_RX.search(s))
    if _DONE_RX.search(s) and "0%" not in s:
        return COL_DONE, blocked
    if _GREEN_RX.search(s):
        return COL_CODIGO, blocked
    if _PROG_RX.search(s):
        return COL_ANDAMENTO, blocked
    # emoji puro no inicio
    if s[:1] in ("✅",):
        return COL_DONE, blocked
    if s[:1] in ("\U0001F7E2",):
        return COL_CODIGO, blocked
    if s[:1] in ("⚡", "\U0001F535", "\U0001F7E1", "\U0001F6A7"):
        return COL_ANDAMENTO, blocked
    return COL_PLANEJADO, blocked


def parse_progress(text: str):
    """Extrai (done, total, pct) de uma celula. Prioridade:
    fracao (N/M) > barra (#### de blocos cheios/total) > percentual (NN%).
    Devolve (done|None, total|None, pct|None)."""
    if not text:
        return None, None, None
    # fracao explicita: (3/8) ou 3/8
    m = re.search(r"\(?\b(\d{1,3})\s*/\s*(\d{1,3})\b\)?", text)
    done = total = pct = None
    if m:
        done, total = int(m.group(1)), int(m.group(2))
        if total:
            pct = round(done / total * 100)
    # barra de blocos cheios
    if pct is None:
        full = text.count("█")          # █
        empty = text.count("░") + text.count("▒") + text.count("▓")
        if full or empty:
            bar_total = full + empty
            if bar_total:
                pct = round(full / bar_total * 100)
    # percentual textual
    if pct is None:
        pm = re.search(r"(\d{1,3})\s*%", text)
        if pm:
            pct = min(100, int(pm.group(1)))
    return done, total, pct


def find_commit(text: str):
    m = re.search(r"`([0-9a-f]{7,40})`", text or "")
    return m.group(1) if m else ""


def clean_desc(s: str) -> str:
    s = s or ""
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)   # links markdown
    s = s.replace("`", "").replace("**", "").replace("~~", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


# ----------------------------------------------------------------------------
# Sprint key / nome
# ----------------------------------------------------------------------------
def sprint_key(cell: str):
    """Extrai uma chave curta do sprint: 'Sprint-CC1', 'Sprint-8C', 'Sprint-1'."""
    m = re.search(r"Sprint[-\s]?([A-Za-z]*\d+[A-Za-z]?)", cell)
    if m:
        return "S" + m.group(1).upper()
    return None


def sprint_name(cell: str):
    name = re.sub(r"\s*\(.*$", "", cell)        # corta " (Sprint-CC1.md)" etc
    name = re.sub(r"\[[^\]]*\]\([^)]*\)", "", name)
    name = clean_desc(name)
    return name[:80]


# ----------------------------------------------------------------------------
# Briefing de sprint — resumo NARRATIVO (o quê / como / por quê) a partir do
# Sprint*.md. Alimenta o "resumo C-level" do painel; degrada com elegância.
# ----------------------------------------------------------------------------
def _md_section(text, name_rx):
    """Corpo de uma seção markdown cujo título (## .. ####) casa name_rx,
    até o próximo header de nível igual ou superior. '' se não achar."""
    lines = text.splitlines()
    head = re.compile(r"^(#{2,4})\s*(?:" + name_rx + r")\s*$", re.I)
    for i, ln in enumerate(lines):
        m = head.match(ln.strip())
        if not m:
            continue
        level = len(m.group(1))
        body, infence = [], False
        for j in range(i + 1, len(lines)):
            if lines[j].lstrip().startswith("```"):
                infence = not infence
                body.append(lines[j])
                continue
            hm = re.match(r"^(#{1,6})\s", lines[j])
            if hm and not infence and len(hm.group(1)) <= level:
                break          # header de verdade (fora de code-block)
            body.append(lines[j])
        return "\n".join(body).strip()
    return ""


def _first_paragraph(body):
    """Primeiro parágrafo de prosa (ignora blockquote, listas, tabelas, headers)."""
    buf = []
    for ln in body.splitlines():
        s = ln.strip()
        if not s:
            if buf:
                break
            continue
        if s[0] in "#>|" or re.match(r"^[-*+]\s|^\d+[.)]\s", s):
            if buf:
                break
            continue
        buf.append(s)
    return clean_desc(" ".join(buf))


def _labeled(body, label_rx, limit=320):
    """Valor de um '**Label:** ...' (linha + itens de lista logo abaixo)."""
    lines = body.splitlines()
    rx = re.compile(r"\*\*\s*(?:" + label_rx + r")\s*:??\s*\*\*\s*:?\s*(.*)", re.I)
    for i, ln in enumerate(lines):
        m = rx.search(ln)
        if not m:
            continue
        parts = [clean_desc(m.group(1))] if clean_desc(m.group(1)) else []
        for j in range(i + 1, len(lines)):
            s = lines[j].strip()
            lm = re.match(r"^(?:[-*+]|\d+[.)])\s+(.*)", s)
            if lm:
                parts.append(clean_desc(lm.group(1)))
            elif not s:
                continue
            else:
                break
        out = "; ".join(p for p in parts if p)
        return out[:limit]
    return ""


def _list_items(body, limit=8):
    """Itens de lista (- , * , 1. , - [ ] ) de um corpo, limpos. Lista de strings."""
    out = []
    for ln in (body or "").splitlines():
        s = ln.strip()
        m = re.match(r"^(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s+)?(.+)", s)
        if m:
            v = clean_desc(m.group(1))
            if v:
                out.append(v)
        if len(out) >= limit:
            break
    return out


def _block_after_label(text, label_rx, max_chars=420):
    """Conteúdo após '**Label:**' até a próxima linha em branco dupla, header,
    ou outro '**...:**'. Inclui itens de lista e linhas de code-block (úteis como
    critério: comandos + '# esperado'). Devolve string limpa multi-linha."""
    lines = text.splitlines()
    rx = re.compile(r"\*\*\s*(?:" + label_rx + r")\s*:?\s*\*\*", re.I)
    for i, ln in enumerate(lines):
        if not rx.search(ln):
            continue
        out, infence = [], False
        for j in range(i + 1, len(lines)):
            s = lines[j].strip()
            if s.startswith("```"):
                infence = not infence
                continue
            if not infence:
                if re.match(r"^#{1,6}\s", lines[j]):
                    break
                if re.match(r"^\*\*[^*]+\*\*\s*:?\s*$", s) and out:
                    break
                if s in ("---", "***"):
                    break
            if s.startswith("#"):           # comentário de code-block = critério legível
                s = s.lstrip("# ").strip()
            lm = re.match(r"^(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s+)?(.+)", s)
            if lm:
                s = lm.group(1)
            cv = clean_desc(s)
            if cv:
                out.append(cv)
            if sum(len(x) for x in out) > max_chars:
                break
        if out:
            return "; ".join(out)[:max_chars]
    return ""


def task_brief(text, task_id, max_chars=420):
    """Contrato de UMA task dentro do Sprint*.md: o que entregar (Builder entrega
    / Entregável) e o critério de aceite (Evaluator valida / DoD / Critério de
    aceite). Localiza a seção da task pelo id no header/negrito. {} se não achar."""
    if not text or not task_id:
        return {}
    tid = re.escape(task_id)
    lines = text.splitlines()
    start = None
    head_rx = re.compile(r"^(#{2,6})\s.*\b" + tid + r"\b", re.I)
    bold_rx = re.compile(r"^\*\*\s*" + tid + r"\b", re.I)
    level = None
    for i, ln in enumerate(lines):
        m = head_rx.match(ln)
        if m:
            start, level = i, len(m.group(1))
            break
        if bold_rx.match(ln.strip()):
            start, level = i, None
            break
    if start is None:
        return {}
    end, infence = len(lines), False
    for j in range(start + 1, len(lines)):
        if lines[j].lstrip().startswith("```"):
            infence = not infence
            continue
        if infence:
            continue          # '#' dentro de code-block não é header
        hm = re.match(r"^(#{1,6})\s", lines[j])
        if hm and (level is None or len(hm.group(1)) <= level):
            end = j
            break
        if level is None and re.match(r"^\*\*\s*(?:TASK|S[\w-]*\d)[-_ ]", lines[j].strip(), re.I):
            end = j
            break
    section = "\n".join(lines[start:end])
    entrega = _block_after_label(section, r"builder\s+entrega|entreg[aá]vel|entrega|o\s+que\s+fazer", max_chars)
    aceite = _block_after_label(
        section, r"evaluator\s+valida|crit[eé]rios?\s+de\s+aceit[ae]|defini[cç][aã]o\s+de\s+pronto|"
                 r"definition\s+of\s+done|\bDoD\b|aceite|valida[cç][aã]o", max_chars)
    out = {}
    if entrega:
        out["entrega"] = entrega
    if aceite:
        out["aceite"] = aceite
    return out


def sprint_brief(text, max_chars=360):
    """Resumo narrativo de um Sprint*.md. Devolve dict com:
      title   — subtítulo do H1 (parte após '—')
      objetivo— o QUE/COMO (Meta/Objetivo/Entregável); degrada p/ 1º parágrafo
      porque  — a justificativa ('Por que este sprint agora')
      fora    — o que NÃO entra no escopo
    Campos ausentes voltam ''. Tudo limpo de markdown e limitado em tamanho."""
    text = text or ""
    title = ""
    hm = re.search(r"^#\s+(.+)$", text, re.M)
    if hm:
        h = clean_desc(hm.group(1))
        h = re.sub(r"^Sprint[-\w.]*\s*[—\-:]\s*", "", h)   # tira "Sprint-CC4.md — "
        title = h[:90]

    meta = _md_section(text, r"meta(?:\s+do\s+sprint)?|objetivo(?:\s+do\s+sprint)?|"
                              r"resumo|escopo(?:\s+do\s+sprint)?|goal|vis[aã]o\s+geral")
    objetivo = ""
    if meta:
        objetivo = _labeled(meta, r"entreg[aá]vel|objetivo|meta|escopo") or _first_paragraph(meta)
    if not objetivo:
        # degrada: subtítulo do blockquote logo após o H1
        bm = re.search(r"^>\s*(?:objetivo\s*:?\s*)?(.+)$", text, re.M | re.I)
        if bm:
            objetivo = clean_desc(bm.group(1))
    objetivo = objetivo[:max_chars]

    porque = ""
    pm = re.search(r"\*\*\s*por\s*qu[eê][^*:]*:?\s*\*\*\s*:?\s*(.+)", text, re.I)
    if pm:
        porque = clean_desc(pm.group(1))[:max_chars]

    fora = _labeled(
        _md_section(text, r"(?:o\s+que\s+)?n[aã]o\s+(?:entra|est[aá]).*") or text,
        r"(?:o\s+que\s+)?n[aã]o\s+(?:entra|est[aá])[^*]*", limit=240)

    # critérios de aceite / DoD no nível da sprint (seção dedicada ou label)
    dod_sec = _md_section(text, r"crit[eé]rios?\s+de\s+aceit[ae]|defini[cç][aã]o\s+de\s+pronto|"
                                r"definition\s+of\s+done|\bDoD\b|princ[ií]pios?\s+obrigat[oó]rios?")
    aceite = ""
    if dod_sec:
        aceite = "; ".join(_list_items(dod_sec, limit=8)) or _first_paragraph(dod_sec)
    if not aceite:
        aceite = _block_after_label(
            text, r"\bDoD\b|defini[cç][aã]o\s+de\s+pronto|crit[eé]rios?\s+de\s+aceit[ae]|"
                  r"princ[ií]pios?\s+obrigat[oó]rios?[^*]*", max_chars=420)
    aceite = aceite[:420]

    # pré-leitura / docs de referência citados pela sprint
    prereq = ""
    qm = re.search(r"(?:\*\*\s*)?(?:pr[eé]-?leitura|pre-?reqs?|refer[eê]ncias?|"
                   r"pr[eé]-?condi[cç][oõ]es?)[^:\n]*:?\s*\*?\*?\s*(.+)", text, re.I)
    if qm:
        prereq = clean_desc(qm.group(1))[:300]

    return {"title": title, "objetivo": objetivo, "porque": porque,
            "fora": fora, "aceite": aceite, "prereq": prereq}


# ----------------------------------------------------------------------------
# TASK id heuristico
# ----------------------------------------------------------------------------
# Aceita: TASK-01 | S_CC4-2 | S3B-1 | S4A-9 | T7T-6 | S8P-4 | DT-CC-10 ...
# (id = prefixo curto alfanumerico + '-' + numero, opcionalmente sufixado por letra)
_TASKID_RX = re.compile(r"^(TASK[-_]?\d+|[A-Za-z][A-Za-z0-9_]{0,9}[-_]\d+[A-Za-z]?)$")
# prefixos que parecem id mas NAO sao TASK (evita falsos positivos no fallback)
_NOT_TASK = re.compile(r"^(ADR|DT|RFC|PR|ISSUE|SESS|SESSAO|SPRINT)[-_]", re.I)


def looks_like_taskid(cell: str) -> bool:
    c = clean_desc(cell)
    if not c or len(c) > 20:
        return False
    if _NOT_TASK.match(c):
        return False
    return bool(_TASKID_RX.match(c))


def derive_sprint(tid: str) -> str:
    """Deriva a chave do sprint a partir do id da task: 'S3B-1'->'S3B',
    'S_CC4-2'->'SCC4', 'TASK-01'->''. Normaliza para casar com sprint_key()."""
    m = re.match(r"^(.*?)[-_]\d+[A-Za-z]?$", tid)
    if not m:
        return ""
    stem = m.group(1)
    if stem.upper().startswith("TASK"):
        return ""
    norm = re.sub(r"[^A-Za-z0-9]", "", stem).upper()
    return norm


# ----------------------------------------------------------------------------
# Extracao de TASKs (tabelas + code-blocks)
# ----------------------------------------------------------------------------
def tasks_from_tables(text: str, sprint_default=""):
    """TASKs vindas de tabelas markdown com header task/tarefa + status."""
    out = []
    for header_keys in (["task", "status"], ["tarefa", "status"]):
        for rows in extract_all_tables(text, header_keys):
            for r in rows:
                # acha a coluna do id
                tid = ""
                for key in ("task", "tarefa", "id", "#"):
                    if key in r and looks_like_taskid(r[key]):
                        tid = clean_desc(r[key])
                        break
                if not tid:
                    # primeira celula que pareca id
                    for v in r.values():
                        if looks_like_taskid(v):
                            tid = clean_desc(v)
                            break
                if not tid:
                    continue
                status_raw = r.get("status", "")
                col, blocked = classify_status(status_raw)
                _, _, pct = parse_progress(status_raw + " " + r.get("progresso", ""))
                sprint = sprint_default or derive_sprint(tid)
                out.append({
                    "id": tid,
                    "sprint": sprint,
                    "desc": clean_desc(r.get("descrição", r.get("descricao",
                            r.get("descrição da task", "")))),
                    "owner": clean_desc(r.get("especialista", r.get("responsável",
                            r.get("responsavel", r.get("owner", ""))))),
                    "deps": clean_desc(r.get("dependências", r.get("dependencias", ""))),
                    "status_raw": clean_desc(status_raw),
                    "col": col,
                    "blocked": blocked,
                    "commit": find_commit(status_raw),
                    "pct": pct,
                })
    return out


_CODEBLOCK_RX = re.compile(r"```.*?```", re.S)
_CB_LINE_RX = re.compile(
    r"^\s*([A-Za-z][\w-]*\d[\w-]*)\s*\|\s*(\[[^\]]*\])?\s*\|?\s*(.*)$")


def tasks_from_codeblocks(text: str, sprint_default=""):
    """TASKs vindas de pseudo-tabelas em code-block:
       'TASK-01 | [######] | desc | CONCLUIDA'  (formato B: tasks em code-block)."""
    out = []
    for block in _CODEBLOCK_RX.findall(text):
        for line in block.splitlines():
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2:
                continue
            tid = clean_desc(parts[0].lstrip("`").strip("# "))
            if not looks_like_taskid(tid):
                continue
            bar = ""
            desc = ""
            status = parts[-1]
            for p in parts[1:]:
                if "█" in p or "░" in p or "[" in p:
                    bar = p
                elif p and p is not parts[-1]:
                    desc = desc or p
            _, _, pct = parse_progress(bar + " " + status)
            col, blocked = classify_status(status)
            out.append({
                "id": tid,
                "sprint": sprint_default,
                "desc": clean_desc(desc),
                "owner": "",
                "deps": "",
                "status_raw": clean_desc(status),
                "col": col,
                "blocked": blocked,
                "commit": "",
                "pct": pct,
            })
    return out
