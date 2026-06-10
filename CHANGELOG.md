# Changelog

All notable changes to **north** are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Gerador de plano de sprint (`/north-doc sprint`).** Novo tipo da fábrica de docs que ajuda a
  **quebrar o trabalho em um sprint** a partir dos docs (PRD/SPEC) — e grava um `Sprint*.md` no
  `plan-build/` **no formato que o painel já lê de volta** (vira kanban + contrato de cada task:
  `Builder entrega:`/`Evaluator valida:`). Embute as convenções travadas no estudo de sprint:
  status reconhecidos pelo kanban, **impedimento como flag** (não coluna), **tags de disciplina**
  (`[ANALISE] [API] [FRONTEND/UI/UX] [PESQUISA]`) e o DoD "só vai a Concluído após testes +
  code-review". Um por feature/microsserviço. Motor read-only (a IA escreve com sua confirmação);
  `north doc template sprint` mostra o esqueleto. Paridade nos 3 runtimes.

## [0.11.1] - 2026-06-09

### Changed
- **Instalação não varre mais o disco — onboarding por enrollment.** Fecha o ciclo do `north init`:
  o instalador (`install.py` e o `npx north-cli`) **não pergunta mais a pasta dos projetos nem
  semeia `scan_root`/auto-varre** no primeiro uso. Em vez disso, onboarda com *"plugue um projeto:
  `north init` na raiz"* — o north passa a rastrear só o que você plugar. **Retrocompatível:** quem
  já tinha `scan_roots` na config segue no modo `scan`; um `--scan-root <pasta>` explícito ainda
  força o scan. O painel nasce no primeiro `north init`/uso (sem build vazio na instalação).

## [0.11.0] - 2026-06-09

### Changed
- **Learning ledger agora é memória BOUNDED (dedup + curadoria, padrão Hermes).** O ledger de
  aprendizado (`north learnings`) deixou de só acumular: ao salvar, **deduplica** near-duplicates
  (mesmo tipo + texto muito parecido, por similaridade de tokens), **reaproveita o que volta**
  (em vez de duplicar, refresca a data e a recência — o que é reusado "sobrevive" mais) e mantém
  um **teto por projeto** (`LEDGER_CAP`, evicta os mais antigos) — pra a memória não inchar nem
  apodrecer. Novo `north learnings prune <project>` cura ledgers já existentes (dedup + teto).
  Stdlib, sem ML; escreve só em `~/.north`.

### Added
- **Enrollment opt-in (`north init` / `/north-init`).** Em vez de auto-varrer todas as pastas dos
  `scan_roots`, agora você **pluga** os projetos que quer acompanhar: `north init` na raiz registra
  o caminho em `~/.north` e o north passa a rastrear **só o que foi plugado** — mata o ruído de
  projetos indesejados no bom-dia/fim-do-dia/painel. **Read-only:** nada é escrito dentro do
  projeto (o caminho vive na casa do north). `north forget <projeto>` des-pluga; `north status`
  mostra o modo e os plugados. **Retrocompatível:** quem já usava continua no modo `scan` legado
  (`discovery_mode`) até rodar `north init` pela primeira vez — então migra para `enrolled`, sem
  quebrar nada. Paridade nos 3 runtimes (`/north-init`, `/north-forget`).

## [0.10.0] - 2026-06-09

### Added
- **Docs vivos no `north-doc`: `CONTEXT.md` e `DECISIONS.md`.** Dois tipos novos da fábrica de
  docs, voltados a **memória técnica do projeto** — `context` é o briefing de 15 min (stack/
  versões, convenções, entidades do domínio, e os "não faça isso porque"); `decisions` é o log
  vivo do **porquê** das escolhas (mais leve que um ADR). Servem de **contexto inicial** tanto
  para uma sessão de IA quanto para o dev manual retomando o projeto. Diferente dos docs de SDLC,
  os vivos vivem na **raiz do projeto** (ou `docs/`), **um por projeto**, e são **detectados e
  linkados no painel** (badges próprios). O motor segue read-only — a IA redige e grava o arquivo
  novo **com sua confirmação**. `north doc template context|decisions`; `north doc list` separa os
  "📌 vivos" do gap de SDLC. Paridade nos 3 runtimes.

## [0.9.1] - 2026-06-09

### Changed
- **Premium UX pass (dashboard + CLI) — "real platform" feel.** The dashboard was re-tuned to
  a calm, dev-platform aesthetic (Linear/Height): a redesigned token system (cooler neutral
  grays in both themes — light default now near-white with subtle borders; dark shifted from
  navy to neutral charcoal), tighter radii (10px), softer layered shadows, restrained accent
  (the focus banner is now a subtle panel with an accent bar instead of a loud gradient),
  calmer KPIs, and consistent hover/transitions. CLI output is now consistent across commands
  via a shared style module — every command leads with a uniform `🧭 north · <cmd>` header.

## [0.9.0] - 2026-06-08

### Added
- **Learning ledger (`north learnings` + wrap-up capture → morning recall).** north now
  remembers what you learn as you build — **decisions, bugs+fixes, patterns, gotchas** — in a
  per-project ledger (`~/.north/learnings/ledger/<project>.jsonl`). `/north-wrap-up` proposes
  1–3 learnings to save (you confirm — capture with triage, no noise), and `/north-morning`
  recalls the recent ones for your active projects so you don't repeat the mistake.
  `north learnings add/list/find <project>`. Read-only over your code; stdlib JSONL.
- **Document factory (`/north-doc` + `north doc`).** Generate the SDLC artifacts — PRD,
  SPEC, SDD, TDD, ADR, SECURITY — anchored in the real project context and the reference
  library, following bundled templates (`references/doc-templates/`). The AI drafts under
  your direction and writes where you confirm (idempotent, cross-linked); the engine stays
  read-only: `north doc list` shows, per project, which doc types exist vs are missing, and
  `north doc template <type>` prints the skeleton. Parity across runtimes.

## [0.8.0] - 2026-06-08

### Added
- **TDD-first development (`/north-dev` + `north task`).** When you start building, north now
  **always offers TDD** (default on; opt out with `tdd_default off`) and writes the **tests
  first** from the task's real **acceptance criteria** — `north task <id>` dumps a task's
  contract (what to deliver + ✅ criteria, from the `Evaluator valida:`/DoD the dashboard
  already extracts), and the `/north-dev` skill drives red→green→refactor, anchoring on the
  bundled TDD reference (3 laws) and the project's own test stack. Read-only over plans; the
  AI writes tests/code with your consent. Parity across runtimes.
- **Reference library north consults (`north library` / `/north-library`).** A curated
  engineering compendium ships **bundled** in `references/compendium/` (architecture, DDD,
  microservices, event-driven/CQRS, Clean Code & SOLID, design patterns, TDD, databases,
  API design, security, spec-driven dev, diagramming, frontend…) and lands in `~/.north`
  on install. You can also **bring your own** with `north library add "<folder>"` (indexed
  locally in `~/.north/library/`). `library find "<topic>"` does a keyword search across
  both (stdlib-only) and the mentor/insight tracks consult it first to anchor what they
  teach and **cite the source**. Hybrid: shipped core + bring-your-own; bundled entries
  flagged `[bundlado]`, large binaries (PDFs) stay local as pointers.

### Fixed
- **`references/` is now published in the npm package.** It was missing from `files`, so the
  concept catalog and bundled compendium wouldn't reach users; added it.

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

[Unreleased]: https://github.com/kayquesanmartin/north-cli/compare/v0.11.1...HEAD
[0.11.1]: https://github.com/kayquesanmartin/north-cli/compare/v0.11.0...v0.11.1
[0.11.0]: https://github.com/kayquesanmartin/north-cli/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/kayquesanmartin/north-cli/compare/v0.9.1...v0.10.0
[0.9.1]: https://github.com/kayquesanmartin/north-cli/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/kayquesanmartin/north-cli/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/kayquesanmartin/north-cli/compare/v0.7.0...v0.8.0
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
