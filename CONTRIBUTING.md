# Contributing to north

Thanks for your interest! north is a local-first, multi-project productivity
copilot for AI coding agents. This guide covers how to develop and propose changes.

## Project shape

- **Engine** — Python (stdlib only), in `src/painel/`. Pure read of your plan
  files; it never writes to them.
- **Launcher / installer** — `bin/north.js` (Node) + `install.py` + `runtimes.py`.
  The npm package is only a cross-platform launcher around the Python engine.
- **Runtime adapters** — `runtimes.py` installs the engine once (`~/.north`) and
  generates per-runtime integration (Claude Code skills, Codex prompts, Gemini
  TOML commands). Adding a new runtime = one adapter; the core doesn't change.

## Local setup

```bash
git clone https://github.com/kayquesanmartin/north-cli.git
cd north-cli
python install.py --runtimes claude --scan-root "/path/to/your/projects"
python src/run.py status
```

No dependencies to install — the engine uses only the Python standard library.

## Commit convention

north follows **[Conventional Commits](https://www.conventionalcommits.org)**:

```
<type>(<optional scope>): <subject>
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `perf`, `ci`.
When a commit closes an issue, reference it in the body (`Closes #NN`).
Versioning is **[SemVer](https://semver.org)**; user-facing changes go in
[`CHANGELOG.md`](CHANGELOG.md).

Examples:

```
feat(gsd): read .planning/ projects into the panel
fix(statusline): never emit an empty line (blanks the bar)
docs: translate README to English (primary) + pt-BR
```

## Pull requests

1. Branch off `main` (e.g. `feat/gemini-adapter`, `fix/scanroot-windows`).
2. Keep PRs focused. Update docs and `CHANGELOG.md` when behavior changes.
3. Make sure it runs on Windows, macOS, and Linux — avoid OS-specific paths
   (use `pathlib`; the engine already branches per-OS for the browser).
4. No secrets, no personal paths, no internal/company names in code or docs.
5. Fill in the PR template.

## Quality bar

- `python -m py_compile install.py runtimes.py src/painel/*.py` must pass.
- The npm tarball must stay clean: `npm pack --dry-run` shows **no** `__pycache__`
  / `.pyc` (the `prepack` script enforces this).
- New runtime support must be additive (don't break existing runtimes).

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
