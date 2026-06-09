# 22 — Enterprise Engineering Practices: How Big Tech Actually Builds Software

This file is the answer to "what does big tech assume as the default way of working, how do their engineers think, how is work organized *before* coding, and how is coding *actually done*?" It is deliberately broad — culture, process, and engineering mechanics — because in practice they are inseparable. The throughline: **at scale, the codebase outlives any individual, so every practice optimizes for the health of the system over time, not the speed of a single change.**

This is the practical, organizational complement to the architectural files. Where [file 10](10-requirements-process.md) covered SDLC and process, and [files 14–15](14-spec-driven-development.md) covered the documents, this file is about *how a senior engineer at a high-performing company carries themselves through the full loop.*

---

## 1. The mindset: how big-tech engineers think

A few mental defaults distinguish senior engineers at high-performing orgs. These are cultural assumptions, not tools:

- **Code health over personal velocity.** The canonical statement of this is Google's: "the primary purpose of code review is to make sure that the overall code health of the codebase is improving over time" ([Google Eng Practices — The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html)). Every review, every CL, is judged by whether it leaves the system better.
- **There is no perfect code, only better code.** Reviewers seek *continuous improvement*, not perfection — a change that improves maintainability shouldn't be blocked for weeks because it isn't flawless ([Google Eng Practices](https://google.github.io/eng-practices/review/reviewer/standard.html)).
- **Ownership and accountability without blame.** Engineers own outcomes end-to-end (you build it, you run it), but failures are treated as system/process failures, not personal ones (see §8 on blameless postmortems).
- **Optimize for the reader, not the writer.** Code is read far more than written. Clarity beats cleverness.
- **Build only what's needed now.** Avoid speculative generality — "implement only what is needed now and not speculative functionality" ([bssw.io summary of Google's guide](https://bssw.io/items/google-guidance-on-code-review)). YAGNI is a cultural value, not just an acronym.
- **Default to writing things down.** Decisions, designs, and incidents are documented so they scale beyond a hallway conversation and survive personnel changes.

> The unifying idea: a senior engineer is accountable for the *long-term cost* of their decisions, paid by everyone who touches the code later. That accountability is what all the practices below are protecting.

---

## 2. Before coding: how work gets organized

High-performing teams resist the urge to jump straight to code. The "before" phase has a recognizable shape:

### Design before implementation
Non-trivial work starts with a **design doc / RFC** (covered in depth in [file 15](15-engineering-documents.md)) that states the problem, the proposed approach, alternatives considered, and trade-offs — circulated for async review *before* significant code is written. This is the cheapest place to catch a bad idea: a design flaw caught in a doc costs a comment; the same flaw caught after launch costs a migration.

### Right-sized planning
Work is decomposed into small, independently shippable units (see [file 20 — sprint planning & slicing](20-sprint-planning-and-scoping.md)). The bias is toward **small batches**: small changes are easier to reason about, review, test, and revert.

### Readiness gates
Before an item is "ready to build," ambiguity is resolved — acceptance criteria, dependencies, non-functional requirements, and the test approach are known (the Definition of Ready, [file 20 §3](20-sprint-planning-and-scoping.md)).

### Tooling and environment first
A new engineer at a mature org can typically get a working dev environment, run the tests, and ship a trivial change on day one — because the org invests heavily in **developer experience**: reproducible environments, fast builds, and one-command setup. Friction in the inner loop is treated as a tax paid by every engineer, every day.

---

## 3. Source control strategy: monorepo vs polyrepo

There is no single right answer, but big tech's most-discussed choice is the **monorepo** — a single, unified repository for many projects.

**Why Google uses one** ([Why Google Stores Billions of Lines of Code in a Single Repository](https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository/), [LinkedIn summary](https://www.linkedin.com/pulse/monorepos-like-google-uses-benefits-nadir-laskar-x93rc)):

- **Single source of truth** — shared libraries are always at one version; no diamond-dependency hell.
- **Atomic cross-project changes** — one commit can update an API and all its callers simultaneously.
- **Visibility and code reuse** — teams discover and reuse code across project boundaries.
- **Consistency at scale** — uniform tooling, standards, and CI across thousands of engineers.

The trade-off: a monorepo demands **sophisticated tooling** (scalable VCS, build systems like Bazel, and strong CI) to remain workable; without it, the repo becomes unusably slow ([LinkedIn](https://www.linkedin.com/pulse/monorepos-like-google-uses-benefits-nadir-laskar-x93rc)). Many companies succeed with polyrepos plus good package management instead. The decision hinges on tooling investment and how tightly coupled your projects are.

---

## 4. Branching: trunk-based development

The branching model high-performing teams converge on is **trunk-based development (TBD)** — all developers integrate small, frequent changes into a single main branch ("trunk"), kept always in a deploy-ready state ([CircleCI — TBD vs feature branches](https://circleci.com/blog/trunk-vs-feature-based-dev/); [Atlassian — Trunk-based Development](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)).

Why it wins over long-lived feature branches (GitFlow):

- **TBD is a required practice for true continuous integration** — CI literally means continuously integrating everyone's work into the mainline, not once a release ([Atlassian](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)).
- **Small changes → easy reviews** — reviewers inspect a few lines, not pages of a months-old branch ([Atlassian](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)).
- **No painful merges / integration hell** — frequent integration means conflicts are tiny and constant rather than huge and rare ([CircleCI](https://circleci.com/blog/trunk-vs-feature-based-dev/)).

The operating rules ([Atlassian](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)):

- Keep the trunk **green** (deployable at every commit).
- Develop in **small batches**; merge to trunk **at least once a day**.
- Use **short-lived** branches (hours to a couple of days), then delete them; keep **three or fewer** active branches.
- Lean on **comprehensive automated tests** and **fast builds** as the safety net.

> The hard prerequisite: TBD without strong automated testing is reckless, because a bad commit breaks everyone. The discipline of "test thoroughly before pushing to main" is what makes it safe ([CircleCI](https://circleci.com/blog/trunk-vs-feature-based-dev/)).

---

## 5. Code review: the central ritual

Code review is the most consistent cultural practice across big tech. Google's publicly documented guidelines are the de-facto industry reference ([Google's Engineering Practices](https://github.com/google/eng-practices)).

**Terminology:** a unit of change is a **CL** ("changelist"; elsewhere a PR/patch); approval is **LGTM** ("Looks Good To Me") ([Google Eng Practices](https://github.com/google/eng-practices)).

**What reviewers actually look at** ([bssw.io](https://bssw.io/items/google-guidance-on-code-review)): design, functionality, complexity, tests, naming, comments, style, and documentation.

**The principles that make review work:**

- **Approve once it improves code health** — even if imperfect. Seek continuous improvement, not perfection ([Google Eng Practices](https://google.github.io/eng-practices/review/reviewer/standard.html)).
- **Mark non-blocking polish as "Nit:"** so the author knows it's optional ([Google Eng Practices](https://google.github.io/eng-practices/review/reviewer/standard.html)).
- **Every human-written line should be reviewed** — and tests/docs ship in the *same* CL as the code ([bssw.io](https://bssw.io/items/google-guidance-on-code-review)).
- **Keep CLs small and cohesive** — split large ones; small CLs review faster and more thoroughly ([bssw.io](https://bssw.io/items/google-guidance-on-code-review)).
- **It's the author's job to fix the CL, not the reviewer's** — and insist on cleanup *now*, because "clean it up later" is how codebases rot ([bssw.io](https://bssw.io/items/google-guidance-on-code-review)).
- **Be courteous; praise good code.** Positive reinforcement offsets change requests and is a real motivator ([bssw.io](https://bssw.io/items/google-guidance-on-code-review)).
- **Don't let reviews stall.** In a TBD/CI world, review promptly — reviewing daily prevents catch-up pile-ups that make reviewers rubber-stamp ([Atlassian](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)).

---

## 6. CI/CD: the automated path to production

Continuous Integration / Continuous Delivery is the machinery that makes trunk-based development and frequent deploys safe.

- **CI** runs the build and the full automated test suite on **every commit to main**, blocking integration of anything that breaks the build ([CircleCI](https://circleci.com/blog/trunk-vs-feature-based-dev/)).
- **CD** automatically promotes passing builds through environments (e.g., to staging, then production) ([CircleCI](https://circleci.com/blog/trunk-vs-feature-based-dev/)).
- **The pipeline shape:** fast unit tests first (fail fast), then heavier integration and end-to-end tests against staging/production-like environments later in the pipeline ([Atlassian](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)).
- **Fast builds are a feature.** Caching and parallelization keep build/test times low so the rhythm of frequent merges is sustainable ([Atlassian](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)).
- **Fix broken builds immediately.** A red trunk blocks the whole team, so recovery is the top priority ([CircleCI](https://circleci.com/blog/trunk-vs-feature-based-dev/)).

Progressive delivery (canary, blue-green, staged rollouts) sits on top of CD to limit blast radius — covered alongside feature flags next.

---

## 7. Decoupling deploy from release: feature flags

A defining big-tech practice: **deployment and release are separate events.** Code is deployed to production "dark" behind a **feature flag** and released by flipping the flag — not by deploying ([Unleash — feature flags for TBD](https://www.getunleash.io/blog/using-feature-flags-to-enable-trunk-based-development); [Flagsmith](https://www.flagsmith.com/blog/trunk-based-development-feature-flags)).

This unlocks several things at once:

- **Trunk-based development at scale** — incomplete features can be merged to main behind an off flag, so work integrates continuously without long-lived branches ([Unleash](https://www.getunleash.io/blog/using-feature-flags-to-enable-trunk-based-development)).
- **Progressive delivery** — expose a feature to 1% → 10% → 100% of users while watching real-time metrics ([LaunchDarkly — Feature Flags 101](https://launchdarkly.com/blog/what-are-feature-flags/)).
- **Instant kill switch** — if a feature misbehaves in production, disable the flag; execution stops immediately with **no rollback, redeploy, or waiting**, cutting MTTR from hours to minutes ([LaunchDarkly](https://launchdarkly.com/blog/what-are-feature-flags/)).
- **Experimentation** — A/B tests and targeted rollouts run off the same flagging system.

The cost: flags are debt. Stale flags accumulate and create combinatorial complexity, so mature teams track and **remove flags** once a feature is fully rolled out.

---

## 8. Reliability culture: SRE, on-call, and blameless postmortems

Once software is in production, big tech treats **operating it** as a first-class engineering discipline — Site Reliability Engineering (SRE).

### SLOs and error budgets
Reliability is defined by **Service Level Objectives**, and the gap below 100% is an **error budget** — a quantified allowance for failure. As long as the budget isn't exhausted, the team ships features fast; when it's blown, the team shifts focus to reliability. This converts "move fast" vs. "stay reliable" from an argument into a number.

### On-call: you build it, you run it
Engineers carry pagers for the services they own. Ownership of production outcomes is what makes them care about operability, observability, and graceful failure — not just passing tests.

### Blameless postmortems
After a significant incident, the team writes a **postmortem** that focuses on **what** went wrong, not **who** caused it — "no individual or team is blamed for the incident" ([Google SRE — Postmortem Culture](https://sre.google/workbook/postmortem-culture/)). The blameless stance treats "human error" as the *start* of the investigation into systemic causes, not the end ([incident.io — postmortem best practices](https://incident.io/blog/sre-incident-postmortem-best-practices)).

A good postmortem contains ([incident.io](https://incident.io/blog/sre-incident-postmortem-best-practices); [Google SRE](https://sre.google/workbook/postmortem-culture/)):

- **Summary** — what happened, when, what was affected (2–3 sentences).
- **Impact** — quantified (users affected, error rate, SLO budget consumed).
- **Timeline** — key events with UTC timestamps, alert to resolution.
- **Contributing factors** — systemic causes, framed blamelessly (process gaps, tooling limits, doc failures).
- **What went well** — reinforce good response behaviors.
- **Action items** — *specific, owned by one named person, due-dated, and prioritized* into mitigative vs. preventative ([incident.io](https://incident.io/blog/sre-incident-postmortem-best-practices)).

Common triggers for a mandatory postmortem: user-visible downtime past a threshold, **data loss of any kind**, on-call intervention (rollback, traffic rerouting), or a monitoring failure ([Google SRE — Postmortem Culture (SRE Book)](https://sre.google/sre-book/postmortem-culture/)). The practice only works if writing good postmortems is **rewarded and celebrated**, not punished ([Google SRE](https://sre.google/sre-book/postmortem-culture/)).

> Why blameless matters operationally: if people fear blame, they hide information, and you lose the data needed to fix the real cause. Psychological safety is a reliability mechanism, not a nicety.

---

## 9. Measuring engineering performance: DORA

The industry-standard, research-backed way to measure software delivery is the **DORA metrics**, from Google's DevOps Research and Assessment team ([DORA — Metrics guide](https://dora.dev/guides/dora-metrics/); [Google Cloud — Four Keys](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)).

| Metric | Measures | What it tells you |
|--------|----------|-------------------|
| **Deployment Frequency** | How often you successfully release to production | Throughput / velocity |
| **Lead Time for Changes** | Time from commit to running in production | Throughput / velocity |
| **Change Failure Rate** | % of deployments causing a production failure | Stability / quality |
| **Failed Deployment Recovery Time** (MTTR) | Time to recover from a failed deployment | Stability / resilience |

The first two measure **velocity**; the last two measure **stability** ([Google Cloud](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)). The crucial DORA finding: these are **not a trade-off** — elite teams are fast *and* stable, and are roughly twice as likely to meet organizational goals ([Google Cloud](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)). A fifth metric, **Reliability**, was later added ([DX — DORA metrics guide](https://getdx.com/blog/dora-metrics/)).

Elite-tier benchmarks ([DX](https://getdx.com/blog/dora-metrics/)): deploy multiple times/day, lead time < 1 day, MTTR < 1 hour.

> Use DORA to find bottlenecks and improve the *system*, never to rank individuals. Like velocity (file 21), the instant it becomes a personal scoreboard it gets gamed.

---

## 10. Documentation and knowledge sharing

Big tech scales knowledge by writing it down in durable, discoverable forms:

- **Design docs / RFCs / ADRs** — decisions and their rationale (see [file 15](15-engineering-documents.md)).
- **Runbooks / playbooks** — step-by-step operational procedures for on-call.
- **Postmortems** — a searchable archive of past failures so the same incident isn't relearned.
- **Onboarding docs and codelabs** — so new engineers ramp without consuming senior time.
- **READMEs and inline docs that ship with code** — tests and docs in the same CL as the change ([bssw.io](https://bssw.io/items/google-guidance-on-code-review)).

The principle: institutional knowledge that lives only in someone's head is a single point of failure.

---

## 11. The full loop (how it all fits together)

A senior engineer's path for a non-trivial change at a high-performing org:

1. **Understand & design** — write/refine a design doc; get async review; resolve ambiguity (DoR).
2. **Slice** — break into small, independently shippable, vertically-sliced units ([file 20](20-sprint-planning-and-scoping.md)).
3. **Branch short-lived from trunk** — or commit straight to trunk behind a flag.
4. **Write code + tests together** — small, cohesive CLs; optimize for the reader.
5. **CI runs on every commit** — fast tests gate the merge; keep trunk green.
6. **Code review** — small CL, prompt LGTM, "Nit:" for polish, author fixes.
7. **Merge to trunk** (at least daily) — integrate continuously.
8. **CD deploys** — automatically promoted through environments, code shipped dark behind a flag.
9. **Progressive release** — flip the flag for 1% → 100%, watch metrics, kill instantly if needed.
10. **Operate** — own it on-call; observe SLOs and error budget.
11. **Learn** — blameless postmortem on incidents; feed action items and DORA trends back into the process.

---

## 12. Anti-patterns big tech actively avoids

- **Long-lived feature branches & merge hell** — the opposite of CI; integration risk balloons.
- **"Clean it up later"** — deferred cleanup is how codebases degenerate ([bssw.io](https://bssw.io/items/google-guidance-on-code-review)).
- **Giant CLs / PRs** — un-reviewable; reviewers rubber-stamp them.
- **Speculative generality (over-engineering)** — building for imagined future needs ([bssw.io](https://bssw.io/items/google-guidance-on-code-review)).
- **Deploy == release** — coupling them removes the kill switch and forces risky big-bang launches.
- **Blame culture** — punishing individuals for incidents hides the information needed to actually fix systems ([Google SRE](https://sre.google/workbook/postmortem-culture/)).
- **Metrics as a personal scoreboard** — weaponizing DORA or velocity destroys their signal.
- **Hero culture / bus factor of one** — undocumented knowledge in one person's head; no postmortems, no runbooks.

---

## Key sources

- [Google's Engineering Practices documentation](https://github.com/google/eng-practices) and [The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html) — the canonical code-review philosophy (code health, continuous improvement, "Nit:", small CLs).
- [bssw.io — Google Guidance on Code Review](https://bssw.io/items/google-guidance-on-code-review) — distilled review practices.
- [Atlassian — Trunk-Based Development](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development) and [CircleCI — Trunk vs. feature-based](https://circleci.com/blog/trunk-vs-feature-based-dev/) — TBD rules, small batches, CI/CD.
- [Why Google Stores Billions of Lines of Code in a Single Repository](https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository/) — the monorepo rationale.
- [LaunchDarkly — Feature Flags 101](https://launchdarkly.com/blog/what-are-feature-flags/), [Unleash](https://www.getunleash.io/blog/using-feature-flags-to-enable-trunk-based-development), [Flagsmith](https://www.flagsmith.com/blog/trunk-based-development-feature-flags) — decoupling deploy from release, progressive delivery, MTTR.
- [Google SRE — Postmortem Culture](https://sre.google/workbook/postmortem-culture/) and [SRE Book](https://sre.google/sre-book/postmortem-culture/), plus [incident.io best practices](https://incident.io/blog/sre-incident-postmortem-best-practices) — blameless postmortems and action items.
- [DORA — Metrics guide](https://dora.dev/guides/dora-metrics/), [Google Cloud — Four Keys](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance), [DX — DORA guide](https://getdx.com/blog/dora-metrics/) — the four (plus one) delivery metrics and benchmarks.
