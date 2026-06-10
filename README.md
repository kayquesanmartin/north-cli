<div align="center">

# 🧭 north

**English · [Português](README.pt-BR.md)**

**A multi-project productivity copilot for AI coding agents — Claude Code, Codex, Gemini CLI.**

north discovers all your projects on its own, reads the progress you already
write in markdown, and turns it into **direction**: what to do now, vital-sign
alerts before you get stuck, and start/end-of-day rituals. It also helps you
**plan, document, build and learn** along the way — an SDLC doc factory, a
plan-stress-test interview, TDD-first development, and mentor tracks that teach
you the concepts **and the libraries** as the AI codes. Local. No cloud.
It never edits your plans — it only reads them.

[![npm](https://img.shields.io/npm/v/north-cli.svg?color=f97316)](https://www.npmjs.com/package/north-cli)
[![License: MIT](https://img.shields.io/badge/license-MIT-f97316.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-3776ab.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/os-Windows%20%C2%B7%20macOS%20%C2%B7%20Linux-0ea5e9.svg)]()
[![Runtimes](https://img.shields.io/badge/runtimes-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Gemini-8b5cf6.svg)]()

</div>

---

## Why north?

Planning tools give you a **snapshot** — where each project stands. north gives
you **vital signs and direction**:

- 🧭 **`/north-focus`** answers the only question that matters each morning: *what do I do now?* — the highest-value next action across **all** your projects, respecting your WIP limit.
- 📍 **Ambient status line**: model · current project's next action · WIP · git branch · vital signs · context-window meter — right in the Claude Code status bar, **every prompt**, without you asking.
- 🩺 **Vital signs** warn you *before* you stall: uncommitted work becoming a risk, a stale branch, a blocker on the critical path, WIP over the limit.
- 🔍 **Auto-discovery**: point it at a folder and it finds every tracked project. New projects show up on their own.
- 🔗 **Interops with [GSD](https://github.com/open-gsd/gsd-core)**: reads `.planning/` (STATE/ROADMAP/HANDOFF) and shows your GSD projects — phases, progress, blockers, next action — in the same panel, next to your `plan-build` projects. north is the *breadth* layer **over** GSD, not a competitor.
- 📥 **Frictionless capture** (`/north-note`): save an idea mid-task without losing focus — it reminds you at end of day.
- 🔒 **Single source of truth**: north **only reads** your `.md` files. It never writes to them.

And, beyond direction, a full **build-with-AI** layer (the AI writes the artifacts under your direction; the engine stays read-only):

- 📄 **SDLC doc factory** (`/north-doc`): PRD · SPEC · SDD · TDD · ADR · SECURITY · living CONTEXT/DECISIONS · **sprint plans** the kanban reads back — anchored in your real project + a bundled reference library.
- 🔥 **Stress-test before you build** (`/north-grill`): instead of agreeing, the AI **interviews you** — one question at a time, each with a recommended answer — walking the decision tree and surfacing the gaps before they become a wrong PRD.
- 🧪 **TDD-first** (`/north-dev`): always offers to write the **tests first** from the task's real acceptance criteria (red → green → refactor).
- 🎓 **Mentor & passive insights** (`/north-learn`, `/north-insight`): learn by doing, or have the AI teach over its own code — concepts (LINQ, async…) **and libraries/frameworks/tools** (MediatR, Gotenberg, Chakra UI…): what it is, what it's for, when to use it — never repeating itself.
- 📚 **Knowledge that compounds** (`/north-library`, `/north-learnings`): a curated engineering compendium the AI cites, plus a per-project learning ledger recalled each morning so you don't repeat the mistake.

> north doesn't replace your planning system — it **reads** it and gives you what's
> missing: focus, rhythm, early warning — and a hand to plan, document, build and learn.

---

## Quickstart

Requires **Python 3.8+**. Works on **Windows, macOS, and Linux**.

```bash
npx north-cli@latest
```

One command. The interactive installer (cross-platform, no need to type "python"):

1. Asks **which runtimes** to install for — Claude Code, Codex, Gemini CLI (or all);
2. Asks the **scope** — global (`~/.north`, `~/.claude`, …) or local;
3. Asks the **folder where your projects live** (suggests the current directory);
4. Installs the **engine once** in `~/.north/` and generates per-runtime integrations;
5. Builds your first panel.

> north is a Python engine; the npm package is the **cross-platform launcher** —
> it detects `python3`/`python`/`py` and installs. The engine lives in a neutral
> home (`~/.north`); each runtime just gets the commands that call it.

### Runtimes (same engine, different shell)

| Runtime | Commands | Where |
|---|---|---|
| **Claude Code** | `/north-focus`, `/north-note`, `/north-panel`… (skills) + status line | `~/.claude/skills/` |
| **Codex** | `/north-focus`, `/north-note`… (prompts) | `~/.codex/prompts/` |
| **Gemini CLI** | `/north:focus`, `/north:note`… (`!{}` commands) | `~/.gemini/commands/north/` |

Non-interactive (CI / scripted):

```bash
npx north-cli install --runtimes claude,codex,gemini --scope global \
    --scan-root "/path/to/projects" --all
```

---

## How it works

north **auto-discovers** projects: it scans your `scan_roots` for folders that
have a `plan-build/` (its native markdown) or a `.planning/` (GSD), normalizes
heterogeneous formats — tables, code blocks, progress bars, status emoji — into
one model, and consolidates portfolio, kanban, sprints, blockers, tech debt, and
git authorship.

```
your projects/
  project-a/
    plan-build/Progress.md   ← north reads (status, current sprint, blockers…)
    plan-build/Sprint-01.md  ← north reads (tasks, progress, authorship)
  project-b/.planning/       ← GSD project — also read
          │
          ▼
   north engine ──reads, never writes──▶ ~/.north/output/dashboard.html
```

### Commands

In your AI runtime as `/north-<cmd>` (Codex `/north-<cmd>` · Gemini `/north:<cmd>`), grouped by intent:

| Group | Commands |
|---|---|
| 🧭 **Direction & rituals** | `/north-focus` · `/north-morning` · `/north-wrap-up` · `/north-panel` |
| 📥 **Capture** | `/north-note <idea>` · `/north-inbox` |
| 📄 **Docs (SDLC)** | `/north-grill` (stress-test the plan) · `/north-doc <prd\|spec\|sdd\|tdd\|adr\|security\|sprint\|context\|decisions>` |
| 🧪 **Build (TDD-first)** | `/north-dev` · `/north-task <id>` |
| 🎓 **Mentor tracks** | `/north-learn` · `/north-review` · `/north-test` · `/north-codebase` · `/north-standup` |
| 💡 **Knowledge & learning** | `/north-insight` · `/north-library` · `/north-learnings` |
| ⚙️ **Config & system** | `/north-init` · `/north-forget` · `/north-status` · `/north-config` · `/north-help` · `/north-uninstall` |

`/north-help` prints the full guided tour. Uninstall anytime: `north uninstall` (preserves your data; `--purge` wipes it too).

In the terminal (or `north <cmd>` if installed via npm):

```bash
north focus        # the single next action + suggested squad
north status      # what's installed, scan_roots, tracked projects
north config      # view/edit config without reinstalling
north panel      # regenerate the dashboard
```

### 🩺 Vital signs

Point-in-time alerts surfaced in the panel and status bar — no history needed:

| Alert | Severity | Fires when | Threshold |
|---|---|---|---|
| Uncommitted work | 🔴 risk | dirty files ≥ limit | `dirty_risk_files` (8) |
| Stale branch | 🟡 warn | days since last commit ≥ limit | `stale_branch_days` (3) |
| Open blocker | 🔴 risk | a blocker sits on the critical path | — |
| WIP over limit | 🟡 warn | in-progress tasks > limit | `wip_limit` (3) |

---

## Configuration

Everything lives in `~/.north/config/projects.json`. Manage it from the CLI —
no reinstall needed:

```bash
north config                                  # show
north config add-root "/another/workspace"    # track another folder
north config project backoffice source gsd    # pin the primary source
north config set theme light                   # theme / wip_limit / thresholds
```

Installation is **global** (one north serves every project); what changes per
machine are the `scan_roots`. When a repo has multiple planning structures
(`plan-build/` + `.planning/`), north shows **one card** with the most recently
active source as primary and the others as a `+GSD` / `+plan-build` badge.

---

## Documentation

- **[Português (README.pt-BR.md)](README.pt-BR.md)** — full docs in Portuguese
- [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md) · [Changelog](CHANGELOG.md)

## Contributing

Issues and PRs are welcome. north uses [Conventional Commits](https://www.conventionalcommits.org)
and [SemVer](https://semver.org). See **[CONTRIBUTING.md](CONTRIBUTING.md)** to get started.

## Security

north is local-first and never transmits your data. Found a vulnerability?
Please follow **[SECURITY.md](SECURITY.md)** (private report) — don't open a public issue.

## License

[MIT](LICENSE) © Kayque Sanmartin de Assis
