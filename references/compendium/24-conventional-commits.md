# 24 — Conventional Commits: A Machine-Readable Commit History

This file is a deep dive on **Conventional Commits** — the lightweight convention that turns your commit log from prose into a structured, parseable contract. The throughline: **a commit message is an API.** Humans read it to understand intent; tools read it to decide version bumps, generate changelogs, and trigger releases. Once you accept that commits are consumed by machines as well as people, the entire convention becomes obvious — and the discipline it demands becomes worth paying for.

This builds directly on [file 22 — enterprise engineering practices](22-enterprise-engineering-practices.md) (trunk-based development, CI/CD, squash merges) and complements [file 21 — sprint progress & tracking](21-sprint-progress-and-tracking.md). The payoff of Conventional Commits is only fully realized inside the automated delivery pipeline described there.

---

## 1. Why structured commits exist at all

A normal commit history (`fixed bug`, `wip`, `more changes`, `asdf`) is write-only memory. Nobody can answer basic questions from it: *What changed between v2.3 and v2.4? Was this release backward-compatible? Which commit introduced this regression?* You answer those by reading diffs — expensive, manual, error-prone.

Conventional Commits is "a lightweight convention on top of commit messages [providing] an easy set of rules for creating an explicit commit history; which makes it easier to write automated tools on top of" ([conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0/)). It dovetails with **Semantic Versioning** by describing, in the commit itself, whether a change is a feature, a fix, or a breaking change.

The concrete payoffs the spec advertises ([Conventional Commits summary](https://www.conventionalcommits.org/en/v1.0.0/)):

- **Automatically generating CHANGELOGs.**
- **Automatically determining a semantic version bump** based on the types of commits landed.
- **Communicating the nature of changes** to teammates, the public, and stakeholders.
- **Triggering build and publish processes.**
- **Making it easier to contribute**, by giving a structured history people can explore.

> The unifying idea: encode *intent* (feature / fix / breaking) in a fixed grammar so a parser — not a human — can make release decisions deterministically.

---

## 2. The grammar

The full message structure ([Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)):

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Concrete examples spanning every feature:

```text
feat(parser): add ability to parse arrays
```
```text
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Reviewed-by: Z
Refs: #123
```
```text
feat(api)!: send an email to the customer when a product is shipped

BREAKING CHANGE: the shipment webhook payload now includes a customer object.
```

The three semantic anchors ([Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)):

1. **`fix:`** — patches a bug → correlates with **PATCH** in SemVer.
2. **`feat:`** — introduces a new feature → correlates with **MINOR** in SemVer.
3. **`BREAKING CHANGE:`** (footer) or **`!`** after the type/scope → introduces a breaking API change → correlates with **MAJOR** in SemVer. A breaking change can ride on a commit of *any* type.

---

## 3. The rules that actually matter (from the spec)

The spec is short but precise; these are the MUST/SHOULD statements senior engineers most often get wrong ([Conventional Commits 1.0.0 — Specification](https://www.conventionalcommits.org/en/v1.0.0/)):

- Commits **MUST** be prefixed with a type, optional scope, optional `!`, then a **required terminal colon and space**.
- A scope **MUST** be a noun describing a section of the codebase, in parentheses, e.g. `fix(parser):`.
- The description **MUST** immediately follow the colon-space.
- A body **MAY** follow, but **MUST** begin one blank line after the description; it is free-form and may span multiple paragraphs.
- Footers **MAY** follow one blank line after the body. Each footer is a word token + `: ` (or ` #`) + value — inspired by the git trailer convention. Footer tokens **MUST** use `-` instead of spaces (e.g. `Reviewed-by`), the lone exception being `BREAKING CHANGE`.
- Breaking changes **MUST** be indicated either in the prefix (`!`) or as a footer. As a footer it **MUST** be uppercase `BREAKING CHANGE:` (or the synonym `BREAKING-CHANGE:`). If `!` is used, the footer **MAY** be omitted and the description describes the break.
- Units of information **MUST NOT** be treated as case-sensitive — *except* `BREAKING CHANGE`, which **MUST** be uppercase.

Two subtleties that trip people up:

- **`feat!` vs `feat` + `BREAKING CHANGE:` footer.** Both signal MAJOR. The `!` is the human-visible flag; the footer carries the migration detail. Use the footer (or both) when you need to explain *what* breaks and *how* to migrate — a bare `!` with a terse description gives changelog readers nothing to act on.
- **Footer parsing is greedy.** A footer's value may contain spaces and newlines; parsing terminates only at the next valid token/separator pair. This is why a stray "BREAKING CHANGE-ish" sentence buried in your body can be silently swallowed or, worse, misparsed.

---

## 4. The type vocabulary

The spec only blesses `feat` and `fix`. Everything else comes from the **Angular convention**, which `@commitlint/config-conventional` adopts. Additional types "have no implicit effect in Semantic Versioning (unless they include a BREAKING CHANGE)" ([Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)). The de-facto standard set:

| Type | Meaning | Typical SemVer effect |
|------|---------|------------------------|
| `feat` | New feature | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentation only | none |
| `style` | Formatting, whitespace, semicolons (no logic change) | none |
| `refactor` | Code change that neither fixes a bug nor adds a feature | none |
| `perf` | Performance improvement | PATCH (often) |
| `test` | Adding/correcting tests | none |
| `build` | Build system or external dependencies (npm, webpack) | none |
| `ci` | CI configuration and scripts | none |
| `chore` | Maintenance, no src/test change | none |
| `revert` | Reverts a previous commit | depends |

This 11-type set is the one most teams converge on in practice ([BAVAGA — Conventional Commit Types cheatsheet](https://www.bavaga.com/blog/2025/01/27/my-ultimate-conventional-commit-types-cheatsheet/)). A few judgment calls:

- **`refactor` vs `perf`:** if behavior is identical and the goal is readability/structure → `refactor`. If the goal is measurably faster/leaner → `perf`.
- **`chore` is a trap.** It's the junk drawer. Overusing it ("`chore: stuff`") destroys the signal the convention exists to create. If a change touches dependencies use `build`, CI use `ci`, docs use `docs`.
- **`feat`/`fix` are the only ones consumers care about** in a published library — they're the ones that move the version. Be honest about them.

---

## 5. SemVer automation: the actual payoff

The reason to endure the discipline is that the version number stops being a human decision. **semantic-release** "automates the whole package release workflow including: determining the next version number, generating the release notes, and publishing" — it "removes the immediate connection between human emotions and version numbers" ([semantic-release on GitHub](https://github.com/semantic-release/semantic-release)).

Its default mapping (Angular preset) ([semantic-release](https://github.com/semantic-release/semantic-release)):

| Commit | Release type |
|--------|--------------|
| `fix(pencil): stop graphite breaking under pressure` | **Patch** |
| `feat(pencil): add 'graphiteWidth' option` | **Minor** |
| `perf(pencil): remove graphiteWidth option` + `BREAKING CHANGE:` footer | **Major** |

Note the warning baked into that last row: the `BREAKING CHANGE:` token **must be in the footer** for semantic-release to detect it.

The release pipeline runs on every push to a release branch (`main`, `next`, `beta`) and executes a fixed sequence ([semantic-release](https://github.com/semantic-release/semantic-release)): *verify conditions → get last release (from git tags) → analyze commits → generate notes → create git tag → prepare → publish → notify.* The whole thing is driven by parsing commit messages since the last tag — which is exactly why malformed commits silently break your release math.

Related tooling in this ecosystem ([Conventional Commits — Tooling](https://www.conventionalcommits.org/en/about/)):

- **commitlint** + **conventional-changelog** — lint and generate changelog.
- **release-please** — Google's PR-based release automation (used heavily for monorepos and libraries).
- **python-semantic-release**, **git-semver** — non-Node implementations for polyglot shops.

---

## 6. Enforcement: commitlint + husky

A convention nobody enforces decays in a week. The standard local guard is **commitlint** wired into a Git **`commit-msg`** hook via **husky** ([commitlint — Local setup](https://commitlint.js.org/guides/local-setup.html)).

```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional husky
npx husky init
echo "npx --no -- commitlint --edit \$1" > .husky/commit-msg
```

```js
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // optionally constrain types/scopes:
    // 'type-enum': [2, 'always', ['feat','fix','docs','refactor','perf','test','build','ci','chore','revert']],
    // 'scope-enum': [2, 'always', ['api','auth','db','ui']],
  },
};
```

`commitlint` checks that messages meet the conventional format ([commitlint on GitHub](https://github.com/conventional-changelog/commitlint)). Crucial operational caveat from the maintainers: **local hooks are advisory** — they're for "fast feedback but can easily be tinkered with" (`--no-verify` bypasses them) ([commitlint — Local setup](https://commitlint.js.org/guides/local-setup.html)). To *guarantee* compliance you must **also lint in CI**, where it can't be skipped. Treat the local hook as ergonomics, the CI check as the gate.

---

## 7. The hard part: Conventional Commits meets squash merges

This is where most real teams stumble, because it collides with trunk-based development ([file 22 §4](22-enterprise-engineering-practices.md)). With **squash-and-merge**, "you lose the individual commit messages from the feature branch" — the only thing that lands on `main` is the squash commit message ([Azure DevOps + Conventional Commits, johnnyreilly](https://johnnyreilly.com/azure-devops-pull-requests-conventional-commits)). So the question becomes: *which* message must be conventional?

There are two coherent strategies, and you must pick one:

**Strategy A — Lint the PR title, squash with it.** The PR title is the conventional commit; on squash-merge the platform uses it as the commit message. Teams enforce this with a CI action that lints the PR title. Vonage does exactly this: "a mandatory GitHub action that verifies our PR title follows Conventional Commits... when a PR is merged, the PR title is set as the commit. We use `squash + merge` so all commit history is removed from `main` and only the Conventional Commit remains" ([Vonage — 3 reasons to use Conventional Commits](https://developer.vonage.com/en/blog/3-reasons-why-you-should-use-conventional-commits)). They even append the Jira ID, e.g. `feat: add retry logic (VIV-123)`, which release-please links automatically.

**Strategy B — Lint every commit, use merge (not squash) commits.** semantic-release "works by analyzing *commits*" and "does not know anything about GitHub PRs" ([semantic-release discussion #2362](https://github.com/semantic-release/semantic-release/discussions/2362)). If you want per-commit granularity in the changelog, preserve the individual conventional commits via a real merge instead of squashing.

Two warnings:

- **The default merge message is hostile to the convention.** Azure DevOps defaults to `Merge PR 123: Title` — which is *not* a conventional commit; you must override the merge commit message ([johnnyreilly](https://johnnyreilly.com/azure-devops-pull-requests-conventional-commits)).
- **A branch may contain conflicting prefixes.** A feature branch with both `feat:` and `fix:` commits, squashed, needs a *conscious* PR title naming the net effect ([semantic-release discussion #2362](https://github.com/semantic-release/semantic-release/discussions/2362)). When a PR squashes multiple meaningful changes, you can list them in the squash commit body — release tools like release-please treat those body lines as if part of the message ([Vonage](https://developer.vonage.com/en/blog/3-reasons-why-you-should-use-conventional-commits)).

> Senior takeaway: decide *PR-title-as-commit* (squash) vs *commit-as-commit* (merge) at the org level, enforce it in CI, and configure the merge button accordingly. Mixing the two is how you get a changelog full of `Merge PR 412`.

---

## 8. Monorepos: scope carries the package

In a monorepo the **scope** does double duty — it identifies *which package* changed, so per-package versioning tools can bump only what moved ([Conventional Commits monorepo issue #118](https://github.com/conventional-commits/conventionalcommits.org/issues/118)). The community pattern:

```text
refactor(client): move logout into a composable
chore(backend): implement event handler for xyz events
test(schema): write unit tests for all scenarios
ci(all): set up pipeline to deploy to staging
```

Here scope = app/package name, with a reserved scope like `all`/`root` for cross-cutting changes ([r/github — managing git history in a monorepo](https://www.reddit.com/r/github/comments/1cdrja6/managing_git_history_in_a_monorepo/)). You can enforce that the only allowed scopes are real package names by deriving the `scope-enum` from each `package.json`'s `name` field via packages like `@commitlint/config-pnpm-scopes` ([r/github](https://www.reddit.com/r/github/comments/1cdrja6/managing_git_history_in_a_monorepo/)). Tools like **Lerna** (`--conventional-commits`) and **release-please** then analyze the history, detect which packages changed and at what level, and bump/publish exactly those ([DEV — monorepo with Lerna + conventional commits](https://dev.to/xcanchal/monorepo-using-lerna-conventional-commits-and-github-packages-4m8m)).

This is directly relevant to your event-driven/distributed work: a monorepo of services with `feat(orders):`, `fix(payments):`, `feat(notifications)!:` lets each service version and release independently off one shared history.

---

## 9. Gitmoji and other alternatives

**Gitmoji** is the main alternative: it uses emojis instead of text types — the sparkles emoji for a feature, a bug emoji for a fix, a flame for removing code, a collision symbol for breaking changes ([gitmoji.dev](https://gitmoji.dev)). Both conventions aim at the same goal — readable, maintainable histories — but make different trade-offs ([fredrkl — Conventional Commits](https://fredrkl.com/blog/conventional-commits/)):

- **Conventional Commits:** plain ASCII, trivially machine-parseable, the lingua franca of release tooling. Slightly verbose.
- **Gitmoji:** scannable at a glance, fun, but emojis are harder to grep/parse, render inconsistently across terminals, and have weaker tooling for SemVer automation.

You can have both: tools like **devmoji** decorate conventional commits with emojis, "using Conventional Commits as a standard... [to make] Semantic Versioning as easy as can be" while adding gitmoji-style color ([devmoji on GitHub](https://github.com/folke/devmoji)). For a team that wants automated releases, Conventional Commits is the correct base layer; gitmoji is a cosmetic overlay at best.

---

## 10. Anti-patterns and when *not* to bother

**Anti-patterns:**

- **`chore:` as a dumping ground.** Erodes all signal. Use the specific type.
- **Lying about type to dodge a version bump** (labeling a feature `fix` to avoid a MINOR). It poisons the changelog and misleads consumers about compatibility.
- **`BREAKING CHANGE` in the body instead of the footer** — semantic-release's Angular preset only reliably detects it in the footer; a body mention may be missed ([semantic-release](https://github.com/semantic-release/semantic-release)).
- **Local-hook-only enforcement.** `--no-verify` exists; without a CI check your guarantee is theatre ([commitlint — Local setup](https://commitlint.js.org/guides/local-setup.html)).
- **Conventional commits on the branch, garbage on the squash.** The squash message is the only one that survives — if it's `Merge PR 123`, your branch discipline was wasted ([johnnyreilly](https://johnnyreilly.com/azure-devops-pull-requests-conventional-commits)).
- **Scopes invented per-commit** (`feat(thing-i-touched):`). Drift makes scope useless; constrain with `scope-enum`.

**When it's not worth it:**

- A solo throwaway prototype or a repo with no release/changelog automation downstream — the convention's value is realized by *tools*; with no tools you get a stricter habit and little else (still a fine habit).
- A repo where you genuinely never publish versions and never produce changelogs. Even then, the structured history helps `git log` archaeology — so the bar for *not* doing it is low.

> The honest cost/benefit: Conventional Commits is cheap to adopt and compounds in value the moment you add automated versioning, changelogs, or releases. For any library, shared service, or anything with consumers, it pays for itself almost immediately. For a personal scratchpad, it's optional.

---

## Key sources

- [Conventional Commits 1.0.0 — full specification](https://www.conventionalcommits.org/en/v1.0.0/)
- [Conventional Commits — Tooling list](https://www.conventionalcommits.org/en/about/)
- [semantic-release — automated versioning & publishing](https://github.com/semantic-release/semantic-release)
- [semantic-release — release-notes-generator](https://github.com/semantic-release/release-notes-generator)
- [semantic-release discussion #2362 — PR titles vs commits](https://github.com/semantic-release/semantic-release/discussions/2362)
- [commitlint — repo](https://github.com/conventional-changelog/commitlint) and [Local setup guide](https://commitlint.js.org/guides/local-setup.html)
- [Vonage — 3 Reasons to Use Conventional Commits (squash + PR title + Jira)](https://developer.vonage.com/en/blog/3-reasons-why-you-should-use-conventional-commits)
- [johnnyreilly — Azure DevOps PRs with Conventional Commits](https://johnnyreilly.com/azure-devops-pull-requests-conventional-commits)
- [Conventional Commits monorepo convention — issue #118](https://github.com/conventional-commits/conventionalcommits.org/issues/118)
- [r/github — managing git history in a monorepo](https://www.reddit.com/r/github/comments/1cdrja6/managing_git_history_in_a_monorepo/)
- [DEV — Monorepo using Lerna, Conventional Commits & GitHub Packages](https://dev.to/xcanchal/monorepo-using-lerna-conventional-commits-and-github-packages-4m8m)
- [gitmoji.dev](https://gitmoji.dev) · [devmoji](https://github.com/folke/devmoji) · [fredrkl — Conventional Commits vs Gitmoji](https://fredrkl.com/blog/conventional-commits/)
- [BAVAGA — Conventional Commit Types cheatsheet](https://www.bavaga.com/blog/2025/01/27/my-ultimate-conventional-commit-types-cheatsheet/)
