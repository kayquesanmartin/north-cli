# Changelog

All notable changes to **north** are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
