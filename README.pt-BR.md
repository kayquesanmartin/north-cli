<div align="center">

# 🧭 north

**[English](README.md) · Português**

**Seu copiloto de produtividade multi-projeto para IAs (Claude Code · Codex · Gemini CLI).**

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

- 🧭 **`/focus`** responde a única pergunta que importa de manhã: *o que eu faço agora?* — a próxima ação de maior valor entre **todos** os projetos, respeitando seu limite de WIP.
- 📍 **Statusline ambiente**: sua próxima ação + alertas direto na barra de status do Claude Code, **a cada prompt** — north presente sem você precisar pedir.
- 🩺 **Sinais vitais** te avisam *antes* de travar: trabalho não commitado virando risco, branch parada, bloqueio no caminho crítico, WIP acima do limite.
- 🔍 **Auto-descoberta**: aponte para uma pasta e ele acha todo projeto com tracking. Projeto novo aparece sozinho no painel.
- 🔗 **Interopera com o [GSD](https://github.com/glamp/get-shit-done)**: lê o `.planning/` (STATE/ROADMAP/HANDOFF) e mostra seus projetos GSD — fases, progresso, bloqueios, próxima ação — no mesmo painel, ao lado dos `plan-build`. north é a camada de largura *sobre* o GSD, não um concorrente.
- 📥 **Captura sem fricção** (`/note`): salva uma ideia no meio de qualquer tarefa sem perder o foco — e te lembra dela no fim do dia.
- 📊 **Painel profissional** em HTML puro (sem build, sem dependência) — portfólio, kanban, sprints, bloqueios, débito técnico e autoria via git.
- 🔒 **Fonte única de verdade**: north **só lê** seus `.md`. Nunca escreve neles.

> north não substitui seu sistema de planejamento — ele o **lê** e te dá o que
> falta: foco, ritmo e alerta precoce.

---

## Instalação

Requisitos: **Python 3.8+**. `git` opcional (habilita autoria e sinais vitais de git). Funciona em **Windows, macOS e Linux**. north é **para IAs** — instala em vários runtimes.

```bash
npx north-cli@latest
```

Um comando. O instalador interativo (cross-plataforma, **sem você digitar "python"**):

1. Pergunta **para quais runtimes** instalar — **Claude Code**, **Codex**, **Gemini CLI** (ou todos);
2. Pergunta o **escopo** — global (`~/.north`, `~/.claude`, …) ou local (`./…`);
3. Pergunta a **pasta dos seus projetos** (sugere o diretório atual);
4. Instala o **motor uma vez** em `~/.north/` e gera as integrações por runtime;
5. Gera o primeiro painel.

> Como funciona: north é um motor Python; o pacote npm é o **lançador cross-plataforma** — detecta `python3`/`python`/`py` e instala. O motor mora num home neutro (`~/.north`) e cada runtime ganha só os comandos que o chamam.

Integração por runtime (mesmo motor, casca diferente):

| Runtime | Comandos | Onde |
|---|---|---|
| **Claude Code** | `/focus`, `/note`, `/panel`… (skills) + statusline | `~/.claude/skills/` |
| **Codex** | `/north-focus`, `/north-note`… (prompts) | `~/.codex/prompts/` |
| **Gemini CLI** | `/north:focus`, `/north:note`… (comandos `!{}`) | `~/.gemini/commands/north/` |

Modo não-interativo (CI / scriptado) e flags:

```bash
npx north-cli install --runtimes claude,codex,gemini --scope global \
    --scan-root "/caminho/dos/projetos" --all
```
`--runtimes <csv>` · `--scope global|local` · `--scan-root "<pasta>"` · `--all` · `--skip-plugins` · `--no-statusline` · `--no-build`

**Via clone** (para desenvolver o north): `git clone … && cd north-cli && python install.py --runtimes claude`.

---

## Uso

### No Claude Code (de qualquer projeto)

| Skill | O que faz |
|---|---|
| `/morning` | Regenera o painel, mostra o **foco do dia** consolidado e abre no navegador |
| `/focus` | A próxima ação de maior valor agora (sprint atual › caminho crítico › desbloqueada) + squad sugerido |
| `/note <ideia>` | Captura rápida — salva na inbox sem quebrar o que você está fazendo |
| `/inbox` | Tria as capturas: validar/fazer agora ou descartar |
| `/panel` | Abre/regenera a Central de Produtividade (dashboard multi-projeto) |
| `/wrap-up` | Regenera o painel e gera um **resumo do dia** por projeto |

### No terminal

```bash
python ~/.north/run.py morning        # foco do dia + abre painel
python ~/.north/run.py focus           # só a próxima ação
python ~/.north/run.py wrap-up     # resumos do dia por projeto
python ~/.north/run.py build          # só regenera o painel
python ~/.north/run.py note "<ideia>"  # captura rápida
python ~/.north/run.py inbox          # lista a inbox
python ~/.north/run.py status         # o que está instalado, scan_roots, projetos rastreados
python ~/.north/run.py config         # ver/editar config sem reinstalar
python ~/.north/run.py open           # abre o painel já gerado
```

> Com a instalação npm, troque `python ~/.north/run.py` por **`north`** em qualquer SO (`north focus`, `north status`, …).

### Setup passo a passo

```bash
# 1. instale (de qualquer lugar — o motor vai pra ~/.north)
npx north-cli@latest
#    pergunta os runtimes (Claude Code/Codex/Gemini), o escopo e a pasta dos projetos.

# 2. veja o que ficou configurado
north status

# 3. ajuste sem reinstalar
north config add-root "C:/outro/workspace"     # rastrear outra pasta
north config project backoffice source gsd     # fixar a fonte primária
north config set theme light                    # tema / wip_limit / etc.

# 4. no dia a dia (no Claude Code): /morning · /focus · /note · /panel · /wrap-up
```

A instalação é **global** (um north serve todos os projetos); o que muda por
máquina são os `scan_roots` — as pastas que ele varre. Rode o install da
**pasta-mãe dos seus projetos**, ou aponte com `--scan-root`/`north config add-root`.

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
  "command": "python \"~/.north/run.py\" statusline", "padding": 1 } }
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
   north (motor)  ──lê, nunca escreve──▶  ~/.north/output/dashboard.html
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

Tudo vive em `~/.north/config/projects.json`:

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
├── bin/north.js            # lançador/instalador interativo cross-plataforma (npx)
├── install.py              # orquestrador do install (flags: --runtimes, --scope)
├── runtimes.py             # motor (1×) + adapters por runtime (Claude/Codex/Gemini)
├── src/
│   ├── run.py              # launcher (vai para a tool home ~/.north/)
│   ├── north_hook.py       # painel "vivo": regenera ao parar uma sessão
│   └── painel/
│       ├── config.py       # projects.json: scan_roots, toggles, settings
│       ├── discovery.py    # registry de source adapters + reconciliação por repo + git
│       ├── gsd.py          # adapter GSD: lê .planning/ (STATE/ROADMAP/HANDOFF)
│       ├── parsers.py      # normaliza formatos heterogêneos de progresso
│       ├── focus.py        # motor de direção ("o que faço agora?") + WIP guard
│       ├── health.py       # sinais vitais (alertas de saúde do portfólio)
│       ├── inbox.py        # captura rápida (/note) e triagem (/inbox)
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
