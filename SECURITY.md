# Security Policy

## north's security model

north is **local-first**:

- It runs on your machine and **only reads** your plan files (`plan-build/`,
  `.planning/`). It never writes to them.
- **No cloud, no telemetry, no analytics, no network calls** from the engine.
  The only outbound tools are the ones *you* invoke (e.g. `git`, `gh` for
  authorship/GitHub features) on your own machine.
- The npm package is a launcher that detects your Python and runs the bundled
  installer — it does not download or execute remote code at runtime.

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Report privately via **GitHub Security Advisories**:
[Report a vulnerability](https://github.com/kayquesanmartin/north-cli/security/advisories/new)

Include: a description, affected version (`north status` / `package.json`),
steps to reproduce, and impact. We aim to acknowledge within **72 hours** and
to ship a fix or mitigation for confirmed issues as quickly as is practical,
crediting you unless you prefer to remain anonymous.

## Scope

In scope: the engine (`src/painel`), the installer (`install.py`, `runtimes.py`),
the launcher (`bin/`), and the generated runtime integrations.

Examples of what we care about: command/path injection via crafted plan files or
arguments, the launcher running unexpected executables, the npm tarball shipping
sensitive or executable artifacts, or any unintended network/file write.

## Good hygiene for contributors

- Never commit secrets, tokens, personal absolute paths, or internal/company
  names. Defaults must be generic.
- The status line and engine read a local cache only — they must not run
  discovery or arbitrary git on every render.
