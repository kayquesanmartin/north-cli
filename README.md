<div align="center">

# 🧭 north

**Seu copiloto de produtividade multi-projeto para o [Claude Code](https://claude.com/claude-code).**

north descobre sozinho todos os seus projetos, lê o progresso que você já
escreve em markdown e transforma isso em **direção** — o que fazer agora,
sinais vitais de risco antes de você travar, e rituais de início e fim de dia.
Tudo local. Zero nuvem. Ele nunca edita seus planos.

[![License: MIT](https://img.shields.io/badge/License-MIT-f97316.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-3776ab.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%C2%B7%20macOS%20%C2%B7%20Linux-0ea5e9.svg)]()
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skills-8b5cf6.svg)](https://claude.com/claude-code)
[![No cloud](https://img.shields.io/badge/cloud-none-22c55e.svg)]()

</div>

---

## Por que north?

Ferramentas de planejamento te dão uma **fotografia** — onde cada projeto está.
north te dá **sinais vitais e direção**:

- 🧭 **`/foco`** responde a única pergunta que importa de manhã: *o que eu faço agora?* — a próxima ação de maior valor entre **todos** os projetos, respeitando seu limite de WIP.
- 📍 **Statusline ambiente**: sua próxima ação + alertas direto na barra de status do Claude Code, **a cada prompt** — north presente sem você precisar pedir.
- 🩺 **Sinais vitais** te avisam *antes* de travar: trabalho não commitado virando risco, branch parada, bloqueio no caminho crítico, WIP acima do limite.
- 🔍 **Auto-descoberta**: aponte para uma pasta e ele acha todo projeto com tracking. Projeto novo aparece sozinho no painel.
- 🔗 **Interopera com o [GSD](https://github.com/glamp/get-shit-done)**: lê o `.planning/` (STATE/ROADMAP/HANDOFF) e mostra seus projetos GSD — fases, progresso, bloqueios, próxima ação — no mesmo painel, ao lado dos `plan-build`. north é a camada de largura *sobre* o GSD, não um concorrente.
- 📥 **Captura sem fricção** (`/btw`): salva uma ideia no meio de qualquer tarefa sem perder o foco — e te lembra dela no fim do dia.
- 📊 **Painel profissional** em HTML puro (sem build, sem dependência) — portfólio, kanban, sprints, bloqueios, débito técnico e autoria via git.
- 🔒 **Fonte única de verdade**: north **só lê** seus `.md`. Nunca escreve neles.

> north não substitui seu sistema de planejamento — ele o **lê** e te dá o que
> falta: foco, ritmo e alerta precoce.

---

## Instalação

Requisitos: **Python 3.8+** e o **[Claude Code](https://claude.com/claude-code)**. `git` opcional (habilita autoria e sinais vitais de git). Funciona em **Windows, macOS e Linux**.

**Via npx** (recomendado — não precisa clonar):

```bash
npx north-cli            # baixa e instala (bootstrap)
# ou, global:
npm install -g north-cli && north install
```

O pacote npm é só um **lançador cross-plataforma**: detecta o Python
(`python3`/`python`/`py`) e roda o `install.py` embutido — north continua sendo
um app Python, sem nuvem e sem reescrever nada em Node.

**Via clone** (para desenvolver o north):

```bash
git clone https://github.com/kayquesanmartin/north-cli.git
cd north-cli
python install.py
```

O instalador (idempotente):

1. Copia o motor para a *tool home* `~/.claude/painel/`.
2. Instala as skills globais em `~/.claude/skills/`.
3. Detecta seus projetos sob a raiz do workspace e **abre um menu** para você escolher quais acompanhar (templates são detectados e ignorados).
4. Gera o primeiro painel.

| Flag | Efeito |
|---|---|
| `--all` | Acompanha todos os projetos achados, sem menu |
| `--scan-root "<caminho>"` | Adiciona uma raiz extra de busca |
| `--skip-plugins` | Não mexe nos plugins do `settings.json` |
| `--no-build` | Não gera o painel ao final |
| `--install-gh` | Tenta instalar o `gh` CLI via winget (Windows) |

---

## Uso

### No Claude Code (de qualquer projeto)

| Skill | O que faz |
|---|---|
| `/bom-dia` | Regenera o painel, mostra o **foco do dia** consolidado e abre no navegador |
| `/foco` | A próxima ação de maior valor agora (sprint atual › caminho crítico › desbloqueada) + squad sugerido |
| `/btw <ideia>` | Captura rápida — salva na inbox sem quebrar o que você está fazendo |
| `/inbox` | Tria as capturas: validar/fazer agora ou descartar |
| `/painel` | Abre/regenera a Central de Produtividade (dashboard multi-projeto) |
| `/fim-do-dia` | Regenera o painel e gera um **resumo do dia** por projeto |

### No terminal

```bash
python ~/.claude/painel/run.py bom-dia        # foco do dia + abre painel
python ~/.claude/painel/run.py foco           # só a próxima ação
python ~/.claude/painel/run.py fim-do-dia     # resumos do dia por projeto
python ~/.claude/painel/run.py build          # só regenera o painel
python ~/.claude/painel/run.py btw "<ideia>"  # captura rápida
python ~/.claude/painel/run.py inbox          # lista a inbox
python ~/.claude/painel/run.py statusline     # 1 linha p/ a barra de status (lê do cwd no stdin)
python ~/.claude/painel/run.py open           # abre o painel já gerado
```

### Barra de status (statusline)

north entrega uma linha ambiente pra [statusline do Claude Code](https://code.claude.com/docs/en/statusline)
que reúne, num só lugar: **modelo · progresso e próxima ação do projeto atual
(detectado pelo `cwd`) · squad sugerido · sinais vitais · diretório · medidor da
janela de contexto** (com normalização de auto-compact).

```
Opus 4.8 │ 🧭 Backoffice Frontend 79% S4B-9 Botão Compartilhar… /backend ⛔1 │ backoffice-frontend ████░░░░░░ 48%
```

O `install.py` configura sozinho — **sem sobrescrever** uma statusline que você
já tenha (nesse caso ele só imprime o trecho pra você compor/colar). Para forçar:
`python install.py --statusline`. Ou cole no `~/.claude/settings.json`:

```jsonc
{ "statusLine": { "type": "command",
  "command": "python \"~/.claude/painel/run.py\" statusline", "padding": 1 } }
```

É barata por design: lê só um cache (`output/state.json`, regenerado a cada
build/ritual) — nunca roda descoberta ou git na barra.

---

## Como funciona

north faz **auto-descoberta**: varre os `scan_roots` procurando pastas com uma
`plan-build/` contendo seus arquivos de progresso, e normaliza formatos
heterogêneos — tabelas markdown, code-blocks, barras de progresso e emojis de
status — num modelo único. A partir daí, consolida portfólio, kanban, sprints,
bloqueios, débito técnico e autoria (via `git log`).

```
seus projetos/
  projeto-a/
    plan-build/
      Progress.md         ← north lê (status, sprint atual, bloqueios…)
      Sprint-01.md        ← north lê (tasks, progresso, autoria)
  projeto-b/
    plan-build/...
          │
          ▼
   north (motor)  ──lê, nunca escreve──▶  ~/.claude/painel/output/dashboard.html
```

### 🔗 Interoperabilidade com o GSD

Se você usa o [GSD](https://github.com/glamp/get-shit-done) (spec-driven development),
o north lê o `.planning/` automaticamente e trata cada projeto GSD como mais um no
portfólio — **sem reimplementar o motor do GSD**, só lendo o estado dele:

| GSD (`.planning/`) | vira no north |
|---|---|
| `ROADMAP.md` → Phases | sprints (CONCLUÍDA→done · LIBERADA→em andamento · BLOQUEADA→bloqueado) |
| Plans (`04-01: …`) | tasks do quadro |
| `STATE.md` → Progress / Blockers | rollup de progresso + sinais vitais |
| `HANDOFF.json` → next_action | dica da próxima ação |

A divisão de papéis: **GSD = profundidade** (um projeto, ciclo completo) · **north
= largura** (todos os projetos, foco e sinais vitais por cima).

#### Múltiplas estruturas no mesmo repo

O north resolve cada repo como **um card só**, mesmo que ele tenha várias
estruturas de planejamento (`plan-build/` + `.planning/` + o que vier). A fonte
**primária** é a mais recentemente ativa (arquivo de plano mais novo); as demais
viram um selo discreto **`+GSD`** / **`+plan-build`**. Para fixar a primária:

```jsonc
"projects": { "backoffice": { "source": "gsd" } }   // ignora a recência
```

Suporte a novas estruturas é um **adapter** (`detect` + `build` + `mtime`) — o
`plan-build` e o `GSD` são os dois primeiros; adicionar outro não toca o core.

### 🩺 Sinais vitais

Alertas *point-in-time* que aparecem no painel (overview e por card), derivados
do estado atual — sem precisar de histórico:

| Alerta | Severidade | Dispara quando | Threshold |
|---|---|---|---|
| **Trabalho não commitado** | 🔴 risco | arquivos sujos ≥ limite | `dirty_risk_files` (8) |
| **Branch parada** | 🟡 atenção | dias sem commit ≥ limite | `stale_branch_days` (3) |
| **Bloqueio aberto** | 🔴 risco | há bloqueio no caminho crítico | — |
| **WIP acima do limite** | 🟡 atenção | tasks "Em Andamento" > limite | `wip_limit` (3) |

---

## Configuração

Tudo vive em `~/.claude/painel/config/projects.json`:

```jsonc
{
  "scan_roots": ["C:/Users/voce/workspace"],   // onde procurar projetos
  "exclude": [],                                 // ids a ignorar
  "projects": {
    "meu-projeto": { "enabled": true, "alias": "Meu Projeto", "color": "#f97316", "order": 0,
                     "source": "gsd" }   // opcional: fixa a fonte primária (senão: por recência)
  },
  "settings": {
    "owner_name": "Seu Nome",
    "theme": "dark",            // dark | light
    "wip_limit": 3,
    "dirty_risk_files": 8,
    "stale_branch_days": 3,
    "open_browser": true,
    "mirror_to_project_docs": true
  }
}
```

Projetos novos aparecem automaticamente (habilitados) na próxima execução —
a config só **ajusta** (liga/desliga, apelido, cor, ordem, thresholds).

---

## Arquitetura

```
north-cli/
├── package.json            # camada npm (npx north-cli)
├── bin/north.js            # lançador cross-plataforma: acha o Python e delega
├── install.py              # o instalável — rode este (ou via npx)
├── src/
│   ├── run.py              # launcher (vai para a tool home ~/.claude/painel/)
│   ├── north_hook.py       # painel "vivo": regenera ao parar uma sessão
│   └── painel/
│       ├── config.py       # projects.json: scan_roots, toggles, settings
│       ├── discovery.py    # registry de source adapters + reconciliação por repo + git
│       ├── gsd.py          # adapter GSD: lê .planning/ (STATE/ROADMAP/HANDOFF)
│       ├── parsers.py      # normaliza formatos heterogêneos de progresso
│       ├── focus.py        # motor de direção ("o que faço agora?") + WIP guard
│       ├── health.py       # sinais vitais (alertas de saúde do portfólio)
│       ├── inbox.py        # captura rápida (/btw) e triagem (/inbox)
│       ├── render.py       # dashboard.html (CSS/JS puro, tema claro/escuro)
│       ├── rituals.py      # bom-dia / fim-do-dia (multi-projeto)
│       └── cli.py          # build | foco | bom-dia | fim-do-dia | inbox | open
├── skills/                 # SKILL.md de cada comando (instalados em ~/.claude/skills)
└── templates/              # template do resumo do dia
```

**Princípios:** sem nuvem, sem dependências externas (só Python stdlib), e
**read-only** sobre seus planos — seus `.md` são a fonte única de verdade.

---

## Roadmap

- [ ] **Snapshot store** — base para métricas históricas (velocity, burndown, aging WIP, tendência) e para retomar contexto ("onde parei / o que eu pensava")
- [ ] Integração GitHub (PRs/CI/issues no painel) + `/standup` dos commits
- [ ] `/relatorio-semanal` executivo a partir dos resumos diários

---

## Licença

[MIT](LICENSE) © Kayque Sanmartin de Assis
