# Changelog

All notable changes to **north** are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Reference library north can consult (`north library` / `/north-library`).** Bring your
  own curated engineering references (Clean Code, SOLID, DDD, TDD, CQRS, security…) with
  `north library add "<folder>"`; north indexes them locally in `~/.north/library/` and the
  mentor/insight tracks consult them (`library find "<topic>"`) to anchor what they teach and
  **cite the source**. Keyword index + search, stdlib-only. "Ship the librarian, not the
  library": the mechanism is in the package; your content stays local (never published, so
  no copyright issue) and survives reinstalls. The mentor/insight skills now consult it first.

### Added
- **`north help` / `/north-help` — the guided tour.** A single command that explains
  everything north offers, grouped by intent (direction & rituals, panel, capture, mentor
  tracks, passive insights, config/system), showing both the terminal form (`north <cmd>`)
  and the in-AI form (`/north-<cmd>`), plus a "primeiros passos". The `/north-help` skill
  runs it and teaches by intent (and can deep-dive a specific command). Parity across runtimes.

### Added
- **Passive insights while the AI codes (`/north-insight`, teach-on-write).** Distinct from
  `/north-learn` (there *you* code): here the AI codes and teaches what it used — short
  micro-lessons on the **hardest/most-important** concept of each change (nullable operators,
  LINQ, pattern matching…), **never repeating** within a cooldown unless the concept comes
  back. The AI detects and ranks the concepts; the north engine is the **memory + scheduler**:
  `north insight check/record/log <lang>`, a per-language ledger at
  `~/.north/learnings/taught/<lang>.md` (markdown table), and a concept catalog at
  `references/concepts/<lang>.md` (C# shipped). Configurable cooldown and minimum level.
  Read-only over your code — the engine only writes its own home. Parity across all runtimes.

### Added
- **SDLC documents detected and linked on the dashboard (read-only).** north now finds the
  PRD / SDD / TDD / SPEC / SECURITY / ADR / UML files inside `plan-build/` and shows them as
  a "📚 Documentos do projeto" section (color-coded by type, click to open the file) plus a
  doc count on the portfolio card; sprint modals surface the sprint's "pré-leitura /
  referências". First slice of the AI-SDLC direction (`docs/north-ai-sdlc-SPEC.md`) — pure
  detection, the engine never writes.

### Added
- **Real sprint/task summary in the executive view (not just done/pending).** The detail
  modal and the project executive summary now read the narrative from `Sprint*.md` — the
  **objective ("what will be done")**, the **rationale ("why now")**, and **out-of-scope** —
  instead of only status counters. The sprint modal leads with this brief; a task shows its
  parent sprint's objective as context; the project view surfaces the current sprint's goal.
  Parsed from `## Meta/Objetivo do Sprint` + `**Entregável**` and degrades gracefully when a
  plan has no prose. Read-only.
- **Acceptance criteria & executed activities in the detail view.** The task modal now shows
  its contract — **🔨 what to deliver (activities)** and **✅ acceptance criteria** — parsed
  from the `**Builder entrega:** / **Evaluator valida:**` (or DoD / "Critério de aceite")
  sections of `Sprint*.md`, fence-aware so `# comments` inside ```` ``` ```` code blocks aren't
  mistaken for headers. The sprint modal surfaces the sprint-level DoD and splits its tasks
  into **executed (done)** vs **pending**.

### Changed
- **Dashboard typography tuned for a modern dev-platform feel.** Inter-first font stack,
  antialiasing, tabular numerals on metrics/percentages, and tighter heading tracking.

### Added
- **Focus follows what *you* are actually touching (not just what it read).** In a shared
  repo, the day's focus used to rank purely by plan-reading, so it could point you at another
  dev's work. north now derives a personal signal from git — your uncommitted working tree
  (strongest), your commits today, your feature branch, and files you last authored — and
  soft-ranks your active project first (nothing is ever hidden; others still show under
  "outros / time"). With no personal signal (fresh clone, start of day) it falls back to the
  old read-only ranking. `/north-morning` now prints a "🎯 SEU FOCO PROVÁVEL (detectado pelo
  git)" block and the skill **confirms it with you** before pinning (`north focus --only`),
  asking which project when git shows no signal. `/north-wrap-up` distinguishes "N commits
  seus" from the team's total. Read-only as always.
- **Optional `north` terminal command (PATH setup at install).** Installing via
  `python install.py` set up the engine and the in-AI skills but never created a `north`
  command on your PATH, so `north …` failed in a plain terminal (only the npm global shim
  provided it). The installer now offers — opt-in — to create a cross-platform launcher in
  `~/.north/bin` (`north` + `north.cmd`) and add that dir to your user PATH (Windows via the
  registry, no `setx` truncation; Unix via your shell rc). Prompted interactively, or drive
  it non-interactively with `--add-to-path` / `--no-path`. Uninstall removes the launcher and
  the PATH entry. Open a new terminal after enabling.
- **Clickable detail modal on the dashboard (C-level + technical).** Clicking any kanban
  task or sprint card opens a centered modal with two reads of the same item: an
  **executive view** (business verdict — delivered / in dev / code-ready / blocked-risk —
  plus the deliverable, sprint/wave, and owner) and a **technical view** (id, sprint key,
  feature, kanban column, raw status from the `.md`, dependencies, commit). The sprint
  modal lists its tasks; clicking one drills straight into the task. Close with the ✕,
  the backdrop, or `Esc`. Read-only as always — it only surfaces what the plans already say.
- **Per-folder task boards (board switcher).** On projects whose plans are split across
  subfolders, the task board no longer mixes everything together. A segmented switcher
  (`📁 Todas · folder-a · folder-b…`) sits above the kanban — pick a folder to see only
  its tasks; each card also carries a color-coded folder tag in the "Todas" view, so you
  always know which `plan-build` subfolder a task came from.
- **Executive (C-level) summary on the project view too.** The per-project page now opens
  with the same executive read the portfolio has — verdict, progress, current sprint,
  blockers/debt, and today's activity — not just raw KPIs.

### Changed
- **Light theme is now the default, with an enterprise-grade palette.** Cooler neutral grays,
  higher-contrast text, softer shadows, and a theme-aware background glow. Status chips
  (risk/attention/priority) were re-tuned for readable contrast on light backgrounds. The
  ◐ toggle still switches to dark.

### Fixed
- **Git worktrees no longer show up as phantom projects.** Discovery walked into
  `.claude/worktrees/`, and since every worktree is a checkout of the same repo, each one
  surfaced as a separate "project" rendering identical sprints/tasks. Discovery now prunes
  `.claude` (worktrees), VCS dirs (`.git`/`.hg`/`.svn`), dependency/cache dirs
  (`node_modules`, virtualenvs, caches) and `archive/` for both `plan-build` and GSD
  `.planning` scans — so only real projects appear, and the scan is much faster on large
  trees. Stale phantom entries self-heal out of `projects.json` on the next scan.

### Added
- **Mentor tracks expanded: `/north-codebase` and `/north-standup`.** Two new learning-first
  behavior skills. `/north-codebase` guides you to understand a project yourself — map the
  architecture, find where things live, read the DB schema and folder organization — you
  explore, the AI asks the questions and anchors in official docs. `/north-standup` trains
  daily/meeting conduct — what to report (done/doing/blocker/ask), when to speak, how to
  surface risk and unblock early. `/north-learn` is now the junior→pleno→senior progression
  hub that routes to the sibling tracks, and `/north-test` gained concrete tooling playbooks
  (Postman/Insomnia, SQL client, Playwright/Cypress). All three runtimes, anchored in docs.
- **Segmented plans are now tracked (features by subfolder).** Discovery descends the
  whole `plan-build` tree instead of only its top level, so plans split across subfolders
  (e.g. `plan-build/calculo/Sprint-1.md`, `plan-build/pricing/Sprint-2.md`) are no longer
  invisible. Each first-level subfolder becomes a **feature group**: the project view shows
  collapsible groups with per-feature progress, and kanban cards carry a feature tag. Sprint
  keys that repeat across features (a `Sprint-1` in two folders) no longer overwrite each
  other. Recency (live-panel trigger) also follows edits in subfolders. Read-only as always.
- **Nested plan-builds fold into the parent project.** A `plan-build` nested inside another
  project (e.g. `projeto/feature-x/plan-build/`) is now absorbed as a **feature** of the
  parent — one card with grouped features — instead of showing up as a separate project.
  Folds into the top-most ancestor (handles deep chains); a nested dir that also has a GSD
  `.planning` stays its own card, so legitimate sub-projects aren't swallowed.

### Fixed
- **Deleted projects no longer linger (config self-heals on scan).** When a project's
  folder/`plan-build` is gone, discovery now prunes its stale entry from `projects.json`
  and reports it (`- N projeto(s) removido(s)…`), so `north status`/`config show` stop
  showing ghosts. Guarded: if a scan finds nothing (e.g. a broken `scan_roots`), nothing
  is pruned — your config is never wiped by a misconfiguration. The dashboard already
  reflected reality on regen; this closes the gap in the persisted state.

### Added
- **Executive (C-level) summary on the dashboard.** The portfolio view now opens with a
  structured exec block: health verdict (healthy / attention / at-risk), global progress,
  on-track vs at-risk counts, open blockers, today's activity, and the top priority —
  clickable to drill into the project. Vital-sign rows are clickable too.

### Added
- **Pre-push guard.** Before `git push` / `gh pr create`, north fetches (best-effort) and
  warns if your branch is behind its upstream or base — "git pull --rebase first" — to avoid
  conflicts. Non-blocking, fast, offline-safe. (PreToolUse hook, alongside the live-panel hook.)

### Fixed
- **Live-panel hook is now actually wired.** `north_hook.py` was copied to `~/.north` but
  never registered in `settings.json`, so the auto-regenerate-on-activity feature was dead.
  Install now registers it (non-destructive merge; third-party hooks preserved) and uninstall
  removes it. It also now triggers on `git push` and `gh pr create`, not just `git commit`.
  Disable with `--no-hooks`.

### Added
- **Mentor tracks (F2): `/north-review` and `/north-test`.** Curated learning tracks
  (behavior skills): review teaches you to read your own diff before opening a PR; test
  teaches real validation (API via Postman/Insomnia, DB, frontend/e2e) — you do it, the AI guides.

## [0.7.0] - 2026-06-03

### Added
- **Mentor mode (`/north-learn`).** A learning-first mode where the AI *orients and you
  implement* — to understand the code, do your own review, and work without the AI. Grounded
  in official docs, level-aware (junior→pleno→senior), teaches the meta (reading code, self
  review, debugging, testing, versioning). Works across Claude/Codex/Gemini via new
  **behavior skills** (commands that live in the runtime, not the engine).

## [0.6.0] - 2026-06-03

### Added
- **Git sync awareness in the rituals.** `/north-morning` and `/north-wrap-up` now flag when
  your branch is **behind its upstream** or **behind the base branch** (main/dev) — so you
  pull/rebase before conflicts pile up, and validate before pushing. Counts come from local
  refs (offline-safe); the ritual skills run `git fetch` first (best-effort) for fresh data
  and guide safe versioning (pull --rebase → test → push). Surfaces as health alerts in the panel too.

## [0.5.0] - 2026-06-03

### Changed
- Installer summary is now **IA-first**: it leads with "start inside your AI" and the first
  command to type per runtime; the terminal path is shown as optional.
- Claude skills are now **namespaced** `north-*` (`/north-focus`, `/north-status`, `/north-config`…),
  matching Codex (`/north-*`) and Gemini (`/north:*`). Avoids collisions with native/other
  commands. Old un-namespaced skills are removed automatically on reinstall.

### Added
- `/status` and `/config` are now **skills inside the AI runtime** (Claude/Codex/Gemini),
  not just terminal commands — north is IA-first, every command works inside the AI.

## [0.4.0] - 2026-06-03

### Added
- **Daily project focus.** `north focus --only <project>` scopes `/morning`,
  `/wrap-up` and `/focus` to a single project for the day; `north focus --all`
  returns to the full portfolio. The dashboard always shows everything — only the
  ritual output is scoped. The focus is sticky until changed.

### Changed
- Installer projects-folder prompt now shows examples, validates the path, and
  **offers to create it** if missing (instead of just warning). Applies to both
  the `npx north-cli` launcher and `install.py`.

## [0.3.0] - 2026-06-03

### Added
- `north uninstall` — removes north from one or all runtimes (Claude/Codex/Gemini)
  and the `~/.north` engine, **preserving your data by default**. Flags: `--runtimes`,
  `--all`, `--purge` (also wipes config/inbox/resumos), `--yes`. Interactive menu when
  run in a terminal. Also available as the `/uninstall` skill.

### Changed
- Renamed the quick-capture command `/btw` → `/note` to avoid a collision with a
  native Claude command. `btw` still works as a legacy alias at the engine level;
  the internal inbox id prefix stays `BTW-` for backward compatibility.
- Adopted **English** as the standard for dev artifacts (branch names, commit messages,
  command/skill names, identifiers). User-facing copy stays pt-BR.
- Renamed the pt-BR commands to English: `/foco`→`/focus`, `/bom-dia`→`/morning`,
  `/fim-do-dia`→`/wrap-up`, `/painel`→`/panel`. The pt-BR names stay as aliases (slash
  commands across Claude/Codex/Gemini + engine), so existing usage keeps working.

## [0.2.1] - 2026-06-03

### Added
- English README as the primary language + `README.pt-BR.md` with a language switcher.
- Community & governance files: `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
  this changelog, GitHub issue/PR templates, `CODEOWNERS`, Dependabot.
- CI (compile + install smoke) and an OIDC trusted-publishing release workflow.

### Changed
- Genericized the default `owner_name` (no personal name baked into the engine).

## [0.2.0]

### Added
- **Multi-runtime installer.** `npx north-cli` is now an interactive installer
  (banner, runtime selection, scope, projects folder) that targets **Claude Code,
  Codex, and Gemini CLI** with one command, cross-platform.
- `runtimes.py`: engine installed **once** to a neutral home (`~/.north`) plus
  per-runtime adapters (Claude skills, Codex prompts, Gemini `!{}` TOML commands).

### Changed
- Engine relocated from `~/.claude/painel` to the runtime-neutral `~/.north`;
  legacy config is migrated automatically and the north status line is repointed.

## [0.1.2]

### Added
- `north config` (CRUD for scan_roots / settings / per-project source, no reinstall)
  and `north status` (what's installed, scan_roots, tracked projects).
- The installer now **asks** for the projects folder instead of assuming the CWD.

## [0.1.1]

### Fixed
- npm tarball no longer ships `__pycache__/*.pyc` (a `prepack` step cleans bytecode).

## [0.1.0]

### Added
- First npm release: cross-platform launcher (`npx north-cli`) around the Python engine.
- Multi-project auto-discovery, focus (`/foco`), vital signs, dashboard, daily
  rituals, quick capture (`/btw`) + inbox, GSD `.planning/` interop, and a rich
  Claude Code status line.

[Unreleased]: https://github.com/kayquesanmartin/north-cli/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/kayquesanmartin/north-cli/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/kayquesanmartin/north-cli/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/kayquesanmartin/north-cli/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/kayquesanmartin/north-cli/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/kayquesanmartin/north-cli/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/kayquesanmartin/north-cli/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/kayquesanmartin/north-cli/releases/tag/v0.2.0
[0.1.2]: https://github.com/kayquesanmartin/north-cli/releases/tag/v0.1.2
[0.1.1]: https://github.com/kayquesanmartin/north-cli/releases/tag/v0.1.1
[0.1.0]: https://github.com/kayquesanmartin/north-cli/releases/tag/v0.1.0
